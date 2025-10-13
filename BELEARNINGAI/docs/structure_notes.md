# Ghi chú cấu trúc backend BELEARNINGAI

Tài liệu này mô tả skeleton backend mới nhất và cách ánh xạ với `HE_THONG.md`.

## 1. Thư mục gốc

- `app/`
  - `main.py`: Khởi tạo FastAPI, middleware, include router tổng `/api/v1`.
  - `database.py`: Kết nối MongoDB, đăng ký Beanie Document (Users, Courses, Classes, Assessments, Enrollments, Quiz, Chat Sessions, Uploads, Progress, Notifications, Dashboard, Refresh Tokens).
- `config/`
  - `config.py`: Pydantic Settings đọc biến môi trường, thông số JWT.
  - `logging_config.py`: Cấu hình logging chuẩn.
- `middleware/`
  - `auth.py`: Placeholder decode/validate JWT.
  - `rbac.py`: Placeholder kiểm tra quyền theo bảng 10.2.
- `controllers/`: Điều phối giữa router ↔ service cho từng module (auth, users, courses, classes, enrollment, assessments, quiz, analytics, ai, uploads, progress, notifications, admin, search, recommendation, permissions).
- `services/`: Logic nghiệp vụ tương ứng, độc lập FastAPI.
- `models/`
  - `models.py`: Khai báo Document & schema core của toàn hệ thống.
- `schemas/`
  - Tách theo module (`auth.py`, `course.py`, `assessment.py`, `analytics.py`, `admin.py`, `ai.py`, `enrollment.py`, `notification.py`, `upload.py`, `search.py`, `user.py`, `common.py`).
- `routers/`: Router FastAPI cho từng nhóm API, `routers.py` gom lại với prefix.`
- `modules/`
  - `course_module.py`: Dataset minh họa (ví dụ Con lắc lò xo).
- `scripts/`
  - `initial_data.py`: Seed dữ liệu mẫu / script hỗ trợ.
- `docs/`
  - `docs.md`: Tổng hợp kiến trúc, mapping endpoint → module.
  - `structure_notes.md`: Tài liệu hiện tại.
- `tests/`: Bộ test pytest. Skeleton tạo thư mục con cho từng module, kịch bản đặt ở `tests/<module>/`.
- `utils/`
  - `utils.py`: Hàm tiện ích chung (vd UTC time).

## 2. Định tuyến API theo module

| Module | Router | Controller | Service | Document/Schema |
|--------|--------|------------|---------|-----------------|
| Auth | `routers/auth_router.py` | `controllers/auth_controller.py` | `services/auth_service.py` | `UserDocument`, `RefreshTokenDocument` |
| Users | `routers/users_router.py` | `controllers/user_controller.py` | `services/user_service.py` | `UserDocument` |
| Courses | `routers/courses_router.py` | `controllers/course_controller.py` | `services/course_service.py` | `CourseDocument` |
| Classes | `routers/classes_router.py` | `controllers/classes_controller.py` | `services/classes_service.py` | `ClassDocument` |
| Assessments | `routers/assessments_router.py` | `controllers/assessment_controller.py` | `services/assessment_service.py` | `AssessmentDocument` |
| Enrollments | `routers/enrollment_router.py` | `controllers/enrollment_controller.py` | `services/enrollment_service.py` | `EnrollmentDocument` |
| Quiz | `routers/quiz_router.py` | `controllers/quiz_controller.py` | `services/quiz_service.py` | `QuizDocument` |
| Analytics | `routers/analytics_router.py` | `controllers/analytics_controller.py` | `services/analytics_service.py` | `ProgressDocument`, `DashboardDocument` |
| AI (Chat/Content) | `routers/ai_router.py` | `controllers/ai_controller.py` | `services/ai_service.py` | `ChatSessionDocument`, `CourseDocument` |
| Uploads | `routers/upload_router.py` | `controllers/upload_controller.py` | `services/upload_service.py` | `FileUploadDocument` |
| Notifications | `routers/notification_router.py` | `controllers/notification_controller.py` | `services/notification_service.py` | `NotificationDocument` |
| Admin | `routers/admin_router.py` | `controllers/admin_controller.py` | `services/admin_service.py` | `UserDocument`, `CourseDocument` |
| Search | `routers/search_router.py` | `controllers/search_controller.py` | `services/search_service.py` | Vector metadata |
| Recommendations | `routers/recommendation_router.py` | `controllers/recommendation_controller.py` | `services/recommendation_service.py` | AI pipeline |
| Permissions | `routers/permissions_router.py` | `controllers/permissions_controller.py` | `services/permissions_service.py` | RBAC policies |

## 3. Quy tắc triển khai

1. **Schema trước**: Định nghĩa Document/Pydantic trong `models/models.py` và schema API trong `schemas/`.
2. **Service thuần logic**: Không sử dụng FastAPI trong service; trả về data models rõ ràng.
3. **Controller điều phối**: Xử lý business flow phức tạp, gom nhiều service, quản lý exception chuẩn `HTTPException`.
4. **Router tối giản**: Nhận request, gọi controller, khai báo Depends (auth, RBAC), response_model rõ ràng.
5. **Tests**: Mỗi module có thư mục test riêng, nếu chưa có logic thật dùng `pytest.mark.skip(reason="Placeholder")`.
6. **Seed dữ liệu**: Dùng script trong `scripts/` hoặc dataset `modules/` cho môi trường dev/local.

## 4. Mapping với HE_THONG.md

- **Mục 7.1 (Auth)** → `auth_router.py`, `auth_service.py`.
- **Mục 7.2 (Course Management)** → `courses_router.py`, `classes_router.py`, `course_service.py`, `classes_service.py`.
- **Mục 7.2 Assessment System** → `assessments_router.py`, `assessment_service.py`.
- **Mục 7.3 Enrollment & Progress** → `enrollment_router.py`, `progress_router.py`, `analytics_router.py`.
- **Mục 7.5 Quiz & Assessment** → `quiz_router.py`, `quiz_service.py`.
- **Mục 7.6 Analytics & Reporting** → `analytics_router.py`, `analytics_service.py`, `dashboard_router.py`.
- **Mục 7.7 Chat & AI** → `chat_router.py`, `ai_router.py`, `chat_service.py`, `ai_service.py`.
- **Mục 7.8 Uploads** → `upload_router.py`, `upload_service.py`.
- **Mục 7.9 Admin** → `admin_router.py`, `permissions_router.py`.
- **Mục 7.10 Search & Recommendations** → `search_router.py`, `recommendation_router.py`.

## 5. Checklist mở rộng

- [ ] Triển khai middleware JWT + RBAC thực tế và gắn vào router.
- [x] Bổ sung seed script và sample dữ liệu cho Classes/Assessments/Analytics (skeleton phục vụ mục 2).
- [x] Cập nhật docs khi từng module chuyển từ placeholder sang logic thật (mục 2 đã cập nhật bảng endpoint).
- [ ] Viết test end-to-end khi API chính hoàn thành.
