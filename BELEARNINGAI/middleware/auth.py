"""Middleware xác thực JWT (placeholder)."""
from typing import Optional

from fastapi import HTTPException, Request, status

from utils.security import decode_token


async def get_current_user(request: Request) -> dict:
    """Giải mã access token từ header Authorization.

    Trả về payload (sub, role, session_id). Hiện tại chỉ làm nhiệm vụ decode cơ bản,
    cần bổ sung truy vấn DB, kiểm tra revoke khi triển khai thực tế.
    """

    auth_header: Optional[str] = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Thiếu token")

    token = auth_header.replace("Bearer ", "", 1).strip()
    payload = decode_token(token)
    return payload
