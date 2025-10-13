# BELEARNINGAI Backend

BELEARNINGAI là bộ khung FastAPI mới tinh cho nền tảng học tập AI trong tài liệu `HE_THONG.md`. Tất cả router, controller và schema đã được dựng sẵn để đội backend tập trung triển khai nghiệp vụ mà không phải loay hoay với cấu trúc ban đầu.

> ⚠️ Mọi handler hiện trả về `MessageResponse` mô phỏng. Hãy thay thế dần bằng logic thật, cập nhật test và tài liệu khi hoàn thành.

## 1. Tính năng giai đoạn này

- **Student**: đăng ký/đăng nhập, bài đánh giá năng lực, học khóa cá nhân/giảng viên, chat AI, theo dõi tiến độ.
- **Instructor**: quản lý lớp, sao chép/tạo khóa, tạo quiz/bài tập, analytics, thông báo.
- **Admin**: quản trị người dùng & phân quyền, kiểm duyệt khóa, giám sát hệ thống, broadcast.


## 2. Cấu trúc thư mục

```text
BELEARNINGAI/
├── app/                 # Điểm khởi động FastAPI, lifecycle hook, router chính
├── config/              # Pydantic settings, logging, thông số môi trường
├── controllers/         # Điều phối request -> service, nơi gắn logic nghiệp vụ
├── docs/                # Tài liệu kỹ thuật đi kèm (mapping endpoint, ghi chú)
├── middleware/          # JWT auth, RBAC và helper bảo mật
├── models/              # Pydantic/Beanie models dùng chung
├── modules/             # Demo data, nội dung AI mẫu
├── routers/             # Định nghĩa tuyến API, gắn với controller tương ứng
├── schemas/             # Request/response schemas theo chuẩn Pydantic
├── services/            # Business logic & tích hợp bên ngoài (GenAI, analytics...)
├── scripts/             # Tiện ích CLI (seed dữ liệu, migrate...)
├── tests/               # Khung pytest để viết unit/integration test
├── utils/               # Hàm hỗ trợ (datetime, security, helper chung)
├── requirements.txt     # Danh sách dependency đã ghim version
├── setup.py             # Cho phép `pip install -e .`
├── Dockerfile           # Build image FastAPI
├── docker-compose.yml   # Dev stack (API + MongoDB)
└── README.md            # Tài liệu bạn đang đọc
```

Thông tin chi tiết hơn về vai trò từng thư mục nằm trong `docs/structure_notes.md`.

## 3. Yêu cầu hệ thống

- Python 3.11.x
- MongoDB 7.x (local hoặc Atlas)
- (Tùy chọn) Docker + Docker Compose nếu muốn chạy bằng container

## 4. Khởi chạy nhanh trên máy local

```powershell
# Tạo môi trường ảo (PowerShell)
python -m venv .venv
.venv\Scripts\Activate

# Cài đặt dependencies
pip install -r requirements.txt
pip install -e .

# Sao chép biến môi trường mẫu
copy .env.example .env
# Cập nhật .env với MongoDB URL, JWT secret, Google API key...

# Khởi chạy server dev
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# (Tùy chọn) chạy test khung để đảm bảo môi trường ổn
pytest
```

Sau khi server chạy, FastAPI sẽ **tự sinh tài liệu**:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## 5. Chạy bằng Docker Compose

```powershell
# Build image và khởi động API + MongoDB
docker compose up --build

# Dừng stack khi không dùng nữa
docker compose down
```

MongoDB được mount qua volume theo cấu hình trong `docker-compose.yml`. Hãy nhớ cập nhật biến môi trường trong file `compose` nếu deploy production.

## 6. Lộ trình hiện thực hóa

1. **Thay thế placeholder** trong `controllers/` bằng lời gọi sang `services/` với logic thật.
2. **Hoàn thiện service layer**, kết nối MongoDB, GenAI SDK, vector search...
3. **Viết test** (pytest + httpx) cho route quan trọng ngay khi hoàn thiện logic.
4. **Cập nhật tài liệu** (`docs/docs.md`, swagger descriptions) để team khác dễ phối hợp.

## 7. Tài liệu liên quan

- `docs/docs.md`: bảng mapping endpoint chi tiết, bám sát `HE_THONG.md`.
- `docs/backend_todo_module2.md`: checklist module còn dang dở.
- `HE_THONG.md`: chuẩn nghiệp vụ – mọi thay đổi cần xin ý kiến trước khi sửa.

Nếu phát hiện thư mục/file chưa rõ chức năng, thêm ghi chú trực tiếp vào `docs/structure_notes.md` để đồng đội mới vào dễ bắt nhịp.
