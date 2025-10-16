"""Quản lý kết nối MongoDB và khởi tạo Beanie ODM."""
from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import get_settings
from models.models import (
    AssessmentDocument,
    ChatDocument,
    ClassDocument,
    CourseDocument,
    DashboardDocument,
    EnrollmentDocument,
    NotificationDocument,
    PasswordResetTokenDocument,
    ProgressDocument,
    QuizDocument,
    RefreshTokenDocument,
    UploadDocument,
    UserDocument,
    VerificationTokenDocument,
)

_settings = get_settings()
_mongo_client: Optional[AsyncIOMotorClient] = None


async def init_database() -> None:
    """Khởi tạo database MongoDB và đăng ký các document."""

    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(_settings.mongodb_url)
    await init_beanie(
        database=_mongo_client[_settings.mongodb_database],
        document_models=[
            UserDocument,
            CourseDocument,
            ClassDocument,
            EnrollmentDocument,
            QuizDocument,
            AssessmentDocument,
            ChatDocument,
            UploadDocument,
            ProgressDocument,
            NotificationDocument,
            DashboardDocument,
            RefreshTokenDocument,
            VerificationTokenDocument,
            PasswordResetTokenDocument,
        ],
    )


async def close_database() -> None:
    """Đóng kết nối MongoDB khi ứng dụng shutdown."""

    if _mongo_client is not None:
        _mongo_client.close()
