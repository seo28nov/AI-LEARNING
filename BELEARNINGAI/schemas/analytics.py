"""Schemas cho module analytics."""
from datetime import datetime
from typing import List

from pydantic import BaseModel


class MetricPoint(BaseModel):
    label: str
    value: float
    trend: float | None = None


class DashboardSection(BaseModel):
    title: str
    metrics: List[MetricPoint]


class StudentDashboardResponse(BaseModel):
    generated_at: datetime
    sections: List[DashboardSection]
