"""Controller dashboard hệ thống."""
from models.models import DashboardResponse
from services.dashboard_service import get_dashboard_stats


async def handle_dashboard_stats() -> DashboardResponse:
    """Trả về số liệu tổng quan."""

    return await get_dashboard_stats()
