"""Kiểm tra cấu hình FastAPI trong main."""
from app.main import app


def test_app_metadata() -> None:
    """Đảm bảo metadata được cấu hình đúng."""

    assert app.title == "AI Learning Platform API"
    assert app.version == "0.1.0"
