"""Router xác thực."""
from fastapi import APIRouter, Depends, Request, Response

from config.config import get_settings
from controllers.auth_controller import (
    handle_forgot_password,
    handle_get_profile,
    handle_login,
    handle_logout,
    handle_refresh,
    handle_register,
    handle_resend_verification,
    handle_reset_password,
    handle_update_password,
    handle_update_profile,
    handle_verify_email,
)
from middleware.auth import get_current_user
from models.models import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from schemas.common import MessageResponse

settings = get_settings()
router = APIRouter(tags=["auth"])


def _set_refresh_cookie(response: Response, token: TokenResponse) -> None:
    """Thiết lập cookie refresh token."""

    secure = settings.environment != "development"
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=token.refresh_expires_in,
        path="/api/v1/auth",
    )


@router.post("/login", response_model=TokenResponse, summary="Đăng nhập")
async def login_route(payload: LoginRequest, request: Request, response: Response) -> TokenResponse:
    """Đăng nhập user."""

    tokens = await handle_login(payload, request)
    _set_refresh_cookie(response, tokens)
    return tokens


@router.post("/register", response_model=UserResponse, summary="Đăng ký tài khoản")
async def register_route(payload: RegisterRequest) -> UserResponse:
    """Đăng ký user mới."""

    return await handle_register(payload)


@router.post("/refresh", response_model=TokenResponse, summary="Làm mới token")
async def refresh_route(payload: RefreshRequest, request: Request, response: Response) -> TokenResponse:
    """Refresh token."""

    tokens = await handle_refresh(payload, request)
    _set_refresh_cookie(response, tokens)
    return tokens


@router.post("/logout", status_code=204, summary="Đăng xuất")
async def logout_route(payload: RefreshRequest, request: Request, response: Response) -> None:
    """Thu hồi refresh token hiện tại."""

    await handle_logout(payload, request)
    response.delete_cookie("refresh_token", path="/api/v1/auth")


@router.get("/me", summary="Thông tin người dùng hiện tại")
async def me_route(current_user: dict = Depends(get_current_user)) -> dict:
    """Trả thông tin user."""

    return await handle_get_profile(current_user)


@router.patch("/me", summary="Cập nhật hồ sơ")
async def update_profile_route(payload: dict, current_user: dict = Depends(get_current_user)) -> dict:
    """Cập nhật hồ sơ user."""

    return await handle_update_profile(payload, current_user)


@router.patch("/me/password", response_model=MessageResponse, summary="Đổi mật khẩu")
async def update_password_route(payload: dict, current_user: dict = Depends(get_current_user)) -> MessageResponse:
    """Đổi mật khẩu user (placeholder)."""

    return await handle_update_password(payload, current_user)


@router.post("/forgot-password", response_model=MessageResponse, summary="Yêu cầu quên mật khẩu")
async def forgot_password_route(payload: dict) -> MessageResponse:
    """Gửi email quên mật khẩu (placeholder)."""

    return await handle_forgot_password(payload)


@router.post("/reset-password", response_model=MessageResponse, summary="Đặt lại mật khẩu")
async def reset_password_route(payload: dict) -> MessageResponse:
    """Đặt lại mật khẩu (placeholder)."""

    return await handle_reset_password(payload)


@router.post("/verify-email", response_model=UserResponse, summary="Xác thực email")
async def verify_email_route(payload: dict) -> UserResponse:
    """Xác thực email bằng token."""
    
    return await handle_verify_email(payload)


@router.post("/resend-verification", response_model=MessageResponse, summary="Gửi lại email xác thực")
async def resend_verification_route(current_user: dict = Depends(get_current_user)) -> MessageResponse:
    """Gửi lại email xác thực cho user hiện tại."""
    
    user_id = current_user.get("sub")
    return await handle_resend_verification(user_id)
