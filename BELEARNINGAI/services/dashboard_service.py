"""Dịch vụ tổng hợp số liệu dashboard."""
from datetime import datetime

from models.models import DashboardMetric, DashboardResponse


async def get_dashboard_stats() -> DashboardResponse:
    """Giả lập trả về số liệu dashboard."""

    metrics = [
        DashboardMetric(name="total_users", value=1250, trend=5.2),
        DashboardMetric(name="active_courses", value=180, trend=2.1),
        DashboardMetric(name="ai_chat_requests", value=1520, trend=8.6),
    ]
    return DashboardResponse(metrics=metrics, generated_at=datetime.utcnow())
