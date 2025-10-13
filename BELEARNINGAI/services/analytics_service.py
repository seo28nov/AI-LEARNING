"""Service placeholder cho analytics."""
from datetime import datetime

from schemas.analytics import DashboardSection, MetricPoint, StudentDashboardResponse


async def get_student_dashboard(user_id: str) -> StudentDashboardResponse:
    """Trả về số liệu demo cho dashboard học viên."""

    _ = user_id
    generated_at = datetime.utcnow()
    section = DashboardSection(
        title="Overview",
        metrics=[
            MetricPoint(label="Đã đăng ký", value=5, trend=12.5),
            MetricPoint(label="Hoàn thành", value=2, trend=5.0),
        ],
    )
    return StudentDashboardResponse(generated_at=generated_at, sections=[section])


async def build_student_dashboard(progress_percent: float) -> StudentDashboardResponse:
    """Hàm dùng cho controller mới, trả về hai section demo."""

    generated_at = datetime.utcnow()
    overview = DashboardSection(
        title="Tổng quan",
        metrics=[
            MetricPoint(label="Tiến độ trung bình", value=progress_percent, trend=1.5),
            MetricPoint(label="Chuỗi ngày học", value=4, trend=0.5),
        ],
    )
    commitment = DashboardSection(
        title="Thói quen học tập",
        metrics=[
            MetricPoint(label="Thời gian học tuần này (phút)", value=180, trend=10.0),
            MetricPoint(label="Số quiz đã làm", value=6, trend=2.0),
        ],
    )
    return StudentDashboardResponse(generated_at=generated_at, sections=[overview, commitment])
