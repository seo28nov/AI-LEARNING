"""Dịch vụ xử lý upload và quản lý file."""
import hashlib
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status, UploadFile

from config.config import get_settings
from models.models import UploadDocument, UserDocument


settings = get_settings()

# Các loại file được phép
ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain',
    'md': 'text/markdown',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
}

# Kích thước file tối đa (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


async def upload_file(
    file: UploadFile,
    user_id: str,
    course_id: Optional[str] = None,
    description: str = ""
) -> dict:
    """Upload file và lưu metadata.
    
    Args:
        file: File upload
        user_id: ID người dùng
        course_id: ID khóa học (optional)
        description: Mô tả file
        
    Returns:
        Thông tin file đã upload
    """
    # Kiểm tra user
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    # Validate file
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )
    
    # Đọc file content
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File quá lớn. Kích thước tối đa: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Tạo file hash
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Kiểm tra file đã tồn tại chưa
    existing = await UploadDocument.find_one(
        UploadDocument.user_id == user_id,
        UploadDocument.file_hash == file_hash
    )
    
    if existing:
        return {
            "id": str(existing.id),
            "message": "File này đã được upload trước đó",
            "file_name": existing.file_name,
            "status": existing.status
        }
    
    # Lưu file vào storage (giả lập - trong thực tế sẽ upload lên S3/R2)
    storage_path = f"uploads/{user_id}/{file_hash[:8]}_{file.filename}"
    file_url = f"https://storage.example.com/{storage_path}"
    
    # TODO: Thực tế sẽ upload lên S3/Cloudflare R2
    # s3_client.upload_fileobj(file_content, bucket, storage_path)
    
    # Tạo upload document
    now = datetime.now(timezone.utc)
    upload_doc = UploadDocument(
        user_id=user_id,
        course_id=course_id,
        file_name=file.filename,
        file_type=file_extension,
        file_size=file_size,
        file_hash=file_hash,
        file_url=file_url,
        storage_path=storage_path,
        description=description,
        status="pending",  # pending -> processing -> completed
        extracted_text="",
        created_at=now,
        updated_at=now
    )
    
    await upload_doc.insert()
    
    # Trigger background task để xử lý file
    # TODO: Implement background task với Celery/RQ
    # extract_text_task.delay(str(upload_doc.id))
    
    return {
        "id": str(upload_doc.id),
        "file_name": upload_doc.file_name,
        "file_size": upload_doc.file_size,
        "file_type": upload_doc.file_type,
        "file_url": upload_doc.file_url,
        "status": upload_doc.status,
        "created_at": upload_doc.created_at
    }


async def get_upload_by_id(upload_id: str, user_id: str) -> dict:
    """Lấy thông tin file đã upload.
    
    Args:
        upload_id: ID upload
        user_id: ID người dùng
        
    Returns:
        Thông tin upload
    """
    upload = await UploadDocument.get(upload_id)
    if upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File không tồn tại"
        )
    
    # Kiểm tra quyền
    if upload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập file này"
        )
    
    return {
        "id": str(upload.id),
        "file_name": upload.file_name,
        "file_type": upload.file_type,
        "file_size": upload.file_size,
        "file_url": upload.file_url,
        "description": upload.description,
        "status": upload.status,
        "extracted_text": upload.extracted_text[:500] if upload.extracted_text else "",  # Preview
        "created_at": upload.created_at,
        "updated_at": upload.updated_at
    }


async def list_user_uploads(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    file_type: Optional[str] = None
) -> tuple[List[dict], int]:
    """Lấy danh sách file đã upload.
    
    Args:
        user_id: ID người dùng
        skip: Bỏ qua
        limit: Giới hạn
        file_type: Lọc theo loại file
        
    Returns:
        Tuple (uploads, total)
    """
    query_conditions = [UploadDocument.user_id == user_id]
    
    if file_type:
        query_conditions.append(UploadDocument.file_type == file_type)
    
    query = UploadDocument.find(*query_conditions)
    total = await query.count()
    uploads = await query.sort(-UploadDocument.created_at).skip(skip).limit(limit).to_list()
    
    upload_list = []
    for upload in uploads:
        upload_list.append({
            "id": str(upload.id),
            "file_name": upload.file_name,
            "file_type": upload.file_type,
            "file_size": upload.file_size,
            "file_url": upload.file_url,
            "status": upload.status,
            "created_at": upload.created_at
        })
    
    return upload_list, total


async def delete_upload(upload_id: str, user_id: str) -> bool:
    """Xóa file đã upload.
    
    Args:
        upload_id: ID upload
        user_id: ID người dùng
        
    Returns:
        True nếu thành công
    """
    upload = await UploadDocument.get(upload_id)
    if upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File không tồn tại"
        )
    
    # Kiểm tra quyền
    if upload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa file này"
        )
    
    # TODO: Xóa file từ storage
    # s3_client.delete_object(bucket, upload.storage_path)
    
    await upload.delete()
    return True


async def process_upload(upload_id: str) -> dict:
    """Xử lý file: trích xuất text, tạo embeddings.
    
    Args:
        upload_id: ID upload
        
    Returns:
        Thông tin xử lý
    """
    upload = await UploadDocument.get(upload_id)
    if upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File không tồn tại"
        )
    
    # Cập nhật trạng thái
    upload.status = "processing"
    upload.updated_at = datetime.now(timezone.utc)
    await upload.save()
    
    try:
        # Trích xuất text từ file
        extracted_text = await extract_text_from_file(upload.file_url, upload.file_type)
        
        # Lưu text đã trích xuất
        upload.extracted_text = extracted_text
        upload.status = "completed"
        upload.updated_at = datetime.now(timezone.utc)
        await upload.save()
        
        # TODO: Tạo vector embeddings và lưu vào vector database
        # embeddings = create_embeddings(extracted_text)
        # vector_db.insert(embeddings, metadata={"upload_id": upload_id})
        
        return {
            "id": upload_id,
            "status": "completed",
            "text_length": len(extracted_text),
            "processed_at": upload.updated_at
        }
        
    except Exception as e:
        # Cập nhật trạng thái lỗi
        upload.status = "failed"
        upload.updated_at = datetime.now(timezone.utc)
        await upload.save()
        
        print(f"Error processing upload {upload_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể xử lý file: {str(e)}"
        )


async def extract_text_from_file(file_url: str, file_type: str) -> str:
    """Trích xuất text từ file.
    
    Args:
        file_url: URL file
        file_type: Loại file
        
    Returns:
        Text đã trích xuất
    """
    # TODO: Implement text extraction
    # Sử dụng các thư viện:
    # - PyPDF2/pdfplumber cho PDF
    # - python-docx cho DOCX
    # - python-pptx cho PPTX
    
    # Giả lập trích xuất text
    if file_type == 'txt':
        # Đọc trực tiếp text file
        return "Sample extracted text from TXT file..."
    elif file_type == 'pdf':
        return "Sample extracted text from PDF file..."
    elif file_type in ['doc', 'docx']:
        return "Sample extracted text from Word document..."
    elif file_type in ['ppt', 'pptx']:
        return "Sample extracted text from PowerPoint..."
    else:
        return ""


async def get_upload_status(upload_id: str, user_id: str) -> dict:
    """Kiểm tra trạng thái xử lý file.
    
    Args:
        upload_id: ID upload
        user_id: ID người dùng
        
    Returns:
        Trạng thái xử lý
    """
    upload = await UploadDocument.get(upload_id)
    if upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File không tồn tại"
        )
    
    # Kiểm tra quyền
    if upload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập file này"
        )
    
    return {
        "id": upload_id,
        "status": upload.status,  # pending/processing/completed/failed
        "file_name": upload.file_name,
        "updated_at": upload.updated_at
    }


async def upload_from_url(
    url: str,
    user_id: str,
    course_id: Optional[str] = None,
    description: str = ""
) -> dict:
    """Upload file từ URL.
    
    Args:
        url: URL file
        user_id: ID người dùng
        course_id: ID khóa học
        description: Mô tả
        
    Returns:
        Thông tin upload
    """
    # TODO: Implement download from URL
    # import requests
    # response = requests.get(url)
    # file_content = response.content
    
    # Giả lập
    file_name = url.split('/')[-1]
    file_extension = file_name.split('.')[-1].lower()
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loại file không được hỗ trợ"
        )
    
    # Tạo upload document
    now = datetime.now(timezone.utc)
    upload_doc = UploadDocument(
        user_id=user_id,
        course_id=course_id,
        file_name=file_name,
        file_type=file_extension,
        file_size=0,  # Sẽ cập nhật sau khi download
        file_hash="",
        file_url=url,
        storage_path="",
        description=description,
        status="pending",
        extracted_text="",
        created_at=now,
        updated_at=now
    )
    
    await upload_doc.insert()
    
    return {
        "id": str(upload_doc.id),
        "file_name": upload_doc.file_name,
        "status": upload_doc.status,
        "created_at": upload_doc.created_at
    }
