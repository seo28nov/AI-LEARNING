"""Định nghĩa schema Pydantic và document lưu dữ liệu hệ thống."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, EmailStr, Field


class LessonContent(BaseModel):
    """Mô tả nội dung từng bài học trong chương."""

    title: str = Field(..., description="Tiêu đề bài học")
    summary: str = Field(..., description="Tóm tắt nội dung để AI chat sử dụng")
    duration_minutes: int = Field(default=15, ge=1, description="Thời lượng dự kiến (phút)")


class ModuleOutline(BaseModel):
    """Định nghĩa một chương học theo HE_THONG.md."""

    name: str = Field(..., description="Tên chương")
    objectives: List[str] = Field(default_factory=list, description="Danh sách mục tiêu học tập")
    lessons: List[LessonContent] = Field(default_factory=list, description="Danh sách bài học trong chương")


class CourseBase(BaseModel):
    """Thông tin cơ bản của khóa học."""

    title: str = Field(..., description="Tên khóa học")
    description: str = Field(..., description="Mô tả khóa học")
    level: str = Field(default="beginner", description="Trình độ: beginner/intermediate/advanced")
    category: str = Field(default="Khoa học", description="Danh mục khóa học")
    estimated_duration_hours: float = Field(default=4.0, ge=0.5, description="Thời lượng ước tính (giờ)")
    tags: List[str] = Field(default_factory=list, description="Từ khóa gợi ý khóa học")


class CourseDocument(Document, CourseBase):
    """Document Beanie lưu trữ khóa học trong MongoDB."""

    created_by: str = Field(..., description="ID người tạo khóa học")
    source_type: str = Field(default="ai_generated", description="Nguồn gốc: manual/ai_generated/from_upload")
    modules: List[ModuleOutline] = Field(default_factory=list, description="Danh sách chương")
    
    # Additional fields for course management
    language: str = Field(default="vi", description="Ngôn ngữ khóa học: vi/en")
    is_published: bool = Field(default=False, description="Khóa học đã công khai hay chưa")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "courses"
        indexes = ["title", "category", "tags", "is_published"]


class CourseCreate(CourseBase):
    """Payload tạo khóa học mới."""

    modules: List[ModuleOutline] = Field(default_factory=list)


class CourseResponse(CourseBase):
    """Schema phản hồi cho API trả khóa học."""

    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    modules: List[ModuleOutline] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class UserRole(str, Enum):
    """Các vai trò hệ thống cho người dùng."""

    student = "student"
    instructor = "instructor"
    admin = "admin"


class UserProfile(BaseModel):
    """Hồ sơ mở rộng cho người dùng."""

    bio: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    learning_goals: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None


class NotificationPreferences(BaseModel):
    """Cài đặt thông báo."""

    email: bool = True
    push: bool = True
    study_reminders: bool = True
    class_updates: bool = True
    achievement: bool = True


class LearningPreferences(BaseModel):
    """Tùy chọn học tập."""

    language: str = "vi"
    timezone: Optional[str] = None
    theme: str = "auto"
    auto_play_next: bool = True
    show_hints: bool = True
    difficulty_preference: Optional[str] = None


class UserPreferences(BaseModel):
    """Bao gồm thông báo và học tập."""

    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)
    learning: LearningPreferences = Field(default_factory=LearningPreferences)


class LearningStats(BaseModel):
    """Thống kê học tập tổng quan."""

    total_courses: int = 0
    completed_courses: int = 0
    total_study_time: int = 0
    streak_days: int = 0
    last_activity: Optional[datetime] = None
    favorite_categories: List[str] = Field(default_factory=list)
    avg_quiz_score: float = 0.0


class UserBase(BaseModel):
    """Thông tin cơ bản của user."""

    email: EmailStr = Field(..., description="Email đăng nhập")
    full_name: str = Field(..., description="Họ tên đầy đủ")
    role: UserRole = Field(default=UserRole.student)
    avatar_url: Optional[str] = Field(default=None)
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class UserDocument(Document, UserBase):
    """Document lưu trữ user."""

    password_hash: str = Field(...)
    is_active: bool = Field(default=True)
    status: str = Field(default="pending")
    learning_stats: LearningStats = Field(default_factory=LearningStats)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = ["email", "role", "status", "created_at"]


class RegisterRequest(UserBase):
    """Payload đăng ký user."""

    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    """Payload đăng nhập."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload làm mới token."""

    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Token trả về sau đăng nhập."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900
    refresh_expires_in: int = 604800


class UserResponse(UserBase):
    """Thông tin user trả về cho FE."""

    id: str = Field(..., alias="_id")
    is_active: bool
    status: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True


class EnrollmentStatus(str, Enum):
    """Trạng thái đăng ký khóa học."""

    pending = "pending"
    active = "active"
    completed = "completed"


class EnrollmentDocument(Document):
    """Document lưu quan hệ học viên - khóa học."""

    course_id: str = Field(...)
    user_id: str = Field(...)
    status: EnrollmentStatus = Field(default=EnrollmentStatus.pending)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Tracking fields
    completed_chapters: List[str] = Field(default_factory=list, description="List chapter IDs đã hoàn thành")
    quiz_scores: dict = Field(default_factory=dict, description="Quiz scores: {quiz_id: score}")
    total_study_time: int = Field(default=0, description="Tổng thời gian học (phút)")
    last_accessed: Optional[datetime] = Field(default=None, description="Lần truy cập cuối")
    completed_at: Optional[datetime] = Field(default=None, description="Thời điểm hoàn thành khóa học")

    class Settings:
        name = "enrollments"
        indexes = [("course_id", "user_id")]


class EnrollmentResponse(BaseModel):
    """Schema trả về cho enrollment."""

    id: str = Field(..., alias="_id")
    course_id: str
    user_id: str
    status: EnrollmentStatus
    progress: float
    enrolled_at: datetime

    class Config:
        populate_by_name = True


class QuizQuestion(BaseModel):
    """Cấu trúc câu hỏi quiz."""

    question: str
    options: List[str]
    correct_answer: Optional[int] = Field(default=None, description="Index của đáp án đúng (0-based)")
    explanation: Optional[str] = Field(default=None, description="Giải thích đáp án")


class QuizDocument(Document):
    """Document lưu quiz theo khóa học."""

    course_id: str = Field(...)
    chapter_id: Optional[str] = Field(default=None, description="Chapter ID nếu quiz thuộc chapter cụ thể")
    title: str = Field(...)
    description: str = Field(default="", description="Mô tả quiz")
    questions: List[QuizQuestion] = Field(default_factory=list)
    time_limit: Optional[int] = Field(default=None, description="Thời gian làm bài (phút)")
    passing_score: float = Field(default=70.0, description="Điểm đạt tối thiểu (%)")
    created_by: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "quizzes"
        indexes = ["course_id", "chapter_id"]


class QuizResponse(BaseModel):
    """Schema trả về cho quiz."""

    id: str = Field(..., alias="_id")
    course_id: str
    title: str
    questions: List[QuizQuestion]

    class Config:
        populate_by_name = True


class ChatMessage(BaseModel):
    """Tin nhắn trong phiên chat."""

    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatDocument(Document):
    """Document lưu lịch sử chat AI."""

    user_id: str = Field(...)
    course_id: Optional[str] = None
    title: str = Field(default="New Chat")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chats"
        indexes = ["user_id", "course_id"]


class ChatResponse(BaseModel):
    """Phản hồi chat gửi về frontend."""

    session_id: str
    answer: str


class UploadDocument(Document):
    """Document lưu thông tin file upload."""

    user_id: str = Field(...)
    course_id: Optional[str] = None
    file_name: str = Field(...)
    file_type: str = Field(...)
    file_size: int = Field(default=0)
    file_hash: str = Field(...)
    file_url: str = Field(...)
    storage_path: str = Field(...)
    description: str = Field(default="")
    status: str = Field(default="pending")  # pending, processing, completed, failed
    extracted_text: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "uploads"
        indexes = ["user_id", "status", "file_hash"]


class UploadResponse(BaseModel):
    """Schema phản hồi cho upload."""

    id: str = Field(..., alias="_id")
    filename: str
    status: str

    class Config:
        populate_by_name = True


class ProgressDocument(Document):
    """Document theo dõi tiến độ học tập."""

    course_id: str = Field(...)
    user_id: str = Field(...)
    completed_lessons: List[str] = Field(default_factory=list)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    streak_days: int = Field(default=0, ge=0)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    learning_sessions: List["StudySessionModel"] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "progress"
        indexes = [("course_id", "user_id")]


class ProgressResponse(BaseModel):
    """Schema trả về tiến độ."""

    id: str = Field(..., alias="_id")
    course_id: str
    user_id: str
    progress: float
    completed_lessons: List[str]
    streak_days: int = 0
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    learning_sessions: List["StudySessionModel"] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class StudySessionModel(BaseModel):
    """Schema mô tả một phiên học, dùng chung nhiều module."""

    session_date: datetime
    duration_minutes: int
    activities: List[str] = Field(default_factory=list)


class NotificationDocument(Document):
    """Document lưu thông báo hệ thống."""

    target_user_id: str = Field(...)
    title: str = Field(...)
    message: str = Field(...)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = ["target_user_id", "is_read"]


class NotificationResponse(BaseModel):
    """Schema thông báo trả về."""

    id: str = Field(..., alias="_id")
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        populate_by_name = True


class RefreshTokenDocument(Document):
    """Document lưu refresh token để quản lý phiên."""

    user_id: str = Field(...)
    token_hash: str = Field(...)
    session_id: str = Field(...)
    fingerprint: Optional[str] = None
    expires_at: datetime = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None

    class Settings:
        name = "refresh_tokens"
        indexes = [
            ("user_id", "session_id"),
            ("token_hash",),
            ("expires_at",),
        ]


class VerificationTokenDocument(Document):
    """Document lưu token xác thực email."""

    user_id: str = Field(..., description="ID người dùng")
    token: str = Field(..., description="Token xác thực")
    token_type: str = Field(default="email_verification", description="Loại token")
    expires_at: datetime = Field(..., description="Thời gian hết hạn")
    used_at: Optional[datetime] = Field(default=None, description="Thời điểm đã sử dụng")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "verification_tokens"
        indexes = [
            ("token",),
            ("user_id", "token_type"),
            ("expires_at",),
        ]


class PasswordResetTokenDocument(Document):
    """Document lưu token reset mật khẩu."""

    user_id: str = Field(..., description="ID người dùng")
    token: str = Field(..., description="Token reset")
    expires_at: datetime = Field(..., description="Thời gian hết hạn")
    used_at: Optional[datetime] = Field(default=None, description="Thời điểm đã sử dụng")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "password_reset_tokens"
        indexes = [
            ("token",),
            ("user_id",),
            ("expires_at",),
        ]


class DashboardMetric(BaseModel):
    """Chỉ số dashboard cơ bản."""

    name: str
    value: float
    trend: Optional[float] = None


class DashboardDocument(Document):
    """Document lưu snapshot số liệu dashboard."""

    snapshot_at: datetime = Field(default_factory=datetime.utcnow)
    metrics: List[DashboardMetric] = Field(default_factory=list)

    class Settings:
        name = "dashboard_metrics"


class DashboardResponse(BaseModel):
    """Schema trả về số liệu dashboard."""

    metrics: List[DashboardMetric]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# CLASS MANAGEMENT - Lớp học của Instructor (Theo SYSTEM.md mục 6.3.1)
# ============================================================================


class ClassDocument(Document):
    """Document lưu thông tin lớp học do Instructor tạo."""

    name: str = Field(..., description="Tên lớp học")
    description: str = Field(default="", description="Mô tả lớp học")
    instructor_id: str = Field(..., description="ID giảng viên tạo lớp")
    course_id: str = Field(..., description="ID khóa học gốc được sử dụng")

    # Thông tin lớp học
    class_code: str = Field(..., description="Mã lớp để học viên tham gia")
    max_students: Optional[int] = Field(default=None, description="Số học viên tối đa (None = không giới hạn)")
    current_students: int = Field(default=0, description="Số học viên hiện tại")
    student_ids: List[str] = Field(default_factory=list, description="Danh sách ID học viên")

    # Thời gian và lịch trình
    start_date: Optional[datetime] = Field(default=None, description="Ngày bắt đầu lớp")
    end_date: Optional[datetime] = Field(default=None, description="Ngày kết thúc lớp")

    # Cài đặt và quy định
    auto_enroll: bool = Field(default=False, description="Tự động duyệt đăng ký")
    allow_late_join: bool = Field(default=True, description="Cho phép tham gia muộn")
    discussion_enabled: bool = Field(default=True, description="Bật thảo luận")
    ai_tutor_enabled: bool = Field(default=True, description="Bật AI tutor cho lớp")

    status: str = Field(
        default="upcoming", description="Trạng thái: upcoming/active/completed/cancelled"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "classes"
        indexes = [
            ("instructor_id", "status"),
            ("class_code",),
            ("student_ids",),
        ]


class ClassResponse(BaseModel):
    """Schema trả về thông tin lớp học."""

    id: str = Field(..., alias="_id")
    name: str
    description: str
    instructor_id: str
    course_id: str
    class_code: str
    max_students: Optional[int] = None
    current_students: int
    student_ids: List[str]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# ============================================================================
# ASSESSMENT SYSTEM - Đánh giá năng lực (Theo SYSTEM.md mục 6.2.2)
# ============================================================================


class AssessmentQuestion(BaseModel):
    """Câu hỏi trong bài đánh giá năng lực."""

    question_id: str = Field(...)
    question_text: str = Field(...)
    question_type: str = Field(default="multiple_choice", description="multiple_choice/true_false/fill_blank")
    options: List[str] = Field(default_factory=list, description="Các lựa chọn (cho trắc nghiệm)")
    correct_answer: Optional[int] = Field(default=None, description="Index đáp án đúng")
    user_answer: Optional[int] = Field(default=None, description="Câu trả lời của người dùng")
    is_correct: Optional[bool] = Field(default=None, description="Đúng hay sai")
    difficulty: str = Field(default="medium", description="easy/medium/hard")
    time_spent_seconds: int = Field(default=0, description="Thời gian làm câu hỏi (giây)")


class TopicAnalysis(BaseModel):
    """Phân tích kết quả theo từng chủ đề."""

    topic: str = Field(..., description="Tên chủ đề cụ thể")
    questions_count: int = Field(default=0)
    correct_count: int = Field(default=0)
    mastery_level: str = Field(default="fair", description="poor/fair/good/excellent")


class AssessmentResult(BaseModel):
    """Kết quả đánh giá năng lực."""

    total_questions: int = Field(default=0)
    correct_answers: int = Field(default=0)
    score: float = Field(default=0.0, description="Điểm số 0-100")
    percentage: float = Field(default=0.0)
    level: str = Field(default="beginner", description="beginner/intermediate/advanced")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list, description="ID các khóa học gợi ý")
    time_taken_minutes: int = Field(default=0)


class AssessmentDocument(Document):
    """Document lưu bài đánh giá năng lực đầu vào."""

    user_id: str = Field(..., description="ID người thực hiện đánh giá")
    assessment_type: str = Field(
        default="skill_assessment", description="skill_assessment/placement_test/quiz"
    )
    category: str = Field(..., description="programming/design/business/marketing")

    # Danh sách câu hỏi và câu trả lời
    questions: List[AssessmentQuestion] = Field(default_factory=list)

    # Kết quả đánh giá
    result: AssessmentResult = Field(default_factory=AssessmentResult)

    # Phân tích chi tiết theo chủ đề
    topic_analysis: List[TopicAnalysis] = Field(default_factory=list)

    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assessments"
        indexes = [
            ("user_id", "assessment_type"),
            ("category",),
            ("completed_at",),
        ]


class AssessmentResponse(BaseModel):
    """Schema trả về kết quả đánh giá."""

    id: str = Field(..., alias="_id")
    user_id: str
    assessment_type: str
    category: str
    result: AssessmentResult
    topic_analysis: List[TopicAnalysis]
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


# Aliases for backward compatibility with course_indexing_service
CourseChapter = ModuleOutline
Lesson = LessonContent
