"""Dịch vụ xử lý thông tin người dùng."""
from datetime import datetime
from typing import List

from models.models import UserResponse, UserRole


async def get_user_profile(user_id: str) -> UserResponse:
    """Giả lập lấy thông tin user."""

    return UserResponse.model_validate(
        {
            "_id": user_id,
            "email": "student@example.com",
            "full_name": "Student Demo",
            "role": UserRole.student,
            "avatar_url": None,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
    )


async def list_users() -> List[UserResponse]:
    """Giả lập danh sách user."""

    return [await get_user_profile("demo-user")]


async def deactivate_user(user_id: str) -> UserResponse:
    """Giả lập vô hiệu hóa user."""

    profile = await get_user_profile(user_id)
    profile.is_active = False
    profile.updated_at = datetime.utcnow()
    return profile
