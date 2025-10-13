"""Hàm tiện ích chung cho dự án."""
from datetime import datetime


def utc_now_str() -> str:
    """Trả về thời gian hiện tại dạng ISO 8601."""

    return datetime.utcnow().isoformat()
