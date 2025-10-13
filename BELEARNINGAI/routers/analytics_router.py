"""Router cho analytics & reporting."""
from fastapi import APIRouter, Depends

from controllers.analytics_controller import (
    handle_admin_courses,
    handle_admin_system,
    handle_admin_users,
    handle_instructor_courses,
    handle_instructor_overview,
    handle_instructor_students,
    handle_student_achievements,
    handle_student_dashboard,
    handle_student_progress,
    handle_student_time_spent,
)
from middleware.auth import get_current_user
from schemas.analytics import StudentDashboardResponse
from schemas.common import MessageResponse

router = APIRouter(tags=["analytics"])


@router.get("/student-dashboard", response_model=StudentDashboardResponse, summary="Dashboard học viên")
async def student_dashboard_route(current_user: dict = Depends(get_current_user)) -> StudentDashboardResponse:
    return await handle_student_dashboard(current_user)


@router.get("/instructor/overview", response_model=MessageResponse, summary="Dashboard giảng viên")
async def instructor_overview_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_instructor_overview(current_user)


@router.get("/admin/system", response_model=MessageResponse, summary="Dashboard hệ thống")
async def admin_system_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_admin_system(current_user)


@router.get("/student/progress", response_model=MessageResponse, summary="Tiến độ chi tiết theo khóa")
async def student_progress_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_student_progress(current_user)


@router.get("/student/time-spent", response_model=MessageResponse, summary="Thời gian học")
async def student_time_spent_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_student_time_spent(current_user)


@router.get("/student/achievements", response_model=MessageResponse, summary="Thành tích học tập")
async def student_achievements_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_student_achievements(current_user)


@router.get("/instructor/courses", response_model=MessageResponse, summary="Hiệu suất khóa học")
async def instructor_courses_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_instructor_courses(current_user)


@router.get("/instructor/students", response_model=MessageResponse, summary="Hoạt động học viên")
async def instructor_students_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_instructor_students(current_user)


@router.get("/admin/users", response_model=MessageResponse, summary="Thống kê người dùng")
async def admin_users_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_admin_users(current_user)


@router.get("/admin/courses", response_model=MessageResponse, summary="Thống kê khóa học")
async def admin_courses_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_admin_courses(current_user)
