"""Cấu hình pytest chung."""
import asyncio
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Tạo event loop riêng cho pytest."""

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Sinh TestClient sử dụng app FastAPI, bỏ qua kết nối DB thật."""

    async def _fake_init_database() -> None:  # noqa: D401
        """Mock init database cho môi trường test."""

    async def _fake_close_database() -> None:  # noqa: D401
        """Mock close database cho môi trường test."""

    monkeypatch.setattr("app.database.init_database", _fake_init_database)
    monkeypatch.setattr("app.database.close_database", _fake_close_database)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def fake_current_user() -> dict:
    """Fixture trả về thông tin user giả cho các test placeholder."""

    return {"sub": "user-test", "role": "student"}
