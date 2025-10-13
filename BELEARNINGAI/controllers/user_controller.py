"""Controller người dùng."""
from typing import List

from models.models import UserResponse
from services.user_service import deactivate_user, get_user_profile, list_users


async def handle_get_profile(user_id: str) -> UserResponse:
    """Trả về thông tin profile."""

    return await get_user_profile(user_id)


async def handle_list_users() -> List[UserResponse]:
    """Danh sách người dùng."""

    return await list_users()


async def handle_deactivate_user(user_id: str) -> UserResponse:
    """Vô hiệu hóa người dùng."""

    return await deactivate_user(user_id)
