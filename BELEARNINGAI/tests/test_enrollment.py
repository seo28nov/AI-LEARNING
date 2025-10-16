"""
Integration Tests - Enrollment & Progress Tracking

Test suite cho enrollment system và progress tracking.
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def course_setup(client: AsyncClient):
    """Fixture: Create instructor, course, and student"""
    # Register instructor
    await client.post(
        "/auth/register",
        json={
            "email": "instructor_enroll@test.com",
            "password": "Instructor123!",
            "full_name": "Enrollment Instructor",
            "role": "instructor"
        }
    )
    
    instructor_login = await client.post(
        "/auth/login",
        json={
            "email": "instructor_enroll@test.com",
            "password": "Instructor123!"
        }
    )
    instructor_token = instructor_login.json()["access_token"]
    
    # Create course with chapters
    course_response = await client.post(
        "/courses",
        headers={"Authorization": f"Bearer {instructor_token}"},
        json={
            "title": "Progress Tracking Course",
            "description": "Track your progress",
            "level": "beginner",
            "category": "programming",
            "status": "published",
            "chapters": [
                {
                    "title": "Chapter 1",
                    "description": "First chapter",
                    "order": 1,
                    "lessons": [
                        {
                            "title": "Lesson 1.1",
                            "content": "First lesson content",
                            "order": 1,
                            "duration_minutes": 10
                        },
                        {
                            "title": "Lesson 1.2",
                            "content": "Second lesson content",
                            "order": 2,
                            "duration_minutes": 15
                        }
                    ]
                },
                {
                    "title": "Chapter 2",
                    "description": "Second chapter",
                    "order": 2,
                    "lessons": [
                        {
                            "title": "Lesson 2.1",
                            "content": "Third lesson content",
                            "order": 1,
                            "duration_minutes": 20
                        }
                    ]
                }
            ]
        }
    )
    course_id = course_response.json()["id"]
    chapters = course_response.json()["chapters"]
    
    # Register student
    await client.post(
        "/auth/register",
        json={
            "email": "student_enroll@test.com",
            "password": "Student123!",
            "full_name": "Enrollment Student",
            "role": "student"
        }
    )
    
    student_login = await client.post(
        "/auth/login",
        json={
            "email": "student_enroll@test.com",
            "password": "Student123!"
        }
    )
    student_token = student_login.json()["access_token"]
    
    return {
        "instructor_token": instructor_token,
        "student_token": student_token,
        "course_id": course_id,
        "chapters": chapters
    }


class TestEnrollment:
    """Test enrollment functionality"""
    
    @pytest.mark.asyncio
    async def test_student_can_enroll(self, client: AsyncClient, course_setup: dict):
        """Test student enrolling in course"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        response = await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == course_id
        assert data["status"] == "active"
        assert "enrolled_at" in data
    
    @pytest.mark.asyncio
    async def test_cannot_enroll_twice(self, client: AsyncClient, course_setup: dict):
        """Test duplicate enrollment prevention"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # First enrollment
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Second enrollment (should fail)
        response = await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        assert response.status_code == 400  # Already enrolled
    
    @pytest.mark.asyncio
    async def test_list_my_enrollments(self, client: AsyncClient, course_setup: dict):
        """Test listing user's enrollments"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # List
        response = await client.get(
            "/enrollments/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any(e["course_id"] == course_id for e in data["items"])
    
    @pytest.mark.asyncio
    async def test_get_enrollment_details(self, client: AsyncClient, course_setup: dict):
        """Test getting enrollment details"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        enroll_response = await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        enrollment_id = enroll_response.json()["id"]
        
        # Get details
        response = await client.get(
            f"/enrollments/{enrollment_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == enrollment_id
        assert data["course_id"] == course_id
    
    @pytest.mark.asyncio
    async def test_unenroll_from_course(self, client: AsyncClient, course_setup: dict):
        """Test unenrolling from course"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        enroll_response = await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        enrollment_id = enroll_response.json()["id"]
        
        # Unenroll
        response = await client.delete(
            f"/enrollments/{enrollment_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 204


class TestProgressTracking:
    """Test progress tracking functionality"""
    
    @pytest.mark.asyncio
    async def test_mark_lesson_complete(self, client: AsyncClient, course_setup: dict):
        """Test marking lesson as complete"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll first
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Get lesson ID
        lesson_id = course_setup["chapters"][0]["lessons"][0]["id"]
        
        # Mark complete
        response = await client.post(
            "/progress/lessons/complete",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "course_id": course_id,
                "lesson_id": lesson_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["lesson_id"] == lesson_id
        assert data["completed"]
    
    @pytest.mark.asyncio
    async def test_get_course_progress(self, client: AsyncClient, course_setup: dict):
        """Test getting course progress"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Complete one lesson
        lesson_id = course_setup["chapters"][0]["lessons"][0]["id"]
        await client.post(
            "/progress/lessons/complete",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "course_id": course_id,
                "lesson_id": lesson_id
            }
        )
        
        # Get progress
        response = await client.get(
            f"/progress/courses/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "progress_percentage" in data
        assert data["progress_percentage"] > 0
    
    @pytest.mark.asyncio
    async def test_progress_calculation(self, client: AsyncClient, course_setup: dict):
        """Test progress percentage calculation"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Complete all lessons in chapter 1 (2 out of 3 total lessons)
        for lesson in course_setup["chapters"][0]["lessons"]:
            await client.post(
                "/progress/lessons/complete",
                headers={"Authorization": f"Bearer {student_token}"},
                json={
                    "course_id": course_id,
                    "lesson_id": lesson["id"]
                }
            )
        
        # Get progress
        response = await client.get(
            f"/progress/courses/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        data = response.json()
        # 2 out of 3 lessons = ~66.67%
        assert data["progress_percentage"] >= 60
        assert data["progress_percentage"] <= 70
    
    @pytest.mark.asyncio
    async def test_complete_entire_course(self, client: AsyncClient, course_setup: dict):
        """Test completing entire course"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Complete all lessons
        for chapter in course_setup["chapters"]:
            for lesson in chapter["lessons"]:
                await client.post(
                    "/progress/lessons/complete",
                    headers={"Authorization": f"Bearer {student_token}"},
                    json={
                        "course_id": course_id,
                        "lesson_id": lesson["id"]
                    }
                )
        
        # Get progress
        response = await client.get(
            f"/progress/courses/{course_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        data = response.json()
        assert data["progress_percentage"] == 100
        assert data["completed"]


class TestEnrollmentStatistics:
    """Test enrollment statistics"""
    
    @pytest.mark.asyncio
    async def test_instructor_can_see_course_enrollments(self, client: AsyncClient, course_setup: dict):
        """Test instructor viewing course enrollments"""
        instructor_token = course_setup["instructor_token"]
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Student enrolls
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Instructor views enrollments
        response = await client.get(
            f"/courses/{course_id}/enrollments",
            headers={"Authorization": f"Bearer {instructor_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
    
    @pytest.mark.asyncio
    async def test_enrollment_count(self, client: AsyncClient, course_setup: dict):
        """Test enrollment count tracking"""
        student_token = course_setup["student_token"]
        course_id = course_setup["course_id"]
        
        # Enroll
        await client.post(
            "/enrollments",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"course_id": course_id}
        )
        
        # Get course details
        response = await client.get(f"/courses/{course_id}")
        
        data = response.json()
        assert "enrollment_count" in data or "enrollments" in data
