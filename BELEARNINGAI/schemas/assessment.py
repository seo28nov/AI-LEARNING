"""Schemas cho module đánh giá năng lực."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AssessmentQuestion(BaseModel):
    question_id: Optional[str] = None
    question_text: str
    question_type: str
    options: List[str] = []
    correct_answer: Optional[int] = None
    difficulty: Optional[str] = None
    time_spent_seconds: Optional[int] = None


class AssessmentStartRequest(BaseModel):
    category: str
    assessment_type: str = "skill_assessment"


class AssessmentSubmitRequest(BaseModel):
    answers: List[int]


class AssessmentSummary(BaseModel):
    id: str
    user_id: str
    category: str
    assessment_type: str
    score: float
    level: str
    strengths: List[str]
    weaknesses: List[str]
    created_at: datetime


class AssessmentTopicInsight(BaseModel):
    """Tổng hợp kết quả theo từng chủ đề để team phân tích sâu hơn."""

    topic: str
    correct: int
    total: int
    mastery_level: str


class RecommendationItem(BaseModel):
    """Mô tả một khóa học gợi ý theo mục 5.1.1 HE_THONG.md."""

    course_id: str
    title: str
    reason: str


class AssessmentResultResponse(BaseModel):
    """Kết quả tổng hợp cho endpoint skill-test."""

    score: float
    level: str
    strengths: List[str]
    weaknesses: List[str]
    topics: List[AssessmentTopicInsight]
    recommended_courses: List[RecommendationItem]
    learning_path: List[str]
    generated_at: datetime
