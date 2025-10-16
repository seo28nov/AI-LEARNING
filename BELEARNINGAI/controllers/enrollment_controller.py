"""Controller quản lý enrollment."""

from fastapi import HTTPException, status

from services.enrollment_service import (
    enroll_course,
    list_enrollments,
    get_enrollment_by_id,
    unenroll_course,
    get_user_course_progress,
    update_user_course_progress
)


async def handle_enroll(user_id: str, course_id: str) -> dict:
    """Đăng ký khóa học."""
    
    return await enroll_course(user_id, course_id)


async def handle_list_enrollments(
    user_id: str,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Danh sách khóa học đã đăng ký."""
    
    enrollments, total = await list_enrollments(
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "enrollments": enrollments,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_get_enrollment(enrollment_id: str, user_id: str) -> dict:
    """Lấy chi tiết enrollment."""
    
    return await get_enrollment_by_id(enrollment_id, user_id)


async def handle_unenroll(enrollment_id: str, user_id: str) -> dict:
    """Hủy đăng ký khóa học."""
    
    await unenroll_course(enrollment_id, user_id)
    return {"message": "Đã hủy đăng ký khóa học"}


async def handle_get_course_progress(user_id: str, course_id: str) -> dict:
    """Lấy tiến độ học của user trong khóa học."""
    
    return await get_user_course_progress(user_id, course_id)


async def handle_update_course_progress(
    user_id: str,
    course_id: str,
    payload: dict
) -> dict:
    """Cập nhật tiến độ học."""
    
    chapter_id = payload.get("chapter_id")
    completed = payload.get("completed", False)
    
    if not chapter_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="chapter_id is required"
        )
    
    return await update_user_course_progress(
        user_id=user_id,
        course_id=course_id,
        chapter_id=chapter_id,
        completed=completed
    )


# Alias cho router
handle_post_course_progress = handle_update_course_progress


async def handle_update_progress(enrollment_id: str, progress: int) -> dict:
    """Cập nhật tiến độ enrollment theo ID.
    
    Args:
        enrollment_id: ID enrollment
        progress: Phần trăm hoàn thành (0-100)
        
    Returns:
        Enrollment data đã cập nhật
    """
    from services.enrollment_service import EnrollmentDocument
    
    enrollment = await EnrollmentDocument.get(enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment không tồn tại"
        )
    
    # Update progress
    enrollment.progress = min(100, max(0, progress))
    await enrollment.save()
    
    return {
        "id": str(enrollment.id),
        "progress": enrollment.progress,
        "message": "Cập nhật tiến độ thành công"
    }
