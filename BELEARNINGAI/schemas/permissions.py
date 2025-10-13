"""Schemas cho module kiểm tra quyền."""
from typing import List

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    resource: str
    actions: List[str]


class RolePermissionMatrix(BaseModel):
    """Mô tả bảng quyền cho từng vai trò."""

    role: str
    permissions: List[PermissionResponse]
