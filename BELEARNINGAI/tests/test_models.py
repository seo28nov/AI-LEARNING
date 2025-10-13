"""Kiểm tra schema Pydantic."""
from models.models import CourseCreate, ModuleOutline


def test_course_create_defaults() -> None:
    """Đảm bảo giá trị mặc định hợp lý."""

    course = CourseCreate(
        title="Demo",
        description="Mô tả",
        modules=[ModuleOutline(name="Chương 1", objectives=[], lessons=[])],
    )
    assert course.level == "beginner"
    assert course.estimated_duration_hours == 4.0
