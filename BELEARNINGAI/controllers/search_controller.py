"""Controller cho tìm kiếm."""
from typing import Optional

from schemas.search import SearchQuery, SearchResponse
from services.search_service import global_search


async def handle_search(payload: SearchQuery) -> SearchResponse:
    return await global_search(payload)


async def handle_search_courses(
    keyword: Optional[str],
    category: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Tìm kiếm khóa học."""
    from services.course_service import get_public_courses
    
    if not keyword:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword is required"
        )
    
    courses, total = await get_public_courses(
        skip=skip,
        limit=limit,
        category=category,
        level=level,
        search=keyword
    )
    
    return {
        "courses": courses,
        "total": total,
        "keyword": keyword,
        "skip": skip,
        "limit": limit
    }


async def handle_search_instructors(
    keyword: Optional[str],
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Tìm kiếm giảng viên."""
    from services.user_service import search_users_by_role
    
    if not keyword:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword is required"
        )
    
    instructors, total = await search_users_by_role(
        role="instructor",
        search=keyword,
        skip=skip,
        limit=limit
    )
    
    return {
        "instructors": instructors,
        "total": total,
        "keyword": keyword,
        "skip": skip,
        "limit": limit
    }


async def handle_search_content(
    keyword: Optional[str],
    course_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Tìm kiếm nội dung khóa học (sẽ sử dụng vector search sau)."""
    
    if not keyword:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword is required"
        )
    
    # TODO: Implement vector search khi RAG ready
    # from services.search_service import search_course_content
    # results = await search_course_content(keyword, course_id)
    
    return {
        "results": [],
        "total": 0,
        "keyword": keyword,
        "message": "Vector search sẽ được implement trong Phase 4"
    }
