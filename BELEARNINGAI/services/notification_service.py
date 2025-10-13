"""Dịch vụ thông báo hệ thống."""
from datetime import datetime
from typing import List

from models.models import NotificationResponse


async def list_notifications(user_id: str) -> List[NotificationResponse]:
    """Giả lập danh sách thông báo."""

    return [
        NotificationResponse.model_validate(
            {
                "_id": "notify-demo",
                "title": "Chào mừng",
                "message": "Bạn đã đăng ký thành công",
                "is_read": False,
                "created_at": datetime.utcnow(),
            }
        )
    ]


async def mark_as_read(notification_id: str) -> NotificationResponse:
    """Giả lập đánh dấu đã đọc."""

    return NotificationResponse.model_validate(
        {
            "_id": notification_id,
            "title": "Thông báo",
            "message": "Đã đọc",
            "is_read": True,
            "created_at": datetime.utcnow(),
        }
    )
