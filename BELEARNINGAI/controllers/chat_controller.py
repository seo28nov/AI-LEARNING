"""Controller chat AI."""
from typing import Optional

from fastapi import HTTPException, status

from services.chat_service import (
    start_chat_session,
    send_message,
    get_chat_history,
    delete_chat_session,
    get_user_chat_sessions
)


async def handle_start_session(user_id: str, course_id: Optional[str] = None) -> dict:
    """Khởi tạo phiên chat mới."""
    
    return await start_chat_session(user_id, course_id)


async def handle_send_message(session_id: str, payload: dict, user_id: str) -> dict:
    """Gửi tin nhắn trong phiên chat."""
    
    message = payload.get("message")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    return await send_message(
        session_id=session_id,
        user_id=user_id,
        message=message
    )


async def handle_get_chat_history(session_id: str, user_id: str) -> dict:
    """Lấy lịch sử chat của phiên."""
    
    return await get_chat_history(session_id, user_id)


async def handle_list_sessions(user_id: str, skip: int = 0, limit: int = 20) -> dict:
    """Danh sách phiên chat của user."""
    
    sessions, total = await get_user_chat_sessions(
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "sessions": sessions,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_delete_session(session_id: str, user_id: str) -> dict:
    """Xóa phiên chat."""
    
    await delete_chat_session(session_id, user_id)
    return {"message": "Phiên chat đã được xóa"}


async def handle_course_chat(course_id: str, payload: dict, user_id: str) -> dict:
    """Chat với context của khóa học cụ thể."""
    
    message = payload.get("message")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    # Start or get session for this course
    session = await start_chat_session(user_id, course_id)
    session_id = session.get("session_id")
    
    # Send message with course context
    return await send_message(
        session_id=session_id,
        user_id=user_id,
        message=message
    )


# Aliases for router compatibility
async def handle_chat_history(session_id: str, current_user: dict) -> dict:
    """Alias for handle_get_chat_history."""
    return await handle_get_chat_history(session_id, current_user["id"])


async def handle_freestyle_chat(payload: dict, current_user: dict) -> dict:
    """Chat tự do không gắn với khóa học cụ thể."""
    user_id = current_user["id"]
    
    message = payload.get("message")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    # Start or get session without course context
    session = await start_chat_session(user_id, course_id=None)
    session_id = session.get("session_id")
    
    # Send message
    return await send_message(
        session_id=session_id,
        user_id=user_id,
        message=message
    )


async def handle_assessment_chat(assessment_id: str, payload: dict, current_user: dict) -> dict:
    """Chat với context của bài đánh giá."""
    user_id = current_user["id"]
    
    message = payload.get("message")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    # Start session with assessment context
    session = await start_chat_session(user_id, course_id=None)
    session_id = session.get("session_id")
    
    # Send message with assessment context
    return await send_message(
        session_id=session_id,
        user_id=user_id,
        message=f"[Assessment {assessment_id}] {message}"
    )
