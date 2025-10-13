"""Controller upload tài liệu."""
from models.models import UploadResponse
from schemas.common import MessageResponse
from services.upload_service import register_upload, update_upload_status


async def handle_register_upload(file_id: str, filename: str) -> UploadResponse:
    """Ghi nhận upload mới."""

    return await register_upload(file_id, filename)


async def handle_update_upload(file_id: str, status: str) -> UploadResponse:
    """Cập nhật trạng thái upload."""

    return await update_upload_status(file_id, status)


async def handle_list_uploads(user_id: str) -> MessageResponse:
    """Placeholder danh sách file upload của người dùng."""

    return MessageResponse(message=f"Placeholder: danh sách file của {user_id}")


async def handle_upload_detail(file_id: str) -> MessageResponse:
    """Placeholder chi tiết file upload."""

    return MessageResponse(message=f"Placeholder: thông tin file {file_id}")


async def handle_delete_upload(file_id: str) -> MessageResponse:
    """Placeholder xóa file upload."""

    return MessageResponse(message=f"Placeholder: đã xóa file {file_id}")


async def handle_process_upload(file_id: str) -> MessageResponse:
    """Placeholder xử lý file upload."""

    return MessageResponse(message=f"Placeholder: đang xử lý file {file_id}")


async def handle_upload_status(file_id: str) -> MessageResponse:
    """Placeholder trạng thái xử lý file."""

    return MessageResponse(message=f"Placeholder: trạng thái xử lý của file {file_id}")


async def handle_upload_from_url(payload: dict) -> MessageResponse:
    """Placeholder upload tài liệu từ URL."""

    url = payload.get("url", "")
    return MessageResponse(message=f"Placeholder: đã nhận yêu cầu tải tài liệu từ {url}")
