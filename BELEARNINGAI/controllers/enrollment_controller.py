"""Controller quản lý enrollment."""
from typing import List

from models.models import EnrollmentResponse
from schemas.common import MessageResponse
from schemas.enrollment import ProgressSnapshot
from services.enrollment_service import enroll_course, list_enrollments, update_progress, update_progress_demo


async def handle_enroll(user_id: str, course_id: str) -> EnrollmentResponse:
    """Đăng ký khóa học."""

    return await enroll_course(user_id, course_id)


async def handle_list_enrollments(user_id: str) -> List[EnrollmentResponse]:
    """Danh sách khóa học đã đăng ký."""

    return await list_enrollments(user_id)


async def handle_update_progress(enrollment_id: str, progress: float) -> EnrollmentResponse:
    """Cập nhật tiến độ học."""

    return await update_progress(enrollment_id, progress)


async def handle_unenroll(user_id: str, course_id: str) -> MessageResponse:
    """Placeholder rời khỏi khóa học."""

    _ = user_id, course_id
    return MessageResponse(message="Placeholder: đã hủy đăng ký khóa học")


async def handle_get_course_progress(user_id: str, course_id: str) -> ProgressSnapshot:
    """Lấy tiến độ khóa học (placeholder)."""

    return await update_progress_demo(user_id, course_id)


async def handle_post_course_progress(user_id: str, course_id: str, payload: dict) -> MessageResponse:
    """Placeholder cập nhật tiến độ khóa học."""

    _ = user_id, course_id, payload
    return MessageResponse(message="Placeholder: tiến độ đã được ghi nhận")
