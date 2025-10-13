"""Router cho quản lý lớp học."""
from typing import List

from fastapi import APIRouter, Depends

from controllers.classes_controller import (
    handle_create_class,
    handle_class_detail,
    handle_generate_invite,
    handle_list_classes,
    handle_list_roster,
    handle_remove_student,
)
from middleware.auth import get_current_user
from schemas.classes import ClassInvitation, RosterStudent
from schemas.common import MessageResponse
from schemas.enrollment import ClassCreateRequest

router = APIRouter(tags=["classes"])


@router.get("/", response_model=list[dict], summary="Danh sách lớp của giảng viên")
async def list_classes_route(current_user: dict = Depends(get_current_user)) -> list[dict]:
    return await handle_list_classes(current_user)


@router.post("/", response_model=dict, summary="Tạo lớp học mới")
async def create_class_route(
    payload: ClassCreateRequest, current_user: dict = Depends(get_current_user)
) -> dict:
    return await handle_create_class(payload, current_user)


@router.get("/{class_id}", response_model=MessageResponse, summary="Chi tiết lớp học")
async def class_detail_route(class_id: str) -> MessageResponse:
    return await handle_class_detail(class_id)


@router.get("/{class_id}/analytics", response_model=MessageResponse, summary="Thống kê lớp học")
async def class_analytics_route(class_id: str) -> MessageResponse:
    _ = class_id
    return MessageResponse(message="Endpoint sẽ trả về thống kê lớp khi triển khai")


@router.post(
    "/{class_id}/invite",
    response_model=ClassInvitation,
    summary="Tạo mã mời lớp học",
)
async def generate_invite_route(class_id: str) -> ClassInvitation:
    return await handle_generate_invite(class_id)


@router.get(
    "/{class_id}/roster",
    response_model=List[RosterStudent],
    summary="Danh sách học viên trong lớp",
)
async def roster_preview_route(class_id: str) -> List[RosterStudent]:
    return await handle_list_roster(class_id)


@router.delete(
    "/{class_id}/students/{student_id}",
    response_model=MessageResponse,
    summary="Xóa học viên khỏi lớp",
)
async def remove_student_route(class_id: str, student_id: str) -> MessageResponse:
    return await handle_remove_student(class_id, student_id)
