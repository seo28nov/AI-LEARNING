"""Service placeholder cho tìm kiếm."""
from schemas.search import SearchQuery, SearchResponse, SearchResultItem


async def global_search(payload: SearchQuery) -> SearchResponse:
    """Tạm trả về danh sách kết quả giả lập."""

    item = SearchResultItem(id="course-1", title="Lập trình Python", snippet="Khóa học Python cơ bản", type="course")
    return SearchResponse(items=[item])
