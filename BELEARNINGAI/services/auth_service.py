"""Dịch vụ xử lý xác thực người dùng."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError

from config.config import get_settings
from models.models import (
    LoginRequest,
    RefreshRequest,
    RefreshTokenDocument,
    RegisterRequest,
    TokenResponse,
    UserDocument,
    UserResponse,
)
from utils.security import (
    build_fingerprint,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_session_id,
    hash_password,
    hash_token,
    verify_password,
)

_settings = get_settings()


async def _ensure_unique_email(email: str) -> None:
    existing = await UserDocument.find_one(UserDocument.email == email)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã tồn tại")


async def _persist_refresh_token(
    *,
    user_id: str,
    refresh_token: str,
    session_id: str,
    fingerprint: Optional[str],
) -> None:
    token_hash = hash_token(refresh_token)
    expire_days = _settings.refresh_token_expire_days
    expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)

    await RefreshTokenDocument(
        user_id=user_id,
        token_hash=token_hash,
        session_id=session_id,
        fingerprint=fingerprint,
        expires_at=expires_at,
    ).insert()

    max_sessions = 5
    query = RefreshTokenDocument.find(RefreshTokenDocument.user_id == user_id).sort("created_at")
    active_tokens = await query.to_list()
    if len(active_tokens) > max_sessions:
        for token in active_tokens[: len(active_tokens) - max_sessions]:
            await token.delete()


async def register(request: RegisterRequest) -> UserResponse:
    """Đăng ký tài khoản mới."""

    email = request.email.lower()
    await _ensure_unique_email(email)

    password_hash = hash_password(request.password)
    now = datetime.now(timezone.utc)

    user = UserDocument(
        email=email,
        full_name=request.full_name,
        role=request.role,
        avatar_url=request.avatar_url,
        profile=request.profile,
        preferences=request.preferences,
        password_hash=password_hash,
        is_active=True,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    await user.insert()

    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def login(request: LoginRequest, http_request: Request) -> TokenResponse:
    """Đăng nhập và sinh token."""

    email = request.email.lower()
    user = await UserDocument.find_one(UserDocument.email == email)
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Thông tin đăng nhập không hợp lệ")

    fingerprint = build_fingerprint(http_request)
    session_id = generate_session_id()

    access_payload = {"sub": str(user.id), "role": user.role.value, "session_id": session_id}
    refresh_payload = {"sub": str(user.id), "session_id": session_id}

    access_token = create_access_token(access_payload)
    refresh_token = create_refresh_token(refresh_payload)

    await _persist_refresh_token(
        user_id=str(user.id),
        refresh_token=refresh_token,
        session_id=session_id,
        fingerprint=fingerprint,
    )

    now = datetime.now(timezone.utc)
    user.last_login = now
    user.status = "active"
    user.updated_at = now
    await user.save()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=_settings.access_token_expire_minutes * 60,
        refresh_expires_in=_settings.refresh_token_expire_days * 24 * 60 * 60,
    )


async def refresh_token(payload: RefreshRequest, http_request: Request) -> TokenResponse:
    """Làm mới token dựa trên refresh token hợp lệ."""

    try:
        decoded = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token không hợp lệ")

    user_id = decoded.get("sub")
    session_id = decoded.get("session_id")
    if user_id is None or session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token thiếu thông tin")

    token_hash = hash_token(payload.refresh_token)
    stored = await RefreshTokenDocument.find_one(
        RefreshTokenDocument.token_hash == token_hash,
        RefreshTokenDocument.user_id == user_id,
        RefreshTokenDocument.session_id == session_id,
    )
    if stored is None or stored.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token đã bị thu hồi")
    if stored.expires_at < datetime.now(timezone.utc):
        await stored.delete()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token đã hết hạn")

    fingerprint = build_fingerprint(http_request)
    if stored.fingerprint != fingerprint:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Fingerprint không khớp")

    user = await UserDocument.get(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tài khoản không khả dụng")

    access_payload = {"sub": str(user.id), "role": user.role.value, "session_id": session_id}
    access_token = create_access_token(access_payload)

    remaining = int((stored.expires_at - datetime.now(timezone.utc)).total_seconds())
    return TokenResponse(
        access_token=access_token,
        refresh_token=payload.refresh_token,
        expires_in=_settings.access_token_expire_minutes * 60,
        refresh_expires_in=max(0, remaining),
    )


async def revoke_session(session_id: str, user_id: str) -> None:
    """Thu hồi refresh token theo session."""

    tokens = await RefreshTokenDocument.find(
        RefreshTokenDocument.user_id == user_id,
        RefreshTokenDocument.session_id == session_id,
    ).to_list()
    for token in tokens:
        token.revoked_at = datetime.now(timezone.utc)
        await token.save()


async def logout(payload: RefreshRequest, http_request: Request) -> None:
    """Thu hồi refresh token dựa trên token người dùng gửi lên."""

    try:
        decoded = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token không hợp lệ")

    user_id = decoded.get("sub")
    session_id = decoded.get("session_id")
    if user_id is None or session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token thiếu thông tin")

    fingerprint = build_fingerprint(http_request)
    token_hash = hash_token(payload.refresh_token)
    stored = await RefreshTokenDocument.find_one(
        RefreshTokenDocument.token_hash == token_hash,
        RefreshTokenDocument.user_id == user_id,
        RefreshTokenDocument.session_id == session_id,
    )
    if stored is None:
        return
    if stored.fingerprint != fingerprint:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Fingerprint không khớp")

    stored.revoked_at = datetime.now(timezone.utc)
    await stored.save()
