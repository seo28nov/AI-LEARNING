"""Router khóa học."""
from typing import List, Optional

from fastapi import APIRouter, Depends

from controllers.course_controller import (
    handle_create_chapter,
    handle_create_course,
    handle_create_course_from_prompt,
    handle_create_course_from_upload,
    handle_delete_chapter,
    handle_duplicate_course,
    handle_get_course,
    handle_list_chapters,
    handle_list_courses,
    handle_list_public_courses,
    handle_recommended_courses,
    handle_search_courses,
    handle_update_chapter,
    handle_update_visibility,
    handle_course_categories,
    handle_index_course,
    handle_reindex_course,
    handle_index_all_courses,
)
from middleware.auth import get_current_user
from models.models import CourseCreate, CourseResponse
from schemas.common import MessageResponse

router = APIRouter(tags=["courses"])


@router.get("/", response_model=List[CourseResponse], summary="Danh sách khóa học")
async def list_courses_route(current_user: dict = Depends(get_current_user)) -> List[CourseResponse]:
    """Endpoint trả danh sách khóa học."""

    _ = current_user
    return await handle_list_courses()


@router.post("/", response_model=CourseResponse, status_code=201, summary="Tạo khóa học")
async def create_course_route(payload: CourseCreate, current_user: str = Depends(get_current_user)) -> CourseResponse:
    """Endpoint tạo khóa học mới."""

    return await handle_create_course(payload, current_user)


@router.get("/{course_id}", response_model=CourseResponse, summary="Xem chi tiết khóa học")
async def get_course_route(course_id: str) -> CourseResponse:
    """Endpoint lấy chi tiết khóa học."""

    return await handle_get_course(course_id)


@router.get("/public", response_model=MessageResponse, summary="Danh sách khóa học công khai")
async def public_courses_route() -> MessageResponse:
    return await handle_list_public_courses()


@router.get("/recommended", response_model=MessageResponse, summary="Gợi ý khóa học")
async def recommended_courses_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_recommended_courses(current_user)


@router.get("/search", response_model=MessageResponse, summary="Tìm kiếm khóa học")
async def search_courses_route(keyword: Optional[str] = None) -> MessageResponse:
    return await handle_search_courses(keyword)


@router.get("/categories", response_model=MessageResponse, summary="Danh mục khóa học")
async def course_categories_route() -> MessageResponse:
    return await handle_course_categories()


@router.post("/from-prompt", response_model=MessageResponse, summary="Tạo khóa học bằng AI")
async def course_from_prompt_route(payload: dict, current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_create_course_from_prompt(payload, current_user)


@router.post("/from-upload", response_model=MessageResponse, summary="Tạo khóa học từ tài liệu")
async def course_from_upload_route(payload: dict, current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_create_course_from_upload(payload, current_user)


@router.post("/{course_id}/duplicate", response_model=MessageResponse, summary="Sao chép khóa học")
async def duplicate_course_route(
    course_id: str, current_user: dict = Depends(get_current_user)
) -> MessageResponse:
    return await handle_duplicate_course(course_id, current_user)


@router.patch("/{course_id}/visibility", response_model=MessageResponse, summary="Cập nhật trạng thái hiển thị")
async def update_visibility_route(
    course_id: str, payload: dict, current_user: dict = Depends(get_current_user)
) -> MessageResponse:
    return await handle_update_visibility(course_id, payload, current_user)


@router.get(
    "/{course_id}/chapters",
    response_model=MessageResponse,
    summary="Danh sách chương của khóa học",
)
async def list_chapters_route(course_id: str) -> MessageResponse:
    return await handle_list_chapters(course_id)


@router.post(
    "/{course_id}/chapters",
    response_model=MessageResponse,
    summary="Thêm chương mới",
)
async def create_chapter_route(course_id: str, payload: dict) -> MessageResponse:
    return await handle_create_chapter(course_id, payload)


@router.put(
    "/{course_id}/chapters/{chapter_id}",
    response_model=MessageResponse,
    summary="Cập nhật chương",
)
async def update_chapter_route(course_id: str, chapter_id: str, payload: dict) -> MessageResponse:
    return await handle_update_chapter(course_id, chapter_id, payload)


@router.delete(
    "/{course_id}/chapters/{chapter_id}",
    response_model=MessageResponse,
    summary="Xóa chương",
)
async def delete_chapter_route(course_id: str, chapter_id: str) -> MessageResponse:
    return await handle_delete_chapter(course_id, chapter_id)


# ============================================================================
# RAG INDEXING ENDPOINTS
# ============================================================================

@router.post(
    "/{course_id}/index",
    response_model=dict,
    summary="Index khóa học vào ChromaDB",
    description="Index nội dung khóa học để sử dụng cho RAG AI chat. Chỉ instructor của khóa học hoặc admin mới có quyền."
)
async def index_course_route(
    course_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Endpoint index course vào vector database."""
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")
    return await handle_index_course(course_id, user_id, user_role)


@router.post(
    "/{course_id}/reindex",
    response_model=dict,
    summary="Reindex khóa học",
    description="Xóa embeddings cũ và index lại. Dùng khi course content thay đổi."
)
async def reindex_course_route(
    course_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Endpoint reindex course."""
    user_id = current_user.get("user_id")
    user_role = current_user.get("role")
    return await handle_reindex_course(course_id, user_id, user_role)


@router.post(
    "/admin/index-all",
    response_model=dict,
    summary="Index tất cả khóa học (Admin only)",
    description="Index tất cả courses vào ChromaDB. Chỉ admin mới có quyền."
)
async def index_all_courses_route(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Endpoint index tất cả courses (admin only)."""
    user_role = current_user.get("role")
    return await handle_index_all_courses(user_role)

