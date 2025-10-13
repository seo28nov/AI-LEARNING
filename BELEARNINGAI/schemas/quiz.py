"""Schemas cho module quiz."""
from typing import List, Optional

from pydantic import BaseModel


class QuizQuestionPayload(BaseModel):
    question_text: str
    question_type: str
    options: List[str] = []
    correct_answer: Optional[int] = None


class QuizCreateRequest(BaseModel):
    course_id: str
    title: str
    questions: List[QuizQuestionPayload]


class QuizResultResponse(BaseModel):
    quiz_id: str
    score: float
    percentage: float
    attempts: int


class QuizQuestionTemplate(BaseModel):
    """Cấu trúc câu hỏi gợi ý từ AI."""

    prompt: str
    answer_type: str
    suggested_options: List[str] = []
    explanation_hint: Optional[str] = None


class QuizGenerationResponse(BaseModel):
    """Phản hồi khi gọi AI builder cho quiz."""

    course_id: str
    topic: str
    questions: List[QuizQuestionTemplate]
    source: str = "ai_suggestion"
