"""Controller cho module đánh giá năng lực."""
from datetime import datetime, timedelta
from typing import List

from schemas.assessment import (
    AssessmentResultResponse,
    AssessmentStartRequest,
    AssessmentSubmitRequest,
    AssessmentSummary,
    RecommendationItem,
)
from schemas.common import MessageResponse
from services.assessment_service import evaluate_skill_test, start_assessment, submit_assessment
from services.recommendation_service import build_learning_path, suggest_courses


async def handle_start_assessment(payload: AssessmentStartRequest, current_user: dict) -> AssessmentSummary:
    user_id = current_user.get("sub", "demo-user")
    return await start_assessment(user_id=user_id, category=payload.category, assessment_type=payload.assessment_type)


async def handle_submit_assessment(assessment_id: str, payload: AssessmentSubmitRequest) -> AssessmentSummary:
    return await submit_assessment(assessment_id=assessment_id, answers=payload.answers)


async def handle_skill_test(payload: AssessmentSubmitRequest, current_user: dict) -> AssessmentResultResponse:
    """Gom dữ liệu đánh giá + lộ trình gợi ý theo mục 5.1.1."""

    user_id = current_user.get("sub", "demo-user")
    base_result = await evaluate_skill_test(user_id=user_id, payload=payload.answers)
    learning_path = await build_learning_path(base_result.strengths, base_result.weaknesses)
    recommendations = await suggest_courses(user_id=user_id, category="programming")
    return base_result.model_copy(
        update={"recommended_courses": recommendations, "learning_path": learning_path}
    )


def _build_placeholder_summary(assessment_id: str, user_id: str, offset_days: int = 0) -> AssessmentSummary:
    created_at = datetime.utcnow() - timedelta(days=offset_days)
    return AssessmentSummary(
        id=assessment_id,
        user_id=user_id,
        category="programming",
        assessment_type="skill_assessment",
        score=75.0,
        level="intermediate",
        strengths=["Biến"],
        weaknesses=["OOP"],
        created_at=created_at,
    )


async def handle_get_assessment_detail(assessment_id: str, current_user: dict) -> AssessmentSummary:
    """Trả về thông tin bài đánh giá (placeholder)."""

    user_id = current_user.get("sub", "demo-user")
    return _build_placeholder_summary(assessment_id, user_id)


async def handle_assessment_history(current_user: dict) -> List[AssessmentSummary]:
    """Danh sách lịch sử bài đánh giá (placeholder)."""

    user_id = current_user.get("sub", "demo-user")
    return [
        _build_placeholder_summary("assessment-1", user_id, offset_days=7),
        _build_placeholder_summary("assessment-2", user_id, offset_days=30),
    ]


async def handle_assessment_result(assessment_id: str, current_user: dict) -> AssessmentResultResponse:
    """Kết quả chi tiết bài đánh giá (placeholder)."""

    user_id = current_user.get("sub", "demo-user")
    dummy_answers = [1, 0, 2, 3]
    return await evaluate_skill_test(user_id=user_id, payload=dummy_answers)


async def handle_assessment_recommendations(assessment_id: str, current_user: dict) -> List[RecommendationItem]:
    """Danh sách gợi ý khóa học dựa trên bài đánh giá (placeholder)."""

    _ = assessment_id
    user_id = current_user.get("sub", "demo-user")
    return await suggest_courses(user_id=user_id, category="programming")


async def handle_assessment_categories() -> MessageResponse:
    """Danh sách lĩnh vực đánh giá (placeholder)."""

    return MessageResponse(message="Placeholder: Programming/Design/Business")
