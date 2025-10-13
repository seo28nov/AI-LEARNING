"""Service placeholder cho gợi ý học tập."""
from datetime import datetime
from typing import List

from schemas.assessment import RecommendationItem
from schemas.recommendation import RecommendationResponse


async def build_learning_path(strengths: list[str], weaknesses: list[str]) -> List[str]:
    """Sinh lộ trình học tập demo dựa trên điểm mạnh/yếu."""

    _ = strengths
    return [
        "Ôn tập kiến thức nền tảng",
        "Hoàn thành module OOP cơ bản",
        "Thực hành dự án mini về thuật toán",
    ] + [f"Tăng cường chủ đề: {item}" for item in weaknesses]


async def suggest_courses(user_id: str, category: str) -> List[RecommendationItem]:
    """Trả về danh sách khóa học minh họa được đề xuất."""

    _ = user_id
    now = datetime.utcnow().strftime("%Y-%m")
    return [
        RecommendationItem(
            course_id="course-python-foundation",
            title="Lập trình Python nền tảng",
            reason=f"Phù hợp để củng cố biến & kiểu dữ liệu ({now})",
        ),
        RecommendationItem(
            course_id="course-oop-fast-track",
            title="OOP trong Python",
            reason="Giải quyết điểm yếu OOP từ bài đánh giá",
        ),
    ]


async def recommend_for_user(user_id: str) -> RecommendationResponse:
    """Trả về danh sách khóa học gợi ý giả lập."""

    return RecommendationResponse(
        user_id=user_id,
        recommended_courses=["course-1", "course-2"],
        learning_path=["course-1", "course-3"],
    )
