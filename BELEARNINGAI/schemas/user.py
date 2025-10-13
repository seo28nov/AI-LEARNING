"""Schemas cho module người dùng."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSummary(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: str
    status: str
    avatar_url: Optional[str] = None


class UserDetail(UserSummary):
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
