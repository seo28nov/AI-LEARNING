"""Controller upload tài liệu."""
from typing import Optional

from fastapi import HTTPException, status

from services.upload_service import (
    register_upload,
    get_upload_by_id,
    list_uploads_by_user,
    update_upload_status,
    delete_upload,
    process_document,
    upload_from_url
)


async def handle_register_upload(
    filename: str,
    file_size: int,
    file_type: str,
    user_id: str,
    course_id: Optional[str] = None
) -> dict:
    """Đăng ký file upload mới."""
    
    return await register_upload(
        filename=filename,
        file_size=file_size,
        file_type=file_type,
        user_id=user_id,
        course_id=course_id
    )


async def handle_get_upload(file_id: str, user_id: str) -> dict:
    """Lấy thông tin file upload."""
    
    return await get_upload_by_id(file_id, user_id)


async def handle_list_uploads(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    course_id: Optional[str] = None
) -> dict:
    """Danh sách file uploads của user."""
    
    uploads, total = await list_uploads_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
        course_id=course_id
    )
    
    return {
        "uploads": uploads,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def handle_update_upload_status(file_id: str, status: str, user_id: str) -> dict:
    """Cập nhật trạng thái upload."""
    
    return await update_upload_status(file_id, status, user_id)


async def handle_delete_upload(file_id: str, user_id: str) -> dict:
    """Xóa file upload."""
    
    await delete_upload(file_id, user_id)
    return {"message": "File đã được xóa"}


async def handle_process_upload(file_id: str, user_id: str) -> dict:
    """Xử lý file upload - extract text, generate embeddings."""
    
    return await process_document(file_id, user_id)


async def handle_upload_from_url(payload: dict, user_id: str) -> dict:
    """Upload tài liệu từ URL."""
    
    url = payload.get("url")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
    
    course_id = payload.get("course_id")
    
    return await upload_from_url(
        url=url,
        user_id=user_id,
        course_id=course_id
    )
