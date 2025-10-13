"""Schemas riêng cho module lớp học."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ClassInvitation(BaseModel):
    """Payload trả về khi tạo mã mời lớp học."""

    class_id: str
    join_code: str
    expires_at: datetime
    invite_url: str


class RosterStudent(BaseModel):
    """Thông tin học viên trong danh sách lớp."""

    student_id: str
    full_name: str
    email: str
    status: str
    last_active: Optional[datetime] = None
    progress_percent: float = 0.0
    tags: List[str] = []
