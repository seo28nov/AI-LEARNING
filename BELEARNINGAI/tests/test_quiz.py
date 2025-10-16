"""
Integration Tests - Quiz & Assessment

Test suite cho quiz creation, taking, và grading.
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def instructor_with_course(client: AsyncClient):
    """Fixture: Instructor with published course"""
    # Register instructor
    await client.post(
        "/auth/register",
        json={
            "email": "instructor_quiz@test.com",
            "password": "Instructor123!",
            "full_name": "Quiz Instructor",
            "role": "instructor"
        }
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "instructor_quiz@test.com",
            "password": "Instructor123!"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create course
    course_response = await client.post(
        "/courses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Python Quiz Course",
            "description": "Course with quizzes",
            "level": "beginner",
            "category": "programming",
            "status": "published"
        }
    )
    course_id = course_response.json()["id"]
    
    return {
        "instructor_token": token,
        "course_id": course_id
    }


@pytest.fixture
async def student_enrolled(client: AsyncClient, instructor_with_course: dict):
    """Fixture: Student enrolled in course"""
    # Register student
    await client.post(
        "/auth/register",
        json={
            "email": "student_quiz@test.com",
            "password": "Student123!",
            "full_name": "Quiz Student",
            "role": "student"
        }
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "student_quiz@test.com",
            "password": "Student123!"
        }
    )
    student_token = login_response.json()["access_token"]
    
    # Enroll in course
    await client.post(
        "/enrollments",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": instructor_with_course["course_id"]}
    )
    
    return {
        **instructor_with_course,
        "student_token": student_token
    }


class TestQuizCreation:
    """Test quiz creation by instructors"""
    
    @pytest.mark.asyncio
    async def test_instructor_can_create_quiz(self, client: AsyncClient, instructor_with_course: dict):
        """Test instructor creates quiz"""
        token = instructor_with_course["instructor_token"]
        course_id = instructor_with_course["course_id"]
        
        response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Python Basics Quiz",
                "description": "Test your Python knowledge",
                "course_id": course_id,
                "time_limit_minutes": 30,
                "passing_score": 70,
                "max_attempts": 3,
                "questions": [
                    {
                        "question_text": "What is Python?",
                        "question_type": "multiple_choice",
                        "points": 10,
                        "options": [
                            {"text": "A programming language", "is_correct": True},
                            {"text": "A snake", "is_correct": False},
                            {"text": "A database", "is_correct": False},
                            {"text": "An IDE", "is_correct": False}
                        ]
                    },
                    {
                        "question_text": "Is Python dynamically typed?",
                        "question_type": "true_false",
                        "points": 5,
                        "options": [
                            {"text": "True", "is_correct": True},
                            {"text": "False", "is_correct": False}
                        ]
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Python Basics Quiz"
        assert data["course_id"] == course_id
        assert len(data["questions"]) == 2
        assert data["time_limit_minutes"] == 30
        assert data["passing_score"] == 70
    
    @pytest.mark.asyncio
    async def test_student_cannot_create_quiz(self, client: AsyncClient, student_enrolled: dict):
        """Test student cannot create quiz"""
        token = student_enrolled["student_token"]
        course_id = student_enrolled["course_id"]
        
        response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Unauthorized Quiz",
                "course_id": course_id,
                "questions": []
            }
        )
        
        assert response.status_code == 403  # Forbidden
    
    @pytest.mark.asyncio
    async def test_create_quiz_with_essay_question(self, client: AsyncClient, instructor_with_course: dict):
        """Test creating quiz with essay question"""
        token = instructor_with_course["instructor_token"]
        course_id = instructor_with_course["course_id"]
        
        response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Python Essay Quiz",
                "course_id": course_id,
                "questions": [
                    {
                        "question_text": "Explain the difference between lists and tuples in Python.",
                        "question_type": "essay",
                        "points": 20
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["questions"][0]["question_type"] == "essay"


class TestQuizRetrieval:
    """Test quiz listing and retrieval"""
    
    @pytest.mark.asyncio
    async def test_list_course_quizzes(self, client: AsyncClient, instructor_with_course: dict):
        """Test listing quizzes for a course"""
        token = instructor_with_course["instructor_token"]
        course_id = instructor_with_course["course_id"]
        
        # Create multiple quizzes
        for i in range(3):
            await client.post(
                "/quizzes",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": f"Quiz {i+1}",
                    "course_id": course_id,
                    "questions": []
                }
            )
        
        # List quizzes
        response = await client.get(
            f"/courses/{course_id}/quizzes",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_quiz_by_id(self, client: AsyncClient, instructor_with_course: dict):
        """Test getting quiz details"""
        token = instructor_with_course["instructor_token"]
        course_id = instructor_with_course["course_id"]
        
        # Create quiz
        create_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Detailed Quiz",
                "course_id": course_id,
                "questions": [
                    {
                        "question_text": "Test question?",
                        "question_type": "multiple_choice",
                        "points": 10,
                        "options": [
                            {"text": "Answer 1", "is_correct": True},
                            {"text": "Answer 2", "is_correct": False}
                        ]
                    }
                ]
            }
        )
        quiz_id = create_response.json()["id"]
        
        # Get quiz
        response = await client.get(
            f"/quizzes/{quiz_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == quiz_id
        assert data["title"] == "Detailed Quiz"


class TestQuizTaking:
    """Test taking quizzes and submitting answers"""
    
    @pytest.mark.asyncio
    async def test_student_can_start_quiz_attempt(self, client: AsyncClient, student_enrolled: dict):
        """Test student starting quiz attempt"""
        instructor_token = student_enrolled["instructor_token"]
        student_token = student_enrolled["student_token"]
        course_id = student_enrolled["course_id"]
        
        # Create quiz
        quiz_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Attempt Quiz",
                "course_id": course_id,
                "questions": [
                    {
                        "question_text": "What is 2+2?",
                        "question_type": "multiple_choice",
                        "points": 10,
                        "options": [
                            {"text": "3", "is_correct": False},
                            {"text": "4", "is_correct": True},
                            {"text": "5", "is_correct": False}
                        ]
                    }
                ]
            }
        )
        quiz_id = quiz_response.json()["id"]
        
        # Start attempt
        response = await client.post(
            f"/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["quiz_id"] == quiz_id
        assert data["status"] == "in_progress"
        assert "started_at" in data
    
    @pytest.mark.asyncio
    async def test_submit_quiz_answers(self, client: AsyncClient, student_enrolled: dict):
        """Test submitting quiz answers"""
        instructor_token = student_enrolled["instructor_token"]
        student_token = student_enrolled["student_token"]
        course_id = student_enrolled["course_id"]
        
        # Create quiz
        quiz_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Submit Quiz",
                "course_id": course_id,
                "passing_score": 60,
                "questions": [
                    {
                        "question_text": "What is 2+2?",
                        "question_type": "multiple_choice",
                        "points": 10,
                        "options": [
                            {"text": "4", "is_correct": True},
                            {"text": "5", "is_correct": False}
                        ]
                    }
                ]
            }
        )
        quiz_id = quiz_response.json()["id"]
        question_id = quiz_response.json()["questions"][0]["id"]
        
        # Start attempt
        attempt_response = await client.post(
            f"/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        attempt_id = attempt_response.json()["id"]
        
        # Submit answers
        response = await client.post(
            f"/quizzes/attempts/{attempt_id}/submit",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "answers": [
                    {
                        "question_id": question_id,
                        "selected_option": "4"
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "score" in data
        assert data["score"] >= 0
    
    @pytest.mark.asyncio
    async def test_max_attempts_limit(self, client: AsyncClient, student_enrolled: dict):
        """Test max attempts limit enforcement"""
        instructor_token = student_enrolled["instructor_token"]
        student_token = student_enrolled["student_token"]
        course_id = student_enrolled["course_id"]
        
        # Create quiz with max 2 attempts
        quiz_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Limited Attempts Quiz",
                "course_id": course_id,
                "max_attempts": 2,
                "questions": [
                    {
                        "question_text": "Test?",
                        "question_type": "multiple_choice",
                        "points": 10,
                        "options": [
                            {"text": "A", "is_correct": True},
                            {"text": "B", "is_correct": False}
                        ]
                    }
                ]
            }
        )
        quiz_id = quiz_response.json()["id"]
        question_id = quiz_response.json()["questions"][0]["id"]
        
        # Attempt 1
        attempt1 = await client.post(
            f"/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        await client.post(
            f"/quizzes/attempts/{attempt1.json()['id']}/submit",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"answers": [{"question_id": question_id, "selected_option": "A"}]}
        )
        
        # Attempt 2
        attempt2 = await client.post(
            f"/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        await client.post(
            f"/quizzes/attempts/{attempt2.json()['id']}/submit",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"answers": [{"question_id": question_id, "selected_option": "A"}]}
        )
        
        # Attempt 3 (should fail)
        response = await client.post(
            f"/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 400  # Max attempts reached


class TestQuizGrading:
    """Test automatic grading"""
    
    @pytest.mark.asyncio
    async def test_automatic_grading_multiple_choice(self, client: AsyncClient, student_enrolled: dict):
        """Test automatic grading for multiple choice"""
        instructor_token = student_enrolled["instructor_token"]
        student_token = student_enrolled["student_token"]
        course_id = student_enrolled["course_id"]
        
        # Create quiz
        quiz_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {instructor_token}"},
            json={
                "title": "Grading Quiz",
                "course_id": course_id,
                "passing_score": 50,
                "questions": [
                    {
                        "question_text": "2+2=?",
                        "question_type": "multiple_choice",
                        "points": 50,
                        "options": [
                            {"text": "4", "is_correct": True},
                            {"text": "5", "is_correct": False}
                        ]
                    },
                    {
                        "question_text": "3+3=?",
                        "question_type": "multiple_choice",
                        "points": 50,
                        "options": [
                            {"text": "6", "is_correct": True},
                            {"text": "7", "is_correct": False}
                        ]
                    }
                ]
            }
        )
        quiz_id = quiz_response.json()["id"]
        questions = quiz_response.json()["questions"]
        
        # Start and submit (1 correct, 1 wrong)
        attempt = await client.post(
            f"/quizzes/{quiz_id}/attempts",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        submit_response = await client.post(
            f"/quizzes/attempts/{attempt.json()['id']}/submit",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "answers": [
                    {"question_id": questions[0]["id"], "selected_option": "4"},  # Correct
                    {"question_id": questions[1]["id"], "selected_option": "7"}   # Wrong
                ]
            }
        )
        
        data = submit_response.json()
        assert data["score"] == 50  # 50% correct
        assert data["passed"]  # passing_score = 50


class TestQuizManagement:
    """Test quiz update and delete"""
    
    @pytest.mark.asyncio
    async def test_instructor_can_update_quiz(self, client: AsyncClient, instructor_with_course: dict):
        """Test updating quiz"""
        token = instructor_with_course["instructor_token"]
        course_id = instructor_with_course["course_id"]
        
        # Create quiz
        create_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Original Quiz",
                "course_id": course_id,
                "questions": []
            }
        )
        quiz_id = create_response.json()["id"]
        
        # Update quiz
        response = await client.put(
            f"/quizzes/{quiz_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Updated Quiz",
                "description": "New description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Quiz"
    
    @pytest.mark.asyncio
    async def test_instructor_can_delete_quiz(self, client: AsyncClient, instructor_with_course: dict):
        """Test deleting quiz"""
        token = instructor_with_course["instructor_token"]
        course_id = instructor_with_course["course_id"]
        
        # Create quiz
        create_response = await client.post(
            "/quizzes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Quiz to Delete",
                "course_id": course_id,
                "questions": []
            }
        )
        quiz_id = create_response.json()["id"]
        
        # Delete
        response = await client.delete(
            f"/quizzes/{quiz_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
