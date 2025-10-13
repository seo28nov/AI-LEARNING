"""Kiểm tra cấu hình kết nối MongoDB."""
from config.config import get_settings


def test_mongodb_settings() -> None:
    """Đảm bảo thông tin kết nối MongoDB có giá trị mặc định hợp lệ."""

    settings = get_settings()
    assert settings.mongodb_url.startswith("mongodb://")
    assert settings.mongodb_database != ""
