"""Dịch vụ theo dõi tiến độ học tập."""
from datetime import datetime

from models.models import ProgressResponse


async def get_progress(user_id: str, course_id: str) -> ProgressResponse:
    """Giả lập trả về tiến độ hiện tại."""

    return ProgressResponse.model_validate(
        {
            "_id": "progress-demo",
            "course_id": course_id,
            "user_id": user_id,
            "progress": 45.0,
            "completed_lessons": ["lesson-1"],
        }
    )


async def update_progress(user_id: str, course_id: str, progress: float) -> ProgressResponse:
    """Giả lập cập nhật tiến độ."""

    response = await get_progress(user_id, course_id)
    response.progress = progress
    response.completed_lessons.append("lesson-auto")
    response_dict = response.model_dump(by_alias=True)
    response_dict["progress"] = progress
    response_dict["completed_lessons"] = response.completed_lessons
    response_dict["_id"] = response.id
    return ProgressResponse.model_validate(response_dict)
