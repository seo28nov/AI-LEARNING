"""
Integration Tests - Authentication & Authorization

Test suite cho auth flow, JWT tokens, và RBAC.
"""
import pytest
from httpx import AsyncClient


class TestAuthentication:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_student(self, client: AsyncClient):
        """Test student registration"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "student@test.com",
                "password": "Student123!",
                "full_name": "Test Student",
                "role": "student"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "student@test.com"
        assert data["role"] == "student"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_instructor(self, client: AsyncClient):
        """Test instructor registration"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "instructor@test.com",
                "password": "Instructor123!",
                "full_name": "Test Instructor",
                "role": "instructor"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "instructor"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test duplicate email registration fails"""
        # Register first user
        await client.post(
            "/auth/register",
            json={
                "email": "duplicate@test.com",
                "password": "Test123!",
                "full_name": "First User",
                "role": "student"
            }
        )
        
        # Try to register with same email
        response = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@test.com",
                "password": "Test456!",
                "full_name": "Second User",
                "role": "student"
            }
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login"""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "login@test.com",
                "password": "Login123!",
                "full_name": "Login User",
                "role": "student"
            }
        )
        
        # Login
        response = await client.post(
            "/auth/login",
            json={
                "email": "login@test.com",
                "password": "Login123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password fails"""
        # Register user
        await client.post(
            "/auth/register",
            json={
                "email": "wrongpass@test.com",
                "password": "Correct123!",
                "full_name": "Test User",
                "role": "student"
            }
        )
        
        # Login with wrong password
        response = await client.post(
            "/auth/login",
            json={
                "email": "wrongpass@test.com",
                "password": "Wrong123!"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails"""
        response = await client.post(
            "/auth/login",
            json={
                "email": "notexist@test.com",
                "password": "Test123!"
            }
        )
        
        assert response.status_code == 401


class TestAuthorization:
    """Test RBAC and protected endpoints"""
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test protected endpoint without token fails"""
        response = await client.get("/users/me")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_token(self, client: AsyncClient):
        """Test protected endpoint with valid token succeeds"""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "protected@test.com",
                "password": "Protected123!",
                "full_name": "Protected User",
                "role": "student"
            }
        )
        
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "protected@test.com",
                "password": "Protected123!"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "protected@test.com"
    
    @pytest.mark.asyncio
    async def test_student_cannot_access_admin_endpoint(self, client: AsyncClient):
        """Test student cannot access admin endpoints"""
        # Register student
        await client.post(
            "/auth/register",
            json={
                "email": "student_rbac@test.com",
                "password": "Student123!",
                "full_name": "Student RBAC",
                "role": "student"
            }
        )
        
        # Login as student
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "student_rbac@test.com",
                "password": "Student123!"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Try to access admin endpoint
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403  # Forbidden
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, client: AsyncClient):
        """Test token refresh works"""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "refresh@test.com",
                "password": "Refresh123!",
                "full_name": "Refresh User",
                "role": "student"
            }
        )
        
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "refresh@test.com",
                "password": "Refresh123!"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestPasswordValidation:
    """Test password validation rules"""
    
    @pytest.mark.asyncio
    async def test_weak_password_rejected(self, client: AsyncClient):
        """Test weak passwords are rejected"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "weak@test.com",
                "password": "weak",  # Too weak
                "full_name": "Weak Password",
                "role": "student"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_strong_password_accepted(self, client: AsyncClient):
        """Test strong passwords are accepted"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "strong@test.com",
                "password": "StrongPass123!@#",
                "full_name": "Strong Password",
                "role": "student"
            }
        )
        
        assert response.status_code == 201


class TestEmailValidation:
    """Test email validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_email_rejected(self, client: AsyncClient):
        """Test invalid email format is rejected"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "invalid-email",  # Invalid format
                "password": "Test123!",
                "full_name": "Invalid Email",
                "role": "student"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_valid_email_accepted(self, client: AsyncClient):
        """Test valid email format is accepted"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "valid.email@example.com",
                "password": "Test123!",
                "full_name": "Valid Email",
                "role": "student"
            }
        )
        
        assert response.status_code == 201
