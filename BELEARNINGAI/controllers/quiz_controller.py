"""Controller quiz."""
from typing import List

from models.models import QuizDocument, QuizResponse
from schemas.common import MessageResponse
from schemas.quiz import QuizGenerationResponse
from services.quiz_service import generate_quiz, generate_quiz_template, list_quizzes, save_quiz


async def handle_generate_quiz(course_id: str) -> QuizResponse:
    """Tạo quiz cho khóa học."""

    return await generate_quiz(course_id)


async def handle_list_quizzes(course_id: str) -> List[QuizResponse]:
    """Lấy danh sách quiz."""

    return await list_quizzes(course_id)


async def handle_save_quiz(document: QuizDocument) -> QuizDocument:
    """Lưu quiz."""

    return await save_quiz(document)


async def handle_ai_quiz_builder(topic: str, num_questions: int) -> QuizGenerationResponse:
    """Sinh template câu hỏi bằng AI mock."""

    return await generate_quiz_template(topic=topic, num_questions=num_questions)


async def handle_list_all_quizzes() -> MessageResponse:
    """Placeholder danh sách quiz của người dùng."""

    return MessageResponse(message="Placeholder: danh sách quiz của người dùng")


async def handle_create_quiz(payload: dict) -> MessageResponse:
    """Placeholder tạo quiz thủ công."""

    title = payload.get("title", "Quiz mới")
    return MessageResponse(message=f"Placeholder: đã tạo quiz '{title}'")


async def handle_quiz_detail(quiz_id: str) -> MessageResponse:
    """Placeholder chi tiết quiz."""

    return MessageResponse(message=f"Placeholder: chi tiết quiz {quiz_id}")


async def handle_update_quiz_detail(quiz_id: str, payload: dict) -> MessageResponse:
    """Placeholder cập nhật quiz."""

    title = payload.get("title", "Quiz")
    return MessageResponse(message=f"Placeholder: quiz {quiz_id} cập nhật thành '{title}'")


async def handle_delete_quiz(quiz_id: str) -> MessageResponse:
    """Placeholder xóa quiz."""

    return MessageResponse(message=f"Placeholder: đã xóa quiz {quiz_id}")


async def handle_quiz_from_content(payload: dict) -> MessageResponse:
    """Placeholder tạo quiz từ nội dung."""

    topic = payload.get("topic", "Nội dung")
    return MessageResponse(message=f"Placeholder: tạo quiz từ nội dung {topic}")


async def handle_adaptive_quiz(payload: dict) -> MessageResponse:
    """Placeholder tạo quiz thích ứng."""

    difficulty = payload.get("difficulty", "medium")
    return MessageResponse(message=f"Placeholder: tạo quiz thích ứng mức {difficulty}")


async def handle_start_quiz(quiz_id: str) -> MessageResponse:
    """Placeholder bắt đầu quiz."""

    return MessageResponse(message=f"Placeholder: bắt đầu làm quiz {quiz_id}")


async def handle_submit_quiz(quiz_id: str, payload: dict) -> MessageResponse:
    """Placeholder nộp quiz."""

    _ = payload
    return MessageResponse(message=f"Placeholder: đã nộp quiz {quiz_id}")


async def handle_quiz_result_detail(quiz_id: str) -> MessageResponse:
    """Placeholder kết quả quiz."""

    return MessageResponse(message=f"Placeholder: kết quả quiz {quiz_id}")


async def handle_quiz_history(current_user: dict) -> MessageResponse:
    """Placeholder lịch sử quiz."""

    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: lịch sử quiz của {user_id}")
