"""Router dashboard."""
from fastapi import APIRouter

from controllers.dashboard_controller import handle_dashboard_stats
from models.models import DashboardResponse

router = APIRouter(tags=["dashboard"])


@router.get("/stats", response_model=DashboardResponse, summary="Số liệu tổng quan")
async def dashboard_stats_route() -> DashboardResponse:
    """Trả về số liệu dashboard."""

    return await handle_dashboard_stats()
