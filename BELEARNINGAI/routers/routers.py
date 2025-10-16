"""Định nghĩa các tuyến API cốt lõi."""
from fastapi import APIRouter

from .admin_router import router as admin_router
from .ai_router import router as ai_router
from .analytics_router import router as analytics_router
from .assessments_router import router as assessments_router
from .auth_router import router as auth_router
from .chat_router import router as chat_router
from .classes_router import router as classes_router
from .courses_router import router as courses_router
from .dashboard_router import router as dashboard_router
from .enrollment_router import router as enrollment_router
from .notification_router import router as notification_router
from .permissions_router import router as permissions_router
from .progress_router import router as progress_router
from .quiz_router import router as quiz_router
from .recommendation_router import router as recommendation_router
from .search_router import router as search_router
from .upload_router import router as upload_router
from .users_router import router as users_router
from .health_router import router as health_router  # NEW

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(permissions_router, prefix="/permissions")
api_router.include_router(courses_router, prefix="/courses")
api_router.include_router(classes_router, prefix="/classes")
api_router.include_router(enrollment_router, prefix="/enrollments")
api_router.include_router(quiz_router, prefix="/quizzes")
api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(ai_router, prefix="/ai")
api_router.include_router(upload_router, prefix="/uploads")
api_router.include_router(progress_router, prefix="/progress")
api_router.include_router(notification_router, prefix="/notifications")
api_router.include_router(dashboard_router, prefix="/dashboard")
api_router.include_router(analytics_router, prefix="/analytics")
api_router.include_router(assessments_router, prefix="/assessments")
api_router.include_router(admin_router, prefix="/admin")
api_router.include_router(search_router, prefix="/search")
api_router.include_router(recommendation_router, prefix="/recommendations")
api_router.include_router(health_router, prefix="/health")  # NEW
