"""Router quiz."""
from typing import List

from fastapi import APIRouter, Depends

from controllers.quiz_controller import (
    handle_adaptive_quiz,
    handle_ai_quiz_builder,
    handle_create_quiz,
    handle_delete_quiz,
    handle_generate_quiz,
    handle_list_all_quizzes,
    handle_list_quizzes,
    handle_quiz_detail,
    handle_quiz_from_content,
    handle_quiz_history,
    handle_quiz_result_detail,
    handle_start_quiz,
    handle_submit_quiz,
    handle_update_quiz_detail,
)
from middleware.auth import get_current_user
from models.models import QuizResponse
from schemas.common import MessageResponse
from schemas.quiz import QuizGenerationResponse

router = APIRouter(tags=["quiz"])


@router.get("/", response_model=MessageResponse, summary="Danh sách quiz của người dùng")
async def list_user_quizzes_route() -> MessageResponse:
    return await handle_list_all_quizzes()


@router.post("/", response_model=MessageResponse, summary="Tạo quiz thủ công")
async def create_quiz_route(payload: dict) -> MessageResponse:
    return await handle_create_quiz(payload)


@router.get("/{quiz_id}", response_model=MessageResponse, summary="Chi tiết quiz")
async def quiz_detail_route(quiz_id: str) -> MessageResponse:
    return await handle_quiz_detail(quiz_id)


@router.put("/{quiz_id}", response_model=MessageResponse, summary="Cập nhật quiz")
async def update_quiz_route(quiz_id: str, payload: dict) -> MessageResponse:
    return await handle_update_quiz_detail(quiz_id, payload)


@router.delete("/{quiz_id}", response_model=MessageResponse, summary="Xóa quiz")
async def delete_quiz_route(quiz_id: str) -> MessageResponse:
    return await handle_delete_quiz(quiz_id)


@router.get("/course/{course_id}", response_model=List[QuizResponse], summary="Danh sách quiz của khóa học")
async def list_quizzes_route(course_id: str) -> List[QuizResponse]:
    """Lấy danh sách quiz theo khóa."""

    return await handle_list_quizzes(course_id)


@router.post("/course/{course_id}/generate", response_model=QuizResponse, summary="Tạo quiz bằng AI")
async def generate_quiz_route(course_id: str) -> QuizResponse:
    """Tạo quiz mới."""

    return await handle_generate_quiz(course_id)


@router.post("/from-course/{course_id}", response_model=QuizResponse, summary="Tạo quiz từ khóa học")
async def quiz_from_course_route(course_id: str) -> QuizResponse:
    return await handle_generate_quiz(course_id)


@router.post("/from-content", response_model=MessageResponse, summary="Tạo quiz từ nội dung")
async def quiz_from_content_route(payload: dict) -> MessageResponse:
    return await handle_quiz_from_content(payload)


@router.post("/adaptive", response_model=MessageResponse, summary="Tạo quiz thích ứng")
async def adaptive_quiz_route(payload: dict) -> MessageResponse:
    return await handle_adaptive_quiz(payload)


@router.post("/ai-builder", response_model=QuizGenerationResponse, summary="Sinh template quiz bằng AI")
async def ai_quiz_builder_route(payload: dict) -> QuizGenerationResponse:
    topic = payload.get("topic", "Kiến thức tổng quan")
    num_questions = int(payload.get("num_questions", 5))
    return await handle_ai_quiz_builder(topic, num_questions)


@router.post("/{quiz_id}/start", response_model=MessageResponse, summary="Bắt đầu làm quiz")
async def start_quiz_route(quiz_id: str) -> MessageResponse:
    return await handle_start_quiz(quiz_id)


@router.post("/{quiz_id}/submit", response_model=MessageResponse, summary="Nộp bài quiz")
async def submit_quiz_route(quiz_id: str, payload: dict) -> MessageResponse:
    return await handle_submit_quiz(quiz_id, payload)


@router.get("/{quiz_id}/result", response_model=MessageResponse, summary="Kết quả quiz")
async def quiz_result_route(quiz_id: str) -> MessageResponse:
    return await handle_quiz_result_detail(quiz_id)


@router.get("/history", response_model=MessageResponse, summary="Lịch sử quiz của người dùng")
async def quiz_history_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    return await handle_quiz_history(current_user)
