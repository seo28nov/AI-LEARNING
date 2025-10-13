"""Schemas cho module gợi ý thông minh."""
from typing import List

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    user_id: str
    recommended_courses: List[str]
    learning_path: List[str]
