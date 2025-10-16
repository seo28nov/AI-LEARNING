"""Tiện ích gửi email cho hệ thống."""
import secrets
from datetime import datetime, timedelta, timezone

from config.config import get_settings

_settings = get_settings()


def generate_verification_token() -> str:
    """Tạo token xác thực email ngẫu nhiên."""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Tạo token reset mật khẩu."""
    return secrets.token_urlsafe(32)


def get_token_expiry(hours: int = 24) -> datetime:
    """Tính thời gian hết hạn token."""
    return datetime.now(timezone.utc) + timedelta(hours=hours)


async def send_verification_email(email: str, token: str, user_name: str) -> bool:
    """Gửi email xác thực tài khoản.
    
    Args:
        email: Email người nhận
        token: Token xác thực
        user_name: Tên người dùng
        
    Returns:
        True nếu gửi thành công
    """
    # TODO: Tích hợp SendGrid hoặc SMTP service
    # Hiện tại chỉ log để phát triển
    verification_url = f"{_settings.frontend_url}/verify-email?token={token}"
    
    print(f"""
    ====== EMAIL VERIFICATION ======
    To: {email}
    Subject: Xác thực tài khoản AI Learning Platform
    
    Xin chào {user_name},
    
    Vui lòng click vào link dưới đây để xác thực tài khoản:
    {verification_url}
    
    Link có hiệu lực trong 24 giờ.
    
    Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email.
    ================================
    """)
    
    return True


async def send_reset_password_email(email: str, token: str, user_name: str) -> bool:
    """Gửi email reset mật khẩu.
    
    Args:
        email: Email người nhận
        token: Token reset
        user_name: Tên người dùng
        
    Returns:
        True nếu gửi thành công
    """
    # TODO: Tích hợp SendGrid hoặc SMTP service
    reset_url = f"{_settings.frontend_url}/reset-password?token={token}"
    
    print(f"""
    ====== PASSWORD RESET ======
    To: {email}
    Subject: Đặt lại mật khẩu AI Learning Platform
    
    Xin chào {user_name},
    
    Bạn đã yêu cầu đặt lại mật khẩu. Click vào link dưới đây:
    {reset_url}
    
    Link có hiệu lực trong 1 giờ.
    
    Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email.
    ============================
    """)
    
    return True


async def send_welcome_email(email: str, user_name: str) -> bool:
    """Gửi email chào mừng sau khi xác thực thành công.
    
    Args:
        email: Email người nhận
        user_name: Tên người dùng
        
    Returns:
        True nếu gửi thành công
    """
    print(f"""
    ====== WELCOME EMAIL ======
    To: {email}
    Subject: Chào mừng đến với AI Learning Platform
    
    Xin chào {user_name},
    
    Chúc mừng bạn đã xác thực tài khoản thành công!
    
    Bắt đầu hành trình học tập của bạn ngay hôm nay.
    ===========================
    """)
    
    return True
