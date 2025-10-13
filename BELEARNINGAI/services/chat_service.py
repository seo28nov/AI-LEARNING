"""Dịch vụ chat AI."""
from datetime import datetime

from models.models import ChatResponse


async def send_chat_message(session_id: str, message: str) -> ChatResponse:
    """Giả lập gửi câu hỏi đến AI."""

    _ = message
    return ChatResponse(session_id=session_id or "session-demo", answer="Đây là câu trả lời mẫu từ AI.")


async def start_chat_session(user_id: str, course_id: str | None = None) -> str:
    """Giả lập khởi tạo phiên chat."""

    _ = (user_id, course_id)
    return f"session-{datetime.utcnow().timestamp()}"
