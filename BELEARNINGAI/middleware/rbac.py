"""Middleware kiểm tra quyền truy cập (placeholder)."""
from fastapi import Depends, HTTPException, status

from middleware.auth import get_current_user


def require_roles(*allowed_roles: str):
    """Factory tạo dependency kiểm tra role người dùng."""

    async def checker(user=Depends(get_current_user)) -> dict:
        role = user.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập")
        return user

    return checker
