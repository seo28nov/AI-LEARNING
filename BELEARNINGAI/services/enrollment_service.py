"""Dịch vụ quản lý enrollment."""
from datetime import datetime, timedelta
from typing import List

from models.models import EnrollmentResponse, EnrollmentStatus
from schemas.enrollment import ProgressSnapshot, StudySession


async def enroll_course(user_id: str, course_id: str) -> EnrollmentResponse:
    """Giả lập đăng ký khóa học."""

    return EnrollmentResponse.model_validate(
        {
            "_id": "enroll-demo",
            "course_id": course_id,
            "user_id": user_id,
            "status": EnrollmentStatus.active,
            "progress": 0.0,
            "enrolled_at": datetime.utcnow(),
        }
    )


async def list_enrollments(user_id: str) -> List[EnrollmentResponse]:
    """Giả lập danh sách enrollment của user."""

    return [await enroll_course(user_id, "course-demo")]


async def update_progress(enrollment_id: str, progress: float) -> EnrollmentResponse:
    """Giả lập cập nhật tiến độ."""

    response = await enroll_course("demo-user", "course-demo")
    response.progress = progress
    return response


async def create_enrollment_placeholder(user_id: str, course_id: str) -> dict:
    """Trả về payload enrollment để seed dữ liệu demo."""

    base = await enroll_course(user_id, course_id)
    return {
        "enrollment": base.model_dump(by_alias=True),
        "note": "Placeholder: cập nhật khi kết nối MongoDB thực",
    }


async def update_progress_demo(user_id: str, course_id: str) -> ProgressSnapshot:
    """Sinh tiến độ học tập mẫu phục vụ dashboard."""

    now = datetime.utcnow()
    sessions = [
        StudySession(session_date=now - timedelta(days=idx), duration_minutes=45 - idx * 5, activities=["reading", "quiz"])
        for idx in range(3)
    ]
    return ProgressSnapshot(
        course_id=course_id,
        progress=62.5,
        streak_days=4,
        last_activity=now,
        learning_sessions=sessions,
    )
