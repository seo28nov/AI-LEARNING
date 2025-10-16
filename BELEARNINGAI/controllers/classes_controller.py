"""Controller cho module lớp học."""

from fastapi import HTTPException, status

from services.classes_service import (
    create_class,
    get_class_by_id,
    list_classes_by_instructor,
    update_class,
    delete_class,
    generate_join_code,
    join_class_with_code,
    get_class_roster,
    remove_student_from_class
)


async def handle_list_classes(
    instructor_id: str,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Danh sách lớp học của instructor."""
    
    classes, total = await list_classes_by_instructor(
        instructor_id=instructor_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "classes": classes,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_create_class(payload: dict, instructor_id: str) -> dict:
    """Tạo lớp học mới."""
    
    return await create_class(
        name=payload.get("name"),
        description=payload.get("description", ""),
        course_id=payload.get("course_id"),
        instructor_id=instructor_id
    )


async def handle_get_class(class_id: str) -> dict:
    """Lấy chi tiết lớp học."""
    
    return await get_class_by_id(class_id)


async def handle_update_class(class_id: str, payload: dict, instructor_id: str) -> dict:
    """Cập nhật lớp học."""
    
    return await update_class(class_id, payload, instructor_id)


async def handle_delete_class(class_id: str, instructor_id: str) -> dict:
    """Xóa lớp học."""
    
    await delete_class(class_id, instructor_id)
    return {"message": "Lớp học đã được xóa"}


async def handle_generate_invite(class_id: str, instructor_id: str) -> dict:
    """Tạo mã mời tham gia lớp."""
    
    return await generate_join_code(class_id, instructor_id)


async def handle_join_class(payload: dict, user_id: str) -> dict:
    """Tham gia lớp bằng mã mời."""
    
    join_code = payload.get("join_code")
    if not join_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Join code is required"
        )
    
    return await join_class_with_code(join_code, user_id)


async def handle_list_roster(class_id: str) -> dict:
    """Danh sách học viên trong lớp."""
    
    students = await get_class_roster(class_id)
    
    return {
        "class_id": class_id,
        "students": students,
        "total": len(students)
    }


async def handle_remove_student(class_id: str, student_id: str, instructor_id: str) -> dict:
    """Xóa học viên khỏi lớp."""
    
    await remove_student_from_class(class_id, student_id, instructor_id)
    return {"message": "Học viên đã được xóa khỏi lớp"}


# Alias for router compatibility
async def handle_class_detail(class_id: str, current_user: dict) -> dict:
    """Alias for handle_get_class."""
    return await handle_get_class(class_id)
