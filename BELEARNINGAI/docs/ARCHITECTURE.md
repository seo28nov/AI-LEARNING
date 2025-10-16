# 🏗 Kiến trúc Hệ thống BE Learning AI

Tài liệu mô tả kiến trúc tổng thể của hệ thống học tập thông minh BE Learning AI.

## Mục lục

1. [Tổng quan Kiến trúc](#tổng-quan-kiến-trúc)
2. [Các Tầng Hệ thống](#các-tầng-hệ-thống)
3. [Flow Dữ liệu](#flow-dữ-liệu)
4. [Database Schema](#database-schema)
5. [Authentication & Authorization](#authentication--authorization)
6. [AI & RAG Pipeline](#ai--rag-pipeline)
7. [API Design](#api-design)
8. [Scalability](#scalability)

---

## Tổng quan Kiến trúc

### Mô hình Kiến trúc

BE Learning AI sử dụng **Layered Architecture** (Kiến trúc phân tầng) với các tầng rõ ràng:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  (Web App, Mobile App, Admin Dashboard)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                       │
│  • NGINX Reverse Proxy                                      │
│  • SSL/TLS Termination                                      │
│  • Rate Limiting                                            │
│  • Load Balancing                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                      (FastAPI App)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌───────────────┐   ┌───────────────┐ │
│  │  MIDDLEWARE  │   │    ROUTERS    │   │  CONTROLLERS  │ │
│  │              │   │               │   │               │ │
│  │ • Auth/JWT   │──▶│ • 18 routers  │──▶│ • 18 ctrls   │ │
│  │ • RBAC       │   │ • /api/v1/*   │   │ • Logic flow │ │
│  │ • CORS       │   │ • REST API    │   │               │ │
│  └──────────────┘   └───────────────┘   └───────┬───────┘ │
└──────────────────────────────────────────────────┼─────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│  • 11 Business Services                                     │
│  • Business Logic                                           │
│  • External API Integration                                 │
├─────────────────────────────────────────────────────────────┤
│  auth_service      user_service      course_service         │
│  enrollment_srv    classes_service   progress_service       │
│  quiz_service      assessment_srv    chat_service           │
│  upload_service    analytics_service                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  DATA LAYER     │ │  AI LAYER    │ │  STORAGE LAYER  │
│                 │ │              │ │                 │
│  • MongoDB      │ │ • Google AI  │ │ • File Storage  │
│  • Beanie ODM   │ │ • Gemini Pro │ │ • S3/Local      │
│  • 16 Models    │ │ • Embeddings │ │                 │
│                 │ │              │ │                 │
│  • Vector DB    │ │ • RAG System │ │                 │
│  • Pinecone/    │ │              │ │                 │
│    Weaviate/    │ │              │ │                 │
│   FAISS VDB    │ │              │ │                 │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.104.1 |
| **Language** | Python | 3.9+ |
| **Database** | MongoDB | 5.0+ |
| **ODM** | Beanie | 1.23.6 |
| **Auth** | JWT (python-jose) | 3.3.0 |
| **AI Engine** | Google Generative AI | 0.3.1 |
| **Vector DB** | FAISS (Facebook AI) | ✅ |
| **Server** | Uvicorn | 0.24.0 |
| **Reverse Proxy** | NGINX | Latest |

---

## Các Tầng Hệ thống

### 1. Presentation Layer (Routers)

**Chức năng:** Định nghĩa các API endpoints, xử lý HTTP requests/responses

**Thành phần:**
- 18 router modules trong `routers/`
- Mỗi router đảm nhiệm một domain cụ thể
- Prefix: `/api/v1/{domain}`

**Ví dụ:**
```python
# routers/courses_router.py
@router.get("/courses", response_model=dict)
async def list_courses(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    return await course_controller.handle_list_courses(
        user_id=current_user["sub"],
        skip=skip,
        limit=limit
    )
```

**Router List:**
1. `auth_router.py` - Authentication
2. `users_router.py` - User management
3. `courses_router.py` - Course CRUD
4. `enrollment_router.py` - Course enrollment
5. `classes_router.py` - Class management
6. `quiz_router.py` - Quiz system
7. `chat_router.py` - AI chat
8. `ai_router.py` - AI features
9. `upload_router.py` - File uploads
10. `progress_router.py` - Learning progress
11. `notification_router.py` - Notifications
12. `dashboard_router.py` - Dashboard stats
13. `analytics_router.py` - Analytics
14. `assessments_router.py` - Skill assessment
15. `admin_router.py` - Admin functions
16. `search_router.py` - Search
17. `recommendation_router.py` - Recommendations
18. `permissions_router.py` - Permissions

### 2. Controller Layer

**Chức năng:** Điều phối request, gọi services, xử lý exceptions

**Trách nhiệm:**
- Validate request data
- Gọi service functions
- Transform response format
- Handle business exceptions

**Pattern:**
```python
# controllers/course_controller.py
async def handle_create_course(payload: dict, user_id: str) -> dict:
    # 1. Validate
    if not payload.get("title"):
        raise HTTPException(400, "Title required")
    
    # 2. Call service
    course = await course_service.create_course(
        title=payload["title"],
        user_id=user_id
    )
    
    # 3. Return formatted response
    return course
```

### 3. Service Layer

**Chức năng:** Business logic chính, tích hợp external services

**Services:**

#### auth_service.py
- Đăng ký/đăng nhập users
- Generate JWT tokens
- Verify email
- Reset password
- Refresh tokens

#### user_service.py
- CRUD user profiles
- Change password
- Manage roles
- User activation/deactivation

#### course_service.py
- CRUD courses
- Publish/unpublish courses
- Duplicate courses
- List courses với filters
- Course approval workflow

#### enrollment_service.py
- Enroll/unenroll courses
- Track enrollment status
- Progress tracking
- Get user enrollments

#### classes_service.py
- Create/manage classes
- Generate join codes
- Student roster
- Remove students

#### quiz_service.py
- Create quizzes
- Generate quizzes với AI
- Submit quiz attempts
- Grade quizzes
- Quiz statistics

#### assessment_service.py
- Skill assessments
- Generate questions với AI
- Evaluate answers
- Provide recommendations
- Track assessment history

#### chat_service.py
- Manage chat sessions
- Send/receive messages
- RAG integration (retrieve context)
- Generate AI responses
- Chat history

#### upload_service.py
- Handle file uploads
- Process documents
- Extract text
- Generate embeddings
- Store to vector DB

#### progress_service.py
- Track chapter progress
- Calculate completion rate
- Time tracking
- Learning streaks

#### analytics_service.py
- Student dashboards
- Instructor dashboards
- Admin system stats
- Course analytics
- User engagement metrics

### 4. Middleware Layer

**Chức năng:** Cross-cutting concerns

#### auth.py
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify JWT token và trả về user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
```

#### rbac.py
```python
def require_role(*allowed_roles: str):
    """Decorator kiểm tra role"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user["role"] not in allowed_roles:
                raise HTTPException(403, "Forbidden")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 5. Data Layer

**Database Models (16 models):**

```python
# models/models.py
class UserDocument(Document):
    email: str
    full_name: str
    hashed_password: str
    role: str  # admin, instructor, student
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("role", 1)]),
        ]
```

**Models:**
1. `UserDocument` - Users
2. `CourseDocument` - Courses
3. `EnrollmentDocument` - Enrollments
4. `ClassDocument` - Classes
5. `QuizDocument` - Quizzes
6. `QuizAttemptDocument` - Quiz submissions
7. `AssessmentDocument` - Assessments
8. `ChatSessionDocument` - Chat sessions
9. `ChatMessageDocument` - Chat messages
10. `UploadDocument` - File uploads
11. `ProgressDocument` - Learning progress
12. `NotificationDocument` - Notifications
13. `AnalyticsDocument` - Analytics data
14. `PermissionDocument` - Permissions
15. `AdminLogDocument` - Admin audit logs
16. `RecommendationDocument` - Recommendations

---

## Flow Dữ liệu

### 1. Authentication Flow

```
Client                  API                     Service                 Database
  │                      │                        │                       │
  ├──POST /auth/login───▶│                        │                       │
  │  {email, password}   │                        │                       │
  │                      ├──handle_login()───────▶│                       │
  │                      │                        ├──find_user()─────────▶│
  │                      │                        │◀─────user─────────────┤
  │                      │                        │                       │
  │                      │                        ├──verify_password()    │
  │                      │                        │                       │
  │                      │                        ├──create_tokens()      │
  │                      │◀─────tokens────────────┤                       │
  │◀─────200 OK──────────┤                        │                       │
  │  {access, refresh}   │                        │                       │
```

### 2. Create Course Flow (với RAG indexing)

```
Client              API              Controller         Service           Vector DB
  │                  │                   │                 │                  │
  ├─POST /courses───▶│                   │                 │                  │
  │                  ├──handle_create()─▶│                 │                  │
  │                  │                   ├──create_course()│                  │
  │                  │                   │                 ├──save to MongoDB │
  │                  │                   │                 │                  │
  │                  │                   │                 ├──extract_text()  │
  │                  │                   │                 │                  │
  │                  │                   │                 ├──generate_embed()│
  │                  │                   │                 │                  │
  │                  │                   │                 ├──index_vectors()─▶│
  │                  │                   │◀────course──────┤                  │
  │◀────201 Created──┤                   │                 │                  │
```

### 3. Chat với RAG Flow

```
Client          API           Controller      Chat Service    Search Service   Vector DB   AI
  │              │                │               │                │              │         │
  ├─POST /chat──▶│                │               │                │              │         │
  │ {message}    │                │               │                │              │         │
  │              ├─handle_send()─▶│               │                │              │         │
  │              │                ├─send_msg()───▶│                │              │         │
  │              │                │               ├─search()──────▶│              │         │
  │              │                │               │                ├──query──────▶│         │
  │              │                │               │                │◀─results─────┤         │
  │              │                │               │◀──context──────┤              │         │
  │              │                │               │                │              │         │
  │              │                │               ├─build_prompt() │              │         │
  │              │                │               │                │              │         │
  │              │                │               ├─generate()─────────────────────────────▶│
  │              │                │               │◀─response──────────────────────────────┤
  │              │                │◀──message─────┤                │              │         │
  │◀────200 OK───┤                │               │                │              │         │
```

---

## Database Schema

### Collections & Relationships

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴──────────┐     N      ┌──────────────┐
│   enrollments   │────────────│   courses    │
└──────┬──────────┘            └──────┬───────┘
       │ 1                            │ 1
       │                              │
       │ N                            │ N
┌──────┴──────────┐            ┌─────┴────────┐
│    progress     │            │   quizzes    │
└─────────────────┘            └──────────────┘

┌─────────────┐     1     ┌──────────────┐
│ chat_session├───────────│ chat_message │
└──────┬──────┘     N     └──────────────┘
       │ N
       │
       │ 1
   ┌───┴───┐
   │ users │
   └───────┘

┌─────────────┐
│ assessments │
└──────┬──────┘
       │ N
       │
       │ 1
   ┌───┴───┐
   │ users │
   └───────┘
```

### Key Indexes

```python
# Performance-critical indexes
users.email (unique)
users.role
courses.instructor_id
courses.is_public
courses.category
enrollments.user_id + course_id (compound, unique)
quiz_attempts.quiz_id + user_id
chat_sessions.user_id
progress.user_id + course_id
```

---

## Authentication & Authorization

### JWT Token Structure

```json
{
  "sub": "user_id_123",
  "email": "user@example.com",
  "role": "student",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"
}
```

### RBAC Matrix

| Endpoint | Student | Instructor | Admin |
|----------|---------|------------|-------|
| GET /courses/public | ✅ | ✅ | ✅ |
| POST /courses | ❌ | ✅ | ✅ |
| DELETE /courses/:id | ❌ | ✅ (own) | ✅ |
| GET /users | ❌ | ❌ | ✅ |
| POST /classes | ❌ | ✅ | ✅ |
| POST /admin/* | ❌ | ❌ | ✅ |
| POST /enrollment | ✅ | ✅ | ✅ |
| POST /quiz/:id/submit | ✅ | ✅ | ✅ |

### Security Features

- ✅ Password hashing với bcrypt (rounds=12)
- ✅ JWT access token (30 mins expiry)
- ✅ JWT refresh token (7 days expiry)
- ✅ Token blacklist on logout
- ✅ Email verification
- ✅ Password reset flow
- ✅ Rate limiting (60 req/min)
- ✅ CORS whitelist
- ✅ HTTPS only (production)
- ✅ Input validation với Pydantic

---

## AI & RAG Pipeline

### RAG Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    INDEXING PIPELINE                        │
└────────────────────────────────────────────────────────────┘

Course Content ──▶ Extract Text ──▶ Chunk (500 words)
                                           │
                                           ▼
                                    Generate Embeddings
                                    (Google AI - 768 dim)
                                           │
                                           ▼
                                    Store in Vector DB
                                    (Pinecone/Weaviate)


┌────────────────────────────────────────────────────────────┐
│                     QUERY PIPELINE                          │
└────────────────────────────────────────────────────────────┘

User Question ──▶ Generate Query Embedding ──▶ Vector Search
                                                      │
                                                      ▼
                                               Top 3 Chunks
                                                      │
                                                      ▼
                    Build Prompt with Context ◀──────┘
                             │
                             ▼
                    Google Gemini Pro
                             │
                             ▼
                    AI Response to User
```

### Embedding Model

- **Model:** `models/embedding-001` (Google AI)
- **Dimension:** 768
- **Task Types:** 
  - `retrieval_document` - cho course content
  - `retrieval_query` - cho user questions

### Vector Database Options

| Feature | Pinecone | Weaviate | FAISS |
|---------|----------|----------|-------|
| **Hosting** | Cloud | Cloud/Local | Local |
| **Setup** | Easy | Medium | Easiest |
| **Performance** | Excellent | Very Good | **Excellent** |
| **Cost** | Paid (free tier) | Paid (free tier) | **Free** |
| **Windows Support** | Good | Good | **Native** |
| **Build Requirements** | None | Docker | **None** |
| **Best for** | Production Scale | Flexible | **All Scenarios** |

---

## API Design

### RESTful Principles

✅ **Resource-based URLs:**
```
/api/v1/courses
/api/v1/courses/{id}
/api/v1/users/{id}/enrollments
```

✅ **HTTP Methods:**
- GET - Retrieve
- POST - Create
- PATCH - Partial update
- PUT - Full update
- DELETE - Remove

✅ **Status Codes:**
- 200 - Success
- 201 - Created
- 400 - Bad request
- 401 - Unauthorized
- 403 - Forbidden
- 404 - Not found
- 500 - Server error

✅ **Pagination:**
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

✅ **Error Format:**
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "field": "field_name"
}
```

### API Versioning

- **Current:** v1
- **Prefix:** `/api/v1/*`
- **Future:** `/api/v2/*` khi có breaking changes

---

## Scalability

### Horizontal Scaling

```
                    ┌─────────────┐
                    │ Load Balancer│
                    │   (NGINX)    │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
     │ API     │      │ API     │     │ API     │
     │ Server 1│      │ Server 2│     │ Server 3│
     └────┬────┘      └────┬────┘     └────┬────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼───────┐
                    │   MongoDB    │
                    │   Cluster    │
                    └──────────────┘
```

### Performance Optimizations

1. **Database:**
   - Indexes trên frequent queries
   - Connection pooling
   - Read replicas

2. **Caching:**
   - Redis cho sessions
   - Cache course listings
   - Cache user profiles

3. **Async Processing:**
   - Background tasks cho email
   - Async indexing cho RAG
   - Queue system (Celery)

4. **CDN:**
   - Static files
   - Course materials
   - Profile images

### Monitoring

- **Metrics:** Prometheus + Grafana
- **Logs:** ELK Stack / CloudWatch
- **Errors:** Sentry
- **APM:** New Relic / Datadog
- **Uptime:** UptimeRobot

---

## Deployment Strategy

### Environments

1. **Development** - Local machines
2. **Staging** - Cloud test environment
3. **Production** - Production servers

### CI/CD Pipeline

```
Code Push ──▶ GitHub ──▶ GitHub Actions
                            │
                            ▼
                    Run Tests (pytest)
                            │
                            ▼
                    Build Docker Image
                            │
                            ▼
                    Push to Registry
                            │
                    ┌───────┴────────┐
                    ▼                ▼
                Staging         Production
                Deploy          Deploy
```

### Backup Strategy

- **Database:** Daily automated backups
- **Retention:** 30 days
- **Storage:** S3/Cloud Storage
- **Recovery:** Point-in-time restore

---

## Security Considerations

### OWASP Top 10 Protection

✅ **A01 - Broken Access Control:** RBAC implemented  
✅ **A02 - Cryptographic Failures:** Bcrypt, JWT, HTTPS  
✅ **A03 - Injection:** Pydantic validation, NoSQL (MongoDB)  
✅ **A04 - Insecure Design:** Secure architecture  
✅ **A05 - Security Misconfiguration:** Environment configs  
✅ **A06 - Vulnerable Components:** Regular updates  
✅ **A07 - Authentication Failures:** JWT, rate limiting  
✅ **A08 - Data Integrity:** Input validation  
✅ **A09 - Logging Failures:** Comprehensive logging  
✅ **A10 - SSRF:** URL validation  

---

## Conclusion

Hệ thống BE Learning AI được thiết kế với:
- ✅ **Scalability** - Có thể mở rộng dễ dàng
- ✅ **Maintainability** - Code rõ ràng, dễ bảo trì
- ✅ **Security** - Bảo mật nhiều lớp
- ✅ **Performance** - Tối ưu hóa tốt
- ✅ **AI-Powered** - Tích hợp AI và RAG

Kiến trúc này sẵn sàng cho production và có thể scale lên hàng nghìn users.

---

**Tài liệu bổ sung:**
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Hướng dẫn cài đặt
- [DEPLOYMENT.md](DEPLOYMENT.md) - Hướng dẫn deploy
- [VECTOR_STORAGE.md](VECTOR_STORAGE.md) - RAG implementation

**Cập nhật:** October 2025  
**Version:** 1.0.0
