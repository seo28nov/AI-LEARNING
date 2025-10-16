"""
Script tạo indexes cho MongoDB collections.
Chạy script này sau khi setup database để tối ưu performance.

Usage:
    python scripts/create_indexes.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config.config import settings


async def create_indexes():
    """Tạo tất cả indexes cần thiết cho MongoDB."""
    
    print("🔗 Đang kết nối MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    print(f"📊 Database: {settings.DATABASE_NAME}\n")
    
    # ========================================
    # USERS COLLECTION
    # ========================================
    print("👤 Tạo indexes cho collection 'users'...")
    
    await db.users.create_index("email", unique=True, name="idx_users_email")
    print("  ✓ email (unique)")
    
    await db.users.create_index("role", name="idx_users_role")
    print("  ✓ role")
    
    await db.users.create_index("is_active", name="idx_users_is_active")
    print("  ✓ is_active")
    
    await db.users.create_index("created_at", name="idx_users_created_at")
    print("  ✓ created_at")
    
    # ========================================
    # COURSES COLLECTION
    # ========================================
    print("\n📚 Tạo indexes cho collection 'courses'...")
    
    await db.courses.create_index("instructor_id", name="idx_courses_instructor")
    print("  ✓ instructor_id")
    
    await db.courses.create_index("category", name="idx_courses_category")
    print("  ✓ category")
    
    await db.courses.create_index("level", name="idx_courses_level")
    print("  ✓ level")
    
    await db.courses.create_index("is_public", name="idx_courses_is_public")
    print("  ✓ is_public")
    
    await db.courses.create_index("status", name="idx_courses_status")
    print("  ✓ status")
    
    # Text search index
    await db.courses.create_index(
        [("title", "text"), ("description", "text")],
        name="idx_courses_text_search"
    )
    print("  ✓ title + description (text search)")
    
    # Compound index cho common queries
    await db.courses.create_index(
        [("is_public", 1), ("category", 1), ("created_at", -1)],
        name="idx_courses_public_category_date"
    )
    print("  ✓ is_public + category + created_at (compound)")
    
    # ========================================
    # ENROLLMENTS COLLECTION
    # ========================================
    print("\n📝 Tạo indexes cho collection 'enrollments'...")
    
    # Compound unique index
    await db.enrollments.create_index(
        [("user_id", 1), ("course_id", 1)],
        unique=True,
        name="idx_enrollments_user_course"
    )
    print("  ✓ user_id + course_id (compound, unique)")
    
    await db.enrollments.create_index("user_id", name="idx_enrollments_user")
    print("  ✓ user_id")
    
    await db.enrollments.create_index("course_id", name="idx_enrollments_course")
    print("  ✓ course_id")
    
    await db.enrollments.create_index("status", name="idx_enrollments_status")
    print("  ✓ status")
    
    await db.enrollments.create_index("enrolled_at", name="idx_enrollments_enrolled_at")
    print("  ✓ enrolled_at")
    
    # ========================================
    # CLASSES COLLECTION
    # ========================================
    print("\n🏫 Tạo indexes cho collection 'classes'...")
    
    await db.classes.create_index("instructor_id", name="idx_classes_instructor")
    print("  ✓ instructor_id")
    
    await db.classes.create_index("course_id", name="idx_classes_course")
    print("  ✓ course_id")
    
    await db.classes.create_index("join_code", unique=True, name="idx_classes_join_code")
    print("  ✓ join_code (unique)")
    
    await db.classes.create_index("created_at", name="idx_classes_created_at")
    print("  ✓ created_at")
    
    # ========================================
    # QUIZZES COLLECTION
    # ========================================
    print("\n📋 Tạo indexes cho collection 'quizzes'...")
    
    await db.quizzes.create_index("course_id", name="idx_quizzes_course")
    print("  ✓ course_id")
    
    await db.quizzes.create_index("chapter_id", name="idx_quizzes_chapter")
    print("  ✓ chapter_id")
    
    await db.quizzes.create_index("instructor_id", name="idx_quizzes_instructor")
    print("  ✓ instructor_id")
    
    await db.quizzes.create_index("created_at", name="idx_quizzes_created_at")
    print("  ✓ created_at")
    
    # ========================================
    # QUIZ ATTEMPTS COLLECTION
    # ========================================
    print("\n✍️ Tạo indexes cho collection 'quiz_attempts'...")
    
    await db.quiz_attempts.create_index(
        [("quiz_id", 1), ("user_id", 1)],
        name="idx_attempts_quiz_user"
    )
    print("  ✓ quiz_id + user_id (compound)")
    
    await db.quiz_attempts.create_index("user_id", name="idx_attempts_user")
    print("  ✓ user_id")
    
    await db.quiz_attempts.create_index("submitted_at", name="idx_attempts_submitted_at")
    print("  ✓ submitted_at")
    
    # ========================================
    # ASSESSMENTS COLLECTION
    # ========================================
    print("\n🎯 Tạo indexes cho collection 'assessments'...")
    
    await db.assessments.create_index("user_id", name="idx_assessments_user")
    print("  ✓ user_id")
    
    await db.assessments.create_index("category", name="idx_assessments_category")
    print("  ✓ category")
    
    await db.assessments.create_index("assessment_type", name="idx_assessments_type")
    print("  ✓ assessment_type")
    
    await db.assessments.create_index(
        [("user_id", 1), ("created_at", -1)],
        name="idx_assessments_user_date"
    )
    print("  ✓ user_id + created_at (compound)")
    
    # ========================================
    # CHAT SESSIONS COLLECTION
    # ========================================
    print("\n💬 Tạo indexes cho collection 'chat_sessions'...")
    
    await db.chat_sessions.create_index("user_id", name="idx_chat_sessions_user")
    print("  ✓ user_id")
    
    await db.chat_sessions.create_index("course_id", name="idx_chat_sessions_course")
    print("  ✓ course_id")
    
    await db.chat_sessions.create_index("created_at", name="idx_chat_sessions_created_at")
    print("  ✓ created_at")
    
    # ========================================
    # CHAT MESSAGES COLLECTION
    # ========================================
    print("\n💭 Tạo indexes cho collection 'chat_messages'...")
    
    await db.chat_messages.create_index("session_id", name="idx_chat_messages_session")
    print("  ✓ session_id")
    
    await db.chat_messages.create_index(
        [("session_id", 1), ("created_at", 1)],
        name="idx_chat_messages_session_date"
    )
    print("  ✓ session_id + created_at (compound)")
    
    # ========================================
    # UPLOADS COLLECTION
    # ========================================
    print("\n📤 Tạo indexes cho collection 'uploads'...")
    
    await db.uploads.create_index("user_id", name="idx_uploads_user")
    print("  ✓ user_id")
    
    await db.uploads.create_index("course_id", name="idx_uploads_course")
    print("  ✓ course_id")
    
    await db.uploads.create_index("status", name="idx_uploads_status")
    print("  ✓ status")
    
    await db.uploads.create_index("uploaded_at", name="idx_uploads_uploaded_at")
    print("  ✓ uploaded_at")
    
    # ========================================
    # PROGRESS COLLECTION
    # ========================================
    print("\n📊 Tạo indexes cho collection 'progress'...")
    
    await db.progress.create_index(
        [("user_id", 1), ("course_id", 1)],
        unique=True,
        name="idx_progress_user_course"
    )
    print("  ✓ user_id + course_id (compound, unique)")
    
    await db.progress.create_index("user_id", name="idx_progress_user")
    print("  ✓ user_id")
    
    await db.progress.create_index("updated_at", name="idx_progress_updated_at")
    print("  ✓ updated_at")
    
    # ========================================
    # NOTIFICATIONS COLLECTION
    # ========================================
    print("\n🔔 Tạo indexes cho collection 'notifications'...")
    
    await db.notifications.create_index("user_id", name="idx_notifications_user")
    print("  ✓ user_id")
    
    await db.notifications.create_index("is_read", name="idx_notifications_is_read")
    print("  ✓ is_read")
    
    await db.notifications.create_index(
        [("user_id", 1), ("is_read", 1), ("created_at", -1)],
        name="idx_notifications_user_read_date"
    )
    print("  ✓ user_id + is_read + created_at (compound)")
    
    # ========================================
    # ANALYTICS COLLECTION
    # ========================================
    print("\n📈 Tạo indexes cho collection 'analytics'...")
    
    await db.analytics.create_index("user_id", name="idx_analytics_user")
    print("  ✓ user_id")
    
    await db.analytics.create_index("course_id", name="idx_analytics_course")
    print("  ✓ course_id")
    
    await db.analytics.create_index("event_type", name="idx_analytics_event_type")
    print("  ✓ event_type")
    
    await db.analytics.create_index("timestamp", name="idx_analytics_timestamp")
    print("  ✓ timestamp")
    
    # ========================================
    # ADMIN LOGS COLLECTION
    # ========================================
    print("\n🔐 Tạo indexes cho collection 'admin_logs'...")
    
    await db.admin_logs.create_index("admin_id", name="idx_admin_logs_admin")
    print("  ✓ admin_id")
    
    await db.admin_logs.create_index("action", name="idx_admin_logs_action")
    print("  ✓ action")
    
    await db.admin_logs.create_index("created_at", name="idx_admin_logs_created_at")
    print("  ✓ created_at")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*60)
    print("✅ Đã tạo thành công tất cả indexes!")
    print("="*60)
    
    # List all collections with index count
    print("\n📋 Tóm tắt indexes theo collection:\n")
    collections = [
        "users", "courses", "enrollments", "classes",
        "quizzes", "quiz_attempts", "assessments",
        "chat_sessions", "chat_messages", "uploads",
        "progress", "notifications", "analytics", "admin_logs"
    ]
    
    total_indexes = 0
    for collection_name in collections:
        indexes = await db[collection_name].list_indexes().to_list(length=None)
        index_count = len(indexes)
        total_indexes += index_count
        print(f"  {collection_name:20} : {index_count:2} indexes")
    
    print(f"\n  {'TOTAL':20} : {total_indexes:2} indexes")
    print("\n✨ Database đã sẵn sàng cho production!")
    
    client.close()


async def drop_all_indexes():
    """Drop tất cả indexes (dùng khi cần recreate)."""
    
    print("⚠️  CẢNH BÁO: Đang xóa tất cả indexes...")
    
    response = input("Bạn có chắc chắn muốn xóa tất cả indexes? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Đã hủy.")
        return
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    collections = await db.list_collection_names()
    
    for collection_name in collections:
        # Keep _id_ index (default)
        indexes = await db[collection_name].list_indexes().to_list(length=None)
        for index in indexes:
            if index["name"] != "_id_":
                await db[collection_name].drop_index(index["name"])
                print(f"  ✓ Đã xóa {collection_name}.{index['name']}")
    
    print("\n✅ Đã xóa tất cả custom indexes.")
    client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MongoDB Indexes Management")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all custom indexes before creating new ones"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        asyncio.run(drop_all_indexes())
    
    asyncio.run(create_indexes())
