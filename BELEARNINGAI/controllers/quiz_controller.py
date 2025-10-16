"""Controller quiz."""
from typing import Optional

from fastapi import HTTPException, status

from services.quiz_service import (
    create_quiz,
    get_quiz_by_id,
    list_quizzes_by_course,
    update_quiz,
    delete_quiz,
    generate_quiz_with_ai,
    submit_quiz_attempt,
    get_quiz_attempts,
    get_quiz_statistics
)


async def handle_create_quiz(payload: dict, user_id: str) -> dict:
    """Tạo quiz mới."""
    
    return await create_quiz(
        title=payload.get("title"),
        description=payload.get("description", ""),
        course_id=payload.get("course_id"),
        chapter_id=payload.get("chapter_id"),
        questions=payload.get("questions", []),
        time_limit=payload.get("time_limit"),
        passing_score=payload.get("passing_score", 70),
        user_id=user_id
    )


async def handle_get_quiz(quiz_id: str) -> dict:
    """Lấy chi tiết quiz."""
    
    return await get_quiz_by_id(quiz_id)


async def handle_list_quizzes(
    course_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> dict:
    """Danh sách quiz."""
    
    if course_id:
        quizzes, total = await list_quizzes_by_course(
            course_id=course_id,
            skip=skip,
            limit=limit
        )
    else:
        # List all quizzes - implement if needed
        quizzes = []
        total = 0
    
    return {
        "quizzes": quizzes,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_update_quiz(quiz_id: str, payload: dict, user_id: str, user_role: str) -> dict:
    """Cập nhật quiz."""
    
    return await update_quiz(quiz_id, payload, user_id, user_role)


async def handle_delete_quiz(quiz_id: str, user_id: str, user_role: str) -> dict:
    """Xóa quiz."""
    
    await delete_quiz(quiz_id, user_id, user_role)
    return {"message": "Quiz đã được xóa"}


async def handle_generate_quiz_ai(payload: dict, user_id: str) -> dict:
    """Tạo quiz bằng AI."""
    
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic is required"
        )
    
    return await generate_quiz_with_ai(
        topic=topic,
        course_id=payload.get("course_id"),
        chapter_id=payload.get("chapter_id"),
        num_questions=payload.get("num_questions", 10),
        difficulty=payload.get("difficulty", "medium"),
        user_id=user_id
    )


async def handle_start_quiz(quiz_id: str, user_id: str) -> dict:
    """Bắt đầu làm quiz - trả về quiz với questions."""
    
    quiz = await get_quiz_by_id(quiz_id)
    
    return {
        "quiz_id": quiz_id,
        "started_at": "now",  # Should be actual timestamp
        "time_limit": quiz.get("time_limit"),
        "questions": quiz.get("questions", [])
    }


async def handle_submit_quiz(quiz_id: str, payload: dict, user_id: str) -> dict:
    """Nộp bài quiz."""
    
    answers = payload.get("answers")
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers are required"
        )
    
    return await submit_quiz_attempt(
        quiz_id=quiz_id,
        user_id=user_id,
        answers=answers
    )


async def handle_quiz_attempts(quiz_id: str, user_id: str) -> dict:
    """Lấy lịch sử làm quiz."""
    
    attempts = await get_quiz_attempts(quiz_id, user_id)
    
    return {
        "quiz_id": quiz_id,
        "attempts": attempts,
        "total": len(attempts)
    }


async def handle_quiz_statistics(quiz_id: str, user_role: str) -> dict:
    """Thống kê quiz (cho instructor/admin)."""
    
    if user_role not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can view quiz statistics"
        )
    
    return await get_quiz_statistics(quiz_id)


# Aliases for router compatibility
handle_adaptive_quiz = handle_generate_quiz_ai
handle_ai_quiz_builder = handle_generate_quiz_ai
handle_generate_quiz = handle_generate_quiz_ai
handle_list_all_quizzes = handle_list_quizzes
handle_quiz_detail = handle_get_quiz
handle_quiz_from_content = handle_generate_quiz_ai
handle_quiz_history = handle_quiz_attempts
handle_quiz_result_detail = handle_get_quiz
handle_update_quiz_detail = handle_update_quiz
