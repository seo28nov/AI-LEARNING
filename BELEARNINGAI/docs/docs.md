# Tài liệu kỹ thuật BELEARNINGAI

Tài liệu này tóm tắt kiến trúc và liên kết trực tiếp với các mục trong `HE_THONG.md`.

## 1. Mục tiêu

- Phản ánh đầy đủ kiến trúc backend FastAPI cho nền tảng học tập AI
- Dễ dàng mở rộng các module: courses, quiz, chat AI, uploads
- Tương thích với MongoDB và vector search đã mô tả

## 2. Sơ đồ kết nối module

```text
FastAPI App (app/main.py)
  ├── Config (config/config.py)
  ├── Logging (config/logging_config.py)
  ├── Database (app/database.py)
  ├── Routers (routers/*.py)
  │     └── Controllers (controllers/*.py)
  │           └── Services (services/*.py)
  │                 └── Models (models/*.py)
  └── Utils (utils/*.py)
```

## 3. Chuẩn module

- Mỗi module đi kèm schema Pydantic ở `models/`
- Business logic nằm tại `services/`
- Routers tự động include trong `app/main.py`
- Controllers xử lý phối hợp nhiều service khi luồng phức tạp

## 4. Dữ liệu mẫu

- `modules/course_module.py`: cung cấp dataset "Con lắc lò xo" (được tái sử dụng cho seed script và testing)
- `scripts/initial_data.py`: seed khóa học demo + hàm `seed_demo_courses()` cho môi trường dev
- Test database trong `tests/test_database_connection.py`

## 5. Checklist Endpoint Skeleton (Placeholder)

| Nhóm | Endpoint | Schema phản hồi | Ghi chú |
|------|----------|-----------------|--------|
| Auth | `GET /api/v1/auth/me` | `MessageResponse` | Placeholder thông tin user hiện tại |
| Assessments | `POST /api/v1/assessments/skill-test` | `AssessmentResultResponse` | Gắn với recommendation mock |
| Assessments | `GET /api/v1/assessments/{id}/result` | `AssessmentResultResponse` | Kết quả chi tiết placeholder |
| Courses | `GET /api/v1/courses/public` | `MessageResponse` | Danh sách khóa công khai (placeholder) |
| Courses | `POST /api/v1/courses/from-prompt` | `MessageResponse` | Tạo khóa học bằng AI mock |
| Enrollments | `GET /api/v1/enrollments/{course_id}/progress` | `ProgressSnapshot` | Dữ liệu demo phục vụ dashboard |
| Analytics | `GET /api/v1/analytics/student-dashboard` | `StudentDashboardResponse` | Dựa trên `build_student_dashboard` |
| Analytics | `GET /api/v1/analytics/instructor/overview` | `MessageResponse` | Placeholder thống kê giảng viên |
| Classes | `POST /api/v1/classes/{id}/invite` | `ClassInvitation` | Tạo join code demo |
| Classes | `GET /api/v1/classes/{id}` | `MessageResponse` | Placeholder chi tiết lớp |
| Quiz | `POST /api/v1/quizzes/from-course/{course_id}` | `QuizResponse` | Dùng generator demo |
| Quiz AI | `POST /api/v1/quizzes/ai-builder` | `QuizGenerationResponse` | Dùng `GenAIService` mock |
| Admin | `GET /api/v1/admin/dashboard/overview` | `SystemSummary` | Placeholder dashboard |
| Admin | `PUT /api/v1/admin/courses/{id}/approve` | `MessageResponse` | Placeholder duyệt khóa |
| Uploads | `POST /api/v1/uploads/{file_id}/process` | `MessageResponse` | Mô phỏng pipeline xử lý |
| Recommendations | `GET /api/v1/recommendations/learning-path` | `MessageResponse` | Placeholder lộ trình học |

## 6. Kiểm thử

- Sử dụng pytest với async test
- Các test mới cho module placeholder được đặt trong thư mục con (`tests/assessments/`, `tests/enrollment/`, ...)
- Mock external services (Google GenAI) qua lớp `services/ai_service.GenAIService`

## 7. Quy trình phát triển

1. Thêm schema mới tại `models/`
2. Viết dịch vụ tương ứng ở `services/`
3. Cập nhật router/controller để expose API
4. Viết test tại `tests/` (unit + integration)
5. Cập nhật docs nếu luồng mới
