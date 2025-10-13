"""Controller cho analytics."""
from schemas.analytics import StudentDashboardResponse
from schemas.common import MessageResponse
from services.analytics_service import build_student_dashboard, get_student_dashboard

from controllers.progress_controller import get_course_progress


async def handle_student_dashboard(current_user: dict) -> StudentDashboardResponse:
    user_id = current_user.get("sub", "demo-user")
    snapshot = await get_course_progress(user_id, course_id="course-demo")
    if snapshot.progress:
        return await build_student_dashboard(snapshot.progress)
    return await get_student_dashboard(user_id=user_id)


async def handle_student_progress(current_user: dict) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: tiến độ chi tiết của {user_id}")


async def handle_student_time_spent(current_user: dict) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: thời gian học của {user_id}")


async def handle_student_achievements(current_user: dict) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: thành tích học tập của {user_id}")


async def handle_instructor_overview(current_user: dict) -> MessageResponse:
    instructor_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: tổng quan giảng viên {instructor_id}")


async def handle_instructor_courses(current_user: dict) -> MessageResponse:
    instructor_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: hiệu suất khóa học của {instructor_id}")


async def handle_instructor_students(current_user: dict) -> MessageResponse:
    instructor_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: hoạt động học viên của {instructor_id}")


async def handle_admin_system(current_user: dict) -> MessageResponse:
    _ = current_user
    return MessageResponse(message="Placeholder: thống kê hệ thống cho admin")


async def handle_admin_users(current_user: dict) -> MessageResponse:
    _ = current_user
    return MessageResponse(message="Placeholder: thống kê người dùng cho admin")


async def handle_admin_courses(current_user: dict) -> MessageResponse:
    _ = current_user
    return MessageResponse(message="Placeholder: thống kê khóa học cho admin")
