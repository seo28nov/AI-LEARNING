"""Dịch vụ quản lý quiz."""
from typing import List

from models.models import QuizDocument, QuizQuestion, QuizResponse
from schemas.quiz import QuizGenerationResponse, QuizQuestionTemplate
from services.ai_service import GenAIService


async def generate_quiz(course_id: str) -> QuizResponse:
    """Giả lập tạo quiz từ khóa học."""

    quiz = QuizResponse(
        _id="quiz-demo",
        course_id=course_id,
        title="Quiz kiểm tra kiến thức",
        questions=[
            QuizQuestion(question="Công thức chu kỳ con lắc lò xo?", options=["T=2π√(m/k)", "T=2π√(l/g)"])
        ],
    )
    return quiz


async def list_quizzes(course_id: str) -> List[QuizResponse]:
    """Giả lập danh sách quiz."""

    return [await generate_quiz(course_id)]


async def save_quiz(quiz: QuizDocument) -> QuizDocument:
    """Placeholder lưu quiz."""

    return quiz


async def generate_quiz_template(topic: str, num_questions: int = 5) -> QuizGenerationResponse:
    """Gọi GenAIService (mock) để sinh template câu hỏi."""

    ai_client = GenAIService()
    raw_questions = await ai_client.generate_quiz_outline(topic=topic, num_questions=num_questions)
    templates = [QuizQuestionTemplate(**item) for item in raw_questions]
    return QuizGenerationResponse(course_id="", topic=topic, questions=templates)
