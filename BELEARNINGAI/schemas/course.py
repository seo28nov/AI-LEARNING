"""Schemas cho module khóa học."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CourseChapter(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    order: int = Field(ge=1, default=1)
    duration_minutes: Optional[int] = None
    materials: List[dict] = Field(default_factory=list)


class CourseBase(BaseModel):
    title: str
    description: str
    category: str
    level: str
    language: str = "vi"
    visibility: str = "draft"
    source: str = "manual"
    tags: List[str] = Field(default_factory=list)


class CourseCreateRequest(CourseBase):
    content: List[CourseChapter] = Field(default_factory=list)


class CourseResponse(CourseBase):
    id: str
    owner_id: str
    stats: dict = Field(default_factory=dict)
    content: List[CourseChapter] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
