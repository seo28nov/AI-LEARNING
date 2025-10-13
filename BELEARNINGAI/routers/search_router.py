"""Router cho tìm kiếm và khám phá."""
from typing import Optional

from fastapi import APIRouter

from controllers.search_controller import (
    handle_search,
    handle_search_content,
    handle_search_courses,
    handle_search_instructors,
)
from schemas.common import MessageResponse
from schemas.search import SearchQuery, SearchResponse

router = APIRouter(tags=["search"])


@router.post("/courses", response_model=SearchResponse, summary="Tìm kiếm khóa học")
async def search_courses_route(payload: SearchQuery) -> SearchResponse:
    return await handle_search(payload)


@router.get("/courses", response_model=MessageResponse, summary="Tìm kiếm khóa học (nhanh)")
async def search_courses_quick_route(keyword: Optional[str] = None) -> MessageResponse:
    return await handle_search_courses(keyword)


@router.get("/instructors", response_model=MessageResponse, summary="Tìm kiếm giảng viên")
async def search_instructors_route(keyword: Optional[str] = None) -> MessageResponse:
    return await handle_search_instructors(keyword)


@router.get("/content", response_model=MessageResponse, summary="Tìm kiếm trong nội dung khóa học")
async def search_content_route(keyword: Optional[str] = None) -> MessageResponse:
    return await handle_search_content(keyword)


@router.get("/global", response_model=MessageResponse, summary="Tìm kiếm toàn hệ thống")
async def search_global_route() -> MessageResponse:
    return MessageResponse(message="Endpoint sẽ trả kết quả tổng hợp khi triển khai")
