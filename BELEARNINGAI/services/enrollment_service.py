"""Dịch vụ quản lý enrollment và tiến độ học tập."""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status

from models.models import (
    EnrollmentDocument,
    EnrollmentStatus,
    CourseDocument,
    UserDocument,
    ClassDocument,
    UserRole
)


async def enroll_course(
    user_id: str,
    course_id: str,
    class_id: Optional[str] = None
) -> dict:
    """Đăng ký khóa học hoặc tham gia lớp học.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        class_id: ID lớp học (optional)
        
    Returns:
        Thông tin enrollment
    """
    # Kiểm tra user
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    # Kiểm tra course
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra khóa học đã published
    if not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Khóa học chưa được công khai"
        )
    
    # Kiểm tra đã enroll chưa
    existing = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn đã đăng ký khóa học này rồi"
        )
    
    # Nếu có class_id, kiểm tra lớp học
    if class_id:
        class_doc = await ClassDocument.get(class_id)
        if class_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lớp học không tồn tại"
            )
        
        # Kiểm tra lớp học đầy chưa
        if class_doc.max_students and class_doc.current_students >= class_doc.max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lớp học đã đầy"
            )
    
    # Tạo enrollment
    now = datetime.now(timezone.utc)
    enrollment_doc = EnrollmentDocument(
        user_id=user_id,
        course_id=course_id,
        class_id=class_id,
        status=EnrollmentStatus.active,
        progress=0.0,
        completed_chapters=[],
        quiz_scores={},
        total_study_time=0,
        last_accessed=now,
        enrolled_at=now,
        completed_at=None
    )
    
    await enrollment_doc.insert()
    
    # Nếu có class, thêm student vào class
    if class_id and class_doc:
        if user_id not in class_doc.student_ids:
            class_doc.student_ids.append(user_id)
            class_doc.current_students += 1
            class_doc.updated_at = now
            await class_doc.save()
    
    return {
        "id": str(enrollment_doc.id),
        "user_id": enrollment_doc.user_id,
        "course_id": enrollment_doc.course_id,
        "class_id": enrollment_doc.class_id,
        "status": enrollment_doc.status,
        "progress": enrollment_doc.progress,
        "enrolled_at": enrollment_doc.enrolled_at
    }


async def unenroll_course(user_id: str, course_id: str) -> bool:
    """Hủy đăng ký khóa học.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        
    Returns:
        True nếu thành công
    """
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bạn chưa đăng ký khóa học này"
        )
    
    # Nếu có class, xóa khỏi class
    if enrollment.class_id:
        class_doc = await ClassDocument.get(enrollment.class_id)
        if class_doc and user_id in class_doc.student_ids:
            class_doc.student_ids.remove(user_id)
            class_doc.current_students -= 1
            class_doc.updated_at = datetime.now(timezone.utc)
            await class_doc.save()
    
    await enrollment.delete()
    return True


async def get_enrollment(user_id: str, course_id: str) -> Optional[dict]:
    """Lấy thông tin enrollment.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        
    Returns:
        Thông tin enrollment hoặc None
    """
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment is None:
        return None
    
    return {
        "id": str(enrollment.id),
        "user_id": enrollment.user_id,
        "course_id": enrollment.course_id,
        "class_id": enrollment.class_id,
        "status": enrollment.status,
        "progress": enrollment.progress,
        "completed_chapters": enrollment.completed_chapters,
        "quiz_scores": enrollment.quiz_scores,
        "total_study_time": enrollment.total_study_time,
        "last_accessed": enrollment.last_accessed,
        "enrolled_at": enrollment.enrolled_at,
        "completed_at": enrollment.completed_at
    }


async def check_enrollment_status(user_id: str, course_id: str) -> dict:
    """Kiểm tra trạng thái đăng ký.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học
        
    Returns:
        {"enrolled": bool, "progress": float, "status": str}
    """
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment is None:
        return {
            "enrolled": False,
            "progress": 0.0,
            "status": None
        }
    
    return {
        "enrolled": True,
        "progress": enrollment.progress,
        "status": enrollment.status
    }


async def list_user_enrollments(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None
) -> tuple[List[dict], int]:
    """Lấy danh sách enrollment của user.
    
    Args:
        user_id: ID người dùng
        skip: Bỏ qua
        limit: Giới hạn
        status: Lọc theo trạng thái
        
    Returns:
        Tuple (enrollments, total)
    """
    query_conditions = [EnrollmentDocument.user_id == user_id]
    
    if status:
        query_conditions.append(EnrollmentDocument.status == status)
    
    query = EnrollmentDocument.find(*query_conditions)
    total = await query.count()
    enrollments = await query.sort(-EnrollmentDocument.enrolled_at).skip(skip).limit(limit).to_list()
    
    enrollment_list = []
    for enrollment in enrollments:
        enrollment_list.append({
            "id": str(enrollment.id),
            "course_id": enrollment.course_id,
            "class_id": enrollment.class_id,
            "status": enrollment.status,
            "progress": enrollment.progress,
            "total_study_time": enrollment.total_study_time,
            "last_accessed": enrollment.last_accessed,
            "enrolled_at": enrollment.enrolled_at
        })
    
    return enrollment_list, total


async def get_course_enrollments(
    course_id: str,
    skip: int = 0,
    limit: int = 10,
    instructor_id: Optional[str] = None
) -> tuple[List[dict], int]:
    """Lấy danh sách enrollment của khóa học (cho instructor/admin).
    
    Args:
        course_id: ID khóa học
        skip: Bỏ qua
        limit: Giới hạn
        instructor_id: ID instructor (để kiểm tra quyền)
        
    Returns:
        Tuple (enrollments, total)
    """
    # Kiểm tra quyền xem
    if instructor_id:
        course = await CourseDocument.get(course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khóa học không tồn tại"
            )
        
        instructor = await UserDocument.get(instructor_id)
        if instructor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instructor không tồn tại"
            )
        
        # Chỉ owner hoặc admin mới xem được
        if course.created_by != instructor_id and instructor.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xem danh sách enrollment"
            )
    
    query = EnrollmentDocument.find(EnrollmentDocument.course_id == course_id)
    total = await query.count()
    enrollments = await query.sort(-EnrollmentDocument.enrolled_at).skip(skip).limit(limit).to_list()
    
    enrollment_list = []
    for enrollment in enrollments:
        enrollment_list.append({
            "id": str(enrollment.id),
            "user_id": enrollment.user_id,
            "status": enrollment.status,
            "progress": enrollment.progress,
            "total_study_time": enrollment.total_study_time,
            "last_accessed": enrollment.last_accessed,
            "enrolled_at": enrollment.enrolled_at
        })
    
    return enrollment_list, total


async def update_enrollment_progress(
    enrollment_id: str,
    user_id: str,
    progress: float,
    completed_chapter: Optional[str] = None
) -> dict:
    """Cập nhật tiến độ học tập.
    
    Args:
        enrollment_id: ID enrollment
        user_id: ID người dùng
        progress: Tiến độ mới (%)
        completed_chapter: ID chapter vừa hoàn thành
        
    Returns:
        Thông tin enrollment sau cập nhật
    """
    enrollment = await EnrollmentDocument.get(enrollment_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment không tồn tại"
        )
    
    # Kiểm tra quyền
    if enrollment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật enrollment này"
        )
    
    # Cập nhật progress
    enrollment.progress = min(progress, 100.0)
    enrollment.last_accessed = datetime.now(timezone.utc)
    
    # Thêm chapter đã hoàn thành
    if completed_chapter and completed_chapter not in enrollment.completed_chapters:
        enrollment.completed_chapters.append(completed_chapter)
    
    # Nếu hoàn thành 100%
    if enrollment.progress >= 100.0 and enrollment.status != EnrollmentStatus.completed:
        enrollment.status = EnrollmentStatus.completed
        enrollment.completed_at = datetime.now(timezone.utc)
    
    await enrollment.save()
    
    return {
        "id": str(enrollment.id),
        "progress": enrollment.progress,
        "status": enrollment.status,
        "completed_chapters": enrollment.completed_chapters,
        "completed_at": enrollment.completed_at,
        "last_accessed": enrollment.last_accessed
    }


async def update_study_time(
    enrollment_id: str,
    user_id: str,
    minutes: int
) -> dict:
    """Cập nhật thời gian học.
    
    Args:
        enrollment_id: ID enrollment
        user_id: ID người dùng
        minutes: Số phút học thêm
        
    Returns:
        Thông tin enrollment
    """
    enrollment = await EnrollmentDocument.get(enrollment_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment không tồn tại"
        )
    
    if enrollment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật enrollment này"
        )
    
    enrollment.total_study_time += minutes
    enrollment.last_accessed = datetime.now(timezone.utc)
    await enrollment.save()
    
    return {
        "id": str(enrollment.id),
        "total_study_time": enrollment.total_study_time,
        "last_accessed": enrollment.last_accessed
    }


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Alias cho controller
list_enrollments = list_user_enrollments
get_user_course_progress = get_enrollment  # get_enrollment trả về progress
update_user_course_progress = update_enrollment_progress


async def get_enrollment_by_id(enrollment_id: str, user_id: str = None) -> Optional[dict]:
    """Lấy enrollment theo ID.
    
    Args:
        enrollment_id: ID enrollment
        user_id: Optional - ID user để check quyền
        
    Returns:
        Enrollment data hoặc None
    """
    enrollment = await EnrollmentDocument.get(enrollment_id)
    
    if enrollment is None:
        return None
    
    # Check quyền nếu user_id được cung cấp
    if user_id and enrollment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập enrollment này"
        )
    
    return {
        "id": str(enrollment.id),
        "user_id": enrollment.user_id,
        "course_id": enrollment.course_id,
        "class_id": enrollment.class_id,
        "status": enrollment.status,
        "progress": enrollment.progress,
        "completed_chapters": enrollment.completed_chapters,
        "enrolled_at": enrollment.enrolled_at,
        "last_accessed": enrollment.last_accessed,
        "completion_date": enrollment.completion_date,
        "total_study_time": enrollment.total_study_time
    }
