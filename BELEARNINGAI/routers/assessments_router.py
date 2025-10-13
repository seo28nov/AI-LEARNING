"""Router cho hệ thống đánh giá năng lực."""
from typing import List

from fastapi import APIRouter, Depends

from controllers.assessment_controller import (
    handle_assessment_categories,
    handle_assessment_history,
    handle_assessment_recommendations,
    handle_assessment_result,
    handle_get_assessment_detail,
    handle_skill_test,
    handle_start_assessment,
    handle_submit_assessment,
)
from middleware.auth import get_current_user
from schemas.assessment import (
    AssessmentResultResponse,
    AssessmentStartRequest,
    AssessmentSubmitRequest,
    AssessmentSummary,
    RecommendationItem,
)
from schemas.common import MessageResponse

router = APIRouter(tags=["assessments"])


@router.get("/categories", response_model=MessageResponse, summary="Danh sách lĩnh vực đánh giá")
async def list_assessment_categories() -> MessageResponse:
    return await handle_assessment_categories()


@router.post("/start", response_model=AssessmentSummary, summary="Bắt đầu bài đánh giá")
async def start_assessment_route(
    payload: AssessmentStartRequest, current_user: dict = Depends(get_current_user)
) -> AssessmentSummary:
    return await handle_start_assessment(payload, current_user)


@router.post("/{assessment_id}/submit", response_model=AssessmentSummary, summary="Nộp bài đánh giá")
async def submit_assessment_route(assessment_id: str, payload: AssessmentSubmitRequest) -> AssessmentSummary:
    return await handle_submit_assessment(assessment_id, payload)


@router.post(
    "/skill-test",
    response_model=AssessmentResultResponse,
    summary="Phân tích kết quả skill-test và gợi ý khóa học",
)
async def skill_test_route(
    payload: AssessmentSubmitRequest, current_user: dict = Depends(get_current_user)
) -> AssessmentResultResponse:
    return await handle_skill_test(payload, current_user)


@router.get(
    "/{assessment_id}",
    response_model=AssessmentSummary,
    summary="Chi tiết bài đánh giá",
)
async def assessment_detail_route(
    assessment_id: str, current_user: dict = Depends(get_current_user)
) -> AssessmentSummary:
    return await handle_get_assessment_detail(assessment_id, current_user)


@router.get(
    "/{assessment_id}/result",
    response_model=AssessmentResultResponse,
    summary="Kết quả chi tiết của bài đánh giá",
)
async def assessment_result_route(
    assessment_id: str, current_user: dict = Depends(get_current_user)
) -> AssessmentResultResponse:
    return await handle_assessment_result(assessment_id, current_user)


@router.get(
    "/history",
    response_model=List[AssessmentSummary],
    summary="Lịch sử các bài đánh giá đã làm",
)
async def assessment_history_route(current_user: dict = Depends(get_current_user)) -> List[AssessmentSummary]:
    return await handle_assessment_history(current_user)


@router.post(
    "/{assessment_id}/recommendations",
    response_model=List[RecommendationItem],
    summary="Gợi ý khóa học dựa trên kết quả",
)
async def assessment_recommendations_route(
    assessment_id: str, current_user: dict = Depends(get_current_user)
) -> List[RecommendationItem]:
    return await handle_assessment_recommendations(assessment_id, current_user)
