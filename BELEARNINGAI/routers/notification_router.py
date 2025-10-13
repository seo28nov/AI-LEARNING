"""Router thông báo."""
from typing import List

from fastapi import APIRouter, Depends, Header

from controllers.notification_controller import handle_list_notifications, handle_mark_as_read
from models.models import NotificationResponse

router = APIRouter(tags=["notifications"])


def get_current_user(user_id: str | None = Header(default="demo-user")) -> str:
    """Giả lập user hiện tại."""

    return user_id or "demo-user"


@router.get("/", response_model=List[NotificationResponse], summary="Danh sách thông báo")
async def list_notifications_route(current_user: str = Depends(get_current_user)) -> List[NotificationResponse]:
    """Lấy thông báo của user."""

    return await handle_list_notifications(current_user)


@router.patch("/{notification_id}/read", response_model=NotificationResponse, summary="Đánh dấu đã đọc")
async def mark_read_route(notification_id: str) -> NotificationResponse:
    """Đánh dấu thông báo đã đọc."""

    return await handle_mark_as_read(notification_id)
