"""Hàm bảo mật dùng chung cho dịch vụ xác thực."""
from datetime import datetime, timedelta, timezone
import hashlib
import uuid
from typing import Any, Dict

from fastapi import Request
from jose import jwt
from passlib.context import CryptContext

from config.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_settings = get_settings()


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng bcrypt."""

    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Kiểm tra mật khẩu người dùng."""

    return pwd_context.verify(password, password_hash)


def _token_payload(base_payload: Dict[str, Any], expires_delta: timedelta) -> Dict[str, Any]:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = base_payload.copy()
    payload.update({"exp": expire})
    return payload


def create_access_token(data: Dict[str, Any]) -> str:
    """Sinh access token JWT."""

    to_encode = _token_payload(data, timedelta(minutes=_settings.access_token_expire_minutes))
    return jwt.encode(to_encode, _settings.jwt_secret_key, algorithm=_settings.jwt_algorithm)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Sinh refresh token JWT."""

    expire_days = getattr(_settings, "refresh_token_expire_days", 7)
    to_encode = _token_payload(data, timedelta(days=expire_days))
    return jwt.encode(to_encode, _settings.jwt_secret_key, algorithm=_settings.jwt_algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    """Giải mã JWT, trả payload."""

    return jwt.decode(token, _settings.jwt_secret_key, algorithms=[_settings.jwt_algorithm])


def generate_session_id() -> str:
    """Sinh mã phiên duy nhất."""

    return uuid.uuid4().hex


def build_fingerprint(request: Request) -> str:
    """Sinh fingerprint dựa trên user-agent và IP."""

    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    raw = f"{user_agent}|{ip}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def hash_token(raw_token: str) -> str:
    """Băm refresh token trước khi lưu DB."""

    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
