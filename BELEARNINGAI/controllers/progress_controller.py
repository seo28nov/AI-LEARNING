"""Controller tiến độ học tập."""
from models.models import ProgressResponse
from schemas.enrollment import ProgressSnapshot
from services.progress_service import get_progress, update_progress


async def handle_get_progress(user_id: str, course_id: str) -> ProgressResponse:
    """Lấy tiến độ hiện tại."""

    return await get_progress(user_id, course_id)


async def handle_update_progress(user_id: str, course_id: str, progress: float) -> ProgressResponse:
    """Cập nhật tiến độ."""

    return await update_progress(user_id, course_id, progress)


async def get_course_progress(user_id: str, course_id: str) -> ProgressSnapshot:
    """Tổng hợp tiến độ dùng cho dashboard analytics."""
    # Sử dụng get_progress thay vì update_progress_demo
    progress_data = await get_progress(user_id, course_id)
    
    # Convert sang ProgressSnapshot format
    return ProgressSnapshot(
        user_id=user_id,
        course_id=course_id,
        progress=progress_data.get("progress", 0.0),
        completed_chapters=progress_data.get("completed_chapters", []),
        last_accessed=progress_data.get("last_accessed")
    )
