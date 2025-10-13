"""Chứa logic nghiệp vụ chính cho khóa học và AI."""
from datetime import datetime
from typing import List

from beanie import PydanticObjectId

from models.models import CourseCreate, CourseDocument, CourseResponse


async def list_courses() -> List[CourseResponse]:
    """Trả về danh sách khóa học hiện có trong MongoDB."""

    courses = await CourseDocument.find_all().to_list()
    return [CourseResponse.model_validate(course, from_attributes=True) for course in courses]


async def create_course(payload: CourseCreate, user_id: str) -> CourseResponse:
    """Tạo khóa học mới với thông tin người dùng hiện tại."""

    course_doc = CourseDocument(
        **payload.model_dump(),
        created_by=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    saved = await course_doc.insert()
    return CourseResponse.model_validate(saved, from_attributes=True)


async def get_course_by_id(course_id: PydanticObjectId) -> CourseResponse | None:
    """Lấy chi tiết khóa học theo ID."""

    course = await CourseDocument.get(course_id)
    if course is None:
        return None
    return CourseResponse.model_validate(course, from_attributes=True)
