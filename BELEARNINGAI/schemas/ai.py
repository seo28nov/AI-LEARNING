"""Schemas cho các endpoint AI."""
from typing import List, Optional

from pydantic import BaseModel, Field


class AIContentRequest(BaseModel):
    topic: str
    level: Optional[str] = None
    language: str = "vi"
    goals: List[str] = Field(default_factory=list)


class AIContentResponse(BaseModel):
    outline: List[str]
    chapters: List[dict]


class AIChatRequest(BaseModel):
    message: str
    course_id: Optional[str] = None
    mode: str = "hybrid"
    session_id: Optional[str] = None


class AIChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[str] = Field(default_factory=list)
