"""Placeholder test cho luồng cập nhật tiến độ."""
import pytest

from services import enrollment_service


@pytest.mark.skip(reason="placeholder: cần kết nối DB thực để kiểm thử")
@pytest.mark.asyncio
async def test_progress_snapshot_contains_sessions():
    """Snapshot demo phải có tối thiểu một learning session."""

    snapshot = await enrollment_service.update_progress_demo("user-demo", "course-demo")
    assert snapshot.learning_sessions
