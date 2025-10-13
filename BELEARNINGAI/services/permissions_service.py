"""Service placeholder cho kiểm tra quyền tài nguyên."""
from schemas.permissions import PermissionResponse, RolePermissionMatrix


async def get_user_permissions(user_id: str) -> PermissionResponse:
    """Trả quyền demo cho user."""

    _ = user_id
    return PermissionResponse(resource="global", actions=["read", "write"])


async def list_roles_matrix() -> list[RolePermissionMatrix]:
    """Tạo bảng quyền giả lập cho admin theo HE_THONG.md mục 10."""

    return [
        RolePermissionMatrix(
            role="student",
            permissions=[
                PermissionResponse(resource="courses", actions=["read", "enroll"]),
                PermissionResponse(resource="quiz", actions=["submit"]),
            ],
        ),
        RolePermissionMatrix(
            role="instructor",
            permissions=[
                PermissionResponse(resource="classes", actions=["create", "update", "view_roster"]),
                PermissionResponse(resource="analytics", actions=["view_class"]),
            ],
        ),
        RolePermissionMatrix(
            role="admin",
            permissions=[
                PermissionResponse(resource="users", actions=["list", "update", "suspend"]),
                PermissionResponse(resource="system", actions=["view_dashboard", "publish_announcement"]),
            ],
        ),
    ]
