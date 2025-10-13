"""Kiểm tra logic khởi tạo database."""
from types import SimpleNamespace

import pytest

import app.database as database


@pytest.mark.asyncio
async def test_init_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Đảm bảo init_database gọi init_beanie với models."""

    called = SimpleNamespace(init=False)

    class DummyClient:
        """Client Mongo giả lập cho test."""

        def __init__(self, *_args, **_kwargs) -> None:
            self.closed = False

        def __getitem__(self, _name):  # noqa: D401,D417
            """Trả về database giả."""

            return {}

        def close(self) -> None:
            """Đánh dấu đã đóng kết nối."""

            self.closed = True

    async def fake_init_beanie(*_args, **_kwargs) -> None:
        called.init = True

    monkeypatch.setattr(database, "AsyncIOMotorClient", DummyClient)
    monkeypatch.setattr(database, "init_beanie", fake_init_beanie)
    monkeypatch.setattr(database, "_mongo_client", None)

    await database.init_database()
    assert called.init is True
