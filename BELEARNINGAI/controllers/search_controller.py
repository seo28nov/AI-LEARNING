"""Controller cho tìm kiếm."""
from typing import Optional

from schemas.common import MessageResponse
from schemas.search import SearchQuery, SearchResponse
from services.search_service import global_search


async def handle_search(payload: SearchQuery) -> SearchResponse:
    return await global_search(payload)


async def handle_search_courses(keyword: Optional[str]) -> MessageResponse:
    if keyword:
        return MessageResponse(message=f"Placeholder: kết quả tìm kiếm khóa học cho '{keyword}'")
    return MessageResponse(message="Placeholder: vui lòng cung cấp từ khóa khóa học")


async def handle_search_instructors(keyword: Optional[str]) -> MessageResponse:
    if keyword:
        return MessageResponse(message=f"Placeholder: kết quả giảng viên cho '{keyword}'")
    return MessageResponse(message="Placeholder: vui lòng cung cấp từ khóa giảng viên")


async def handle_search_content(keyword: Optional[str]) -> MessageResponse:
    if keyword:
        return MessageResponse(message=f"Placeholder: kết quả nội dung cho '{keyword}'")
    return MessageResponse(message="Placeholder: vui lòng cung cấp từ khóa nội dung")
