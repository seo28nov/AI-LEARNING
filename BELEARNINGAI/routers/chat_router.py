"""Router chat AI."""
from fastapi import APIRouter, Depends

from controllers.chat_controller import (
    handle_assessment_chat,
    handle_chat_history,
    handle_course_chat,
    handle_delete_session,
    handle_freestyle_chat,
    handle_list_sessions,
    handle_send_message,
    handle_start_session,
)
from middleware.auth import get_current_user
from models.models import ChatResponse
from schemas.common import MessageResponse

router = APIRouter(tags=["chat"])


@router.get("/sessions", response_model=MessageResponse, summary="Danh sách phiên chat")
async def list_sessions_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return await handle_list_sessions(user_id)


@router.post("/sessions", summary="Khởi tạo phiên chat")
async def start_session_route(
    user_id: str, course_id: str | None = None
) -> dict[str, str]:
    """Khởi tạo phiên chat mới."""

    session_id = await handle_start_session(user_id, course_id)
    return {"session_id": session_id}


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse, summary="Gửi câu hỏi tới AI")
async def send_message_route(session_id: str, message: str) -> ChatResponse:
    """Gửi tin nhắn trong phiên chat."""

    return await handle_send_message(session_id, message)


@router.delete(
    "/sessions/{session_id}",
    response_model=MessageResponse,
    summary="Xóa phiên chat",
)
async def delete_session_route(session_id: str) -> MessageResponse:
    return await handle_delete_session(session_id)


@router.post("/freestyle", response_model=MessageResponse, summary="Chat tự do với AI")
async def freestyle_chat_route(payload: dict) -> MessageResponse:
    return await handle_freestyle_chat(payload)


@router.post(
    "/course/{course_id}",
    response_model=MessageResponse,
    summary="Chat về khóa học",
)
async def course_chat_route(course_id: str, payload: dict) -> MessageResponse:
    return await handle_course_chat(course_id, payload)


@router.post("/assessment", response_model=MessageResponse, summary="Chat hỗ trợ bài đánh giá")
async def assessment_chat_route(payload: dict) -> MessageResponse:
    return await handle_assessment_chat(payload)


@router.get("/history", response_model=MessageResponse, summary="Lịch sử chat")
async def chat_history_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return await handle_chat_history(user_id)
