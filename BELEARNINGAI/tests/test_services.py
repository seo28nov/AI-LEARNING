"""Kiểm tra lớp services."""
from datetime import datetime
from types import SimpleNamespace

import pytest

import services.course_service as course_services


@pytest.mark.asyncio
async def test_list_courses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Đảm bảo list_courses trả về list CourseResponse."""

    class DummyQuery:
        async def to_list(self):  # noqa: D401
            """Fake dữ liệu trả về."""

            return [
                SimpleNamespace(
                    _id="1",
                    title="Demo",
                    description="Mô tả",
                    level="beginner",
                    category="Test",
                    estimated_duration_hours=1.0,
                    tags=["demo"],
                    modules=[],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            ]

    monkeypatch.setattr(course_services.CourseDocument, "find_all", lambda: DummyQuery())

    result = await course_services.list_courses()
    assert result[0].title == "Demo"
