"""Dịch vụ quản lý khóa học."""
from datetime import datetime, timezone
from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from models.models import CourseCreate, CourseDocument, CourseResponse, UserRole


async def list_courses(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    level: Optional[str] = None,
    visibility: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> tuple[List[CourseResponse], int]:
    """Trả về danh sách khóa học với filter và pagination.
    
    Args:
        skip: Số lượng bỏ qua
        limit: Số lượng tối đa
        category: Lọc theo danh mục
        level: Lọc theo cấp độ
        visibility: Lọc theo hiển thị (public/private/draft)
        search: Tìm kiếm trong title/description
        tags: Lọc theo tags
        
    Returns:
        Tuple (danh sách courses, tổng số)
    """
    # Xây dựng query conditions
    query_conditions = []
    
    if category:
        query_conditions.append(CourseDocument.category == category)
    
    if level:
        query_conditions.append(CourseDocument.level == level)
    
    if visibility:
        query_conditions.append(CourseDocument.visibility == visibility)
    
    if search:
        query_conditions.append({
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]
        })
    
    if tags:
        query_conditions.append({"tags": {"$in": tags}})
    
    # Query
    if query_conditions:
        query = CourseDocument.find(*query_conditions)
    else:
        query = CourseDocument.find_all()
    
    # Count và pagination
    total = await query.count()
    courses = await query.skip(skip).limit(limit).to_list()
    
    return [CourseResponse.model_validate(course, from_attributes=True) for course in courses], total


async def create_course(payload: CourseCreate, user_id: str, visibility: str = "draft") -> CourseResponse:
    """Tạo khóa học mới.
    
    Args:
        payload: Dữ liệu khóa học
        user_id: ID người tạo
        visibility: Trạng thái hiển thị
        
    Returns:
        Khóa học vừa tạo
    """
    now = datetime.now(timezone.utc)
    
    course_doc = CourseDocument(
        **payload.model_dump(),
        created_by=user_id,
        visibility=visibility,
        created_at=now,
        updated_at=now,
    )
    saved = await course_doc.insert()
    return CourseResponse.model_validate(saved, from_attributes=True)


async def get_course_by_id(course_id: PydanticObjectId) -> Optional[CourseResponse]:
    """Lấy chi tiết khóa học theo ID.
    
    Args:
        course_id: ID khóa học
        
    Returns:
        Thông tin khóa học hoặc None
    """
    course = await CourseDocument.get(course_id)
    if course is None:
        return None
    return CourseResponse.model_validate(course, from_attributes=True)


async def update_course(
    course_id: PydanticObjectId,
    update_data: dict,
    user_id: str,
    user_role: UserRole
) -> CourseResponse:
    """Cập nhật khóa học.
    
    Args:
        course_id: ID khóa học
        update_data: Dữ liệu cập nhật
        user_id: ID người cập nhật
        user_role: Vai trò người dùng
        
    Returns:
        Khóa học sau khi cập nhật
    """
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khóa học không tồn tại")
    
    # Kiểm tra quyền: chỉ owner hoặc admin mới được sửa
    if course.created_by != user_id and user_role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền sửa khóa học này"
        )
    
    # Các trường được phép update
    allowed_fields = {
        "title", "description", "level", "category", 
        "estimated_duration_hours", "tags", "modules"
    }
    
    for field, value in update_data.items():
        if field in allowed_fields and hasattr(course, field):
            setattr(course, field, value)
    
    course.updated_at = datetime.now(timezone.utc)
    await course.save()
    
    return CourseResponse.model_validate(course, from_attributes=True)


async def delete_course(
    course_id: PydanticObjectId,
    user_id: str,
    user_role: UserRole
) -> bool:
    """Xóa khóa học.
    
    Args:
        course_id: ID khóa học
        user_id: ID người xóa
        user_role: Vai trò người dùng
        
    Returns:
        True nếu xóa thành công
    """
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khóa học không tồn tại")
    
    # Kiểm tra quyền
    if course.created_by != user_id and user_role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa khóa học này"
        )
    
    await course.delete()
    return True


async def publish_course(
    course_id: PydanticObjectId,
    user_id: str,
    user_role: UserRole
) -> CourseResponse:
    """Publish khóa học (chuyển từ draft sang public).
    
    Args:
        course_id: ID khóa học
        user_id: ID người publish
        user_role: Vai trò người dùng
        
    Returns:
        Khóa học sau khi publish
    """
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khóa học không tồn tại")
    
    # Kiểm tra quyền
    if course.created_by != user_id and user_role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền publish khóa học này"
        )
    
    course.visibility = "public"
    course.updated_at = datetime.now(timezone.utc)
    await course.save()
    
    return CourseResponse.model_validate(course, from_attributes=True)


async def unpublish_course(
    course_id: PydanticObjectId,
    user_id: str,
    user_role: UserRole
) -> CourseResponse:
    """Unpublish khóa học (chuyển về draft).
    
    Args:
        course_id: ID khóa học
        user_id: ID người unpublish
        user_role: Vai trò người dùng
        
    Returns:
        Khóa học sau khi unpublish
    """
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khóa học không tồn tại")
    
    # Kiểm tra quyền
    if course.created_by != user_id and user_role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền unpublish khóa học này"
        )
    
    course.visibility = "draft"
    course.updated_at = datetime.now(timezone.utc)
    await course.save()
    
    return CourseResponse.model_validate(course, from_attributes=True)


async def duplicate_course(
    course_id: PydanticObjectId,
    user_id: str,
    new_title: Optional[str] = None
) -> CourseResponse:
    """Sao chép khóa học.
    
    Args:
        course_id: ID khóa học gốc
        user_id: ID người sao chép
        new_title: Tiêu đề mới (optional)
        
    Returns:
        Khóa học mới được sao chép
    """
    original = await CourseDocument.get(course_id)
    if original is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khóa học không tồn tại")
    
    # Tạo bản sao
    now = datetime.now(timezone.utc)
    course_data = original.model_dump(exclude={"id", "created_at", "updated_at", "created_by"})
    
    if new_title:
        course_data["title"] = new_title
    else:
        course_data["title"] = f"{original.title} (Copy)"
    
    course_data["created_by"] = user_id
    course_data["visibility"] = "draft"  # Copy luôn bắt đầu ở draft
    course_data["created_at"] = now
    course_data["updated_at"] = now
    
    new_course = CourseDocument(**course_data)
    await new_course.insert()
    
    return CourseResponse.model_validate(new_course, from_attributes=True)


async def get_courses_by_instructor(
    instructor_id: str,
    skip: int = 0,
    limit: int = 10
) -> tuple[List[CourseResponse], int]:
    """Lấy danh sách khóa học của instructor.
    
    Args:
        instructor_id: ID instructor
        skip: Bỏ qua
        limit: Giới hạn
        
    Returns:
        Tuple (courses, total)
    """
    query = CourseDocument.find(CourseDocument.created_by == instructor_id)
    total = await query.count()
    courses = await query.skip(skip).limit(limit).to_list()
    
    return [CourseResponse.model_validate(c, from_attributes=True) for c in courses], total


async def get_public_courses(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    level: Optional[str] = None,
) -> tuple[List[CourseResponse], int]:
    """Lấy danh sách khóa học công khai.
    
    Args:
        skip: Bỏ qua
        limit: Giới hạn
        category: Lọc danh mục
        level: Lọc cấp độ
        
    Returns:
        Tuple (courses, total)
    """
    return await list_courses(
        skip=skip,
        limit=limit,
        category=category,
        level=level,
        visibility="public"
    )
