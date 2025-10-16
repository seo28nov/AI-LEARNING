"""Controller cho gợi ý học tập."""
from services.recommendation_service import recommend_for_user


async def handle_recommendation(user_id: str) -> dict:
    """Gợi ý khóa học cho user."""
    return await recommend_for_user(user_id)


async def handle_learning_path(user_id: str, payload: dict = None) -> dict:
    """Tạo lộ trình học tập cá nhân hóa."""
    from services.recommendation_service import build_learning_path
    
    # Lấy thông tin từ assessment results nếu có
    strengths = payload.get("strengths", []) if payload else []
    weaknesses = payload.get("weaknesses", []) if payload else []
    goals = payload.get("goals", []) if payload else []
    
    learning_path = await build_learning_path(
        user_id=user_id,
        strengths=strengths,
        weaknesses=weaknesses,
        goals=goals
    )
    
    return {
        "user_id": user_id,
        "learning_path": learning_path,
        "total_steps": len(learning_path)
    }


async def handle_instructor_suggestion(user_id: str, category: str = None) -> dict:
    """Gợi ý giảng viên phù hợp."""
    from services.user_service import get_top_instructors
    
    instructors = await get_top_instructors(
        category=category,
        limit=5
    )
    
    return {
        "instructors": instructors,
        "category": category,
        "total": len(instructors)
    }


async def handle_similar_courses(course_id: str, limit: int = 5) -> dict:
    """Gợi ý khóa học tương tự."""
    from services.recommendation_service import get_similar_courses
    
    similar = await get_similar_courses(course_id, limit)
    
    return {
        "course_id": course_id,
        "similar_courses": similar,
        "total": len(similar)
    }
