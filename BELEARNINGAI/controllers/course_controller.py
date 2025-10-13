"""Controller điều phối luồng dữ liệu khóa học."""
from typing import List, Optional

from fastapi import HTTPException, status
from beanie import PydanticObjectId

from models.models import CourseCreate, CourseResponse
from schemas.common import MessageResponse
from services.course_service import create_course, get_course_by_id, list_courses


async def handle_list_courses() -> List[CourseResponse]:
    """Controller lấy danh sách khóa học phục vụ router."""

    return await list_courses()


async def handle_create_course(payload: CourseCreate, user_id: str) -> CourseResponse:
    """Controller tạo khóa học và xử lý ngoại lệ nghiệp vụ."""

    return await create_course(payload, user_id)


async def handle_get_course(course_id: str) -> CourseResponse:
    """Controller lấy khóa học theo ID, raise 404 nếu không thấy."""

    try:
        object_id = PydanticObjectId(course_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID không hợp lệ") from exc

    course = await get_course_by_id(object_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy khóa học")
    return course


async def handle_list_public_courses() -> MessageResponse:
    """Placeholder danh sách khóa học công khai."""

    return MessageResponse(message="Placeholder: danh sách khóa học công khai")


async def handle_recommended_courses(current_user: dict) -> MessageResponse:
    """Placeholder gợi ý khóa học theo người dùng."""

    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: khóa học gợi ý cho {user_id}")


async def handle_search_courses(keyword: Optional[str]) -> MessageResponse:
    """Placeholder tìm kiếm khóa học."""

    if not keyword:
        return MessageResponse(message="Placeholder: nhập từ khóa để tìm kiếm khóa học")
    return MessageResponse(message=f"Placeholder: kết quả tìm kiếm cho '{keyword}'")


async def handle_course_categories() -> MessageResponse:
    """Placeholder danh mục khóa học."""

    return MessageResponse(message="Placeholder: Programming/Design/Business")


async def handle_create_course_from_prompt(payload: dict, current_user: dict) -> MessageResponse:
    """Placeholder tạo khóa học bằng AI."""

    topic = payload.get("topic", "Chủ đề chưa xác định")
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: AI đang sinh khóa học '{topic}' cho {user_id}")


async def handle_create_course_from_upload(payload: dict, current_user: dict) -> MessageResponse:
    """Placeholder tạo khóa học từ file upload."""

    filename = payload.get("filename", "tài liệu")
    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: Đang xử lý file {filename} cho {user_id}")


async def handle_duplicate_course(course_id: str, current_user: dict) -> MessageResponse:
    """Placeholder sao chép khóa học."""

    user_id = current_user.get("sub", "demo-user")
    return MessageResponse(message=f"Placeholder: khóa học {course_id} được sao chép cho {user_id}")


async def handle_update_visibility(course_id: str, payload: dict, current_user: dict) -> MessageResponse:
    """Placeholder cập nhật trạng thái hiển thị khóa học."""

    visibility = payload.get("visibility", "public")
    _ = current_user
    return MessageResponse(message=f"Placeholder: khóa học {course_id} chuyển sang trạng thái {visibility}")


async def handle_list_chapters(course_id: str) -> MessageResponse:
    """Placeholder danh sách chương của khóa học."""

    return MessageResponse(message=f"Placeholder: chương học cho khóa {course_id}")


async def handle_create_chapter(course_id: str, payload: dict) -> MessageResponse:
    """Placeholder thêm chương mới."""

    chapter_title = payload.get("title", "Chương mới")
    return MessageResponse(message=f"Placeholder: đã tạo chương '{chapter_title}' cho khóa {course_id}")


async def handle_update_chapter(course_id: str, chapter_id: str, payload: dict) -> MessageResponse:
    """Placeholder cập nhật chương."""

    chapter_title = payload.get("title", "Chương cập nhật")
    return MessageResponse(
        message=f"Placeholder: đã cập nhật chương {chapter_id} của khóa {course_id} thành '{chapter_title}'"
    )


async def handle_delete_chapter(course_id: str, chapter_id: str) -> MessageResponse:
    """Placeholder xóa chương."""

    return MessageResponse(message=f"Placeholder: đã xóa chương {chapter_id} khỏi khóa {course_id}")
