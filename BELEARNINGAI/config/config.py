"""Định nghĩa cấu hình ứng dụng FastAPI dựa trên HE_THONG.md."""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Lớp Settings đọc biến môi trường cho toàn hệ thống."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="allow"  # Cho phép extra fields từ .env
    )

    app_name: str = Field(default="AI Learning Platform API", description="Tên ứng dụng phục vụ hiển thị metadata")
    environment: str = Field(default="development", description="Môi trường chạy: development/staging/production")

    mongodb_url: str = Field(default="mongodb://localhost:27017", description="Kết nối MongoDB chính")
    mongodb_database: str = Field(default="ai_learning_app", description="Tên database MongoDB")

    jwt_secret_key: str = Field(default="change_me", description="Khóa bí mật ký JWT")
    jwt_algorithm: str = Field(default="HS256", description="Thuật toán ký JWT")
    access_token_expire_minutes: int = Field(default=15, description="Thời hạn token truy cập (phút)")
    refresh_token_expire_days: int = Field(default=7, description="Thời hạn refresh token (ngày)")

    google_api_key: str = Field(default="", description="API key cho Google GenAI")
    
    # Vector Database Settings - FAISS
    vector_persist_directory: str = Field(
        default="./faiss_db",
        description="Directory lưu trữ FAISS vector data (persistent storage)"
    )
    
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], description="Danh sách origin cho CORS")
    recommender_model: str = Field(
        default="gemini-1.5-pro",
        description="Model sử dụng cho gợi ý khóa học (placeholder, override qua ENV)",
    )
    frontend_url: str = Field(default="http://localhost:3000", description="URL frontend để tạo link email")


@lru_cache
def get_settings() -> Settings:
    """Trả về singleton Settings, tránh đọc file nhiều lần."""

    return Settings()


# Create singleton instance for backward compatibility
settings = get_settings()
