"""
User Flow Testing Script

Test complete workflows for all 3 user roles:
- Admin: User management → Course approval → Analytics
- Instructor: Create course → Class → Quiz → Analytics
- Student: Enroll → Learn → Quiz → Chat with RAG

Usage:
    python scripts/test_user_flows.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from httpx import AsyncClient, ASGITransport  # noqa: E402
from app.main import app  # noqa: E402
from colorama import init, Fore, Style  # noqa: E402

# Initialize colorama for colored output
init(autoreset=True)


class UserFlowTester:
    """Test complete user workflows"""
    
    def __init__(self):
        self.base_url = "http://test"
        self.client = None
        self.results = {
            "admin": {"passed": 0, "failed": 0, "tests": []},
            "instructor": {"passed": 0, "failed": 0, "tests": []},
            "student": {"passed": 0, "failed": 0, "tests": []}
        }
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}{text.center(70)}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_test(self, test_name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = f"{Fore.GREEN}✓ PASS" if passed else f"{Fore.RED}✗ FAIL"
        print(f"{status}{Style.RESET_ALL} - {test_name}")
        if details:
            print(f"      {Fore.YELLOW}{details}{Style.RESET_ALL}")
    
    def record_test(self, role: str, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        if passed:
            self.results[role]["passed"] += 1
        else:
            self.results[role]["failed"] += 1
        self.results[role]["tests"].append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
    
    async def setup(self):
        """Setup test client"""
        transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=transport, base_url=self.base_url)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    # ========== ADMIN WORKFLOW ==========
    
    async def test_admin_workflow(self):
        """Test complete admin workflow"""
        self.print_header("ADMIN WORKFLOW TEST")
        
        try:
            # Step 1: Register admin
            register_response = await self.client.post(
                "/auth/register",
                json={
                    "email": "admin_flow@test.com",
                    "password": "Admin123!",
                    "full_name": "Admin Flow Test",
                    "role": "admin"
                }
            )
            passed = register_response.status_code == 201
            self.print_test("Admin Registration", passed)
            self.record_test("admin", "Register", passed)
            
            if not passed:
                return
            
            # Step 2: Login
            login_response = await self.client.post(
                "/auth/login",
                json={
                    "email": "admin_flow@test.com",
                    "password": "Admin123!"
                }
            )
            passed = login_response.status_code == 200
            self.print_test("Admin Login", passed)
            self.record_test("admin", "Login", passed)
            
            if not passed:
                return
            
            admin_token = login_response.json()["access_token"]
            
            # Step 3: Create instructor for testing
            await self.client.post(
                "/auth/register",
                json={
                    "email": "instructor_for_admin@test.com",
                    "password": "Instructor123!",
                    "full_name": "Instructor For Admin",
                    "role": "instructor"
                }
            )
            
            # Step 4: List all users
            users_response = await self.client.get(
                "/admin/users",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            passed = users_response.status_code == 200
            user_count = len(users_response.json().get("items", []))
            self.print_test("List All Users", passed, f"Found {user_count} users")
            self.record_test("admin", "List Users", passed, f"{user_count} users")
            
            # Step 5: Change user role
            users = users_response.json()["items"]
            instructor = next((u for u in users if u["email"] == "instructor_for_admin@test.com"), None)
            
            if instructor:
                role_response = await self.client.put(
                    f"/admin/users/{instructor['id']}/role",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={"role": "student"}
                )
                passed = role_response.status_code == 200
                self.print_test("Change User Role", passed, "instructor → student")
                self.record_test("admin", "Change Role", passed)
            
            # Step 6: Create course for approval testing
            instructor_login = await self.client.post(
                "/auth/login",
                json={
                    "email": "instructor_for_admin@test.com",
                    "password": "Instructor123!"
                }
            )
            
            if instructor_login.status_code == 200:
                instructor_token = instructor_login.json()["access_token"]
                
                # Change back to instructor role
                await self.client.put(
                    f"/admin/users/{instructor['id']}/role",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={"role": "instructor"}
                )
                
                # Create course
                course_response = await self.client.post(
                    "/courses",
                    headers={"Authorization": f"Bearer {instructor_token}"},
                    json={
                        "title": "Course Pending Approval",
                        "description": "Test course approval",
                        "level": "beginner",
                        "category": "programming",
                        "status": "draft"
                    }
                )
                
                if course_response.status_code == 201:
                    course_id = course_response.json()["id"]
                    
                    # Step 7: Approve course
                    approve_response = await self.client.post(
                        f"/admin/courses/{course_id}/approve",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
                    passed = approve_response.status_code == 200
                    self.print_test("Approve Course", passed)
                    self.record_test("admin", "Approve Course", passed)
            
            # Step 8: View analytics
            analytics_response = await self.client.get(
                "/admin/analytics/platform",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            passed = analytics_response.status_code == 200
            if passed:
                data = analytics_response.json()
                details = f"Users: {data.get('total_users', 0)}, Courses: {data.get('total_courses', 0)}"
            else:
                details = ""
            self.print_test("View Platform Analytics", passed, details)
            self.record_test("admin", "View Analytics", passed, details)
            
            print(f"\n{Fore.GREEN}✅ Admin workflow completed successfully!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Admin workflow failed: {str(e)}{Style.RESET_ALL}")
            self.record_test("admin", "Workflow", False, str(e))
    
    # ========== INSTRUCTOR WORKFLOW ==========
    
    async def test_instructor_workflow(self):
        """Test complete instructor workflow"""
        self.print_header("INSTRUCTOR WORKFLOW TEST")
        
        try:
            # Step 1: Register instructor
            register_response = await self.client.post(
                "/auth/register",
                json={
                    "email": "instructor_flow@test.com",
                    "password": "Instructor123!",
                    "full_name": "Instructor Flow Test",
                    "role": "instructor"
                }
            )
            passed = register_response.status_code == 201
            self.print_test("Instructor Registration", passed)
            self.record_test("instructor", "Register", passed)
            
            if not passed:
                return
            
            # Step 2: Login
            login_response = await self.client.post(
                "/auth/login",
                json={
                    "email": "instructor_flow@test.com",
                    "password": "Instructor123!"
                }
            )
            passed = login_response.status_code == 200
            self.print_test("Instructor Login", passed)
            self.record_test("instructor", "Login", passed)
            
            if not passed:
                return
            
            instructor_token = login_response.json()["access_token"]
            
            # Step 3: Create course with chapters
            course_response = await self.client.post(
                "/courses",
                headers={"Authorization": f"Bearer {instructor_token}"},
                json={
                    "title": "Complete Python Course",
                    "description": "Full Python programming course",
                    "level": "beginner",
                    "category": "programming",
                    "status": "published",
                    "chapters": [
                        {
                            "title": "Introduction",
                            "description": "Getting started",
                            "order": 1,
                            "lessons": [
                                {
                                    "title": "What is Python?",
                                    "content": "Python is a high-level programming language...",
                                    "order": 1,
                                    "duration_minutes": 15
                                }
                            ]
                        }
                    ]
                }
            )
            passed = course_response.status_code == 201
            self.print_test("Create Course with Chapters", passed)
            self.record_test("instructor", "Create Course", passed)
            
            if not passed:
                return
            
            course_id = course_response.json()["id"]
            
            # Step 4: Create class
            class_response = await self.client.post(
                "/classes",
                headers={"Authorization": f"Bearer {instructor_token}"},
                json={
                    "name": "Python Beginner Class",
                    "course_id": course_id,
                    "description": "Beginner Python class",
                    "start_date": "2024-01-01T00:00:00",
                    "end_date": "2024-06-30T00:00:00",
                    "max_students": 30
                }
            )
            passed = class_response.status_code == 201
            self.print_test("Create Class", passed)
            self.record_test("instructor", "Create Class", passed)
            
            # Step 5: Create quiz
            quiz_response = await self.client.post(
                "/quizzes",
                headers={"Authorization": f"Bearer {instructor_token}"},
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
                                {"text": "A snake", "is_correct": False}
                            ]
                        }
                    ]
                }
            )
            passed = quiz_response.status_code == 201
            self.print_test("Create Quiz", passed)
            self.record_test("instructor", "Create Quiz", passed)
            
            # Step 6: View course analytics
            analytics_response = await self.client.get(
                f"/analytics/courses/{course_id}",
                headers={"Authorization": f"Bearer {instructor_token}"}
            )
            passed = analytics_response.status_code == 200
            self.print_test("View Course Analytics", passed)
            self.record_test("instructor", "View Analytics", passed)
            
            # Step 7: View enrollments
            enrollment_response = await self.client.get(
                f"/courses/{course_id}/enrollments",
                headers={"Authorization": f"Bearer {instructor_token}"}
            )
            passed = enrollment_response.status_code == 200
            enrollment_count = len(enrollment_response.json().get("items", []))
            self.print_test("View Enrollments", passed, f"{enrollment_count} students enrolled")
            self.record_test("instructor", "View Enrollments", passed)
            
            print(f"\n{Fore.GREEN}✅ Instructor workflow completed successfully!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Instructor workflow failed: {str(e)}{Style.RESET_ALL}")
            self.record_test("instructor", "Workflow", False, str(e))
    
    # ========== STUDENT WORKFLOW ==========
    
    async def test_student_workflow(self):
        """Test complete student workflow"""
        self.print_header("STUDENT WORKFLOW TEST")
        
        try:
            # Setup: Create instructor and course first
            await self.client.post(
                "/auth/register",
                json={
                    "email": "instructor_for_student@test.com",
                    "password": "Instructor123!",
                    "full_name": "Instructor For Student",
                    "role": "instructor"
                }
            )
            
            instructor_login = await self.client.post(
                "/auth/login",
                json={
                    "email": "instructor_for_student@test.com",
                    "password": "Instructor123!"
                }
            )
            instructor_token = instructor_login.json()["access_token"]
            
            # Create course
            course_response = await self.client.post(
                "/courses",
                headers={"Authorization": f"Bearer {instructor_token}"},
                json={
                    "title": "Student Learning Course",
                    "description": "Course for student workflow test",
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
                                    "title": "Lesson 1",
                                    "content": "Python is created by Guido van Rossum. It emphasizes code readability.",
                                    "order": 1,
                                    "duration_minutes": 10
                                },
                                {
                                    "title": "Lesson 2",
                                    "content": "Variables in Python are dynamically typed.",
                                    "order": 2,
                                    "duration_minutes": 15
                                }
                            ]
                        }
                    ]
                }
            )
            course_id = course_response.json()["id"]
            lessons = course_response.json()["chapters"][0]["lessons"]
            
            # Create quiz
            quiz_response = await self.client.post(
                "/quizzes",
                headers={"Authorization": f"Bearer {instructor_token}"},
                json={
                    "title": "Student Quiz",
                    "course_id": course_id,
                    "passing_score": 70,
                    "questions": [
                        {
                            "question_text": "What is Python?",
                            "question_type": "multiple_choice",
                            "points": 100,
                            "options": [
                                {"text": "A programming language", "is_correct": True},
                                {"text": "A snake", "is_correct": False}
                            ]
                        }
                    ]
                }
            )
            quiz_id = quiz_response.json()["id"]
            question_id = quiz_response.json()["questions"][0]["id"]
            
            # Now test student workflow
            
            # Step 1: Register student
            register_response = await self.client.post(
                "/auth/register",
                json={
                    "email": "student_flow@test.com",
                    "password": "Student123!",
                    "full_name": "Student Flow Test",
                    "role": "student"
                }
            )
            passed = register_response.status_code == 201
            self.print_test("Student Registration", passed)
            self.record_test("student", "Register", passed)
            
            if not passed:
                return
            
            # Step 2: Login
            login_response = await self.client.post(
                "/auth/login",
                json={
                    "email": "student_flow@test.com",
                    "password": "Student123!"
                }
            )
            passed = login_response.status_code == 200
            self.print_test("Student Login", passed)
            self.record_test("student", "Login", passed)
            
            if not passed:
                return
            
            student_token = login_response.json()["access_token"]
            
            # Step 3: Browse courses
            courses_response = await self.client.get("/courses")
            passed = courses_response.status_code == 200
            course_count = len(courses_response.json().get("items", []))
            self.print_test("Browse Courses", passed, f"Found {course_count} courses")
            self.record_test("student", "Browse Courses", passed)
            
            # Step 4: Enroll in course
            enroll_response = await self.client.post(
                "/enrollments",
                headers={"Authorization": f"Bearer {student_token}"},
                json={"course_id": course_id}
            )
            passed = enroll_response.status_code == 201
            self.print_test("Enroll in Course", passed)
            self.record_test("student", "Enroll", passed)
            
            # Step 5: Complete lessons
            for i, lesson in enumerate(lessons, 1):
                progress_response = await self.client.post(
                    "/progress/lessons/complete",
                    headers={"Authorization": f"Bearer {student_token}"},
                    json={
                        "course_id": course_id,
                        "lesson_id": lesson["id"]
                    }
                )
                passed = progress_response.status_code == 200
                self.print_test(f"Complete Lesson {i}", passed)
                self.record_test("student", f"Lesson {i}", passed)
            
            # Step 6: Check progress
            progress_response = await self.client.get(
                f"/progress/courses/{course_id}",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            passed = progress_response.status_code == 200
            if passed:
                progress = progress_response.json().get("progress_percentage", 0)
                details = f"{progress}% complete"
            else:
                details = ""
            self.print_test("View Progress", passed, details)
            self.record_test("student", "View Progress", passed, details)
            
            # Step 7: Take quiz
            attempt_response = await self.client.post(
                f"/quizzes/{quiz_id}/attempts",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            passed = attempt_response.status_code == 201
            self.print_test("Start Quiz Attempt", passed)
            self.record_test("student", "Start Quiz", passed)
            
            if passed:
                attempt_id = attempt_response.json()["id"]
                
                # Submit quiz
                submit_response = await self.client.post(
                    f"/quizzes/attempts/{attempt_id}/submit",
                    headers={"Authorization": f"Bearer {student_token}"},
                    json={
                        "answers": [
                            {
                                "question_id": question_id,
                                "selected_option": "A programming language"
                            }
                        ]
                    }
                )
                passed = submit_response.status_code == 200
                if passed:
                    score = submit_response.json().get("score", 0)
                    details = f"Score: {score}/100"
                else:
                    details = ""
                self.print_test("Submit Quiz", passed, details)
                self.record_test("student", "Submit Quiz", passed, details)
            
            # Step 8: Create chat session
            chat_response = await self.client.post(
                "/chat/sessions",
                headers={"Authorization": f"Bearer {student_token}"},
                json={
                    "title": "Python Questions",
                    "course_id": course_id
                }
            )
            passed = chat_response.status_code == 201
            self.print_test("Create Chat Session", passed)
            self.record_test("student", "Create Chat", passed)
            
            if passed:
                session_id = chat_response.json()["id"]
                
                # Step 9: Send message with RAG
                message_response = await self.client.post(
                    f"/chat/sessions/{session_id}/messages",
                    headers={"Authorization": f"Bearer {student_token}"},
                    json={
                        "message": "Who created Python?",
                        "use_rag": True
                    }
                )
                passed = message_response.status_code == 200
                if passed:
                    ai_response = message_response.json().get("ai_message", {}).get("content", "")
                    rag_used = "guido" in ai_response.lower()
                    details = "RAG used correctly" if rag_used else "RAG may not be active"
                else:
                    details = ""
                self.print_test("Chat with RAG", passed, details)
                self.record_test("student", "Chat with RAG", passed, details)
            
            print(f"\n{Fore.GREEN}✅ Student workflow completed successfully!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Student workflow failed: {str(e)}{Style.RESET_ALL}")
            self.record_test("student", "Workflow", False, str(e))
    
    # ========== SUMMARY ==========
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total_passed = 0
        total_failed = 0
        
        for role, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            total_passed += passed
            total_failed += failed
            
            if total > 0:
                success_rate = (passed / total) * 100
                status_color = Fore.GREEN if success_rate == 100 else Fore.YELLOW if success_rate >= 70 else Fore.RED
                
                print(f"{status_color}{role.upper()}:{Style.RESET_ALL}")
                print(f"  Passed: {Fore.GREEN}{passed}{Style.RESET_ALL}")
                print(f"  Failed: {Fore.RED}{failed}{Style.RESET_ALL}")
                print(f"  Success Rate: {status_color}{success_rate:.1f}%{Style.RESET_ALL}\n")
        
        total = total_passed + total_failed
        if total > 0:
            overall_rate = (total_passed / total) * 100
            overall_color = Fore.GREEN if overall_rate == 100 else Fore.YELLOW if overall_rate >= 70 else Fore.RED
            
            print(f"{Fore.CYAN}OVERALL:{Style.RESET_ALL}")
            print(f"  Total Passed: {Fore.GREEN}{total_passed}{Style.RESET_ALL}")
            print(f"  Total Failed: {Fore.RED}{total_failed}{Style.RESET_ALL}")
            print(f"  Success Rate: {overall_color}{overall_rate:.1f}%{Style.RESET_ALL}\n")
            
            if overall_rate == 100:
                print(f"{Fore.GREEN}🎉 ALL TESTS PASSED! 🎉{Style.RESET_ALL}\n")
            elif overall_rate >= 70:
                print(f"{Fore.YELLOW}⚠️  Most tests passed, but some need attention{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.RED}❌ Many tests failed, please review{Style.RESET_ALL}\n")


async def main():
    """Main test runner"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}USER FLOW TESTING")
    print(f"{Fore.CYAN}Testing complete workflows for Admin, Instructor, and Student")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    tester = UserFlowTester()
    
    try:
        await tester.setup()
        
        # Run all workflows
        await tester.test_admin_workflow()
        await tester.test_instructor_workflow()
        await tester.test_student_workflow()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal error: {str(e)}{Style.RESET_ALL}")
    
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    # Install colorama if not available
    try:
        import colorama  # noqa: F401
    except ImportError:
        print("Installing colorama...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    
    asyncio.run(main())
