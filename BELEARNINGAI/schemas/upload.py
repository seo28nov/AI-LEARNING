"""Schemas cho module upload tài liệu."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UploadInitResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime


class UploadProcessStatus(BaseModel):
    id: str
    status: str
    extracted_text_length: Optional[int] = None
    chunk_count: Optional[int] = None
