"""Schema cho module xác thực."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AuthRegisterRequest(BaseModel):
    """Yêu cầu đăng ký tài khoản."""

    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(default="student")


class AuthLoginRequest(BaseModel):
    """Yêu cầu đăng nhập."""

    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    """Phản hồi token sau khi đăng nhập."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class AuthProfileResponse(BaseModel):
    """Thông tin user trả về cho FE."""

    id: str
    full_name: str
    email: EmailStr
    role: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
