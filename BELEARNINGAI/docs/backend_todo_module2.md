# TODO Backend Mục 2 – Khung Triển Khai

> **Lưu ý chung**
> - Tất cả nhiệm vụ dưới đây chỉ yêu cầu xây dựng **khung và code mẫu** để team backend hiện thực chi tiết sau.
> - Mọi ghi chú, comment và commit phải dùng tiếng Việt theo `tailieubosung/`.
> - Các file đã tồn tại cần được mở rộng đúng module tương ứng, không tạo logic hoàn chỉnh.
> - Khi viết test mẫu, dùng `pytest.mark.skip(reason="placeholder")` nếu chưa có nội dung thật.

## 1. Đánh giá năng lực & Gợi ý khóa học (Assessments + Recommendation)

- [x] `schemas/assessment.py`: Bổ sung schema `AssessmentResultResponse`, `RecommendationItem` bám sát mục 5.1.1 và 5.1.2.
- [x] `services/assessment_service.py`: Thêm phương thức khung `evaluate_skill_test()` và `analyze_topics()` trả về dữ liệu giả lập.
- [x] `services/recommendation_service.py`: Khai báo hàm `build_learning_path()` và `suggest_courses()` với danh sách mẫu, có docstring mô tả luồng AI.
- [x] `controllers/assessment_controller.py`: Gọi service mới, mapping dữ liệu sang schema placeholder.
- [x] `routers/assessments_router.py`: Đảm bảo endpoint `POST /api/v1/assessments/skill-test` trả về schema mới.
- [x] `tests/assessments/test_assessment_routes.py`: Tạo file, viết test mẫu sử dụng client giả và đánh dấu skip.
- [x] `tests/recommendation/test_recommendation_service.py`: Thêm unit test khung cho `build_learning_path()`.

Ví dụ khung service:

```python
# services/assessment_service.py
async def evaluate_skill_test(payload: AssessmentPayload) -> AssessmentResult:
    """Phân tích kết quả quiz đầu vào và trả về thống kê tổng quan."""
    return AssessmentResult(score=82, level="intermediate", strengths=["variables"], weaknesses=["oop"])
```

## 2. Đăng ký & Theo dõi tiến độ (Enrollment + Progress + Analytics)

- [x] `schemas/enrollment.py`: Hoàn thiện model `ProgressSnapshot`, `StudySession`.
- [x] `services/enrollment_service.py`: Tạo hàm `create_enrollment_placeholder()` và `update_progress_demo()` trả về dict demo.
- [x] `services/analytics_service.py`: Bổ sung `build_student_dashboard()` trả dữ liệu thống kê mẫu theo HE_THONG.md.
- [x] `controllers/progress_controller.py`: Viết hàm khung `get_course_progress()` sử dụng services trên.
- [x] `routers/analytics_router.py`: Đảm bảo route `/analytics/student-dashboard` phản hồi schema mới.
- [x] `models/models.py`: Kiểm tra `ProgressDocument`, thêm trường `streak_days`, `learning_sessions` nếu thiếu.
- [x] `tests/enrollment/test_progress_flow.py`: File test mô tả luồng cập nhật tiến độ (skip tạm thời).

## 3. Quản lý lớp học & mã mời (Classes)

- [x] `schemas/classes.py`: Tạo schema `ClassInvitation`, `RosterStudent`.
- [x] `services/classes_service.py`: Viết phương thức `generate_join_code()` và `list_roster_preview()` trả về dữ liệu giả.
- [x] `controllers/classes_controller.py`: Dùng service mới cho endpoint mã mời và danh sách học viên.
- [x] `routers/classes_router.py`: Kiểm tra route `POST /classes/{class_id}/invite` và `GET /classes/{class_id}/roster`.
- [x] `tests/classes/test_class_invitation.py`: Test mẫu đảm bảo response chứa khóa `join_code`.

## 4. Quiz builder & AI hỗ trợ (Quiz + Assessment)

- [x] `schemas/quiz.py`: Thêm schema `QuizQuestionTemplate` và `QuizGenerationResponse`.
- [x] `services/quiz_service.py`: Tạo hàm `generate_quiz_template()` gọi `services/ai_service.GenAIService` (mock) với dữ liệu giả.
- [x] `controllers/quiz_controller.py`: Endpoint `/quiz/ai-builder` trả về kết cấu câu hỏi mẫu.
- [x] `tests/quiz/test_quiz_generator.py`: Test placeholder với skip, mô tả kỳ vọng dữ liệu.

## 5. Quản trị hệ thống & Audit (Admin + Permissions)

- [x] `schemas/admin.py`: Thêm `SystemSummary`, `UserAuditLog`.
- [x] `services/admin_service.py`: Viết phương thức `get_system_overview()` và `list_audit_logs()` trả về danh sách demo.
- [x] `services/permissions_service.py`: Bổ sung `list_roles_matrix()` trả về bảng quyền mẫu.
- [x] `controllers/admin_controller.py`: Khai thác service mới, đảm bảo dùng `current_user` đã inject.
- [x] `routers/admin_router.py`: Route `/dashboard/overview` dùng schema `SystemSummary`.
- [x] `tests/admin/test_admin_overview.py`: Test placeholder xác minh trường `uptime_percent` tồn tại.

## 6. Đồng bộ tài liệu & dữ liệu mẫu

- [x] `docs/docs.md`: Cập nhật bảng mapping endpoint ↔ schema mới, ghi rõ "placeholder".
- [x] `docs/structure_notes.md`: Đánh dấu các mục đã có khung trong checklist.
- [x] `modules/course_module.py`: Bổ sung dữ liệu course mẫu từ "con lắc lò xo" (tối đa 1-2 chương) dạng dict.
- [x] `scripts/initial_data.py`: Viết hàm `seed_demo_courses()` gọi vào dataset mới.

## 7. Kiểm thử & cấu hình

- [x] `tests/conftest.py`: Thêm fixture `fake_current_user` dùng chung cho các module.
- [x] `tests/__init__.py`: Đặt comment hướng dẫn bật/skip placeholder.
- [x] `config/config.py`: Ghi chú biến môi trường cần cho các module mới (ví dụ `RECOMMENDER_MODEL`).
- [x] `README.md` (trong `BELEARNINGAI/`): Cập nhật mục "Lộ trình triển khai" với liên kết tới file todo này.

## 8. Theo dõi tiến độ

- Sau khi hoàn tất từng checklist, cập nhật trạng thái vào bảng dưới (chỉ điền ✅/🚧/⛔).

| Nhóm nhiệm vụ | Trạng thái | Ghi chú |
|---------------|-----------|--------|
| Assessments & Recommendation | ✅ | Skeleton hoàn thành, chờ dữ liệu thật |
| Enrollment & Progress | ✅ | Đã có progress snapshot/demo analytics |
| Classes | ✅ | Join code & roster mẫu sẵn sàng |
| Quiz & AI Builder | ✅ | AI builder dùng GenAI mock |
| Admin & Audit | ✅ | Dashboard + audit log placeholder |
| Docs & Seed Data | ✅ | Docs, dataset & seed script cập nhật |
| Kiểm thử & Config | ✅ | Fixture + hướng dẫn skip test placeholder |

---
**Nhắc nhở**: Giữ nguyên cấu trúc module hiện tại, chỉ điền skeleton theo checklist. Khi chuyển sang logic thật phải cập nhật test và tài liệu tương ứng.
