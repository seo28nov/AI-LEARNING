"""Controller điều phối luồng dữ liệu khóa học."""
from typing import List, Optional

from fastapi import HTTPException, status

from schemas.common import MessageResponse
from services.course_service import (
    list_courses,
    create_course,
    get_course_by_id,
    update_course,
    delete_course,
    publish_course,
    unpublish_course,
    duplicate_course,
    get_courses_by_instructor,
    get_public_courses
)
from services.chat_service import generate_course_content
from services.course_indexing_service import course_indexing_service


async def handle_list_courses(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None
) -> dict:
    """Lấy danh sách khóa học với filters."""
    
    courses, total = await list_courses(
        user_id=user_id,
        skip=skip,
        limit=limit,
        category=category,
        level=level,
        search=search
    )
    
    return {
        "courses": courses,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_create_course(payload: dict, user_id: str) -> dict:
    """Tạo khóa học mới."""
    
    return await create_course(
        title=payload.get("title"),
        description=payload.get("description", ""),
        category=payload.get("category"),
        level=payload.get("level", "beginner"),
        language=payload.get("language", "vi"),
        chapters=payload.get("chapters", []),
        user_id=user_id
    )


async def handle_get_course(course_id: str) -> dict:
    """Lấy chi tiết khóa học."""
    
    return await get_course_by_id(course_id)


async def handle_update_course(course_id: str, payload: dict, user_id: str, user_role: str) -> dict:
    """Cập nhật khóa học."""
    
    return await update_course(course_id, payload, user_id, user_role)


async def handle_delete_course(course_id: str, user_id: str, user_role: str) -> dict:
    """Xóa khóa học."""
    
    await delete_course(course_id, user_id, user_role)
    return {"message": "Khóa học đã được xóa"}


async def handle_publish_course(course_id: str, user_id: str, user_role: str) -> dict:
    """Công khai khóa học."""
    
    return await publish_course(course_id, user_id, user_role)


async def handle_unpublish_course(course_id: str, user_id: str, user_role: str) -> dict:
    """Ẩn khóa học."""
    
    return await unpublish_course(course_id, user_id, user_role)


async def handle_list_public_courses(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None
) -> dict:
    """Danh sách khóa học công khai."""
    
    courses, total = await get_public_courses(
        skip=skip,
        limit=limit,
        category=category,
        level=level,
        search=search
    )
    
    return {
        "courses": courses,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_instructor_courses(
    instructor_id: str,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Danh sách khóa học của instructor."""
    
    courses, total = await get_courses_by_instructor(
        instructor_id=instructor_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "courses": courses,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_duplicate_course(course_id: str, user_id: str, user_role: str) -> dict:
    """Sao chép khóa học."""
    
    return await duplicate_course(course_id, user_id, user_role)


async def handle_create_course_from_prompt(payload: dict, user_id: str) -> dict:
    """Tạo khóa học bằng AI từ prompt."""
    
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic is required"
        )
    
    level = payload.get("level", "beginner")
    num_chapters = payload.get("num_chapters", 5)
    
    # Generate course content với AI
    course_content = await generate_course_content(
        topic=topic,
        level=level,
        num_chapters=num_chapters
    )
    
    # Tạo course từ generated content
    return await create_course(
        title=course_content.get("title"),
        description=course_content.get("description"),
        category=payload.get("category", "programming"),
        level=level,
        language="vi",
        chapters=course_content.get("chapters", []),
        user_id=user_id
    )


async def handle_search_courses(
    keyword: str,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Tìm kiếm khóa học."""
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword is required"
        )
    
    courses, total = await get_public_courses(
        skip=skip,
        limit=limit,
        search=keyword
    )
    
    return {
        "courses": courses,
        "total": total,
        "keyword": keyword,
        "skip": skip,
        "limit": limit
    }


async def handle_course_categories() -> dict:
    """Danh sách categories."""
    
    categories = [
        {"id": "programming", "name": "Lập trình"},
        {"id": "design", "name": "Thiết kế"},
        {"id": "business", "name": "Kinh doanh"},
        {"id": "data_science", "name": "Khoa học dữ liệu"},
        {"id": "marketing", "name": "Marketing"},
        {"id": "languages", "name": "Ngôn ngữ"}
    ]
    
    return {"categories": categories}



async def handle_create_chapter(course_id: str, payload: dict) -> MessageResponse:
    """Placeholder thêm chương mới."""

    chapter_title = payload.get("title", "Chương mới")
    return MessageResponse(message=f"Placeholder: đã tạo chương '{chapter_title}' cho khóa {course_id}")


async def handle_update_chapter(course_id: str, chapter_id: str, payload: dict) -> MessageResponse:
    """Placeholder cập nhật chương."""

    chapter_title = payload.get("title", "Chương cập nhật")
    return MessageResponse(
        message=f"Placeholder: đã cập nhật chương {chapter_id} của khóa {course_id} thành '{chapter_title}'"
    )


async def handle_delete_chapter(course_id: str, chapter_id: str) -> MessageResponse:
    """Placeholder xóa chương."""

    return MessageResponse(message=f"Placeholder: đã xóa chương {chapter_id} khỏi khóa {course_id}")


async def handle_index_course(course_id: str, user_id: str, user_role: str) -> dict:
    """
    Index course vào FAISS Vector Database để sử dụng cho RAG.
    
    Args:
        course_id: ID của course cần index
        user_id: ID người thực hiện
        user_role: Role của user (instructor/admin)
        
    Returns:
        Dict với thông tin indexing
    """
    from models.models import CourseDocument
    
    # Lấy course từ MongoDB
    course = await CourseDocument.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra quyền: instructor chỉ index course của mình, admin index tất cả
    if user_role != "admin" and str(course.created_by) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền index khóa học này"
        )
    
    # Index course
    result = await course_indexing_service.index_course(course)
    
    return {
        "message": "Khóa học đã được index thành công",
        "course_id": course_id,
        "course_title": course.title,
        **result
    }


async def handle_reindex_course(course_id: str, user_id: str, user_role: str) -> dict:
    """
    Reindex course (xóa embeddings cũ và index lại).
    
    Args:
        course_id: ID của course cần reindex
        user_id: ID người thực hiện
        user_role: Role của user
        
    Returns:
        Dict với thông tin reindexing
    """
    from models.models import CourseDocument
    
    # Lấy course
    course = await CourseDocument.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra quyền
    if user_role != "admin" and str(course.created_by) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền reindex khóa học này"
        )
    
    # Reindex course
    result = await course_indexing_service.reindex_course(str(course.id))
    
    return {
        "message": "Khóa học đã được reindex thành công",
        "course_id": course_id,
        "course_title": course.title,
        **result
    }


async def handle_index_all_courses(user_role: str) -> dict:
    """
    Index tất cả courses vào FAISS Vector Database (Admin only).
    
    Args:
        user_role: Role của user (phải là admin)
        
    Returns:
        Dict với thống kê indexing
    """
    from models.models import CourseDocument
    
    # Chỉ admin mới được index all
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền index tất cả khóa học"
        )
    
    # Lấy tất cả courses
    courses = await CourseDocument.find_all().to_list()
    
    if not courses:
        return {
            "message": "Không có khóa học nào để index",
            "total": 0,
            "successful": 0,
            "failed": 0
        }
    
    # Index từng course
    successful = 0
    failed = 0
    errors = []
    
    for course in courses:
        try:
            await course_indexing_service.index_course(course)
            successful += 1
        except Exception as e:
            failed += 1
            errors.append({
                "course_id": str(course.id),
                "course_title": course.title,
                "error": str(e)
            })
    
    return {
        "message": f"Đã index {successful}/{len(courses)} khóa học",
        "total": len(courses),
        "successful": successful,
        "failed": failed,
        "errors": errors if errors else None
    }


# Missing functions for router compatibility
async def handle_create_course_from_upload(payload: dict, user_id: str) -> dict:
    """Tạo khóa học từ file upload (PDF, etc.)."""
    # Placeholder implementation
    return {
        "message": "Course creation from upload is not yet implemented",
        "course_id": None,
        "status": "pending"
    }


async def handle_list_chapters(course_id: str) -> dict:
    """Lấy danh sách chương của khóa học."""
    course = await get_course_by_id(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get modules (chapters) from course
    modules = course.get("modules", [])
    
    return {
        "course_id": course_id,
        "chapters": modules,
        "total": len(modules)
    }


async def handle_recommended_courses(user_id: str) -> List[dict]:
    """Lấy danh sách khóa học được gợi ý cho user."""
    # Placeholder - could integrate with recommendation service
    public_courses = await get_public_courses(limit=10)
    
    return {
        "user_id": user_id,
        "recommendations": public_courses[:5],
        "total": len(public_courses[:5])
    }


async def handle_update_visibility(course_id: str, payload: dict, user_id: str, user_role: str) -> dict:
    """Update course visibility (publish/unpublish)."""
    is_published = payload.get("is_published")
    
    if is_published is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="is_published field is required"
        )
    
    if is_published:
        return await handle_publish_course(course_id, user_id, user_role)
    else:
        return await handle_unpublish_course(course_id, user_id, user_role)
