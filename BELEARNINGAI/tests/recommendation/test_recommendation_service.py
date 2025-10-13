"""Kiểm thử placeholder cho recommendation service."""
import pytest

from services import recommendation_service


@pytest.mark.skip(reason="placeholder: cần dữ liệu thật khi implement ML")
@pytest.mark.asyncio
async def test_build_learning_path_returns_steps():
    """Learning path demo phải trả về ít nhất ba bước."""

    steps = await recommendation_service.build_learning_path(["arrays"], ["oop"])
    assert len(steps) >= 3
