"""Controller xác thực người dùng."""
from fastapi import Request

from models.models import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from schemas.common import MessageResponse
from services.auth_service import login, logout, refresh_token, register


async def handle_login(payload: LoginRequest, request: Request) -> TokenResponse:
    """Xử lý luồng đăng nhập."""

    return await login(payload, request)


async def handle_register(payload: RegisterRequest) -> UserResponse:
    """Xử lý đăng ký tài khoản."""

    return await register(payload)


async def handle_refresh(payload: RefreshRequest, request: Request) -> TokenResponse:
    """Xử lý refresh token."""

    return await refresh_token(payload, request)


async def handle_logout(payload: RefreshRequest, request: Request) -> None:
    """Xử lý thu hồi phiên đăng nhập."""

    await logout(payload, request)


async def handle_get_profile(current_user: dict) -> MessageResponse:
    """Placeholder trả thông tin người dùng hiện tại."""

    user_id = current_user.get("sub", "unknown")
    return MessageResponse(message=f"Placeholder: thông tin người dùng {user_id}")


async def handle_update_profile(payload: dict, current_user: dict) -> MessageResponse:
    """Placeholder cập nhật hồ sơ người dùng."""

    _ = payload, current_user
    return MessageResponse(message="Placeholder: cập nhật hồ sơ thành công")


async def handle_update_password(payload: dict, current_user: dict) -> MessageResponse:
    """Placeholder đổi mật khẩu người dùng."""

    _ = payload, current_user
    return MessageResponse(message="Placeholder: mật khẩu đã được đổi")


async def handle_forgot_password(payload: dict) -> MessageResponse:
    """Placeholder gửi email quên mật khẩu."""

    _ = payload
    return MessageResponse(message="Placeholder: đã gửi hướng dẫn đặt lại mật khẩu")


async def handle_reset_password(payload: dict) -> MessageResponse:
    """Placeholder đặt lại mật khẩu từ token."""

    _ = payload
    return MessageResponse(message="Placeholder: mật khẩu đã được đặt lại")


async def handle_verify_email(payload: dict) -> MessageResponse:
    """Placeholder xác thực email người dùng."""

    _ = payload
    return MessageResponse(message="Placeholder: email đã được xác thực")
