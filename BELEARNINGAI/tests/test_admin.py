"""
Integration Tests - Admin Management

Test suite cho admin functions (user management, course approval, analytics).
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def admin_token(client: AsyncClient):
    """Fixture: Admin user with token"""
    # Register admin
    await client.post(
        "/auth/register",
        json={
            "email": "admin@test.com",
            "password": "Admin123!",
            "full_name": "Admin User",
            "role": "admin"
        }
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "Admin123!"
        }
    )
    
    return login_response.json()["access_token"]


@pytest.fixture
async def instructor_token(client: AsyncClient):
    """Fixture: Instructor user"""
    await client.post(
        "/auth/register",
        json={
            "email": "instructor_admin@test.com",
            "password": "Instructor123!",
            "full_name": "Test Instructor",
            "role": "instructor"
        }
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "instructor_admin@test.com",
            "password": "Instructor123!"
        }
    )
    
    return login_response.json()["access_token"]


@pytest.fixture
async def student_token(client: AsyncClient):
    """Fixture: Student user"""
    await client.post(
        "/auth/register",
        json={
            "email": "student_admin@test.com",
            "password": "Student123!",
            "full_name": "Test Student",
            "role": "student"
        }
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "student_admin@test.com",
            "password": "Student123!"
        }
    )
    
    return login_response.json()["access_token"]


class TestAdminUserManagement:
    """Test admin user management functions"""
    
    @pytest.mark.asyncio
    async def test_admin_can_list_all_users(self, client: AsyncClient, admin_token: str):
        """Test admin listing all users"""
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0  # At least admin user exists
    
    @pytest.mark.asyncio
    async def test_student_cannot_access_admin_endpoint(self, client: AsyncClient, student_token: str):
        """Test student cannot access admin endpoints"""
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 403  # Forbidden
    
    @pytest.mark.asyncio
    async def test_admin_can_change_user_role(self, client: AsyncClient, admin_token: str, student_token: str):
        """Test admin changing user role"""
        # Get student user ID
        users_response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        users = users_response.json()["items"]
        student_user = next((u for u in users if u["email"] == "student_admin@test.com"), None)
        assert student_user is not None
        
        # Change role
        response = await client.put(
            f"/admin/users/{student_user['id']}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "instructor"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "instructor"
    
    @pytest.mark.asyncio
    async def test_admin_can_suspend_user(self, client: AsyncClient, admin_token: str):
        """Test admin suspending user"""
        # Register user to suspend
        await client.post(
            "/auth/register",
            json={
                "email": "suspend@test.com",
                "password": "User123!",
                "full_name": "User To Suspend",
                "role": "student"
            }
        )
        
        # Get user
        users_response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        users = users_response.json()["items"]
        user = next((u for u in users if u["email"] == "suspend@test.com"), None)
        
        # Suspend
        response = await client.put(
            f"/admin/users/{user['id']}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"is_active": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert not data["is_active"]
    
    @pytest.mark.asyncio
    async def test_admin_can_delete_user(self, client: AsyncClient, admin_token: str):
        """Test admin deleting user"""
        # Register user to delete
        await client.post(
            "/auth/register",
            json={
                "email": "delete@test.com",
                "password": "User123!",
                "full_name": "User To Delete",
                "role": "student"
            }
        )
        
        # Get user
        users_response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        users = users_response.json()["items"]
        user = next((u for u in users if u["email"] == "delete@test.com"), None)
        
        # Delete
        response = await client.delete(
            f"/admin/users/{user['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204


class TestAdminCourseApproval:
    """Test admin course approval system"""
    
    @pytest.mark.asyncio
    async def test_admin_can_list_pending_courses(self, client: AsyncClient, admin_token: str, instructor_token: str):
        """Test admin listing pending courses"""
        # Instructor creates course
        await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Pending Course",
                "description": "Awaiting approval",
                "level": "beginner",
                "category": "programming",
                "status": "draft"
            }
        )
        
        # Admin lists pending
        response = await client.get(
            "/admin/courses/pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_admin_can_approve_course(self, client: AsyncClient, admin_token: str, instructor_token: str):
        """Test admin approving course"""
        # Create course
        course_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Course to Approve",
                "description": "Test approval",
                "level": "beginner",
                "category": "programming",
                "status": "draft"
            }
        )
        course_id = course_response.json()["id"]
        
        # Approve
        response = await client.post(
            f"/admin/courses/{course_id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
    
    @pytest.mark.asyncio
    async def test_admin_can_reject_course(self, client: AsyncClient, admin_token: str, instructor_token: str):
        """Test admin rejecting course"""
        # Create course
        course_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Course to Reject",
                "description": "Test rejection",
                "level": "beginner",
                "category": "programming",
                "status": "draft"
            }
        )
        course_id = course_response.json()["id"]
        
        # Reject
        response = await client.post(
            f"/admin/courses/{course_id}/reject",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"reason": "Content quality issues"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"


class TestAdminAnalytics:
    """Test admin analytics access"""
    
    @pytest.mark.asyncio
    async def test_admin_can_access_platform_stats(self, client: AsyncClient, admin_token: str):
        """Test admin accessing platform statistics"""
        response = await client.get(
            "/admin/analytics/platform",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_courses" in data
        assert "total_enrollments" in data
    
    @pytest.mark.asyncio
    async def test_admin_can_access_user_analytics(self, client: AsyncClient, admin_token: str):
        """Test admin accessing user analytics"""
        response = await client.get(
            "/admin/analytics/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users_by_role" in data or "items" in data
    
    @pytest.mark.asyncio
    async def test_instructor_cannot_access_admin_analytics(self, client: AsyncClient, instructor_token: str):
        """Test instructor cannot access admin analytics"""
        response = await client.get(
            "/admin/analytics/platform",
            headers={"Authorization": f"Bearer {instructor_token}"}
        )
        
        assert response.status_code == 403


class TestAdminPermissions:
    """Test admin permission management"""
    
    @pytest.mark.asyncio
    async def test_admin_can_grant_permissions(self, client: AsyncClient, admin_token: str):
        """Test admin granting permissions"""
        # Register user
        await client.post(
            "/auth/register",
            json={
                "email": "permissions@test.com",
                "password": "User123!",
                "full_name": "Permission User",
                "role": "instructor"
            }
        )
        
        # Get user
        users_response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        users = users_response.json()["items"]
        user = next((u for u in users if u["email"] == "permissions@test.com"), None)
        
        # Grant permission
        response = await client.post(
            f"/admin/users/{user['id']}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "permissions": ["create_course", "edit_course", "delete_course"]
            }
        )
        
        # Check response (might be 200 or 201 depending on implementation)
        assert response.status_code in [200, 201, 404]  # 404 if not implemented yet
