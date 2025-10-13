"""Router cho gợi ý học tập."""
from fastapi import APIRouter, Depends

from controllers.recommendation_controller import (
    handle_instructor_suggestion,
    handle_learning_path,
    handle_recommendation,
)
from middleware.auth import get_current_user
from schemas.common import MessageResponse
from schemas.recommendation import RecommendationResponse

router = APIRouter(tags=["recommendations"])


@router.get(
    "/courses",
    response_model=RecommendationResponse,
    summary="Gợi ý khóa học theo AI",
)
async def recommend_courses_route(current_user: dict = Depends(get_current_user)) -> RecommendationResponse:
    return await handle_recommendation(current_user)


@router.get(
    "/learning-path",
    response_model=MessageResponse,
    summary="Gợi ý lộ trình học",
)
async def recommend_learning_path_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_learning_path(current_user)


@router.get(
    "/instructors",
    response_model=MessageResponse,
    summary="Gợi ý giảng viên",
)
async def recommend_instructors_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_instructor_suggestion(current_user)
