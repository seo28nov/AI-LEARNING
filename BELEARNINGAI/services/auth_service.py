"""Dịch vụ xử lý xác thực người dùng."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError

from config.config import get_settings
from models.models import (
    LoginRequest,
    PasswordResetTokenDocument,
    RefreshRequest,
    RefreshTokenDocument,
    RegisterRequest,
    TokenResponse,
    UserDocument,
    UserResponse,
    VerificationTokenDocument,
)
from utils.email import (
    generate_reset_token,
    generate_verification_token,
    get_token_expiry,
    send_reset_password_email,
    send_verification_email,
    send_welcome_email,
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


async def request_email_verification(user_id: str) -> str:
    """Tạo và gửi email xác thực cho người dùng.
    
    Args:
        user_id: ID người dùng cần xác thực
        
    Returns:
        Token xác thực (để testing)
    """
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    if user.status == "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã được xác thực")
    
    # Tạo token mới
    token = generate_verification_token()
    expires_at = get_token_expiry(hours=24)
    
    # Lưu token vào database
    verification_token = VerificationTokenDocument(
        user_id=str(user.id),
        token=token,
        token_type="email_verification",
        expires_at=expires_at,
    )
    await verification_token.insert()
    
    # Gửi email
    await send_verification_email(user.email, token, user.full_name)
    
    return token


async def verify_email(token: str) -> UserResponse:
    """Xác thực email bằng token.
    
    Args:
        token: Token xác thực
        
    Returns:
        Thông tin người dùng sau khi xác thực
    """
    # Tìm token trong database
    verification = await VerificationTokenDocument.find_one(
        VerificationTokenDocument.token == token,
        VerificationTokenDocument.token_type == "email_verification",
    )
    
    if verification is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token không hợp lệ")
    
    if verification.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token đã được sử dụng")
    
    if verification.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token đã hết hạn")
    
    # Cập nhật trạng thái user
    user = await UserDocument.get(verification.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    user.status = "active"
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    # Đánh dấu token đã sử dụng
    verification.used_at = datetime.now(timezone.utc)
    await verification.save()
    
    # Gửi email chào mừng
    await send_welcome_email(user.email, user.full_name)
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def request_password_reset(email: str) -> bool:
    """Gửi email reset mật khẩu.
    
    Args:
        email: Email người dùng
        
    Returns:
        True nếu thành công
    """
    email = email.lower()
    user = await UserDocument.find_one(UserDocument.email == email)
    
    # Không tiết lộ thông tin user có tồn tại hay không
    if user is None:
        return True
    
    # Tạo token reset
    token = generate_reset_token()
    expires_at = get_token_expiry(hours=1)  # Token reset chỉ có hiệu lực 1 giờ
    
    # Lưu token vào database
    reset_token = PasswordResetTokenDocument(
        user_id=str(user.id),
        token=token,
        expires_at=expires_at,
    )
    await reset_token.insert()
    
    # Gửi email
    await send_reset_password_email(user.email, token, user.full_name)
    
    return True


async def reset_password(token: str, new_password: str) -> bool:
    """Đặt lại mật khẩu bằng token.
    
    Args:
        token: Token reset
        new_password: Mật khẩu mới
        
    Returns:
        True nếu thành công
    """
    # Validate mật khẩu mới
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu phải có ít nhất 8 ký tự"
        )
    
    # Tìm token trong database
    reset_token_doc = await PasswordResetTokenDocument.find_one(
        PasswordResetTokenDocument.token == token,
    )
    
    if reset_token_doc is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token không hợp lệ")
    
    if reset_token_doc.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token đã được sử dụng")
    
    if reset_token_doc.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token đã hết hạn")
    
    # Cập nhật mật khẩu
    user = await UserDocument.get(reset_token_doc.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    # Đánh dấu token đã sử dụng
    reset_token_doc.used_at = datetime.now(timezone.utc)
    await reset_token_doc.save()
    
    # Thu hồi tất cả refresh tokens của user (bắt buộc đăng nhập lại)
    tokens = await RefreshTokenDocument.find(
        RefreshTokenDocument.user_id == str(user.id)
    ).to_list()
    for token_doc in tokens:
        token_doc.revoked_at = datetime.now(timezone.utc)
        await token_doc.save()
    
    return True
