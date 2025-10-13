"""Schemas cho module tìm kiếm."""
from typing import List

from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: str
    categories: List[str] = []
    level: str | None = None


class SearchResultItem(BaseModel):
    id: str
    title: str
    snippet: str
    type: str


class SearchResponse(BaseModel):
    items: List[SearchResultItem]
