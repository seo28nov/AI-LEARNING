"""Controller người dùng."""
from typing import Optional

from fastapi import HTTPException, status

from services.user_service import (
    get_user_profile,
    update_user_profile,
    list_users,
    deactivate_user,
    activate_user,
    change_user_role
)


async def handle_get_profile(user_id: str) -> dict:
    """Lấy thông tin profile người dùng."""
    
    return await get_user_profile(user_id)


async def handle_update_profile(user_id: str, payload: dict) -> dict:
    """Cập nhật profile."""
    
    return await update_user_profile(user_id, payload)


async def handle_list_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    search: Optional[str] = None
) -> dict:
    """Danh sách người dùng (admin only)."""
    
    users, total = await list_users(
        skip=skip,
        limit=limit,
        role=role,
        search=search
    )
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_deactivate_user(user_id: str, admin_id: str) -> dict:
    """Vô hiệu hóa người dùng (admin only)."""
    
    return await deactivate_user(user_id, admin_id)


async def handle_activate_user(user_id: str, admin_id: str) -> dict:
    """Kích hoạt lại người dùng (admin only)."""
    
    return await activate_user(user_id, admin_id)


async def handle_change_role(user_id: str, new_role: str, admin_id: str) -> dict:
    """Thay đổi vai trò người dùng (admin only)."""
    
    if new_role not in ["student", "instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: student, instructor, or admin"
        )
    
    return await change_user_role(user_id, new_role, admin_id)
