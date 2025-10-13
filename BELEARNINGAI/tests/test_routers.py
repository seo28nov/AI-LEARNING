"""Kiểm tra các route khóa học."""
from datetime import datetime

import pytest

from models.models import CourseResponse, ModuleOutline


def test_list_courses_route(monkeypatch: pytest.MonkeyPatch, client) -> None:
    """Đảm bảo route trả danh sách khóa học."""

    async def fake_handle_list_courses():
        return [
            CourseResponse(
                _id="123",
                title="Khoá học thử",
                description="Mô tả",
                level="beginner",
                category="Test",
                estimated_duration_hours=1.0,
                tags=["demo"],
                modules=[ModuleOutline(name="Chương", objectives=[], lessons=[])],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        ]

    monkeypatch.setattr("controllers.course_controller.handle_list_courses", fake_handle_list_courses)

    response = client.get("/api/v1/courses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_course_route(monkeypatch: pytest.MonkeyPatch, client) -> None:
    """Đảm bảo route tạo khóa học trả về dữ liệu."""

    async def fake_handle_create_course(_payload, _user_id):
        return CourseResponse(
            _id="123",
            title="Khoá học thử",
            description="Mô tả",
            level="beginner",
            category="Test",
            estimated_duration_hours=1.0,
            tags=["demo"],
            modules=[ModuleOutline(name="Chương", objectives=[], lessons=[])],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    monkeypatch.setattr("controllers.course_controller.handle_create_course", fake_handle_create_course)

    response = client.post(
        "/api/v1/courses/",
        json={
            "title": "Khoá học thử",
            "description": "Mô tả",
            "level": "beginner",
            "category": "Test",
            "estimated_duration_hours": 1.0,
            "tags": ["demo"],
            "modules": [],
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Khoá học thử"
