"""Schemas cho module quản trị."""
from datetime import datetime
from typing import List

from pydantic import BaseModel


class AdminUserUpdate(BaseModel):
    role: str
    status: str


class AdminBroadcastRequest(BaseModel):
    title: str
    message: str
    audience_roles: List[str]


class AdminSystemStats(BaseModel):
    users: int
    courses: int
    active_sessions: int
    generated_at: datetime


class SystemSummary(BaseModel):
    """Tổng hợp số liệu phục vụ dashboard admin."""

    uptime_percent: float
    total_users: int
    total_courses: int
    active_today: int
    alerts: List[str]
    generated_at: datetime


class UserAuditLog(BaseModel):
    """Bản ghi audit cho thao tác quản trị."""

    action_id: str
    actor_id: str
    action: str
    target: str
    created_at: datetime
