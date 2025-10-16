"""Controller xác thực người dùng."""
from fastapi import Request, HTTPException, status

from models.models import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from schemas.common import MessageResponse
from services.auth_service import (
    login,
    logout,
    refresh_token,
    register,
    request_email_verification,
    request_password_reset,
    reset_password,
    verify_email,
)
from services.user_service import (
    get_user_profile,
    update_user_profile,
    change_user_password
)


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


async def handle_get_profile(current_user: dict) -> dict:
    """Lấy thông tin người dùng hiện tại."""

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không xác định được user"
        )
    
    return await get_user_profile(user_id)


async def handle_update_profile(payload: dict, current_user: dict) -> dict:
    """Cập nhật hồ sơ người dùng."""

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không xác định được user"
        )
    
    return await update_user_profile(user_id, payload)


async def handle_update_password(payload: dict, current_user: dict) -> MessageResponse:
    """Đổi mật khẩu người dùng."""

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không xác định được user"
        )
    
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu mật khẩu hiện tại hoặc mật khẩu mới"
        )
    
    await change_user_password(user_id, current_password, new_password)
    return MessageResponse(message="Mật khẩu đã được đổi thành công")


async def handle_forgot_password(payload: dict) -> MessageResponse:
    """Gửi email reset mật khẩu."""
    
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email không hợp lệ"
        )
    
    await request_password_reset(email)
    return MessageResponse(message="Nếu email tồn tại, link reset mật khẩu đã được gửi")


async def handle_reset_password(payload: dict) -> MessageResponse:
    """Đặt lại mật khẩu từ token."""
    
    token = payload.get("token")
    new_password = payload.get("new_password")
    
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token hoặc mật khẩu mới không hợp lệ"
        )
    
    await reset_password(token, new_password)
    return MessageResponse(message="Mật khẩu đã được đặt lại thành công. Vui lòng đăng nhập lại")


async def handle_verify_email(payload: dict) -> UserResponse:
    """Xác thực email người dùng."""
    
    token = payload.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token không hợp lệ"
        )
    
    return await verify_email(token)


async def handle_resend_verification(user_id: str) -> MessageResponse:
    """Gửi lại email xác thực."""
    
    await request_email_verification(user_id)
    return MessageResponse(message="Email xác thực đã được gửi lại")
