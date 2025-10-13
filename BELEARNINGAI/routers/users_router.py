"""Router người dùng."""
from typing import List

from fastapi import APIRouter, Depends, Header

from controllers.user_controller import handle_deactivate_user, handle_get_profile, handle_list_users
from models.models import UserResponse

router = APIRouter(tags=["users"])


def get_current_user(user_id: str | None = Header(default="demo-user")) -> str:
    """Giả lập lấy user hiện tại."""

    return user_id or "demo-user"


@router.get("/me", response_model=UserResponse, summary="Thông tin cá nhân")
async def me_route(current_user: str = Depends(get_current_user)) -> UserResponse:
    """Lấy profile người dùng hiện tại."""

    return await handle_get_profile(current_user)


@router.get("/", response_model=List[UserResponse], summary="Danh sách người dùng")
async def list_users_route() -> List[UserResponse]:
    """Lấy danh sách tất cả người dùng."""

    return await handle_list_users()


@router.patch("/{user_id}/deactivate", response_model=UserResponse, summary="Vô hiệu hóa user")
async def deactivate_user_route(user_id: str) -> UserResponse:
    """Vô hiệu hóa user."""

    return await handle_deactivate_user(user_id)
