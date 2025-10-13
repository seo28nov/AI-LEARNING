"""Dịch vụ xử lý upload tài liệu."""
from models.models import UploadResponse


async def register_upload(file_id: str, filename: str) -> UploadResponse:
    """Giả lập trả về thông tin upload."""

    return UploadResponse.model_validate({"_id": file_id, "filename": filename, "status": "processing"})


async def update_upload_status(file_id: str, status: str) -> UploadResponse:
    """Giả lập cập nhật trạng thái upload."""

    return UploadResponse.model_validate({"_id": file_id, "filename": "unknown", "status": status})
