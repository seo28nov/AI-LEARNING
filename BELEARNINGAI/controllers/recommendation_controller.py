"""Controller cho gợi ý học tập."""
from schemas.common import MessageResponse
from schemas.recommendation import RecommendationResponse
from services.recommendation_service import recommend_for_user


async def handle_recommendation(current_user: dict) -> RecommendationResponse:
    user_id = current_user.get("sub", "demo-user")
    return await recommend_for_user(user_id)


async def handle_learning_path(current_user: dict) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: lộ trình học được đề xuất cho {user_id}")


async def handle_instructor_suggestion(current_user: dict) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: gợi ý giảng viên phù hợp cho {user_id}")
