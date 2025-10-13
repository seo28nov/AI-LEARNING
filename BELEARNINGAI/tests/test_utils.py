"""Kiểm tra hàm tiện ích."""
from utils.utils import utc_now_str


def test_utc_now_str_format() -> None:
    """Đảm bảo chuỗi thời gian chứa ký tự 'T'."""

    value = utc_now_str()
    assert "T" in value
