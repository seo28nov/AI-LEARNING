"""Kiểm tra lớp Settings."""
from config.config import Settings


def test_settings_defaults() -> None:
    """Đảm bảo giá trị mặc định chính xác."""

    settings = Settings()
    assert settings.app_name == "AI Learning Platform API"
    assert settings.environment == "development"
