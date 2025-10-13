"""Kiểm tra endpoint health cơ bản."""

def test_health_endpoint(client) -> None:
    """Đảm bảo /health trả về trạng thái ok."""

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
