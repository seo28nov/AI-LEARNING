"""Kiểm thử placeholder cho mã mời lớp học."""
import pytest

from services import classes_service


@pytest.mark.skip(reason="placeholder: cần tích hợp DB lớp học thực")
@pytest.mark.asyncio
async def test_generate_join_code_format():
    """Join code demo phải bắt đầu bằng tiền tố JOIN."""

    invite = await classes_service.generate_join_code("class-xyz")
    assert invite.join_code.startswith("JOIN-")
