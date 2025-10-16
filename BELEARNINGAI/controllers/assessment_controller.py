"""Controller cho module đánh giá năng lực."""
from typing import Optional

from fastapi import HTTPException, status

from services.assessment_service import (
    create_assessment,
    submit_assessment,
    get_assessment_by_id,
    list_user_assessments,
    generate_questions
)


async def handle_start_assessment(payload: dict, user_id: str) -> dict:
    """Bắt đầu bài đánh giá năng lực."""
    
    category = payload.get("category")
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is required"
        )
    
    return await create_assessment(
        user_id=user_id,
        category=category,
        assessment_type=payload.get("assessment_type", "skill_assessment")
    )


async def handle_submit_assessment(assessment_id: str, payload: dict, user_id: str) -> dict:
    """Nộp bài đánh giá."""
    
    answers = payload.get("answers")
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers are required"
        )
    
    return await submit_assessment(
        assessment_id=assessment_id,
        user_id=user_id,
        answers=answers
    )


async def handle_get_assessment(assessment_id: str, user_id: str) -> dict:
    """Lấy chi tiết bài đánh giá."""
    
    return await get_assessment_by_id(assessment_id, user_id)


async def handle_get_assessment_result(assessment_id: str, user_id: str) -> dict:
    """Lấy kết quả bài đánh giá."""
    
    return await get_assessment_by_id(assessment_id, user_id)


async def handle_assessment_history(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None
) -> dict:
    """Lịch sử đánh giá của user."""
    
    assessments, total = await list_user_assessments(
        user_id=user_id,
        skip=skip,
        limit=limit,
        category=category
    )
    
    return {
        "assessments": assessments,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_generate_questions(payload: dict) -> dict:
    """Generate câu hỏi đánh giá bằng AI."""
    
    category = payload.get("category")
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is required"
        )
    
    return await generate_questions(
        category=category,
        difficulty=payload.get("difficulty", "medium"),
        num_questions=payload.get("num_questions", 10)
    )


async def handle_assessment_categories() -> dict:
    """Danh sách categories cho đánh giá."""
    
    categories = [
        {"id": "programming", "name": "Lập trình"},
        {"id": "web_development", "name": "Web Development"},
        {"id": "data_science", "name": "Khoa học dữ liệu"},
        {"id": "design", "name": "Thiết kế"},
        {"id": "business", "name": "Kinh doanh"}
    ]
    
    return {"categories": categories}


async def handle_assessment_recommendations(assessment_id: str, current_user: dict) -> dict:
    """Lấy gợi ý khóa học dựa trên kết quả đánh giá."""
    user_id = current_user["id"]
    
    # Get assessment result first
    assessment = await get_assessment_by_id(assessment_id, user_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Return basic recommendations for now
    return {
        "assessment_id": assessment_id,
        "recommendations": [
            {
                "course_id": "sample-course-1",
                "title": "Khóa học cơ bản",
                "reason": "Phù hợp với kết quả đánh giá của bạn",
                "match_percentage": 85
            }
        ],
        "learning_path": [],
        "generated_at": "2025-10-16T00:00:00Z"
    }


# Alias functions for router compatibility
async def handle_assessment_result(assessment_id: str, current_user: dict) -> dict:
    """Alias for handle_get_assessment_result."""
    return await handle_get_assessment_result(assessment_id, current_user["id"])


async def handle_get_assessment_detail(assessment_id: str, current_user: dict) -> dict:
    """Alias for handle_get_assessment."""
    return await handle_get_assessment(assessment_id, current_user["id"])


async def handle_skill_test(payload: dict, current_user: dict) -> dict:
    """Alias for handle_start_assessment - skill test."""
    return await handle_start_assessment(payload, current_user["id"])
