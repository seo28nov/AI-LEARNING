"""Router cho các tính năng AI ngoài chat cơ bản."""
from fastapi import APIRouter

from controllers.ai_controller import (
    handle_ai_chat,
    handle_ai_course_generation,
    handle_ai_course_recommendations,
    handle_ai_learning_path,
    handle_ai_quiz_generation,
)
from schemas.ai import AIChatRequest, AIChatResponse, AIContentRequest, AIContentResponse
from schemas.common import MessageResponse

router = APIRouter(tags=["ai"])


@router.post("/content-generation", response_model=AIContentResponse, summary="Sinh nội dung khóa học bằng AI")
async def ai_content_generation_route(payload: AIContentRequest) -> AIContentResponse:
    return await handle_ai_course_generation(payload)


@router.post("/chat", response_model=AIChatResponse, summary="Chat AI nâng cao")
async def ai_chat_route(payload: AIChatRequest) -> AIChatResponse:
    return await handle_ai_chat(payload)


@router.post("/quiz-generation", response_model=MessageResponse, summary="AI sinh quiz")
async def ai_quiz_generation_route(payload: dict) -> MessageResponse:
    return await handle_ai_quiz_generation(payload)


@router.post("/course-recommendations", response_model=MessageResponse, summary="AI gợi ý khóa học")
async def ai_course_recommendations_route(payload: dict) -> MessageResponse:
    return await handle_ai_course_recommendations(payload)


@router.post("/learning-path", response_model=MessageResponse, summary="AI tạo lộ trình học")
async def ai_learning_path_route(payload: dict) -> MessageResponse:
    return await handle_ai_learning_path(payload)
