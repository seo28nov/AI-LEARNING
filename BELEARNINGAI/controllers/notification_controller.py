"""Controller thông báo."""
from typing import List

from models.models import NotificationResponse
from services.notification_service import list_notifications, mark_as_read


async def handle_list_notifications(user_id: str) -> List[NotificationResponse]:
    """Lấy danh sách thông báo."""

    return await list_notifications(user_id)


async def handle_mark_as_read(notification_id: str) -> NotificationResponse:
    """Đánh dấu thông báo đã đọc."""

    return await mark_as_read(notification_id)
