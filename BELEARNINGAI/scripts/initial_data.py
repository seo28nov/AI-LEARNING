"""Script seed dữ liệu mẫu cho hệ thống."""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import get_settings
from models.models import (
    UserDocument,
    UserRole,
    CourseDocument,
    EnrollmentDocument,
    EnrollmentStatus,
    ClassDocument,
    QuizDocument,
    QuizQuestion,
    AssessmentDocument,
    AssessmentQuestion,
    AssessmentResult,
    TopicAnalysis,
    ProgressDocument,
    StudySessionModel,
    ChatDocument,
    ChatMessage,
    UploadDocument
)
from services.auth_service import hash_password


async def init_db():
    """Khởi tạo kết nối database."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[
            UserDocument,
            CourseDocument,
            EnrollmentDocument,
            ClassDocument,
            QuizDocument,
            AssessmentDocument,
            ProgressDocument,
            ChatDocument,
            UploadDocument
        ]
    )
    
    return client


async def seed_users() -> dict:
    """Tạo users mẫu.
    
    Returns:
        Dict chứa user IDs theo role
    """
    print("\n=== Seeding Users ===")
    
    users_data = [
        {
            "name": "Admin User",
            "email": "admin@example.com",
            "password": "admin123",
            "role": UserRole.admin,
            "status": "active"
        },
        {
            "name": "Nguyễn Văn Giảng",
            "email": "instructor@example.com",
            "password": "instructor123",
            "role": UserRole.instructor,
            "status": "active",
            "bio": "Giảng viên lập trình với 10 năm kinh nghiệm"
        },
        {
            "name": "Trần Thị Học",
            "email": "student1@example.com",
            "password": "student123",
            "role": UserRole.student,
            "status": "active"
        },
        {
            "name": "Lê Văn Hiếu",
            "email": "student2@example.com",
            "password": "student123",
            "role": UserRole.student,
            "status": "active"
        },
        {
            "name": "Phạm Thị Mai",
            "email": "student3@example.com",
            "password": "student123",
            "role": UserRole.student,
            "status": "active"
        }
    ]
    
    user_ids = {}
    now = datetime.now(timezone.utc)
    
    for user_data in users_data:
        # Kiểm tra đã tồn tại chưa
        existing = await UserDocument.find_one(UserDocument.email == user_data["email"])
        if existing:
            print(f"  ✓ User {user_data['email']} đã tồn tại")
            user_ids[user_data["role"]] = user_ids.get(user_data["role"], []) + [str(existing.id)]
            continue
        
        # Tạo mới
        hashed_password = hash_password(user_data.pop("password"))
        user = UserDocument(
            **user_data,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now
        )
        
        await user.insert()
        print(f"  + Created {user_data['name']} ({user_data['role']})")
        
        user_ids[user_data["role"]] = user_ids.get(user_data["role"], []) + [str(user.id)]
    
    print(f"✅ Seeded {len(users_data)} users")
    return user_ids


async def seed_courses(instructor_ids: List[str]) -> List[str]:
    """Tạo courses mẫu.
    
    Args:
        instructor_ids: List instructor IDs
        
    Returns:
        List course IDs
    """
    print("\n=== Seeding Courses ===")
    
    instructor_id = instructor_ids[0] if instructor_ids else "default-instructor"
    now = datetime.now(timezone.utc)
    
    courses_data = [
        {
            "title": "Lập trình Python từ A-Z",
            "description": "Khóa học Python toàn diện cho người mới bắt đầu",
            "category": "programming",
            "level": "beginner",
            "language": "vi",
            "is_published": True,
            "chapters": [
                {
                    "title": "Giới thiệu Python",
                    "description": "Tìm hiểu về Python và cài đặt môi trường",
                    "content": "Python là ngôn ngữ lập trình phổ biến...",
                    "order": 1,
                    "duration_minutes": 45
                },
                {
                    "title": "Biến và Kiểu dữ liệu",
                    "description": "Học về biến, kiểu dữ liệu cơ bản",
                    "content": "Biến trong Python được khai báo đơn giản...",
                    "order": 2,
                    "duration_minutes": 60
                },
                {
                    "title": "Cấu trúc điều khiển",
                    "description": "If-else, loops trong Python",
                    "content": "Câu lệnh if trong Python...",
                    "order": 3,
                    "duration_minutes": 75
                }
            ]
        },
        {
            "title": "Web Development với FastAPI",
            "description": "Xây dựng REST API hiện đại với FastAPI",
            "category": "programming",
            "level": "intermediate",
            "language": "vi",
            "is_published": True,
            "chapters": [
                {
                    "title": "Giới thiệu FastAPI",
                    "description": "Tìm hiểu về FastAPI framework",
                    "content": "FastAPI là framework hiện đại...",
                    "order": 1,
                    "duration_minutes": 30
                },
                {
                    "title": "Routing và Path Parameters",
                    "description": "Tạo routes và xử lý parameters",
                    "content": "FastAPI routing rất đơn giản...",
                    "order": 2,
                    "duration_minutes": 45
                }
            ]
        },
        {
            "title": "Data Science với Pandas",
            "description": "Phân tích dữ liệu với thư viện Pandas",
            "category": "data_science",
            "level": "intermediate",
            "language": "vi",
            "is_published": True,
            "chapters": [
                {
                    "title": "Pandas DataFrame",
                    "description": "Làm việc với DataFrame",
                    "content": "DataFrame là cấu trúc dữ liệu chính...",
                    "order": 1,
                    "duration_minutes": 60
                }
            ]
        }
    ]
    
    course_ids = []
    
    for course_data in courses_data:
        # Kiểm tra đã tồn tại
        existing = await CourseDocument.find_one(CourseDocument.title == course_data["title"])
        if existing:
            print(f"  ✓ Course '{course_data['title']}' đã tồn tại")
            course_ids.append(str(existing.id))
            continue
        
        # Tạo mới
        course = CourseDocument(
            **course_data,
            created_by=instructor_id,
            created_at=now,
            updated_at=now
        )
        
        await course.insert()
        print(f"  + Created '{course_data['title']}'")
        course_ids.append(str(course.id))
    
    print(f"✅ Seeded {len(courses_data)} courses")
    return course_ids


async def seed_enrollments(student_ids: List[str], course_ids: List[str]):
    """Tạo enrollments mẫu.
    
    Args:
        student_ids: List student IDs
        course_ids: List course IDs
    """
    print("\n=== Seeding Enrollments ===")
    
    now = datetime.now(timezone.utc)
    count = 0
    
    for student_id in student_ids:
        for i, course_id in enumerate(course_ids[:2]):  # Mỗi student enroll 2 courses
            # Kiểm tra đã enroll chưa
            existing = await EnrollmentDocument.find_one(
                EnrollmentDocument.user_id == student_id,
                EnrollmentDocument.course_id == course_id
            )
            
            if existing:
                continue
            
            # Tạo enrollment
            progress = 30.0 + (i * 20)  # 30%, 50%
            enrollment = EnrollmentDocument(
                user_id=student_id,
                course_id=course_id,
                status=EnrollmentStatus.active,
                progress=progress,
                completed_chapters=[],
                quiz_scores={},
                total_study_time=120 + (i * 60),
                last_accessed=now - timedelta(days=i),
                enrolled_at=now - timedelta(days=10),
                completed_at=None
            )
            
            await enrollment.insert()
            count += 1
    
    print(f"✅ Seeded {count} enrollments")


async def seed_classes(instructor_ids: List[str], course_ids: List[str]) -> List[str]:
    """Tạo classes mẫu.
    
    Args:
        instructor_ids: List instructor IDs
        course_ids: List course IDs
        
    Returns:
        List class IDs
    """
    print("\n=== Seeding Classes ===")
    
    instructor_id = instructor_ids[0] if instructor_ids else "default-instructor"
    now = datetime.now(timezone.utc)
    
    classes_data = [
        {
            "name": "Lớp Python Khoá 1",
            "description": "Lớp học Python cho người mới bắt đầu",
            "course_id": course_ids[0] if course_ids else "default-course",
            "class_code": "PY2025K1",
            "max_students": 30,
            "status": "active"
        }
    ]
    
    class_ids = []
    
    for class_data in classes_data:
        # Kiểm tra đã tồn tại
        existing = await ClassDocument.find_one(ClassDocument.class_code == class_data["class_code"])
        if existing:
            print(f"  ✓ Class '{class_data['name']}' đã tồn tại")
            class_ids.append(str(existing.id))
            continue
        
        # Tạo mới
        class_doc = ClassDocument(
            **class_data,
            instructor_id=instructor_id,
            current_students=0,
            student_ids=[],
            created_at=now,
            updated_at=now
        )
        
        await class_doc.insert()
        print(f"  + Created '{class_data['name']}'")
        class_ids.append(str(class_doc.id))
    
    print(f"✅ Seeded {len(classes_data)} classes")
    return class_ids


async def seed_quizzes(course_ids: List[str]):
    """Tạo quizzes mẫu.
    
    Args:
        course_ids: List course IDs
    """
    print("\n=== Seeding Quizzes ===")
    
    if not course_ids:
        print("⚠️  Không có courses, bỏ qua seed quizzes")
        return
    
    now = datetime.now(timezone.utc)
    course_id = course_ids[0]
    
    quiz_data = {
        "course_id": course_id,
        "chapter_id": "chapter_1",
        "title": "Quiz: Kiến thức cơ bản Python",
        "description": "Kiểm tra kiến thức về Python cơ bản",
        "questions": [
            QuizQuestion(
                question="Python là ngôn ngữ lập trình gì?",
                options=[
                    "Compiled",
                    "Interpreted",
                    "Assembly",
                    "Machine code"
                ],
                correct_answer=1,
                explanation="Python là ngôn ngữ thông dịch (interpreted)"
            ),
            QuizQuestion(
                question="Kiểu dữ liệu nào sau đây là immutable?",
                options=[
                    "List",
                    "Dictionary",
                    "Tuple",
                    "Set"
                ],
                correct_answer=2,
                explanation="Tuple là kiểu dữ liệu không thể thay đổi (immutable)"
            )
        ],
        "time_limit": 15,
        "passing_score": 70.0
    }
    
    # Kiểm tra đã tồn tại
    existing = await QuizDocument.find_one(
        QuizDocument.course_id == course_id,
        QuizDocument.title == quiz_data["title"]
    )
    
    if existing:
        print("  ✓ Quiz đã tồn tại")
        return
    
    quiz = QuizDocument(
        **quiz_data,
        created_at=now,
        updated_at=now
    )
    
    await quiz.insert()
    print("  + Created quiz")
    print("✅ Seeded 1 quiz")


async def seed_assessments(student_ids: List[str]):
    """Tạo assessments mẫu.
    
    Args:
        student_ids: List student IDs
    """
    print("\n=== Seeding Assessments ===")
    
    if not student_ids:
        print("⚠️  Không có students, bỏ qua seed assessments")
        return
    
    now = datetime.now(timezone.utc)
    count = 0
    
    # Assessment 1: Python programming
    assessment_data_1 = {
        "user_id": student_ids[0],
        "assessment_type": "skill_assessment",
        "category": "programming",
        "questions": [
            AssessmentQuestion(
                question_id="py_q1",
                question_text="Python là ngôn ngữ lập trình gì?",
                question_type="multiple_choice",
                options=["Compiled", "Interpreted", "Assembly", "Machine code"],
                correct_answer=1,
                user_answer=1,
                is_correct=True,
                difficulty="easy",
                time_spent_seconds=15
            ),
            AssessmentQuestion(
                question_id="py_q2",
                question_text="Hàm nào dùng để in ra màn hình?",
                question_type="multiple_choice",
                options=["echo()", "print()", "display()", "show()"],
                correct_answer=1,
                user_answer=1,
                is_correct=True,
                difficulty="easy",
                time_spent_seconds=10
            ),
            AssessmentQuestion(
                question_id="py_q3",
                question_text="List comprehension nào sau đây đúng?",
                question_type="multiple_choice",
                options=[
                    "[x for x in range(10)]",
                    "{x for x in range(10)}",
                    "(x for x in range(10))",
                    "All of the above"
                ],
                correct_answer=3,
                user_answer=0,
                is_correct=False,
                difficulty="medium",
                time_spent_seconds=30
            )
        ],
        "result": AssessmentResult(
            total_questions=3,
            correct_answers=2,
            score=66.7,
            percentage=66.7,
            level="beginner",
            strengths=["Cú pháp cơ bản", "Hàm built-in"],
            weaknesses=["List comprehension", "Advanced syntax"],
            recommendations=["python-basic", "python-intermediate"],
            time_taken_minutes=1
        ),
        "topic_analysis": [
            TopicAnalysis(
                topic="Python Basics",
                questions_count=2,
                correct_count=2,
                mastery_level="good"
            ),
            TopicAnalysis(
                topic="Advanced Python",
                questions_count=1,
                correct_count=0,
                mastery_level="poor"
            )
        ],
        "completed_at": now
    }
    
    # Kiểm tra đã tồn tại
    existing = await AssessmentDocument.find_one(
        AssessmentDocument.user_id == student_ids[0],
        AssessmentDocument.category == "programming"
    )
    
    if not existing:
        assessment = AssessmentDocument(**assessment_data_1, created_at=now)
        await assessment.insert()
        print("  + Created Python assessment")
        count += 1
    else:
        print("  ✓ Python assessment đã tồn tại")
    
    # Assessment 2: Data Science
    if len(student_ids) > 1:
        assessment_data_2 = {
            "user_id": student_ids[1],
            "assessment_type": "skill_assessment",
            "category": "data_science",
            "questions": [
                AssessmentQuestion(
                    question_id="ds_q1",
                    question_text="Pandas DataFrame có bao nhiêu chiều?",
                    question_type="multiple_choice",
                    options=["1", "2", "3", "4"],
                    correct_answer=1,
                    user_answer=1,
                    is_correct=True,
                    difficulty="easy",
                    time_spent_seconds=12
                ),
                AssessmentQuestion(
                    question_id="ds_q2",
                    question_text="Hàm nào dùng để đọc CSV?",
                    question_type="multiple_choice",
                    options=["read_csv()", "load_csv()", "import_csv()", "get_csv()"],
                    correct_answer=0,
                    user_answer=0,
                    is_correct=True,
                    difficulty="easy",
                    time_spent_seconds=10
                )
            ],
            "result": AssessmentResult(
                total_questions=2,
                correct_answers=2,
                score=100.0,
                percentage=100.0,
                level="intermediate",
                strengths=["Pandas basics", "Data import/export"],
                weaknesses=[],
                recommendations=["pandas-advanced", "data-visualization"],
                time_taken_minutes=1
            ),
            "topic_analysis": [
                TopicAnalysis(
                    topic="Pandas Basics",
                    questions_count=2,
                    correct_count=2,
                    mastery_level="excellent"
                )
            ],
            "completed_at": now
        }
        
        existing = await AssessmentDocument.find_one(
            AssessmentDocument.user_id == student_ids[1],
            AssessmentDocument.category == "data_science"
        )
        
        if not existing:
            assessment = AssessmentDocument(**assessment_data_2, created_at=now)
            await assessment.insert()
            print("  + Created Data Science assessment")
            count += 1
        else:
            print("  ✓ Data Science assessment đã tồn tại")
    
    print(f"✅ Seeded {count} assessments")


async def seed_progress(student_ids: List[str], course_ids: List[str]):
    """Tạo progress tracking mẫu.
    
    Args:
        student_ids: List student IDs
        course_ids: List course IDs
    """
    print("\n=== Seeding Progress ===")
    
    if not student_ids or not course_ids:
        print("⚠️  Không có students hoặc courses, bỏ qua seed progress")
        return
    
    now = datetime.now(timezone.utc)
    count = 0
    
    # Progress cho mỗi enrollment
    for student_id in student_ids:
        for i, course_id in enumerate(course_ids[:2]):  # 2 courses đầu
            # Kiểm tra đã tồn tại
            existing = await ProgressDocument.find_one(
                ProgressDocument.user_id == student_id,
                ProgressDocument.course_id == course_id
            )
            
            if existing:
                continue
            
            # Tạo progress data
            progress_value = 30.0 + (i * 20)  # 30%, 50%
            completed_lessons_count = int(3 * progress_value / 100)  # Giả sử 3 lessons
            
            progress = ProgressDocument(
                user_id=student_id,
                course_id=course_id,
                progress=progress_value,
                completed_lessons=[f"lesson_{j+1}" for j in range(completed_lessons_count)],
                streak_days=5 + i,
                last_activity=now - timedelta(days=i),
                learning_sessions=[
                    StudySessionModel(
                        session_date=now - timedelta(days=7),
                        duration_minutes=45,
                        activities=["Watched lesson 1", "Completed quiz 1"]
                    ),
                    StudySessionModel(
                        session_date=now - timedelta(days=3),
                        duration_minutes=60,
                        activities=["Watched lesson 2", "Practiced coding"]
                    )
                ],
                updated_at=now
            )
            
            await progress.insert()
            count += 1
    
    print(f"✅ Seeded {count} progress records")


async def seed_chats(student_ids: List[str], course_ids: List[str]):
    """Tạo chat sessions mẫu.
    
    Args:
        student_ids: List student IDs
        course_ids: List course IDs
    """
    print("\n=== Seeding Chats ===")
    
    if not student_ids or not course_ids:
        print("⚠️  Không có students hoặc courses, bỏ qua seed chats")
        return
    
    now = datetime.now(timezone.utc)
    count = 0
    
    # Chat 1: Python course Q&A
    chat_data_1 = {
        "user_id": student_ids[0],
        "course_id": course_ids[0] if course_ids else None,
        "title": "Hỏi về Python basics",
        "messages": [
            ChatMessage(
                role="user",
                content="Giải thích cho tôi về list comprehension trong Python",
                timestamp=now - timedelta(minutes=10)
            ),
            ChatMessage(
                role="assistant",
                content="List comprehension là cách viết ngắn gọn để tạo list mới từ list có sẵn. Ví dụ: [x*2 for x in range(5)] sẽ tạo [0, 2, 4, 6, 8]",
                timestamp=now - timedelta(minutes=9)
            ),
            ChatMessage(
                role="user",
                content="Cho tôi ví dụ với điều kiện if",
                timestamp=now - timedelta(minutes=5)
            ),
            ChatMessage(
                role="assistant",
                content="Ví dụ với if: [x for x in range(10) if x % 2 == 0] sẽ chỉ lấy số chẵn: [0, 2, 4, 6, 8]",
                timestamp=now - timedelta(minutes=4)
            )
        ]
    }
    
    existing = await ChatDocument.find_one(
        ChatDocument.user_id == student_ids[0],
        ChatDocument.title == "Hỏi về Python basics"
    )
    
    if not existing:
        chat = ChatDocument(**chat_data_1, created_at=now - timedelta(minutes=10), updated_at=now)
        await chat.insert()
        print("  + Created Python Q&A chat")
        count += 1
    else:
        print("  ✓ Python Q&A chat đã tồn tại")
    
    # Chat 2: General AI tutor
    if len(student_ids) > 1:
        chat_data_2 = {
            "user_id": student_ids[1],
            "course_id": None,  # General chat
            "title": "AI Tutor Chat",
            "messages": [
                ChatMessage(
                    role="user",
                    content="Tôi nên học gì trước: Python hay JavaScript?",
                    timestamp=now - timedelta(hours=2)
                ),
                ChatMessage(
                    role="assistant",
                    content="Nếu bạn muốn bắt đầu với lập trình web, JavaScript là lựa chọn tốt. Nếu quan tâm đến data science hoặc AI, nên học Python trước.",
                    timestamp=now - timedelta(hours=2)
                )
            ]
        }
        
        existing = await ChatDocument.find_one(
            ChatDocument.user_id == student_ids[1],
            ChatDocument.title == "AI Tutor Chat"
        )
        
        if not existing:
            chat = ChatDocument(**chat_data_2, created_at=now - timedelta(hours=2), updated_at=now - timedelta(hours=2))
            await chat.insert()
            print("  + Created AI Tutor chat")
            count += 1
        else:
            print("  ✓ AI Tutor chat đã tồn tại")
    
    print(f"✅ Seeded {count} chat sessions")


async def seed_uploads(instructor_ids: List[str], course_ids: List[str]):
    """Tạo upload records mẫu.
    
    Args:
        instructor_ids: List instructor IDs
        course_ids: List course IDs
    """
    print("\n=== Seeding Uploads ===")
    
    if not instructor_ids or not course_ids:
        print("⚠️  Không có instructors hoặc courses, bỏ qua seed uploads")
        return
    
    now = datetime.now(timezone.utc)
    count = 0
    
    # Upload 1: PDF course material
    upload_data_1 = {
        "user_id": instructor_ids[0],
        "course_id": course_ids[0] if course_ids else None,
        "file_name": "python_basics_slides.pdf",
        "file_type": "application/pdf",
        "file_size": 2500000,  # 2.5 MB
        "file_hash": "abc123def456python",
        "file_url": "/uploads/python_basics_slides.pdf",
        "storage_path": "./uploads/python_basics_slides.pdf",
        "description": "Slide bài giảng Python cơ bản",
        "status": "completed",
        "extracted_text": "Python là ngôn ngữ lập trình... (extracted text here)"
    }
    
    existing = await UploadDocument.find_one(
        UploadDocument.file_hash == "abc123def456python"
    )
    
    if not existing:
        upload = UploadDocument(**upload_data_1, created_at=now - timedelta(days=5), updated_at=now - timedelta(days=5))
        await upload.insert()
        print("  + Created PDF upload")
        count += 1
    else:
        print("  ✓ PDF upload đã tồn tại")
    
    # Upload 2: Code file
    upload_data_2 = {
        "user_id": instructor_ids[0],
        "course_id": course_ids[0] if course_ids else None,
        "file_name": "example_code.py",
        "file_type": "text/x-python",
        "file_size": 5000,  # 5 KB
        "file_hash": "xyz789code123",
        "file_url": "/uploads/example_code.py",
        "storage_path": "./uploads/example_code.py",
        "description": "Code mẫu Python",
        "status": "completed",
        "extracted_text": "def hello():\n    print('Hello World')\n..."
    }
    
    existing = await UploadDocument.find_one(
        UploadDocument.file_hash == "xyz789code123"
    )
    
    if not existing:
        upload = UploadDocument(**upload_data_2, created_at=now - timedelta(days=3), updated_at=now - timedelta(days=3))
        await upload.insert()
        print("  + Created code file upload")
        count += 1
    else:
        print("  ✓ Code file upload đã tồn tại")
    
    print(f"✅ Seeded {count} upload records")


async def seed_all():
    """Seed tất cả dữ liệu mẫu."""
    client = await init_db()
    
    try:
        print("\n" + "="*50)
        print("  SEED SAMPLE DATA FOR AI LEARNING PLATFORM")
        print("="*50)
        
        # 1. Seed users
        user_ids = await seed_users()
        
        # 2. Seed courses
        instructor_ids = user_ids.get(UserRole.instructor, [])
        course_ids = await seed_courses(instructor_ids)
        
        # 3. Seed enrollments
        student_ids = user_ids.get(UserRole.student, [])
        await seed_enrollments(student_ids, course_ids)
        
        # 4. Seed classes
        await seed_classes(instructor_ids, course_ids)
        
        # 5. Seed quizzes
        await seed_quizzes(course_ids)
        
        # 6. Seed assessments
        await seed_assessments(student_ids)
        
        # 7. Seed progress
        await seed_progress(student_ids, course_ids)
        
        # 8. Seed chats
        await seed_chats(student_ids, course_ids)
        
        # 9. Seed uploads
        await seed_uploads(instructor_ids, course_ids)
        
        print("\n" + "="*50)
        print("  ✅ SEED COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"  - Users: {sum(len(v) for v in user_ids.values())}")
        print(f"  - Courses: {len(course_ids)}")
        print(f"  - Enrollments: {len(student_ids) * 2}")
        print("  - Classes: 1")
        print("  - Quizzes: 1")
        print("  - Assessments: 2")
        print(f"  - Progress: {len(student_ids) * 2}")
        print("  - Chats: 2")
        print("  - Uploads: 2")
        print("\n🔑 Login credentials:")
        print("  Admin: admin@example.com / admin123")
        print("  Instructor: instructor@example.com / instructor123")
        print("  Student: student1@example.com / student123")
        print("\n💡 Next steps:")
        print("  1. Run: python scripts/seed_embeddings.py")
        print("  2. Start app: uvicorn app.main:app --reload")
        print("  3. Test RAG: POST /api/v1/chat")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_all())
