"""Schema dùng chung cho API responses."""
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaInfo(BaseModel):
    """Thông tin phân trang."""

    total: int = 0
    page: int = 1
    size: int = 10


class PaginatedResponse(BaseModel, Generic[T]):
    """Bao bọc danh sách có phân trang."""

    data: List[T]
    meta: MetaInfo = Field(default_factory=MetaInfo)


class MessageResponse(BaseModel):
    """Trả về thông điệp đơn giản."""

    message: str = Field(default="Chức năng đang phát triển")
