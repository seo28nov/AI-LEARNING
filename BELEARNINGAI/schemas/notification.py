"""Schemas cho module thông báo."""
from datetime import datetime
from typing import List

from pydantic import BaseModel


class NotificationCreateRequest(BaseModel):
    title: str
    message: str
    target_user_ids: List[str]


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
