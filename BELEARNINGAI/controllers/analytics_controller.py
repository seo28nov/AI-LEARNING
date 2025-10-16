"""Controller cho analytics."""
from typing import Optional

from fastapi import HTTPException, status

from services.analytics_service import (
    get_student_dashboard,
    get_student_progress_stats,
    get_instructor_dashboard,
    get_instructor_course_stats,
    get_admin_system_stats,
    get_course_analytics
)


async def handle_student_dashboard(user_id: str) -> dict:
    """Dashboard tổng quan cho student."""
    
    return await get_student_dashboard(user_id)


async def handle_student_progress(user_id: str, course_id: Optional[str] = None) -> dict:
    """Thống kê tiến độ học của student."""
    
    return await get_student_progress_stats(user_id, course_id)


async def handle_instructor_dashboard(instructor_id: str) -> dict:
    """Dashboard tổng quan cho instructor."""
    
    return await get_instructor_dashboard(instructor_id)


async def handle_instructor_course_stats(instructor_id: str, course_id: Optional[str] = None) -> dict:
    """Thống kê khóa học của instructor."""
    
    return await get_instructor_course_stats(instructor_id, course_id)


async def handle_admin_system_stats(user_role: str) -> dict:
    """Thống kê hệ thống cho admin."""
    
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await get_admin_system_stats()


async def handle_course_analytics(course_id: str, current_user: dict) -> dict:
    """Thống kê chi tiết khóa học."""
    
    if current_user.get("role") not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or admin access required"
        )
    
    return await get_course_analytics(course_id, current_user["id"])


# Additional handlers for router compatibility
async def handle_admin_courses(current_user: dict) -> dict:
    """Thống kê khóa học cho admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await get_admin_system_stats()


async def handle_admin_system(current_user: dict) -> dict:
    """Dashboard hệ thống cho admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await get_admin_system_stats()


async def handle_admin_users(current_user: dict) -> dict:
    """Thống kê người dùng cho admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return await get_admin_system_stats()


async def handle_instructor_courses(current_user: dict) -> dict:
    """Hiệu suất khóa học cho instructor."""
    if current_user.get("role") not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or admin access required"
        )
    
    return await get_instructor_course_stats(current_user["id"])


async def handle_instructor_overview(current_user: dict) -> dict:
    """Dashboard tổng quan cho instructor."""
    if current_user.get("role") not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or admin access required"
        )
    
    return await get_instructor_dashboard(current_user["id"])


async def handle_instructor_students(current_user: dict) -> dict:
    """Hoạt động học viên cho instructor."""
    if current_user.get("role") not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or admin access required"
        )
    
    return await get_instructor_course_stats(current_user["id"])


async def handle_student_achievements(current_user: dict) -> dict:
    """Thành tích học tập cho student."""
    return await get_student_progress_stats(current_user["id"])


async def handle_student_time_spent(current_user: dict) -> dict:
    """Thời gian học cho student."""
    return await get_student_progress_stats(current_user["id"])
