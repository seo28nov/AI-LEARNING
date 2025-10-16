"""Dịch vụ xử lý thông tin người dùng."""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status

from models.models import UserDocument, UserResponse, UserRole
from utils.security import hash_password


async def get_user_profile(user_id: str) -> UserResponse:
    """Lấy thông tin user theo ID.
    
    Args:
        user_id: ID người dùng
        
    Returns:
        Thông tin người dùng
    """
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def get_user_by_email(email: str) -> Optional[UserResponse]:
    """Tìm user theo email.
    
    Args:
        email: Email người dùng
        
    Returns:
        Thông tin người dùng hoặc None
    """
    user = await UserDocument.find_one(UserDocument.email == email.lower())
    if user is None:
        return None
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def update_user_profile(user_id: str, update_data: dict) -> UserResponse:
    """Cập nhật thông tin hồ sơ người dùng.
    
    Args:
        user_id: ID người dùng
        update_data: Dữ liệu cập nhật
        
    Returns:
        Thông tin người dùng sau khi cập nhật
    """
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    # Chỉ cho phép cập nhật một số trường
    allowed_fields = {"full_name", "avatar_url", "profile", "preferences"}
    
    for field, value in update_data.items():
        if field in allowed_fields and hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def change_user_password(user_id: str, current_password: str, new_password: str) -> bool:
    """Đổi mật khẩu người dùng.
    
    Args:
        user_id: ID người dùng
        current_password: Mật khẩu hiện tại
        new_password: Mật khẩu mới
        
    Returns:
        True nếu thành công
    """
    from utils.security import verify_password
    
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    # Xác thực mật khẩu hiện tại
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không đúng"
        )
    
    # Validate mật khẩu mới
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải có ít nhất 8 ký tự"
        )
    
    # Cập nhật mật khẩu
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    return True


async def list_users(
    skip: int = 0,
    limit: int = 10,
    role: Optional[UserRole] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[List[UserResponse], int]:
    """Lấy danh sách người dùng với phân trang và filter.
    
    Args:
        skip: Số lượng bỏ qua
        limit: Số lượng tối đa trả về
        role: Lọc theo vai trò
        status: Lọc theo trạng thái
        search: Tìm kiếm theo tên hoặc email
        
    Returns:
        Tuple (danh sách users, tổng số)
    """
    # Xây dựng query
    query_conditions = []
    
    if role:
        query_conditions.append(UserDocument.role == role)
    
    if status:
        query_conditions.append(UserDocument.status == status)
    
    if search:
        # Tìm kiếm trong tên hoặc email (case insensitive)
        query_conditions.append(
            {"$or": [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]}
        )
    
    # Query với conditions
    if query_conditions:
        query = UserDocument.find(*query_conditions)
    else:
        query = UserDocument.find_all()
    
    # Đếm tổng số
    total = await query.count()
    
    # Lấy dữ liệu với pagination
    users = await query.skip(skip).limit(limit).to_list()
    
    # Convert sang response schema
    user_responses = []
    for user in users:
        payload = user.model_dump(by_alias=True, exclude={"password_hash"})
        payload["_id"] = str(user.id)
        user_responses.append(UserResponse.model_validate(payload))
    
    return user_responses, total


async def deactivate_user(user_id: str, admin_id: str) -> UserResponse:
    """Vô hiệu hóa tài khoản người dùng (chỉ admin).
    
    Args:
        user_id: ID người dùng cần vô hiệu hóa
        admin_id: ID admin thực hiện
        
    Returns:
        Thông tin người dùng sau khi vô hiệu hóa
    """
    # Kiểm tra admin
    admin = await UserDocument.get(admin_id)
    if admin is None or admin.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền vô hiệu hóa tài khoản"
        )
    
    # Lấy user cần vô hiệu hóa
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    # Không cho phép vô hiệu hóa chính mình
    if str(user.id) == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể vô hiệu hóa chính mình"
        )
    
    # Vô hiệu hóa
    user.is_active = False
    user.status = "suspended"
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def activate_user(user_id: str, admin_id: str) -> UserResponse:
    """Kích hoạt lại tài khoản người dùng (chỉ admin).
    
    Args:
        user_id: ID người dùng cần kích hoạt
        admin_id: ID admin thực hiện
        
    Returns:
        Thông tin người dùng sau khi kích hoạt
    """
    # Kiểm tra admin
    admin = await UserDocument.get(admin_id)
    if admin is None or admin.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền kích hoạt tài khoản"
        )
    
    # Lấy user cần kích hoạt
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    # Kích hoạt
    user.is_active = True
    user.status = "active"
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)


async def update_user_role(user_id: str, new_role: UserRole, admin_id: str) -> UserResponse:
    """Thay đổi vai trò người dùng (chỉ admin).
    
    Args:
        user_id: ID người dùng
        new_role: Vai trò mới
        admin_id: ID admin thực hiện
        
    Returns:
        Thông tin người dùng sau khi cập nhật
    """
    # Kiểm tra admin
    admin = await UserDocument.get(admin_id)
    if admin is None or admin.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền thay đổi vai trò"
        )
    
    # Lấy user
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    # Cập nhật vai trò
    user.role = new_role
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    payload = user.model_dump(by_alias=True, exclude={"password_hash"})
    payload["_id"] = str(user.id)
    return UserResponse.model_validate(payload)
