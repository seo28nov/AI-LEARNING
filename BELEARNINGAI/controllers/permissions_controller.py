"""Controller kiểm tra quyền truy cập."""
from schemas.permissions import PermissionResponse
from services.permissions_service import get_user_permissions


async def handle_permissions(current_user: dict) -> PermissionResponse:
    user_id = current_user.get("sub", "demo-user")
    return await get_user_permissions(user_id)
