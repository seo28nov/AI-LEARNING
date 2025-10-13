"""Service placeholder cho quản lý lớp học."""
from datetime import datetime, timedelta
from typing import List

from schemas.classes import ClassInvitation, RosterStudent
from schemas.enrollment import ClassCreateRequest


async def list_classes(instructor_id: str) -> List[dict]:
    """Trả danh sách lớp giả lập."""

    _ = instructor_id
    return [
        {
            "id": "class-1",
            "name": "Lớp React 101",
            "status": "active",
            "start_date": datetime.utcnow().isoformat(),
        }
    ]


async def create_class(payload: ClassCreateRequest, instructor_id: str) -> dict:
    """Placeholder tạo lớp học."""

    return {
        "id": "class-new",
        "name": payload.name,
        "course_id": payload.course_id,
        "instructor_id": instructor_id,
    }


async def generate_join_code(class_id: str) -> ClassInvitation:
    """Sinh mã mời giả lập cho lớp học."""

    expires_at = datetime.utcnow() + timedelta(days=3)
    join_code = f"JOIN-{class_id[-4:].upper()}"
    invite_url = f"https://learning.local/classes/{class_id}?code={join_code}"
    return ClassInvitation(class_id=class_id, join_code=join_code, expires_at=expires_at, invite_url=invite_url)


async def list_roster_preview(class_id: str) -> List[RosterStudent]:
    """Trả danh sách học viên demo phục vụ UI roster."""

    _ = class_id
    return [
        RosterStudent(
            student_id="student-1",
            full_name="Nguyễn Văn A",
            email="student1@example.com",
            status="active",
            last_active=datetime.utcnow() - timedelta(hours=2),
            progress_percent=72.5,
            tags=["quiz-high", "focus"],
        ),
        RosterStudent(
            student_id="student-2",
            full_name="Trần Thị B",
            email="student2@example.com",
            status="pending",
            last_active=None,
            progress_percent=10.0,
            tags=["new"],
        ),
    ]
