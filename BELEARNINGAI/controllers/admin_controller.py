"""Controller cho chức năng quản trị."""
from typing import List

from schemas.admin import AdminBroadcastRequest, AdminSystemStats, SystemSummary, UserAuditLog
from schemas.common import MessageResponse
from services.admin_service import (
    create_announcement,
    get_system_overview,
    get_system_stats,
    list_audit_logs,
)
from services.permissions_service import list_roles_matrix


async def handle_system_stats() -> AdminSystemStats:
    return await get_system_stats()


async def handle_broadcast(payload: AdminBroadcastRequest) -> dict:
    return await create_announcement(payload)


async def handle_system_overview() -> SystemSummary:
    return await get_system_overview()


async def handle_audit_logs(limit: int = 5) -> List[UserAuditLog]:
    return await list_audit_logs(limit)


async def handle_roles_matrix():
    return await list_roles_matrix()


async def handle_admin_users_list() -> MessageResponse:
    """Placeholder danh sách người dùng."""

    return MessageResponse(message="Placeholder: danh sách người dùng với phân trang")


async def handle_admin_update_role(user_id: str, payload: dict) -> MessageResponse:
    """Placeholder cập nhật vai trò người dùng."""

    new_role = payload.get("role", "student")
    return MessageResponse(message=f"Placeholder: đã đổi vai trò {user_id} thành {new_role}")


async def handle_admin_suspend_user(user_id: str) -> MessageResponse:
    """Placeholder khóa tài khoản người dùng."""

    return MessageResponse(message=f"Placeholder: đã vô hiệu hóa tài khoản {user_id}")


async def handle_pending_courses() -> MessageResponse:
    """Placeholder danh sách khóa học chờ duyệt."""

    return MessageResponse(message="Placeholder: danh sách khóa học chờ duyệt")


async def handle_approve_course(course_id: str) -> MessageResponse:
    """Placeholder duyệt khóa học."""

    return MessageResponse(message=f"Placeholder: đã duyệt khóa học {course_id}")


async def handle_reject_course(course_id: str, payload: dict) -> MessageResponse:
    """Placeholder từ chối khóa học."""

    reason = payload.get("reason", "Không đạt yêu cầu")
    return MessageResponse(message=f"Placeholder: từ chối khóa học {course_id} - {reason}")


async def handle_system_backup() -> MessageResponse:
    """Placeholder sao lưu hệ thống."""

    return MessageResponse(message="Placeholder: yêu cầu sao lưu đã được lên lịch")
