"""Service placeholder cho chức năng quản trị."""
from datetime import datetime, timedelta

from schemas.admin import AdminBroadcastRequest, AdminSystemStats, SystemSummary, UserAuditLog


async def get_system_stats() -> AdminSystemStats:
    """Trả về số liệu hệ thống giả lập."""

    return AdminSystemStats(users=1200, courses=340, active_sessions=85, generated_at=datetime.utcnow())


async def create_announcement(payload: AdminBroadcastRequest) -> dict:
    """Gửi thông báo broadcast (placeholder)."""

    return {"message": "Thông báo đã được ghi nhận", "audience": payload.audience_roles}


async def get_system_overview() -> SystemSummary:
    """Tạo dữ liệu demo cho dashboard admin."""

    return SystemSummary(
        uptime_percent=99.8,
        total_users=1247,
        total_courses=156,
        active_today=320,
        alerts=["Cảnh báo: bộ nhớ server-2 > 80%"],
        generated_at=datetime.utcnow(),
    )


async def list_audit_logs(limit: int = 5) -> list[UserAuditLog]:
    """Trả danh sách log thao tác gần đây."""

    now = datetime.utcnow()
    base_time = now - timedelta(minutes=limit * 3)
    logs: list[UserAuditLog] = []
    for index in range(limit):
        logs.append(
            UserAuditLog(
                action_id=f"audit-{index}",
                actor_id="admin-demo",
                action="update_user_role",
                target=f"user-{index}",
                created_at=base_time + timedelta(minutes=index * 3),
            )
        )
    return logs
