"""
Integration Tests - Courses Management

Test suite cho course CRUD operations và workflows.
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def instructor_token(client: AsyncClient):
    """Fixture to get instructor token"""
    # Register instructor
    await client.post(
        "/auth/register",
        json={
            "email": "instructor_course@test.com",
            "password": "Instructor123!",
            "full_name": "Course Instructor",
            "role": "instructor"
        }
    )
    
    # Login
    response = await client.post(
        "/auth/login",
        json={
            "email": "instructor_course@test.com",
            "password": "Instructor123!"
        }
    )
    
    return response.json()["access_token"]


@pytest.fixture
async def student_token(client: AsyncClient):
    """Fixture to get student token"""
    # Register student
    await client.post(
        "/auth/register",
        json={
            "email": "student_course@test.com",
            "password": "Student123!",
            "full_name": "Course Student",
            "role": "student"
        }
    )
    
    # Login
    response = await client.post(
        "/auth/login",
        json={
            "email": "student_course@test.com",
            "password": "Student123!"
        }
    )
    
    return response.json()["access_token"]


class TestCourseCreation:
    """Test course creation"""
    
    @pytest.mark.asyncio
    async def test_instructor_can_create_course(self, client: AsyncClient, instructor_token: str):
        """Test instructor can create course"""
        response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Python Fundamentals",
                "description": "Learn Python from scratch",
                "level": "beginner",
                "category": "programming",
                "tags": ["python", "programming", "beginner"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Python Fundamentals"
        assert data["level"] == "beginner"
        assert data["status"] == "draft"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_student_cannot_create_course(self, client: AsyncClient, student_token: str):
        """Test student cannot create course"""
        response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "title": "Unauthorized Course",
                "description": "This should fail",
                "level": "beginner",
                "category": "programming"
            }
        )
        
        assert response.status_code == 403  # Forbidden
    
    @pytest.mark.asyncio
    async def test_create_course_with_chapters(self, client: AsyncClient, instructor_token: str):
        """Test creating course with chapters"""
        response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Complete Python Course",
                "description": "Comprehensive Python course",
                "level": "intermediate",
                "category": "programming",
                "chapters": [
                    {
                        "title": "Introduction",
                        "description": "Getting started with Python",
                        "order": 1,
                        "lessons": [
                            {
                                "title": "What is Python?",
                                "content": "Python is a programming language...",
                                "order": 1,
                                "duration_minutes": 15
                            }
                        ]
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["chapters"]) == 1
        assert len(data["chapters"][0]["lessons"]) == 1


class TestCourseRetrieval:
    """Test course retrieval"""
    
    @pytest.mark.asyncio
    async def test_list_courses(self, client: AsyncClient):
        """Test listing courses"""
        response = await client.get("/courses")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_get_course_by_id(self, client: AsyncClient, instructor_token: str):
        """Test getting course by ID"""
        # Create course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Test Course",
                "description": "Test Description",
                "level": "beginner",
                "category": "test"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # Get course
        response = await client.get(f"/courses/{course_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
        assert data["title"] == "Test Course"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_course(self, client: AsyncClient):
        """Test getting non-existent course returns 404"""
        response = await client.get("/courses/nonexistent-id-12345")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_filter_courses_by_level(self, client: AsyncClient):
        """Test filtering courses by level"""
        response = await client.get("/courses?level=beginner")
        
        assert response.status_code == 200
        data = response.json()
        # All courses should be beginner level
        for course in data["items"]:
            assert course["level"] == "beginner"
    
    @pytest.mark.asyncio
    async def test_search_courses(self, client: AsyncClient):
        """Test searching courses"""
        response = await client.get("/courses?search=Python")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)


class TestCourseUpdate:
    """Test course updates"""
    
    @pytest.mark.asyncio
    async def test_instructor_can_update_own_course(self, client: AsyncClient, instructor_token: str):
        """Test instructor can update their own course"""
        # Create course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Original Title",
                "description": "Original Description",
                "level": "beginner",
                "category": "test"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # Update course
        response = await client.put(
            f"/courses/{course_id}",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Updated Title",
                "description": "Updated Description",
                "level": "intermediate"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
        assert data["level"] == "intermediate"
    
    @pytest.mark.asyncio
    async def test_add_chapter_to_course(self, client: AsyncClient, instructor_token: str):
        """Test adding chapter to course"""
        # Create course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Course for Chapters",
                "description": "Test",
                "level": "beginner",
                "category": "test"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # Add chapter
        response = await client.post(
            f"/courses/{course_id}/chapters",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "New Chapter",
                "description": "Chapter description",
                "order": 1
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Chapter"


class TestCourseDelete:
    """Test course deletion"""
    
    @pytest.mark.asyncio
    async def test_instructor_can_delete_own_course(self, client: AsyncClient, instructor_token: str):
        """Test instructor can delete their own course"""
        # Create course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Course to Delete",
                "description": "Will be deleted",
                "level": "beginner",
                "category": "test"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # Delete course
        response = await client.delete(
            f"/courses/{course_id}",
            headers={"Authorization": f"Bearer {instructor_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify course is deleted
        get_response = await client.get(f"/courses/{course_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_student_cannot_delete_course(self, client: AsyncClient, instructor_token: str, student_token: str):
        """Test student cannot delete course"""
        # Instructor creates course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Protected Course",
                "description": "Cannot be deleted by student",
                "level": "beginner",
                "category": "test"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # Student tries to delete
        response = await client.delete(
            f"/courses/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 403


class TestCourseEnrollment:
    """Test course enrollment"""
    
    @pytest.mark.asyncio
    async def test_student_can_enroll(self, client: AsyncClient, instructor_token: str, student_token: str):
        """Test student can enroll in published course"""
        # Create and publish course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Enrollable Course",
                "description": "Course for enrollment",
                "level": "beginner",
                "category": "test",
                "status": "published"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # Student enrolls
        response = await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == course_id
        assert data["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_cannot_enroll_twice(self, client: AsyncClient, instructor_token: str, student_token: str):
        """Test student cannot enroll in same course twice"""
        # Create course
        create_response = await client.post(
            "/courses",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Duplicate Enrollment Course",
                "description": "Test",
                "level": "beginner",
                "category": "test",
                "status": "published"
            }
        )
        
        course_id = create_response.json()["id"]
        
        # First enrollment
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Second enrollment should fail
        response = await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        assert response.status_code == 400
