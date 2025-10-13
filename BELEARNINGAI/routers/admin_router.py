"""Router cho API quản trị."""
from typing import List

from fastapi import APIRouter

from controllers.admin_controller import (
    handle_admin_suspend_user,
    handle_admin_update_role,
    handle_admin_users_list,
    handle_approve_course,
    handle_audit_logs,
    handle_broadcast,
    handle_pending_courses,
    handle_roles_matrix,
    handle_system_overview,
    handle_system_stats,
    handle_reject_course,
    handle_system_backup,
)
from schemas.admin import AdminBroadcastRequest, AdminSystemStats, SystemSummary, UserAuditLog
from schemas.common import MessageResponse
from schemas.permissions import RolePermissionMatrix

router = APIRouter(tags=["admin"])


@router.get("/system/stats", response_model=AdminSystemStats, summary="Thống kê hệ thống")
async def system_stats_route() -> AdminSystemStats:
    return await handle_system_stats()


@router.post("/announcements", response_model=MessageResponse, summary="Gửi thông báo toàn hệ thống")
async def broadcast_route(payload: AdminBroadcastRequest) -> MessageResponse:
    await handle_broadcast(payload)
    return MessageResponse(message="Đã ghi nhận thông báo, sẽ gửi async")


@router.get(
    "/dashboard/overview",
    response_model=SystemSummary,
    summary="Dashboard tổng quan cho admin",
)
async def dashboard_overview_route() -> SystemSummary:
    return await handle_system_overview()


@router.get("/audit/logs", response_model=List[UserAuditLog], summary="Danh sách audit log")
async def audit_logs_route(limit: int = 5) -> List[UserAuditLog]:
    return await handle_audit_logs(limit)


@router.get("/permissions/matrix", response_model=List[RolePermissionMatrix], summary="Bảng quyền hệ thống")
async def permission_matrix_route() -> List[RolePermissionMatrix]:
    return await handle_roles_matrix()


@router.get("/users", response_model=MessageResponse, summary="Danh sách người dùng")
async def admin_users_route() -> MessageResponse:
    return await handle_admin_users_list()


@router.put("/users/{user_id}/role", response_model=MessageResponse, summary="Cập nhật vai trò người dùng")
async def admin_update_role_route(user_id: str, payload: dict) -> MessageResponse:
    return await handle_admin_update_role(user_id, payload)


@router.delete("/users/{user_id}", response_model=MessageResponse, summary="Vô hiệu hóa người dùng")
async def admin_suspend_user_route(user_id: str) -> MessageResponse:
    return await handle_admin_suspend_user(user_id)


@router.get("/courses/pending", response_model=MessageResponse, summary="Khóa học chờ duyệt")
async def pending_courses_route() -> MessageResponse:
    return await handle_pending_courses()


@router.put("/courses/{course_id}/approve", response_model=MessageResponse, summary="Duyệt khóa học")
async def approve_course_route(course_id: str) -> MessageResponse:
    return await handle_approve_course(course_id)


@router.put("/courses/{course_id}/reject", response_model=MessageResponse, summary="Từ chối khóa học")
async def reject_course_route(course_id: str, payload: dict) -> MessageResponse:
    return await handle_reject_course(course_id, payload)


@router.post("/system/backup", response_model=MessageResponse, summary="Sao lưu hệ thống")
async def system_backup_route() -> MessageResponse:
    return await handle_system_backup()
