"""Controller cho chức năng quản trị."""
from typing import List

from schemas.admin import AdminBroadcastRequest, AdminSystemStats, SystemSummary, UserAuditLog
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


async def handle_admin_users_list(
    skip: int = 0,
    limit: int = 20,
    role: str = None,
    is_active: bool = None
) -> dict:
    """Danh sách người dùng với filters."""
    from services.user_service import list_users
    
    users, total = await list_users(
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active
    )
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_admin_update_role(user_id: str, payload: dict, admin_id: str) -> dict:
    """Cập nhật vai trò người dùng."""
    from services.user_service import change_user_role
    
    new_role = payload.get("role")
    if not new_role:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role is required"
        )
    
    return await change_user_role(user_id, new_role, admin_id)


async def handle_admin_suspend_user(user_id: str, admin_id: str) -> dict:
    """Khóa tài khoản người dùng."""
    from services.user_service import deactivate_user
    
    return await deactivate_user(user_id, admin_id)


async def handle_admin_activate_user(user_id: str, admin_id: str) -> dict:
    """Kích hoạt lại tài khoản."""
    from services.user_service import activate_user
    
    return await activate_user(user_id, admin_id)


async def handle_pending_courses(skip: int = 0, limit: int = 10) -> dict:
    """Danh sách khóa học chờ duyệt."""
    from services.course_service import list_pending_courses
    
    courses, total = await list_pending_courses(skip=skip, limit=limit)
    
    return {
        "courses": courses,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_approve_course(course_id: str, admin_id: str) -> dict:
    """Duyệt khóa học."""
    from services.course_service import approve_course
    
    return await approve_course(course_id, admin_id)


async def handle_reject_course(course_id: str, payload: dict, admin_id: str) -> dict:
    """Từ chối khóa học."""
    from services.course_service import reject_course
    
    reason = payload.get("reason", "Không đạt yêu cầu chất lượng")
    
    return await reject_course(course_id, reason, admin_id)


async def handle_system_backup(admin_id: str) -> dict:
    """Tạo bản sao lưu hệ thống."""
    import asyncio
    from datetime import datetime
    
    # Trigger backup task (async)
    backup_id = f"backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    # In production, this would trigger actual backup
    asyncio.create_task(_perform_backup(backup_id, admin_id))
    
    return {
        "message": "Backup đã được lên lịch",
        "backup_id": backup_id,
        "status": "pending"
    }


async def _perform_backup(backup_id: str, admin_id: str):
    """Thực hiện backup (background task)."""
    # TODO: Implement actual backup logic
    # - Export MongoDB collections
    # - Upload to S3/cloud storage
    # - Send notification when complete
    pass
