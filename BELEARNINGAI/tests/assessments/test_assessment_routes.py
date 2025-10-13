"""Kiểm thử placeholder cho router assessments."""
import pytest


@pytest.mark.skip(reason="placeholder: sẽ cập nhật khi triển khai logic thực")
def test_skill_test_endpoint(client):
    """Đảm bảo endpoint skill-test hoạt động khi có current_user."""

    response = client.post(
        "/api/v1/assessments/skill-test",
        json={"answers": [1, 0, 2]},
    )
    assert response.status_code == 200
