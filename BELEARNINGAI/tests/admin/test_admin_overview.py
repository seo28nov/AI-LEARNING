"""Placeholder test cho dashboard admin."""
import pytest

from services import admin_service


@pytest.mark.skip(reason="placeholder: cần dữ liệu thực từ monitoring")
@pytest.mark.asyncio
async def test_system_overview_contains_uptime():
    """Dashboard demo phải chứa trường uptime_percent."""

    summary = await admin_service.get_system_overview()
    assert summary.uptime_percent > 0
