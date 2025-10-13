"""Controller chat AI."""
from models.models import ChatResponse
from schemas.common import MessageResponse
from services.chat_service import send_chat_message, start_chat_session


async def handle_start_session(user_id: str, course_id: str | None = None) -> str:
    """Khởi tạo phiên chat."""

    return await start_chat_session(user_id, course_id)


async def handle_send_message(session_id: str, message: str) -> ChatResponse:
    """Gửi câu hỏi tới AI."""

    return await send_chat_message(session_id, message)


async def handle_list_sessions(user_id: str) -> MessageResponse:
    """Placeholder danh sách phiên chat."""

    return MessageResponse(message=f"Placeholder: danh sách phiên chat của {user_id}")


async def handle_delete_session(session_id: str) -> MessageResponse:
    """Placeholder xóa phiên chat."""

    return MessageResponse(message=f"Placeholder: đã xóa phiên chat {session_id}")


async def handle_freestyle_chat(payload: dict) -> MessageResponse:
    """Placeholder chat tự do với AI."""

    prompt = payload.get("message", "")
    return MessageResponse(message=f"Placeholder: trả lời cho '{prompt}'")


async def handle_course_chat(course_id: str, payload: dict) -> MessageResponse:
    """Placeholder chat theo khóa học."""

    _ = payload
    return MessageResponse(message=f"Placeholder: phản hồi AI cho khóa {course_id}")


async def handle_assessment_chat(payload: dict) -> MessageResponse:
    """Placeholder chat hỗ trợ làm bài test."""

    question = payload.get("question", "")
    return MessageResponse(message=f"Placeholder: gợi ý cho câu hỏi '{question}'")


async def handle_chat_history(user_id: str) -> MessageResponse:
    """Placeholder lịch sử chat."""

    return MessageResponse(message=f"Placeholder: lịch sử chat của {user_id}")
