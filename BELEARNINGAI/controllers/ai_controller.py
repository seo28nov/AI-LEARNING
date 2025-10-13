"""Controller cho các endpoint AI."""
from schemas.ai import AIChatRequest, AIChatResponse, AIContentRequest, AIContentResponse
from schemas.common import MessageResponse
from services.ai_service import chat_with_ai, generate_course_from_prompt


async def handle_ai_course_generation(payload: AIContentRequest) -> AIContentResponse:
    return await generate_course_from_prompt(payload)


async def handle_ai_chat(payload: AIChatRequest) -> AIChatResponse:
    return await chat_with_ai(payload)


async def handle_ai_quiz_generation(payload: dict) -> MessageResponse:
    """Placeholder sinh quiz bằng AI."""

    topic = payload.get("topic", "Chủ đề")
    return MessageResponse(message=f"Placeholder: AI đang sinh quiz cho {topic}")


async def handle_ai_course_recommendations(payload: dict) -> MessageResponse:
    """Placeholder gợi ý khóa học bằng AI."""

    user_id = payload.get("user_id", "unknown")
    return MessageResponse(message=f"Placeholder: AI gợi ý khóa học cho {user_id}")


async def handle_ai_learning_path(payload: dict) -> MessageResponse:
    """Placeholder tạo lộ trình học cá nhân hóa."""

    goal = payload.get("goal", "mục tiêu học tập")
    return MessageResponse(message=f"Placeholder: AI tạo lộ trình cho mục tiêu {goal}")
