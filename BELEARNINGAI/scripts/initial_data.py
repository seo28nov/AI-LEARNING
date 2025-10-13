"""Script seed dữ liệu khóa học mẫu."""
import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import get_settings
from models.models import CourseDocument
from modules.course_module import build_demo_course


async def seed_courses() -> None:
    """Chèn dữ liệu khóa học "Con lắc lò xo" vào MongoDB."""

    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    try:
        await init_beanie(database=client[settings.mongodb_database], document_models=[CourseDocument])
        payload = build_demo_course()
        exists = await CourseDocument.find_one(CourseDocument.title == payload.title)
        if exists:
            print("Khóa học đã tồn tại, bỏ qua")
            return
        await CourseDocument(**payload.model_dump(), created_by="seed-script").insert()
        print("Seed dữ liệu thành công")
    finally:
        client.close()


async def seed_demo_courses() -> None:
    """Hàm tiện ích được gọi từ task khác để seed dataset demo."""

    await seed_courses()


if __name__ == "__main__":
    asyncio.run(seed_courses())
