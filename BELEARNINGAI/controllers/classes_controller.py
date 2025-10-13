"""Controller cho module lớp học."""
from typing import List

from schemas.classes import ClassInvitation, RosterStudent
from schemas.common import MessageResponse
from schemas.enrollment import ClassCreateRequest
from services.classes_service import create_class, generate_join_code, list_classes, list_roster_preview


async def handle_list_classes(current_user: dict) -> list[dict]:
    user_id = current_user.get("sub", "demo-user")
    return await list_classes(instructor_id=user_id)


async def handle_create_class(payload: ClassCreateRequest, current_user: dict) -> dict:
    user_id = current_user.get("sub", "demo-user")
    return await create_class(payload, instructor_id=user_id)


async def handle_generate_invite(class_id: str) -> ClassInvitation:
    return await generate_join_code(class_id)


async def handle_list_roster(class_id: str) -> List[RosterStudent]:
    return await list_roster_preview(class_id)


async def handle_class_detail(class_id: str) -> MessageResponse:
    """Placeholder chi tiết lớp học."""

    return MessageResponse(message=f"Placeholder: chi tiết lớp {class_id}")


async def handle_remove_student(class_id: str, student_id: str) -> MessageResponse:
    """Placeholder xóa học viên khỏi lớp."""

    _ = class_id, student_id
    return MessageResponse(message="Placeholder: học viên đã được xóa khỏi lớp")
