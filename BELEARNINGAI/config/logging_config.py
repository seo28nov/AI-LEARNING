"""Cấu hình logging chuẩn cho dự án."""
import logging
from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        }
    },
    "loggers": {
        "uvicorn": {"handlers": ["console"], "level": "INFO"},
        "app": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


def setup_logging() -> None:
    """Khởi tạo logging dựa trên LOGGING_CONFIG."""

    dictConfig(LOGGING_CONFIG)
    logging.getLogger("app").info("Khởi tạo logging thành công")
