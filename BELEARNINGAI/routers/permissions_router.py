"""Router kiểm tra quyền của người dùng."""
from fastapi import APIRouter, Depends

from controllers.permissions_controller import handle_permissions
from schemas.permissions import PermissionResponse
from middleware.auth import get_current_user

router = APIRouter(tags=["permissions"])


@router.get("/me", response_model=PermissionResponse)
async def my_permissions_route(current_user: dict = Depends(get_current_user)):
    return await handle_permissions(current_user)
