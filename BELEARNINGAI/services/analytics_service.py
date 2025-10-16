"""Dịch vụ phân tích và thống kê."""
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException, status

from models.models import (
    UserDocument,
    UserRole,
    CourseDocument,
    EnrollmentDocument,
    ProgressDocument,
    QuizDocument,
    ClassDocument
)


async def get_student_dashboard(user_id: str) -> dict:
    """Lấy dashboard cho học viên.
    
    Args:
        user_id: ID học viên
        
    Returns:
        Dashboard data
    """
    user = await UserDocument.get(user_id)
    if user is None or user.role != UserRole.student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Học viên không tồn tại"
        )
    
    # Lấy enrollments
    enrollments = await EnrollmentDocument.find(
        EnrollmentDocument.user_id == user_id
    ).to_list()
    
    # Lấy progress
    all_progress = await ProgressDocument.find(
        ProgressDocument.user_id == user_id
    ).to_list()
    
    # Tính toán metrics
    total_courses = len(enrollments)
    active_courses = sum(1 for e in enrollments if e.status == "active")
    completed_courses = sum(1 for e in enrollments if e.status == "completed")
    
    # Tiến độ trung bình
    avg_progress = sum(e.progress for e in enrollments) / total_courses if total_courses > 0 else 0
    
    # Thời gian học tổng
    total_study_time = sum(e.total_study_time for e in enrollments)
    
    # Streak dài nhất
    max_streak = max((p.streak_days for p in all_progress), default=0)
    
    # Hoạt động gần đây
    recent_activity = []
    for enrollment in sorted(enrollments, key=lambda x: x.last_accessed, reverse=True)[:5]:
        course = await CourseDocument.get(enrollment.course_id)
        if course:
            recent_activity.append({
                "course_id": enrollment.course_id,
                "course_title": course.title,
                "last_accessed": enrollment.last_accessed,
                "progress": enrollment.progress
            })
    
    return {
        "overview": {
            "total_courses": total_courses,
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "average_progress": round(avg_progress, 2)
        },
        "study_stats": {
            "total_study_time": total_study_time,
            "max_streak": max_streak,
            "avg_study_time_per_day": round(total_study_time / 30, 2) if total_study_time > 0 else 0
        },
        "recent_activity": recent_activity,
        "generated_at": datetime.now(timezone.utc)
    }


async def get_instructor_dashboard(instructor_id: str) -> dict:
    """Lấy dashboard cho giảng viên.
    
    Args:
        instructor_id: ID giảng viên
        
    Returns:
        Dashboard data
    """
    instructor = await UserDocument.get(instructor_id)
    if instructor is None or instructor.role not in [UserRole.instructor, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giảng viên không tồn tại"
        )
    
    # Lấy courses của instructor
    courses = await CourseDocument.find(
        CourseDocument.created_by == instructor_id
    ).to_list()
    
    course_ids = [str(c.id) for c in courses]
    
    # Lấy enrollments cho các courses
    total_enrollments = 0
    active_enrollments = 0
    
    for course_id in course_ids:
        enrollments = await EnrollmentDocument.find(
            EnrollmentDocument.course_id == course_id
        ).to_list()
        
        total_enrollments += len(enrollments)
        active_enrollments += sum(1 for e in enrollments if e.status == "active")
    
    # Lấy classes
    classes = await ClassDocument.find(
        ClassDocument.instructor_id == instructor_id
    ).to_list()
    
    total_students = sum(c.current_students for c in classes)
    
    # Course performance
    course_stats = []
    for course in courses[:10]:  # Top 10
        enrollments = await EnrollmentDocument.find(
            EnrollmentDocument.course_id == str(course.id)
        ).to_list()
        
        completion_rate = 0
        if enrollments:
            completed = sum(1 for e in enrollments if e.status == "completed")
            completion_rate = (completed / len(enrollments)) * 100
        
        course_stats.append({
            "course_id": str(course.id),
            "title": course.title,
            "enrollments": len(enrollments),
            "completion_rate": round(completion_rate, 2)
        })
    
    return {
        "overview": {
            "total_courses": len(courses),
            "total_classes": len(classes),
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments,
            "total_students": total_students
        },
        "course_performance": course_stats,
        "generated_at": datetime.now(timezone.utc)
    }


async def get_admin_dashboard() -> dict:
    """Lấy dashboard cho admin.
    
    Returns:
        Dashboard data với system stats
    """
    # Tổng số users
    total_users = await UserDocument.find().count()
    students = await UserDocument.find(UserDocument.role == UserRole.student).count()
    instructors = await UserDocument.find(UserDocument.role == UserRole.instructor).count()
    admins = await UserDocument.find(UserDocument.role == UserRole.admin).count()
    
    # Tổng số courses
    total_courses = await CourseDocument.find().count()
    published_courses = await CourseDocument.find(CourseDocument.is_published).count()
    
    # Tổng số enrollments
    total_enrollments = await EnrollmentDocument.find().count()
    active_enrollments = await EnrollmentDocument.find(EnrollmentDocument.status == "active").count()
    
    # Tổng số classes
    total_classes = await ClassDocument.find().count()
    
    # User growth (30 ngày qua)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    new_users = await UserDocument.find(
        UserDocument.created_at >= thirty_days_ago
    ).count()
    
    # Top courses
    all_courses = await CourseDocument.find().limit(100).to_list()
    course_enrollment_counts = []
    
    for course in all_courses:
        enrollment_count = await EnrollmentDocument.find(
            EnrollmentDocument.course_id == str(course.id)
        ).count()
        
        course_enrollment_counts.append({
            "course_id": str(course.id),
            "title": course.title,
            "instructor_id": course.created_by,
            "enrollments": enrollment_count
        })
    
    top_courses = sorted(course_enrollment_counts, key=lambda x: x["enrollments"], reverse=True)[:10]
    
    return {
        "system_stats": {
            "total_users": total_users,
            "students": students,
            "instructors": instructors,
            "admins": admins,
            "new_users_30d": new_users
        },
        "content_stats": {
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_classes": total_classes,
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments
        },
        "top_courses": top_courses,
        "generated_at": datetime.now(timezone.utc)
    }


async def get_course_analytics(course_id: str, instructor_id: str) -> dict:
    """Lấy phân tích chi tiết cho khóa học.
    
    Args:
        course_id: ID khóa học
        instructor_id: ID giảng viên
        
    Returns:
        Course analytics
    """
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra quyền
    instructor = await UserDocument.get(instructor_id)
    if course.created_by != instructor_id and instructor.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem analytics"
        )
    
    # Lấy enrollments
    enrollments = await EnrollmentDocument.find(
        EnrollmentDocument.course_id == course_id
    ).to_list()
    
    total_enrollments = len(enrollments)
    active_enrollments = sum(1 for e in enrollments if e.status == "active")
    completed_enrollments = sum(1 for e in enrollments if e.status == "completed")
    
    # Completion rate
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
    
    # Average progress
    avg_progress = sum(e.progress for e in enrollments) / total_enrollments if total_enrollments > 0 else 0
    
    # Total study time
    total_study_time = sum(e.total_study_time for e in enrollments)
    
    # Enrollment trend (30 ngày qua)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_enrollments = [e for e in enrollments if e.enrolled_at >= thirty_days_ago]
    
    # Quiz performance
    quizzes = await QuizDocument.find(QuizDocument.course_id == course_id).to_list()
    quiz_stats = []
    
    for quiz in quizzes:
        quiz_key_prefix = f"{quiz.chapter_id}_{str(quiz.id)}"
        
        attempts = 0
        total_score = 0
        
        for enrollment in enrollments:
            for key, score in enrollment.quiz_scores.items():
                if key.startswith(quiz_key_prefix):
                    attempts += 1
                    total_score += score
        
        avg_score = total_score / attempts if attempts > 0 else 0
        
        quiz_stats.append({
            "quiz_id": str(quiz.id),
            "title": quiz.title,
            "attempts": attempts,
            "average_score": round(avg_score, 2)
        })
    
    return {
        "course_info": {
            "id": course_id,
            "title": course.title,
            "category": course.category,
            "level": course.level
        },
        "enrollment_stats": {
            "total": total_enrollments,
            "active": active_enrollments,
            "completed": completed_enrollments,
            "completion_rate": round(completion_rate, 2),
            "recent_30d": len(recent_enrollments)
        },
        "learning_stats": {
            "average_progress": round(avg_progress, 2),
            "total_study_time": total_study_time,
            "avg_study_time_per_student": round(total_study_time / total_enrollments, 2) if total_enrollments > 0 else 0
        },
        "quiz_performance": quiz_stats,
        "generated_at": datetime.now(timezone.utc)
    }


async def get_student_progress_report(
    user_id: str,
    course_id: Optional[str] = None
) -> dict:
    """Lấy báo cáo tiến độ chi tiết cho học viên.
    
    Args:
        user_id: ID học viên
        course_id: ID khóa học (optional)
        
    Returns:
        Progress report
    """
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    if course_id:
        # Báo cáo cho 1 khóa học
        enrollment = await EnrollmentDocument.find_one(
            EnrollmentDocument.user_id == user_id,
            EnrollmentDocument.course_id == course_id
        )
        
        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bạn chưa đăng ký khóa học này"
            )
        
        progress = await ProgressDocument.find_one(
            ProgressDocument.user_id == user_id,
            ProgressDocument.course_id == course_id
        )
        
        course = await CourseDocument.get(course_id)
        
        return {
            "course": {
                "id": course_id,
                "title": course.title if course else "Unknown"
            },
            "progress": enrollment.progress,
            "completed_chapters": len(enrollment.completed_chapters),
            "quiz_scores": enrollment.quiz_scores,
            "total_study_time": enrollment.total_study_time,
            "streak_days": progress.streak_days if progress else 0,
            "last_accessed": enrollment.last_accessed,
            "enrolled_at": enrollment.enrolled_at
        }
    else:
        # Báo cáo tổng hợp
        enrollments = await EnrollmentDocument.find(
            EnrollmentDocument.user_id == user_id
        ).to_list()
        
        course_reports = []
        for enrollment in enrollments:
            course = await CourseDocument.get(enrollment.course_id)
            progress = await ProgressDocument.find_one(
                ProgressDocument.user_id == user_id,
                ProgressDocument.course_id == enrollment.course_id
            )
            
            course_reports.append({
                "course_id": enrollment.course_id,
                "course_title": course.title if course else "Unknown",
                "progress": enrollment.progress,
                "status": enrollment.status,
                "study_time": enrollment.total_study_time,
                "streak_days": progress.streak_days if progress else 0
            })
        
        return {
            "total_courses": len(enrollments),
            "courses": course_reports,
            "generated_at": datetime.now(timezone.utc)
        }


async def get_time_spent_analytics(
    user_id: str,
    period: str = "week"  # week, month, year
) -> dict:
    """Lấy phân tích thời gian học.
    
    Args:
        user_id: ID người dùng
        period: Khoảng thời gian
        
    Returns:
        Time analytics
    """
    # Xác định khoảng thời gian
    now = datetime.now(timezone.utc)
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)
    
    # Lấy enrollments
    enrollments = await EnrollmentDocument.find(
        EnrollmentDocument.user_id == user_id
    ).to_list()
    
    # Tính tổng thời gian trong period
    total_time = sum(e.total_study_time for e in enrollments)
    
    # Ước tính thời gian trung bình mỗi ngày
    days = (now - start_date).days
    avg_time_per_day = total_time / days if days > 0 else 0
    
    # Thời gian theo từng khóa học
    time_by_course = []
    for enrollment in enrollments:
        course = await CourseDocument.get(enrollment.course_id)
        time_by_course.append({
            "course_id": enrollment.course_id,
            "course_title": course.title if course else "Unknown",
            "study_time": enrollment.total_study_time
        })
    
    return {
        "period": period,
        "total_time": total_time,
        "avg_time_per_day": round(avg_time_per_day, 2),
        "time_by_course": sorted(time_by_course, key=lambda x: x["study_time"], reverse=True),
        "generated_at": datetime.now(timezone.utc)
    }


# Alias functions for compatibility
async def get_student_progress_stats(user_id: str, course_id: Optional[str] = None) -> dict:
    """Alias for get_student_progress_report."""
    return await get_student_progress_report(user_id, course_id)


async def get_instructor_course_stats(instructor_id: str) -> dict:
    """Alias for get_instructor_dashboard."""
    return await get_instructor_dashboard(instructor_id)


async def get_admin_system_stats() -> dict:
    """Alias for get_admin_dashboard."""
    return await get_admin_dashboard()
