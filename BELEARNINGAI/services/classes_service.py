"""Dịch vụ quản lý lớp học (dành cho Instructor)."""
import secrets
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status

from models.models import ClassDocument, CourseDocument, UserDocument, UserRole


def generate_class_code() -> str:
    """Tạo mã lớp học ngẫu nhiên (8 ký tự)."""
    return secrets.token_urlsafe(6).upper()[:8]


async def create_class(
    name: str,
    course_id: str,
    instructor_id: str,
    description: str = "",
    max_students: Optional[int] = None,
    **kwargs
) -> dict:
    """Tạo lớp học mới từ khóa học có sẵn.
    
    Args:
        name: Tên lớp học
        course_id: ID khóa học gốc
        instructor_id: ID giảng viên
        description: Mô tả lớp học
        max_students: Số học viên tối đa
        **kwargs: Các thiết lập khác
        
    Returns:
        Thông tin lớp học vừa tạo
    """
    # Kiểm tra instructor
    instructor = await UserDocument.get(instructor_id)
    if instructor is None or instructor.role not in [UserRole.instructor, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ instructor hoặc admin mới có thể tạo lớp học"
        )
    
    # Kiểm tra khóa học tồn tại
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Tạo mã lớp duy nhất
    class_code = generate_class_code()
    
    # Kiểm tra mã lớp đã tồn tại chưa
    existing = await ClassDocument.find_one(ClassDocument.class_code == class_code)
    while existing is not None:
        class_code = generate_class_code()
        existing = await ClassDocument.find_one(ClassDocument.class_code == class_code)
    
    # Tạo lớp học
    now = datetime.now(timezone.utc)
    class_doc = ClassDocument(
        name=name,
        description=description,
        instructor_id=instructor_id,
        course_id=course_id,
        class_code=class_code,
        max_students=max_students,
        current_students=0,
        student_ids=[],
        status="upcoming",
        created_at=now,
        updated_at=now,
        **kwargs
    )
    
    await class_doc.insert()
    
    return {
        "id": str(class_doc.id),
        "name": class_doc.name,
        "description": class_doc.description,
        "instructor_id": class_doc.instructor_id,
        "course_id": class_doc.course_id,
        "class_code": class_doc.class_code,
        "max_students": class_doc.max_students,
        "current_students": class_doc.current_students,
        "status": class_doc.status,
        "created_at": class_doc.created_at,
        "updated_at": class_doc.updated_at
    }


async def get_class_by_id(class_id: str, user_id: str, user_role: UserRole) -> dict:
    """Lấy thông tin chi tiết lớp học.
    
    Args:
        class_id: ID lớp học
        user_id: ID người yêu cầu
        user_role: Vai trò người dùng
        
    Returns:
        Thông tin lớp học
    """
    class_doc = await ClassDocument.get(class_id)
    if class_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại"
        )
    
    # Kiểm tra quyền xem: instructor owner, student trong lớp, hoặc admin
    is_instructor = class_doc.instructor_id == user_id
    is_student = user_id in class_doc.student_ids
    is_admin = user_role == UserRole.admin
    
    if not (is_instructor or is_student or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem lớp học này"
        )
    
    return {
        "id": str(class_doc.id),
        "name": class_doc.name,
        "description": class_doc.description,
        "instructor_id": class_doc.instructor_id,
        "course_id": class_doc.course_id,
        "class_code": class_doc.class_code,
        "max_students": class_doc.max_students,
        "current_students": class_doc.current_students,
        "student_ids": class_doc.student_ids,
        "status": class_doc.status,
        "created_at": class_doc.created_at,
        "updated_at": class_doc.updated_at
    }


async def get_class_by_code(class_code: str) -> Optional[dict]:
    """Tìm lớp học theo mã lớp (để join).
    
    Args:
        class_code: Mã lớp học
        
    Returns:
        Thông tin lớp học hoặc None
    """
    class_doc = await ClassDocument.find_one(ClassDocument.class_code == class_code.upper())
    if class_doc is None:
        return None
    
    return {
        "id": str(class_doc.id),
        "name": class_doc.name,
        "description": class_doc.description,
        "instructor_id": class_doc.instructor_id,
        "course_id": class_doc.course_id,
        "class_code": class_doc.class_code,
        "max_students": class_doc.max_students,
        "current_students": class_doc.current_students,
        "status": class_doc.status
    }


async def add_student_to_class(class_id: str, student_id: str, instructor_id: str) -> dict:
    """Thêm học viên vào lớp.
    
    Args:
        class_id: ID lớp học
        student_id: ID học viên
        instructor_id: ID giảng viên thực hiện
        
    Returns:
        Thông tin lớp học sau khi cập nhật
    """
    class_doc = await ClassDocument.get(class_id)
    if class_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại"
        )
    
    # Kiểm tra quyền
    if class_doc.instructor_id != instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giảng viên của lớp mới có thể thêm học viên"
        )
    
    # Kiểm tra học viên tồn tại
    student = await UserDocument.get(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Học viên không tồn tại"
        )
    
    # Kiểm tra đã trong lớp chưa
    if student_id in class_doc.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Học viên đã có trong lớp"
        )
    
    # Kiểm tra giới hạn số lượng
    if class_doc.max_students and class_doc.current_students >= class_doc.max_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lớp học đã đầy"
        )
    
    # Thêm học viên
    class_doc.student_ids.append(student_id)
    class_doc.current_students += 1
    class_doc.updated_at = datetime.now(timezone.utc)
    await class_doc.save()
    
    return {
        "id": str(class_doc.id),
        "name": class_doc.name,
        "current_students": class_doc.current_students,
        "student_ids": class_doc.student_ids,
        "updated_at": class_doc.updated_at
    }


async def remove_student_from_class(class_id: str, student_id: str, instructor_id: str) -> dict:
    """Xóa học viên khỏi lớp.
    
    Args:
        class_id: ID lớp học
        student_id: ID học viên
        instructor_id: ID giảng viên thực hiện
        
    Returns:
        Thông tin lớp học sau khi cập nhật
    """
    class_doc = await ClassDocument.get(class_id)
    if class_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại"
        )
    
    # Kiểm tra quyền
    if class_doc.instructor_id != instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giảng viên của lớp mới có thể xóa học viên"
        )
    
    # Kiểm tra học viên có trong lớp
    if student_id not in class_doc.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Học viên không có trong lớp"
        )
    
    # Xóa học viên
    class_doc.student_ids.remove(student_id)
    class_doc.current_students -= 1
    class_doc.updated_at = datetime.now(timezone.utc)
    await class_doc.save()
    
    return {
        "id": str(class_doc.id),
        "name": class_doc.name,
        "current_students": class_doc.current_students,
        "student_ids": class_doc.student_ids,
        "updated_at": class_doc.updated_at
    }


async def update_class(
    class_id: str,
    update_data: dict,
    instructor_id: str
) -> dict:
    """Cập nhật thông tin lớp học.
    
    Args:
        class_id: ID lớp học
        update_data: Dữ liệu cập nhật
        instructor_id: ID giảng viên
        
    Returns:
        Thông tin lớp học sau khi cập nhật
    """
    class_doc = await ClassDocument.get(class_id)
    if class_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại"
        )
    
    # Kiểm tra quyền
    if class_doc.instructor_id != instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giảng viên của lớp mới có thể cập nhật"
        )
    
    # Các trường được phép update
    allowed_fields = {
        "name", "description", "max_students", "start_date", "end_date",
        "auto_enroll", "allow_late_join", "discussion_enabled", "ai_tutor_enabled",
        "status"
    }
    
    for field, value in update_data.items():
        if field in allowed_fields and hasattr(class_doc, field):
            setattr(class_doc, field, value)
    
    class_doc.updated_at = datetime.now(timezone.utc)
    await class_doc.save()
    
    return {
        "id": str(class_doc.id),
        "name": class_doc.name,
        "description": class_doc.description,
        "max_students": class_doc.max_students,
        "status": class_doc.status,
        "updated_at": class_doc.updated_at
    }


async def delete_class(class_id: str, instructor_id: str) -> bool:
    """Xóa lớp học.
    
    Args:
        class_id: ID lớp học
        instructor_id: ID giảng viên
        
    Returns:
        True nếu xóa thành công
    """
    class_doc = await ClassDocument.get(class_id)
    if class_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại"
        )
    
    # Kiểm tra quyền
    if class_doc.instructor_id != instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ giảng viên của lớp mới có thể xóa"
        )
    
    await class_doc.delete()
    return True


async def list_classes(
    instructor_id: str,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None
) -> tuple[List[dict], int]:
    """Lấy danh sách lớp học của instructor.
    
    Args:
        instructor_id: ID giảng viên
        skip: Bỏ qua
        limit: Giới hạn
        status: Lọc theo trạng thái
        
    Returns:
        Tuple (classes, total)
    """
    query_conditions = [ClassDocument.instructor_id == instructor_id]
    
    if status:
        query_conditions.append(ClassDocument.status == status)
    
    query = ClassDocument.find(*query_conditions)
    total = await query.count()
    classes = await query.skip(skip).limit(limit).to_list()
    
    class_list = []
    for class_doc in classes:
        class_list.append({
            "id": str(class_doc.id),
            "name": class_doc.name,
            "description": class_doc.description,
            "course_id": class_doc.course_id,
            "class_code": class_doc.class_code,
            "current_students": class_doc.current_students,
            "max_students": class_doc.max_students,
            "status": class_doc.status,
            "created_at": class_doc.created_at,
            "updated_at": class_doc.updated_at
        })
    
    return class_list, total


async def get_student_classes(
    student_id: str,
    skip: int = 0,
    limit: int = 10
) -> tuple[List[dict], int]:
    """Lấy danh sách lớp học mà học viên tham gia.
    
    Args:
        student_id: ID học viên
        skip: Bỏ qua
        limit: Giới hạn
        
    Returns:
        Tuple (classes, total)
    """
    query = ClassDocument.find(ClassDocument.student_ids == student_id)
    total = await query.count()
    classes = await query.skip(skip).limit(limit).to_list()
    
    class_list = []
    for class_doc in classes:
        class_list.append({
            "id": str(class_doc.id),
            "name": class_doc.name,
            "description": class_doc.description,
            "course_id": class_doc.course_id,
            "instructor_id": class_doc.instructor_id,
            "current_students": class_doc.current_students,
            "status": class_doc.status,
            "created_at": class_doc.created_at
        })
    
    return class_list, total


# Aliases and missing functions for controller compatibility
async def list_classes_by_instructor(
    instructor_id: str,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None
) -> tuple:
    """Alias for list_classes filtered by instructor."""
    return await list_classes(
        instructor_id=instructor_id,
        skip=skip,
        limit=limit,
        status=status
    )


async def generate_join_code(class_id: str, instructor_id: str) -> dict:
    """Generate a unique join code for the class."""
    import secrets
    
    class_doc = await ClassDocument.get(class_id)
    if not class_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    if class_doc.instructor_id != instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructor can generate join code"
        )
    
    # Generate 8-character code
    join_code = secrets.token_urlsafe(6).upper()[:8]
    
    # Update class with join code
    class_doc.join_code = join_code
    await class_doc.save()
    
    return {
        "class_id": str(class_doc.id),
        "join_code": join_code,
        "expires_at": None  # Can add expiration logic later
    }


async def join_class_with_code(join_code: str, student_id: str) -> dict:
    """Allow student to join class using join code."""
    class_doc = await ClassDocument.find_one(ClassDocument.join_code == join_code)
    
    if not class_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid join code"
        )
    
    # Check if already enrolled
    if student_id in class_doc.student_ids:
        return {
            "message": "Already enrolled in this class",
            "class_id": str(class_doc.id),
            "class_name": class_doc.name
        }
    
    # Add student to class
    class_doc.student_ids.append(student_id)
    class_doc.current_students += 1
    await class_doc.save()
    
    return {
        "message": "Successfully joined class",
        "class_id": str(class_doc.id),
        "class_name": class_doc.name
    }


async def get_class_roster(class_id: str, user_id: str, user_role: UserRole) -> dict:
    """Get list of students in a class."""
    class_doc = await ClassDocument.get(class_id)
    
    if not class_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # Check permissions
    if user_role == UserRole.student and user_id not in class_doc.student_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this class"
        )
    
    if user_role == UserRole.instructor and class_doc.instructor_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the instructor of this class"
        )
    
    # Get student details
    students = []
    for student_id in class_doc.student_ids:
        user = await UserDocument.get(student_id)
        if user:
            students.append({
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "enrolled_at": class_doc.created_at  # Can track individual enrollment dates
            })
    
    return {
        "class_id": str(class_doc.id),
        "class_name": class_doc.name,
        "total_students": class_doc.current_students,
        "students": students
    }
