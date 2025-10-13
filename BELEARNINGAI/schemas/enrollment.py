"""Schemas cho module enrollment & lớp học."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ClassScheduleItem(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    timezone: Optional[str] = None


class ClassCreateRequest(BaseModel):
    name: str
    course_id: str
    description: Optional[str] = None
    max_students: Optional[int] = None
    schedule: List[ClassScheduleItem] = []


class EnrollmentResponse(BaseModel):
    id: str
    course_id: str
    user_id: str
    status: str
    progress: float
    enrolled_at: datetime


class StudySession(BaseModel):
    """Thống kê một phiên học theo yêu cầu dashboard học viên."""

    session_date: datetime
    duration_minutes: int
    activities: List[str]


class ProgressSnapshot(BaseModel):
    """Ảnh chụp tiến độ dùng cho analytics."""

    course_id: str
    progress: float
    streak_days: int
    last_activity: datetime
    learning_sessions: List[StudySession]
