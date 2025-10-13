"""Service placeholder cho các tính năng AI."""
from typing import List

from schemas.ai import AIChatRequest, AIChatResponse, AIContentRequest, AIContentResponse


class GenAIService:
    """Mock service mô phỏng gọi Google GenAI theo HE_THONG.md."""

    async def generate_quiz_outline(self, topic: str, num_questions: int) -> List[dict]:
        """Trả về danh sách câu hỏi demo dựa trên topic."""

        return [
            {
                "prompt": f"Giải thích khái niệm {topic} (câu {index + 1})",
                "answer_type": "multiple_choice",
                "suggested_options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
                "explanation_hint": "Trích từ giáo trình chương 1",
            }
            for index in range(num_questions)
        ]


async def generate_course_from_prompt(payload: AIContentRequest) -> AIContentResponse:
    """Giả lập sinh outline khóa học bằng AI."""

    outline = [f"Chương 1: Giới thiệu về {payload.topic}", "Chương 2: Thực hành"]
    chapters = [{"title": item, "lessons": []} for item in outline]
    return AIContentResponse(outline=outline, chapters=chapters)


async def chat_with_ai(request: AIChatRequest) -> AIChatResponse:
    """Giả lập trả lời chat."""

    answer = f"AI trả lời cho câu hỏi: {request.message}"
    session_id = request.session_id or "demo-session"
    return AIChatResponse(session_id=session_id, answer=answer, sources=[])
