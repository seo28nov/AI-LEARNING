"""Kiểm tra cấu hình logging."""
import logging

from config.logging_config import LOGGING_CONFIG, setup_logging


def test_logging_configuration() -> None:
    """Đảm bảo logging config có handler console."""

    setup_logging()
    logger = logging.getLogger("app")
    assert "console" in LOGGING_CONFIG["handlers"]
    assert logger.level == logging.INFO
