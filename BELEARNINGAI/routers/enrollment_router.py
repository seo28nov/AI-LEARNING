"""Router enrollment."""
from typing import List

from fastapi import APIRouter, Depends

from controllers.enrollment_controller import (
    handle_enroll,
    handle_get_course_progress,
    handle_list_enrollments,
    handle_post_course_progress,
    handle_unenroll,
    handle_update_progress,
)
from middleware.auth import get_current_user
from models.models import EnrollmentResponse
from schemas.common import MessageResponse
from schemas.enrollment import ProgressSnapshot

router = APIRouter(tags=["enrollments"])


@router.post("/{course_id}", response_model=EnrollmentResponse, summary="Đăng ký khóa học")
async def enroll_route(course_id: str, current_user: dict = Depends(get_current_user)) -> EnrollmentResponse:
    """Đăng ký khóa học."""

    user_id = current_user.get("sub", "demo-user")
    return await handle_enroll(user_id, course_id)


@router.delete("/{course_id}", response_model=MessageResponse, summary="Hủy đăng ký khóa học")
async def unenroll_route(course_id: str, current_user: dict = Depends(get_current_user)) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return await handle_unenroll(user_id, course_id)


@router.get("/", response_model=List[EnrollmentResponse], summary="Danh sách khóa học đã đăng ký")
async def my_enrollments_route(current_user: dict = Depends(get_current_user)) -> List[EnrollmentResponse]:
    """Danh sách khóa học đã đăng ký."""

    user_id = current_user.get("sub", "demo-user")
    return await handle_list_enrollments(user_id)


@router.get(
    "/{course_id}/progress",
    response_model=ProgressSnapshot,
    summary="Tiến độ học tập theo khóa",
)
async def course_progress_route(
    course_id: str, current_user: dict = Depends(get_current_user)
) -> ProgressSnapshot:
    user_id = current_user.get("sub", "demo-user")
    return await handle_get_course_progress(user_id, course_id)


@router.post(
    "/{course_id}/progress",
    response_model=MessageResponse,
    summary="Cập nhật tiến độ khóa học",
)
async def course_progress_update_route(
    course_id: str, payload: dict, current_user: dict = Depends(get_current_user)
) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return await handle_post_course_progress(user_id, course_id, payload)


@router.patch("/{enrollment_id}/progress", response_model=EnrollmentResponse, summary="Cập nhật tiến độ")
async def update_progress_route(enrollment_id: str, progress: float) -> EnrollmentResponse:
    """Cập nhật tiến độ học tập."""

    return await handle_update_progress(enrollment_id, progress)
