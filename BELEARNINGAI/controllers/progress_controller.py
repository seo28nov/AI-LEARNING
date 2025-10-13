"""Controller tiến độ học tập."""
from models.models import ProgressResponse
from schemas.enrollment import ProgressSnapshot
from services.enrollment_service import update_progress_demo
from services.progress_service import get_progress, update_progress


async def handle_get_progress(user_id: str, course_id: str) -> ProgressResponse:
    """Lấy tiến độ hiện tại."""

    return await get_progress(user_id, course_id)


async def handle_update_progress(user_id: str, course_id: str, progress: float) -> ProgressResponse:
    """Cập nhật tiến độ."""

    return await update_progress(user_id, course_id, progress)


async def get_course_progress(user_id: str, course_id: str) -> ProgressSnapshot:
    """Tổng hợp tiến độ dùng cho dashboard analytics."""

    return await update_progress_demo(user_id, course_id)
