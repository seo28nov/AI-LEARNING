"""Router tiến độ học tập."""
from fastapi import APIRouter, Depends

from controllers.progress_controller import handle_get_progress, handle_update_progress
from middleware.auth import get_current_user
from models.models import ProgressResponse

router = APIRouter(tags=["progress"])


@router.get("/course/{course_id}", response_model=ProgressResponse, summary="Xem tiến độ khóa học")
async def get_progress_route(course_id: str, current_user: dict = Depends(get_current_user)) -> ProgressResponse:
    """Lấy tiến độ học tập."""

    user_id = current_user.get("sub", "demo-user")
    return await handle_get_progress(user_id, course_id)


@router.patch("/course/{course_id}", response_model=ProgressResponse, summary="Cập nhật tiến độ khóa học")
async def update_progress_route(
    course_id: str,
    progress: float,
    current_user: dict = Depends(get_current_user),
) -> ProgressResponse:
    """Cập nhật tiến độ học tập."""

    user_id = current_user.get("sub", "demo-user")
    return await handle_update_progress(user_id, course_id, progress)
