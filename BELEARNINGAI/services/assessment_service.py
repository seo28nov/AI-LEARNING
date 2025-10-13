"""Service placeholder cho module đánh giá năng lực."""
from datetime import datetime
from typing import List

from schemas.assessment import (
    AssessmentResultResponse,
    AssessmentSummary,
    AssessmentTopicInsight,
)


async def start_assessment(user_id: str, category: str, assessment_type: str) -> AssessmentSummary:
    """Tạm thời trả về dữ liệu giả lập cho quá trình start assessment."""

    now = datetime.utcnow()
    return AssessmentSummary(
        id="demo-assessment",
        user_id=user_id,
        category=category,
        assessment_type=assessment_type,
        score=0,
        level="beginner",
        strengths=[],
        weaknesses=[],
        created_at=now,
    )


async def submit_assessment(assessment_id: str, answers: list[int]) -> AssessmentSummary:
    """Placeholder chấm điểm, trả định dạng chuẩn."""

    score = float(len(answers) * 10)
    now = datetime.utcnow()
    return AssessmentSummary(
        id=assessment_id,
        user_id="demo-user",
        category="programming",
        assessment_type="skill_assessment",
        score=score,
        level="intermediate",
        strengths=["arrays"],
        weaknesses=["oop"],
        created_at=now,
    )


async def analyze_topics(category: str) -> List[AssessmentTopicInsight]:
    """Sinh dữ liệu phân tích chủ đề để FE hiển thị theo mục 5.1.1."""

    _ = category
    return [
        AssessmentTopicInsight(topic="Biến & Kiểu dữ liệu", correct=4, total=5, mastery_level="good"),
        AssessmentTopicInsight(topic="OOP", correct=2, total=5, mastery_level="fair"),
    ]


async def evaluate_skill_test(user_id: str, payload: list[int]) -> AssessmentResultResponse:
    """Tổng hợp kết quả skill-test, trả dữ liệu demo phục vụ FE."""

    _ = user_id
    score = 78.0
    return AssessmentResultResponse(
        score=score,
        level="intermediate",
        strengths=["Biến cơ bản", "Cấu trúc điều khiển"],
        weaknesses=["OOP", "Giải thuật"],
        topics=await analyze_topics("programming"),
        recommended_courses=[],
        learning_path=[],
        generated_at=datetime.utcnow(),
    )
