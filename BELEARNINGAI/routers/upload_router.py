"""Router upload tài liệu."""
from fastapi import APIRouter, Depends

from controllers.upload_controller import (
    handle_delete_upload,
    handle_list_uploads,
    handle_process_upload,
    handle_register_upload,
    handle_update_upload,
    handle_upload_detail,
    handle_upload_from_url,
    handle_upload_status,
)
from middleware.auth import get_current_user
from models.models import UploadResponse
from schemas.common import MessageResponse

router = APIRouter(tags=["uploads"])


@router.post("/", response_model=UploadResponse, summary="Đăng ký upload mới")
async def register_upload_route(filename: str) -> UploadResponse:
    """Đăng ký upload file."""

    return await handle_register_upload("file-demo", filename)


@router.patch("/{file_id}", response_model=UploadResponse, summary="Cập nhật trạng thái upload")
async def update_upload_route(file_id: str, status: str) -> UploadResponse:
    """Cập nhật trạng thái file."""

    return await handle_update_upload(file_id, status)


@router.get("/", response_model=MessageResponse, summary="Danh sách file của người dùng")
async def list_uploads_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    user_id = current_user.get("sub", "demo-user")
    return await handle_list_uploads(user_id)


@router.get("/{file_id}", response_model=MessageResponse, summary="Chi tiết file")
async def upload_detail_route(file_id: str) -> MessageResponse:
    return await handle_upload_detail(file_id)


@router.delete("/{file_id}", response_model=MessageResponse, summary="Xóa file")
async def delete_upload_route(file_id: str) -> MessageResponse:
    return await handle_delete_upload(file_id)


@router.post("/{file_id}/process", response_model=MessageResponse, summary="Xử lý file")
async def process_upload_route(file_id: str) -> MessageResponse:
    return await handle_process_upload(file_id)


@router.get("/{file_id}/status", response_model=MessageResponse, summary="Trạng thái xử lý file")
async def upload_status_route(file_id: str) -> MessageResponse:
    return await handle_upload_status(file_id)


@router.post("/url", response_model=MessageResponse, summary="Upload tài liệu từ URL")
async def upload_from_url_route(payload: dict) -> MessageResponse:
    return await handle_upload_from_url(payload)
