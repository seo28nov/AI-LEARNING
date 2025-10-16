"""Dịch vụ theo dõi tiến độ học tập chi tiết."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from models.models import (
    ProgressDocument,
    EnrollmentDocument,
    CourseDocument,
    UserDocument
)


async def get_or_create_progress(user_id: str, course_id: str) -> dict:
    """Lấy hoặc tạo mới progress document.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        
    Returns:
        Thông tin progress
    """
    # Tìm progress hiện có
    progress = await ProgressDocument.find_one(
        ProgressDocument.user_id == user_id,
        ProgressDocument.course_id == course_id
    )
    
    if progress:
        return {
            "id": str(progress.id),
            "user_id": progress.user_id,
            "course_id": progress.course_id,
            "progress": progress.progress,
            "completed_lessons": progress.completed_lessons,
            "quiz_attempts": progress.quiz_attempts,
            "total_study_time": progress.total_study_time,
            "streak_days": progress.streak_days,
            "last_activity": progress.last_activity,
            "created_at": progress.created_at,
            "updated_at": progress.updated_at
        }
    
    # Kiểm tra enrollment
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bạn chưa đăng ký khóa học này"
        )
    
    # Tạo progress mới
    now = datetime.now(timezone.utc)
    progress = ProgressDocument(
        user_id=user_id,
        course_id=course_id,
        progress=0.0,
        completed_lessons=[],
        quiz_attempts={},
        total_study_time=0,
        streak_days=0,
        last_activity=now,
        created_at=now,
        updated_at=now
    )
    
    await progress.insert()
    
    return {
        "id": str(progress.id),
        "user_id": progress.user_id,
        "course_id": progress.course_id,
        "progress": progress.progress,
        "completed_lessons": progress.completed_lessons,
        "quiz_attempts": progress.quiz_attempts,
        "total_study_time": progress.total_study_time,
        "streak_days": progress.streak_days,
        "last_activity": progress.last_activity,
        "created_at": progress.created_at,
        "updated_at": progress.updated_at
    }


async def update_chapter_progress(
    user_id: str,
    course_id: str,
    chapter_id: str,
    completed: bool = True
) -> dict:
    """Cập nhật tiến độ hoàn thành chapter.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        chapter_id: ID chapter
        completed: Đã hoàn thành hay chưa
        
    Returns:
        Thông tin progress sau cập nhật
    """
    # Lấy progress
    progress = await ProgressDocument.find_one(
        ProgressDocument.user_id == user_id,
        ProgressDocument.course_id == course_id
    )
    
    if progress is None:
        # Tạo mới nếu chưa có
        progress_data = await get_or_create_progress(user_id, course_id)
        progress = await ProgressDocument.get(progress_data["id"])
    
    # Cập nhật completed_lessons
    if completed and chapter_id not in progress.completed_lessons:
        progress.completed_lessons.append(chapter_id)
    elif not completed and chapter_id in progress.completed_lessons:
        progress.completed_lessons.remove(chapter_id)
    
    # Tính toán progress %
    course = await CourseDocument.get(course_id)
    if course and course.chapters:
        total_chapters = len(course.chapters)
        completed_count = len(progress.completed_lessons)
        progress.progress = (completed_count / total_chapters) * 100.0
    
    # Cập nhật streak
    progress.streak_days = await calculate_streak(user_id, course_id)
    progress.last_activity = datetime.now(timezone.utc)
    progress.updated_at = datetime.now(timezone.utc)
    
    await progress.save()
    
    # Cập nhật enrollment progress
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment:
        enrollment.progress = progress.progress
        if chapter_id not in enrollment.completed_chapters:
            enrollment.completed_chapters.append(chapter_id)
        enrollment.last_accessed = datetime.now(timezone.utc)
        await enrollment.save()
    
    return {
        "id": str(progress.id),
        "progress": progress.progress,
        "completed_lessons": progress.completed_lessons,
        "streak_days": progress.streak_days,
        "last_activity": progress.last_activity
    }


async def track_completion(
    user_id: str,
    course_id: str,
    lesson_id: str,
    time_spent: int
) -> dict:
    """Theo dõi hoàn thành bài học.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        lesson_id: ID bài học
        time_spent: Thời gian học (phút)
        
    Returns:
        Thông tin progress
    """
    progress = await ProgressDocument.find_one(
        ProgressDocument.user_id == user_id,
        ProgressDocument.course_id == course_id
    )
    
    if progress is None:
        progress_data = await get_or_create_progress(user_id, course_id)
        progress = await ProgressDocument.get(progress_data["id"])
    
    # Cập nhật thời gian học
    progress.total_study_time += time_spent
    progress.last_activity = datetime.now(timezone.utc)
    progress.updated_at = datetime.now(timezone.utc)
    
    await progress.save()
    
    # Cập nhật enrollment study time
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment:
        enrollment.total_study_time += time_spent
        enrollment.last_accessed = datetime.now(timezone.utc)
        await enrollment.save()
    
    return {
        "id": str(progress.id),
        "total_study_time": progress.total_study_time,
        "last_activity": progress.last_activity
    }


async def calculate_streak(user_id: str, course_id: str) -> int:
    """Tính số ngày học liên tiếp.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        
    Returns:
        Số ngày streak
    """
    progress = await ProgressDocument.find_one(
        ProgressDocument.user_id == user_id,
        ProgressDocument.course_id == course_id
    )
    
    if progress is None or progress.last_activity is None:
        return 0
    
    now = datetime.now(timezone.utc)
    last_activity = progress.last_activity
    
    # Tính số ngày kể từ lần học cuối
    days_diff = (now - last_activity).days
    
    if days_diff == 0:
        # Hôm nay đã học, giữ nguyên streak
        return progress.streak_days
    elif days_diff == 1:
        # Học liên tiếp, tăng streak
        return progress.streak_days + 1
    else:
        # Bỏ quá 1 ngày, reset streak
        return 0


async def get_learning_stats(user_id: str, course_id: Optional[str] = None) -> dict:
    """Lấy thống kê học tập tổng quan.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học (optional, None = tất cả khóa)
        
    Returns:
        Thống kê học tập
    """
    # Kiểm tra user
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    if course_id:
        # Thống kê cho 1 khóa học
        progress = await ProgressDocument.find_one(
            ProgressDocument.user_id == user_id,
            ProgressDocument.course_id == course_id
        )
        
        if progress is None:
            return {
                "course_id": course_id,
                "progress": 0.0,
                "completed_lessons": 0,
                "total_study_time": 0,
                "streak_days": 0,
                "last_activity": None
            }
        
        return {
            "course_id": course_id,
            "progress": progress.progress,
            "completed_lessons": len(progress.completed_lessons),
            "total_study_time": progress.total_study_time,
            "streak_days": progress.streak_days,
            "last_activity": progress.last_activity
        }
    else:
        # Thống kê tổng hợp tất cả khóa học
        all_progress = await ProgressDocument.find(
            ProgressDocument.user_id == user_id
        ).to_list()
        
        total_courses = len(all_progress)
        total_study_time = sum(p.total_study_time for p in all_progress)
        avg_progress = sum(p.progress for p in all_progress) / total_courses if total_courses > 0 else 0
        
        # Tìm streak dài nhất
        max_streak = max((p.streak_days for p in all_progress), default=0)
        
        # Khóa học gần nhất
        latest = max(all_progress, key=lambda p: p.last_activity) if all_progress else None
        
        return {
            "total_courses": total_courses,
            "total_study_time": total_study_time,
            "average_progress": round(avg_progress, 2),
            "max_streak": max_streak,
            "last_activity": latest.last_activity if latest else None
        }


async def update_study_time(
    user_id: str,
    course_id: str,
    minutes: int
) -> dict:
    """Cập nhật thời gian học.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        minutes: Số phút học thêm
        
    Returns:
        Thông tin progress
    """
    progress = await ProgressDocument.find_one(
        ProgressDocument.user_id == user_id,
        ProgressDocument.course_id == course_id
    )
    
    if progress is None:
        progress_data = await get_or_create_progress(user_id, course_id)
        progress = await ProgressDocument.get(progress_data["id"])
    
    progress.total_study_time += minutes
    progress.last_activity = datetime.now(timezone.utc)
    progress.updated_at = datetime.now(timezone.utc)
    
    await progress.save()
    
    return {
        "id": str(progress.id),
        "total_study_time": progress.total_study_time,
        "last_activity": progress.last_activity
    }


async def record_quiz_attempt(
    user_id: str,
    course_id: str,
    quiz_id: str,
    score: float
) -> dict:
    """Ghi nhận kết quả quiz.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        quiz_id: ID quiz
        score: Điểm số
        
    Returns:
        Thông tin progress
    """
    progress = await ProgressDocument.find_one(
        ProgressDocument.user_id == user_id,
        ProgressDocument.course_id == course_id
    )
    
    if progress is None:
        progress_data = await get_or_create_progress(user_id, course_id)
        progress = await ProgressDocument.get(progress_data["id"])
    
    # Lưu điểm quiz (giữ điểm cao nhất)
    if quiz_id not in progress.quiz_attempts or score > progress.quiz_attempts[quiz_id]:
        progress.quiz_attempts[quiz_id] = score
    
    progress.last_activity = datetime.now(timezone.utc)
    progress.updated_at = datetime.now(timezone.utc)
    
    await progress.save()
    
    # Cập nhật enrollment quiz scores
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment:
        if quiz_id not in enrollment.quiz_scores or score > enrollment.quiz_scores[quiz_id]:
            enrollment.quiz_scores[quiz_id] = score
        enrollment.last_accessed = datetime.now(timezone.utc)
        await enrollment.save()
    
    return {
        "id": str(progress.id),
        "quiz_attempts": progress.quiz_attempts,
        "last_activity": progress.last_activity
    }


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Alias cho controller
get_progress = get_or_create_progress


async def update_progress(user_id: str, course_id: str, progress_value: float) -> dict:
    """Cập nhật progress percentage.
    
    Args:
        user_id: ID user
        course_id: ID course
        progress_value: Giá trị progress (0-100)
        
    Returns:
        Progress data
    """
    progress = await get_or_create_progress(user_id, course_id)
    
    # Update progress trong ProgressDocument
    progress_doc = await ProgressDocument.get(progress["id"])
    if progress_doc:
        # Progress value được tính từ completed chapters
        # Ở đây chỉ return current progress
        pass
    
    return progress
