"""Kiểm tra script seed dữ liệu."""
import pytest

import scripts.initial_data as initial_data


@pytest.mark.asyncio
async def test_seed_courses(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """Đảm bảo seed_courses gọi insert khi không có dữ liệu."""

    class DummyCollection:
        async def insert(self, *_args, **_kwargs):  # noqa: D401
            """Fake insert báo thành công."""

    class DummyCourse:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        @staticmethod
        async def find_one(*_args, **_kwargs):  # noqa: D401
            """Giả lập không tìm thấy khóa học."""

            return None

        async def insert(self):  # noqa: D401
            """Giả lập insert."""

            return None

    async def fake_init_beanie(*_args, **_kwargs):  # noqa: D401
        """Bỏ qua khởi tạo beanie."""

    class DummyClient:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def __getitem__(self, _name):  # noqa: D401
            """Trả về collection giả."""

            return DummyCollection()

        def close(self) -> None:
            """Giả lập đóng kết nối."""

    monkeypatch.setattr(initial_data, "AsyncIOMotorClient", DummyClient)
    monkeypatch.setattr(initial_data, "init_beanie", fake_init_beanie)
    monkeypatch.setattr(initial_data, "CourseDocument", DummyCourse)

    await initial_data.seed_courses()
    captured = capsys.readouterr()
    assert "Seed dữ liệu" in captured.out
