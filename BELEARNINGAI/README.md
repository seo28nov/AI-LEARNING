# BeLearning AI - Nền tảng Giáo dục Backend

> **Phiên bản**: 2.0  
> **Cập nhật**: 2025-10-16

Nền tảng giáo dục hiện đại với tính năng AI, hệ thống RAG, và quản lý khóa học toàn diện.

## Tính năng chính

### Học tập với AI
- **Hệ thống RAG**: Retrieval-Augmented Generation với ChromaDB
- **Chat thông minh**: AI trả lời dựa trên nội dung khóa học thực tế
- **Tạo khóa học**: AI tự động tạo khóa học từ prompt
- **Tạo quiz**: Tạo câu hỏi thông minh từ nội dung khóa học

### Quản lý khóa học
- **Hệ thống đa vai trò**: Admin, Giảng viên, Học viên
- **Phê duyệt khóa học**: Quy trình kiểm duyệt khóa học
- **Theo dõi tiến độ**: Theo dõi tiến độ chi tiết
- **Hệ thống lớp học**: Giảng viên tạo lớp, học viên tham gia bằng code

### Bảo mật và xác thực
- **JWT Authentication**: Xác thực dựa trên token bảo mật
- **RBAC**: Kiểm soát truy cập dựa trên vai trò
- **Password Hashing**: Bcrypt với salt
- **CORS**: Whitelist origin có thể cấu hình

### Hiệu năng và khả năng mở rộng
- **Bất đồng bộ**: FastAPI + Motor (async MongoDB)
- **Vector Search**: Tìm kiếm ngữ nghĩa nhanh với ChromaDB
- **Indexing hiệu quả**: MongoDB indexes cho truy vấn tối ưu
- **Batch Processing**: Tạo embedding hiệu quả

---

## Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│                  (React/Next.js Frontend)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┴────────────────────────────────────┐
│                      API LAYER (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Routers  │─▶│Controller│─▶│ Services │─▶│ External │       │
│  │ (18)     │  │ (18)     │  │ (11)     │  │ APIs     │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                          Middleware                             │
│                    (Auth, RBAC, CORS)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│   MongoDB      │  │   ChromaDB      │  │  Google AI     │
│  (Database)    │  │ (Vector Store)  │  │ (Embeddings +  │
│                │  │                 │  │  Gemini Pro)   │
└────────────────┘  └─────────────────┘  └────────────────┘
```

**Kiến trúc phân tầng**:
1. **API Layer**: FastAPI routers + controllers
2. **Service Layer**: Business logic + tích hợp bên ngoài
3. **Data Layer**: MongoDB (Beanie ODM) + ChromaDB
4. **Security Layer**: JWT + RBAC middleware

---

## Bắt đầu nhanh

### Yêu cầu hệ thống
- Python 3.11+
- MongoDB 7.x (local hoặc Atlas)
- Google AI API Key (cho embeddings và chat)

### Cài đặt

```powershell
# 1. Clone repository
git clone <repo-url>
cd BELEARNINGAI

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env
# Edit .env với your keys:
#   - MONGODB_URL
#   - GOOGLE_API_KEY
#   - JWT_SECRET_KEY

# 5. Initialize database
python scripts/initial_data.py
python scripts/create_indexes.py

# 6. Run server
uvicorn app.main:app --reload
```

Server chạy tại: **http://localhost:8000**

### Tài liệu API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Kiểm thử

### Unit Tests
```powershell
pytest tests/
```

### Kiểm thử hệ thống RAG
```powershell
python scripts/test_rag.py
```

Bao gồm các tests:
- Embedding Service (Google AI)
- Vector Service (ChromaDB)
- Course Indexing Pipeline
- RAG Chat Integration

---

## Cấu trúc dự án

```
BELEARNINGAI/
├── app/
│   ├── main.py              # FastAPI application
│   └── database.py          # MongoDB connection
├── config/
│   ├── config.py            # Settings (Pydantic)
│   └── logging_config.py    # Logging setup
├── controllers/             # 18 controllers (82 functions)
│   ├── auth_controller.py
│   ├── course_controller.py
│   ├── chat_controller.py
│   └── ...
├── services/                # 11 services (business logic)
│   ├── embedding_service.py      # Google AI embeddings
│   ├── vector_service.py         # ChromaDB operations
│   ├── course_indexing_service.py # RAG indexing
│   ├── chat_service.py           # AI chat + RAG
│   └── ...
├── models/
│   └── models.py            # 16 MongoDB models
├── schemas/                 # Request/Response schemas
├── routers/                 # 18 API routers
├── middleware/              # Auth + RBAC
├── scripts/
│   ├── initial_data.py      # Seed database
│   ├── create_indexes.py    # MongoDB indexes
│   └── test_rag.py          # RAG testing
├── docs/                    # 35,000+ words documentation
│   ├── SETUP_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── ARCHITECTURE.md
│   ├── CHROMADB_RAG_GUIDE.md  # ⭐ Comprehensive RAG guide
│   └── ...
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

---

## Cấu hình

### Biến môi trường

```env
# Application
APP_NAME="BeLearning AI Platform"
ENVIRONMENT=development  # development/staging/production

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=belearning_db

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
GOOGLE_API_KEY=your-google-ai-api-key

# Vector Database (ChromaDB)
CHROMA_PERSIST_DIRECTORY=./chroma_db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Tại sao chọn ChromaDB?

ChromaDB được chọn làm vector database vì:
- **Local storage** - Ưu tiên bảo mật, dữ liệu lưu local
- **Miễn phí và mã nguồn mở** - Không có chi phí định kỳ
- **Dễ cài đặt** - Không cần API keys hoặc tài khoản
- **Sẵn sàng production** - Ổn định và hiệu năng tốt
- **Hoàn hảo cho giáo dục** - Nội dung nhạy cảm lưu local

---

## Tài liệu

### Cài đặt và triển khai
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** (5,000 words)
  - Các bước cài đặt
  - Cấu hình
  - Cài đặt database
  - Testing

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** (4,000 từ)
  - Cài đặt production
  - Triển khai Docker
  - Triển khai Cloud (AWS, GCP, Azure)
  - Giám sát và backup

### Kiến trúc và RAG
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** (6,000 từ)
  - Tổng quan hệ thống
  - Công nghệ sử dụng
  - Sơ đồ luồng dữ liệu
  - Tính năng bảo mật

- **[CHROMADB_RAG_GUIDE.md](docs/CHROMADB_RAG_GUIDE.md)** (14,000 từ)
  - Cài đặt ChromaDB
  - RAG pipeline
  - Chiến lược indexing
  - Xử lý sự cố

---

## API Endpoints

### Xác thực (`/auth`)
- `POST /register` - Đăng ký người dùng mới
- `POST /login` - Đăng nhập và nhận JWT
- `POST /refresh` - Làm mới access token
- `POST /logout` - Đăng xuất

### Khóa học (`/courses`)
- `GET /courses` - Danh sách khóa học (filter, search, pagination)
- `POST /courses` - Tạo khóa học (giảng viên)
- `GET /courses/{id}` - Chi tiết khóa học
- `PUT /courses/{id}` - Cập nhật khóa học
- `DELETE /courses/{id}` - Xóa khóa học
- `POST /courses/generate` - AI tạo khóa học

### Chat (`/chat`)
- `POST /chat/sessions` - Tạo chat session
- `POST /chat/sessions/{id}/messages` - Gửi tin nhắn (RAG enabled)
- `GET /chat/sessions/{id}` - Lịch sử chat
- `GET /chat/sessions` - Danh sách chats của user

### Admin (`/admin`)
- `GET /admin/users` - Danh sách tất cả users
- `PUT /admin/users/{id}/role` - Thay đổi vai trò
- `POST /admin/users/{id}/suspend` - Tạm ngưng user
- `POST /admin/courses/{id}/approve` - Phê duyệt khóa học
- `GET /admin/analytics` - Thống kê hệ thống

... và 100+ endpoints khác

---

## Công nghệ sử dụng

### Backend
- **FastAPI** 0.116 - Modern async web framework
- **Pydantic** 2.11 - Data validation
- **Motor** 3.5 - Async MongoDB driver
- **Beanie** 2.0 - Async ODM for MongoDB

### AI và ML
- **Google Generative AI** - Gemini Pro (chat + embeddings)
- **ChromaDB** 0.5 - Vector database cho RAG

### Bảo mật
- **python-jose** - Xử lý JWT
- **passlib** - Password hashing (bcrypt)

### Xử lý file
- **PyPDF2** - Trích xuất text từ PDF
- **python-magic** - Phát hiện loại file

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support

---

## Vai trò và quyền hạn

### Học viên (Student)
- Đăng ký khóa học
- Theo dõi tiến độ
- Làm quiz
- Chat với AI (RAG)
- Xem đề xuất

### Giảng viên (Instructor)
- Tạo/cập nhật khóa học
- Tạo lớp học
- Tạo quiz/đánh giá
- Xem thống kê
- Quản lý học viên

### Quản trị viên (Admin)
- Quản lý người dùng
- Phê duyệt/từ chối khóa học
- Xem thống kê hệ thống
- Backup hệ thống
- Gửi thông báo

---

## Tính năng bảo mật

- JWT authentication với refresh tokens
- Role-based access control (RBAC)
- Password hashing (bcrypt)
- CORS protection
- Input validation (Pydantic)
- Rate limiting (đang lên kế hoạch)
- SQL injection prevention (MongoDB)

---

## Kiểm thử

### Test Coverage

**Integration Tests** (82 tests)
```powershell
# Chạy tất cả tests
pytest -v

# Chạy test cụ thể
pytest tests/test_auth.py -v
pytest tests/test_courses.py -v
pytest tests/test_chat.py -v
```

**User Flow Tests** (3 kịch bản)
```powershell
# Test quy trình người dùng hoàn chỉnh
python scripts/test_user_flows.py
```

**AI Integration Tests** (6 tests)
```powershell
# Test tính năng AI: generation, RAG, performance
python scripts/test_ai_integration.py
```

**RAG System Tests**
```powershell
# Test vector database và semantic search
python scripts/test_rag.py
```

**Security Tests** (4 danh mục)
```powershell
# Test authentication, authorization, input validation
python scripts/test_security.py
```

**Performance Tests** (5 danh mục)
```powershell
# Test thời gian response API, concurrency, database
python scripts/test_performance.py
```

**E2E Tests** (3 user journeys)
```powershell
# Test quy trình hoàn chỉnh từ đầu đến cuối
python scripts/test_e2e.py
```

Chi tiết xem `docs/TESTING_GUIDE.md`

---

## Hiệu năng

**Thời gian response API**
- Trung bình: <100ms (EXCELLENT)
- P95: <300ms
- P99: <500ms

**Vector Search**
- Trung bình: <50ms cho 1000+ documents
- Concurrent searches: 20+ req/s

**Thao tác Database**
- Insert: <50ms trung bình
- Query: <100ms cho truy vấn phức tạp với indexes

**Xử lý đồng thời**
- 20+ concurrent requests: Hiệu năng ổn định
- Throughput: 50+ req/s

Chi tiết metrics xem output của `python scripts/test_performance.py`

---

## Triển khai

### Docker

```powershell
# Build image
docker build -t belearning-api .

# Run container
docker run -p 8000:8000 --env-file .env belearning-api
```

### Docker Compose

```powershell
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

### Production Checklist
- [ ] Đổi `JWT_SECRET_KEY` thành giá trị ngẫu nhiên bảo mật
- [ ] Set `ENVIRONMENT=production`
- [ ] Sử dụng MongoDB Atlas hoặc production instance
- [ ] Bật HTTPS (reverse proxy)
- [ ] Setup backup cho ChromaDB data
- [ ] Cấu hình monitoring (Sentry, etc.)
- [ ] Review CORS origins
- [ ] Setup CI/CD pipeline

---

## Xử lý sự cố

### Vấn đề thường gặp

**1. Kết nối MongoDB thất bại**
```powershell
# Check MongoDB is running
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux

# Test connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print(AsyncIOMotorClient('mongodb://localhost:27017').server_info())"
```

**2. Google AI API Error**
- Verify `GOOGLE_API_KEY` in `.env`
- Check API quota: https://aistudio.google.com/app/apikey
- Free tier: 60 requests/minute

**3. ChromaDB Initialization Failed**
```powershell
# Check directory permissions
icacls .\chroma_db  # Windows
ls -la ./chroma_db  # Linux

# Recreate directory
Remove-Item -Recurse -Force .\chroma_db
New-Item -ItemType Directory .\chroma_db
```

**4. Import Errors**
```powershell
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

- **Documentation**: `/docs` folder
- **Issues**: GitHub Issues
- **Email**: support@belearning.ai (placeholder)

---

## 📄 License

[Your License Here - e.g., MIT]

---

## 🎉 Acknowledgments

- **FastAPI** - Amazing web framework
- **Google AI** - Powerful AI models
- **ChromaDB** - Excellent vector database
- **MongoDB** - Reliable database

---

**Made with ❤️ for education**

## 1. Tính năng giai đoạn này

- **Học viên**: Đăng ký/đăng nhập, bài đánh giá năng lực, học khóa cá nhân/giảng viên, chat AI, theo dõi tiến độ
- **Giảng viên**: Quản lý lớp, sao chép/tạo khóa, tạo quiz/bài tập, analytics, thông báo
- **Admin**: Quản trị người dùng và phân quyền, kiểm duyệt khóa, giám sát hệ thống, broadcast

## Cấu trúc thư mục

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

## Yêu cầu hệ thống

- Python 3.11.x
- MongoDB 7.x (local hoặc Atlas)
- (Tùy chọn) Docker + Docker Compose nếu muốn chạy bằng container

## Khởi chạy nhanh trên máy local

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

Sau khi server chạy, FastAPI sẽ tự sinh tài liệu:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Chạy bằng Docker Compose

```powershell
# Build image và khởi động API + MongoDB
docker compose up --build

# Dừng stack khi không dùng nữa
docker compose down
```

MongoDB được mount qua volume theo cấu hình trong `docker-compose.yml`.

## Tài liệu liên quan

- `docs/CHROMADB_RAG_GUIDE.md`: Hướng dẫn chi tiết về RAG system
- `docs/TESTING_GUIDE.md`: Hướng dẫn testing
- `docs/ARCHITECTURE.md`: Kiến trúc hệ thống
- `docs/DEPLOYMENT.md`: Hướng dẫn triển khai

Nếu phát hiện thư mục/file chưa rõ chức năng, thêm ghi chú trực tiếp vào `docs/structure_notes.md`.
