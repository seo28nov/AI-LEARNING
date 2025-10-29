# AI-LEARNING
https://ailearningdemoui.vercel.app/





# TÀI LIỆU CHI TIẾT CHỨC NĂNG HỆ THỐNG AI LEARNING PLATFORM
> Người tạo: NGUYỄN NGỌC TUẤN ANH  
> Phân tích chi tiết chức năng theo vai trò và nhóm chức năng  
> Ngày cập nhật: 29/10/2025

## MỤC LỤC

1. [TỔNG QUAN PHÂN QUYỀN](#1-tổng-quan-phân-quyền)
2. [CHỨC NĂNG CHO HỌC VIÊN (STUDENT)](#2-chức-năng-cho-học-viên-student)
3. [CHỨC NĂNG CHO GIẢNG VIÊN (INSTRUCTOR)](#3-chức-năng-cho-giảng-viên-instructor)
4. [CHỨC NĂNG CHO QUẢN TRỊ VIÊN (ADMIN)](#4-chức-năng-cho-quản-trị-viên-admin)
5. [CHỨC NĂNG CHUNG (COMMON)](#5-chức-năng-chung-common)


---

## 1. TỔNG QUAN PHÂN QUYỀN

### 1.1 Cấu trúc vai trò

| Vai trò | Mã định danh | Mức độ quyền | Đối tượng chính |
|---------|--------------|--------------|-----------------|
| **Admin** | `admin` |  (Level 3) | Quản lý toàn hệ thống |
| **Instructor** | `instructor` |  (Level 2) | Giảng dạy và quản lý lớp học |
| **Student** | `student` | (Level 1) | Học tập và tự phát triển |


## 2. CHỨC NĂNG CHO HỌC VIÊN (STUDENT)

### 2.1 NHÓM CHỨC NĂNG: XÁC THỰC & QUẢN LÝ TÀI KHOẢN

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.1.1 | **Đăng ký tài khoản** | Tạo tài khoản mới với email, mật khẩu.  | `POST /api/v1/auth/register` | Public |
| 2.1.2 | **Đăng nhập** |  email + password. Nhận JWT access token và refresh token. | `POST /api/v1/auth/login` | Public |
| 2.1.3 | **Đăng xuất** | Vô hiệu hóa token hiện tại. Xóa session trên client. | `POST /api/v1/auth/logout` | Student |
| 2.1.4 | **Xem hồ sơ cá nhân** | Hiển thị thông tin: tên, email, avatar, bio, ngày tham gia. | `GET /api/v1/users/me` | Student |
| 2.1.5 | **Cập nhật hồ sơ** | Chỉnh sửa tên, avatar, bio, thông tin liên hệ, sở thích. | `PUT /api/v1/users/me` | Student |


---

### 2.2 NHÓM CHỨC NĂNG: ĐÁNH GIÁ NĂNG LỰC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.2.1 | **Xem danh sách bài đánh giá** | Hiển thị các bài test theo danh mục: Programming, Design, Business, Marketing, etc. | `GET /api/v1/assessments` | Student |
| 2.2.2 | **Làm bài đánh giá** | Trả lời các câu hỏi trắc nghiệm/quizz. Có giới hạn thời gian. AI đánh giá tự động. | `POST /api/v1/assessments/{id}/attempt` | Student |
| 2.2.3 | **Xem kết quả đánh giá** | Điểm số, phân loại trình độ (Beginner/Intermediate/Advanced). Phân tích điểm mạnh/yếu. | `GET /api/v1/assessments/{id}/results` | Student |
| 2.2.4 | **Nhận gợi ý khóa học** | AI phân tích kết quả và đề xuất khóa học phù hợp với level. | `GET /api/v1/recommendations/based-on-assessment` | Student |

---

### 2.3 NHÓM CHỨC NĂNG: ĐĂNG KÝ KHÓA HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.3.1 | **Tìm kiếm khóa học** | Tìm theo từ khóa, danh mục, level, giá. Hỗ trợ filter và sort. | `GET /api/v1/courses/search` | Student |
| 2.3.2 | **Xem danh sách khóa học** | Hiển thị tất cả khóa học được publish bởi Admin. | `GET /api/v1/courses/public` | Student |
| 2.3.3 | **Xem chi tiết khóa học** | Thông tin đầy đủ: mô tả, nội dung, giảng viên | `GET /api/v1/courses/{id}` | Student |
| 2.3.4 | **Đăng ký khóa học** | Enroll vào khóa học. | `POST /api/v1/enrollments` | Student |
| 2.3.5 | **Xem khóa học đã đăng ký** | Danh sách tất cả khóa học đang học, đã hoàn thành, bị hủy. | `GET /api/v1/enrollments/my-courses` | Student |
| 2.3.6 | **Hủy đăng ký khóa học** | Rút khỏi khóa học chưa hoàn thành. | `DELETE /api/v1/enrollments/{id}` | Student |

---

### 2.4 NHÓM CHỨC NĂNG: HỌC TẬP & THEO DÕI TIẾN ĐỘ

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.4.1 | **Xem nội dung bài học** | Đọc content text, xem video, tài liệu đính kèm. | `GET /api/v1/courses/{id}/lessons/{lessonId}` | Student (enrolled) |
| 2.4.2 | **Đánh dấu hoàn thành bài học** | Mark lesson as completed. Tự động cập nhật progress. | `POST /api/v1/progress/complete-lesson` | Student |
| 2.4.3 | **Xem tiến độ khóa học** | Phần trăm hoàn thành, số bài đã học/tổng số. Progress bar. | `GET /api/v1/progress/course/{courseId}` | Student |
| 2.4.4 | **Làm quiz** | Trả lời câu hỏi trắc nghiệm/quizz. Giới hạn thời gian. | `POST /api/v1/quizzes/{id}/attempt` | Student |
| 2.4.5 | **Xem kết quả quiz** | Điểm số, đáp án đúng/sai, giải thích chi tiết. | `GET /api/v1/quizzes/{id}/results` | Student |
| 2.4.6 | **Làm lại quiz** | Cho phép làm lại nhiều lần để cải thiện điểm. | `POST /api/v1/quizzes/{id}/retake` | Student |

---

### 2.5 NHÓM CHỨC NĂNG: KHÓA HỌC CÁ NHÂN (PERSONAL COURSE)

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.5.1 | **Tạo khóa học từ prompt** | Nhập mô tả, AI tự động sinh cấu trúc khóa học và nội dung. | `POST /api/v1/courses/from-prompt` | Student |
| 2.5.2 | **Tạo khóa học thủ công** | Tạo khóa học trống, tự thêm module và lesson. | `POST /api/v1/courses/personal` | Student |
| 2.5.3 | **Xem danh sách khóa học cá nhân** | Hiển thị tất cả khóa học do mình tạo. | `GET /api/v1/courses/my-personal` | Student |
| 2.5.4 | **Chỉnh sửa khóa học cá nhân** | Sửa tiêu đề, mô tả, thêm/xóa module, lesson. | `PUT /api/v1/courses/personal/{id}` | Student (owner) |
| 2.5.5 | **Xóa khóa học cá nhân** | Xóa vĩnh viễn khóa học đã tạo. | `DELETE /api/v1/courses/personal/{id}` | Student (owner) |


---

### 2.6 NHÓM CHỨC NĂNG: TƯƠNG TÁC VỚI AI CHATBOT

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.6.1 | **Chat về khóa học** | Hỏi đáp với AI về nội dung khóa học cụ thể. AI trả lời dựa trên context của khóa học. | `POST /api/v1/chat/course/{courseId}` | Student (enrolled) |
| 2.6.2 | **Chat chung** | Hỏi đáp bất kỳ chủ đề nào | `POST /api/v1/chat/general` | Student | (Xem xét bỏ qua)
| 2.6.3 | **Xem lịch sử chat** | Lưu trữ toàn bộ conversation. Có thể xem lại. | `GET /api/v1/chat/history` | Student |
| 2.6.4 | **Xóa lịch sử chat** | Xóa conversation cụ thể hoặc toàn bộ. | `DELETE /api/v1/chat/history/{id}` | Student |


### 2.7 NHÓM CHỨC NĂNG: DASHBOARD & ANALYTICS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.7.1 | **Dashboard tổng quan** | Hiển thị: khóa học đang học, tiến độ, quiz gần đây | `GET /api/v1/dashboard/student` | Student |
| 2.7.2 | **Thống kê học tập** | Số giờ học, số bài hoàn thành, điểm trung bình, streak. | `GET /api/v1/analytics/learning-stats` | Student |
| 2.7.3 | **Biểu đồ tiến độ** | Visualize progress theo thời gian (ngày/tuần/tháng). | `GET /api/v1/analytics/progress-chart` | Student |
| 2.7.4 | **Đề xuất khóa học** | AI gợi ý khóa học dựa trên lịch sử học và sở thích. | `GET /api/v1/recommendations` | Student |

---


## 3. CHỨC NĂNG CHO GIẢNG VIÊN (INSTRUCTOR)

### 3.1 NHÓM CHỨC NĂNG: QUẢN LÝ LỚP HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.1.1 | **Tạo lớp học mới** | Tạo lớp từ khóa học công khai có sẵn. Đặt tên lớp, mô tả, thời gian bắt đầu/kết thúc. | `POST /api/v1/classes` | Instructor |
| 3.1.2 | **Xem danh sách lớp học** | Hiển thị tất cả lớp do mình quản lý. | `GET /api/v1/classes/my-classes` | Instructor |
| 3.1.3 | **Xem chi tiết lớp học** | Thông tin lớp: số học viên, khóa học gắn liền, tiến độ chung. | `GET /api/v1/classes/{id}` | Instructor (owner) |
| 3.1.4 | **Chỉnh sửa thông tin lớp** | Sửa tên, mô tả, thời gian, trạng thái lớp. | `PUT /api/v1/classes/{id}` | Instructor (owner) |
| 3.1.5 | **Xóa lớp học** | Xóa lớp (chỉ khi chưa có học viên hoặc đã kết thúc). | `DELETE /api/v1/classes/{id}` | Instructor (owner) |


---

### 3.2 NHÓM CHỨC NĂNG: QUẢN LÝ HỌC VIÊN

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.2.1 | **Mời học viên vào lớp** | Gửi link mời (1 mã code đơn giản) | `POST /api/v1/classes/{id}/invite` | Instructor (owner) |
| 3.2.2 | **Xem danh sách học viên** | Hiển thị tất cả học viên trong lớp với thông tin cơ bản. | `GET /api/v1/classes/{id}/students` | Instructor (owner) |
| 3.2.3 | **Xem hồ sơ học viên** | Chi tiết: tiến độ học, điểm quiz, hoạt động gần đây. | `GET /api/v1/classes/{id}/students/{studentId}` | Instructor (owner) |
| 3.2.4 | **Xóa học viên khỏi lớp** | Remove student khỏi lớp học. | `DELETE /api/v1/classes/{id}/students/{studentId}` | Instructor (owner) |
| 3.2.5 | **Theo dõi tiến độ học viên** | Xem chi tiết từng học viên: bài học đã hoàn thành, quiz đã làm. | `GET /api/v1/classes/{id}/progress` | Instructor (owner) |

---


### 3.3 NHÓM CHỨC NĂNG: QUẢN LÝ QUIZ & ASSIGNMENTS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.3.1 | **Tạo quiz** | Tạo bài kiểm tra với câu hỏi trắc nghiệm/quizz. Đặt thời gian, điểm pass. | `POST /api/v1/quizzes` | Instructor |
| 3.3.2 | **Xem danh sách quiz** | Tất cả quiz đã tạo cho các khóa học. | `GET /api/v1/quizzes/my-quizzes` | Instructor |
| 3.3.3 | **Chỉnh sửa quiz** | Sửa câu hỏi, đáp án, thời gian, điểm. | `PUT /api/v1/quizzes/{id}` | Instructor (owner) |
| 3.3.4 | **Xóa quiz** | Xóa quiz (chỉ khi chưa có học viên làm). | `DELETE /api/v1/quizzes/{id}` | Instructor (owner) |
| 3.3.5 | **Xem kết quả quiz của lớp** | Thống kê: điểm trung bình, số người pass/fail, phân bổ điểm. | `GET /api/v1/quizzes/{id}/class-results` | Instructor (owner) |

---
---

### 3.4 NHÓM CHỨC NĂNG: DASHBOARD & ANALYTICS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.4.1 | **Dashboard giảng viên** | Tổng quan: số lớp, số học viên, lớp đã tạo| `GET /api/v1/dashboard/instructor` | Instructor |
| 3.4.2 | **Thống kê lớp học** | Số học viên , điểm trung bình. | `GET /api/v1/analytics/class/{id}` | Instructor (owner) |
| 3.4.3| **Báo cáo tiến độ lớp** | Chi tiết tiến độ từng học viên hoặc tổng quan | `GET /api/v1/classes/{id}/progress-report` | Instructor (owner) |

---

## 4. CHỨC NĂNG CHO QUẢN TRỊ VIÊN (ADMIN)

### 4.1 NHÓM CHỨC NĂNG: QUẢN LÝ NGƯỜI DÙNG

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.1.1 | **Xem danh sách tất cả người dùng** | Hiển thị tất cả users: Students, Instructors, Admins. Filter theo role, status. | `GET /api/v1/admin/users` | Admin |
| 4.1.2 | **Xem chi tiết người dùng** | Thông tin đầy đủ: profile, hoạt động | `GET /api/v1/admin/users/{id}` | Admin |
| 4.1.3 | **Tạo người dùng mới** | Tạo account cho user (ví dụ: tạo Instructor mới). | `POST /api/v1/admin/users` | Admin |
| 4.1.4 | **Chỉnh sửa thông tin người dùng** | Sửa role, email, tên, status. | `PUT /api/v1/admin/users/{id}` | Admin |
| 4.1.5 | **Xóa người dùng** | Xóa vĩnh viễn  | `DELETE /api/v1/admin/users/{id}` | Admin |
| 4.1.6 | **Phân quyền người dùng** | Thay đổi role: Student ↔ Instructor ↔ Admin. | `PUT /api/v1/admin/users/{id}/role` | Admin |
| 4.1.7 | **Reset mật khẩu người dùng** | Force reset password cho user. | `POST /api/v1/admin/users/{id}/reset-password` | Admin |

---

### 4.2 NHÓM CHỨC NĂNG: QUẢN LÝ KHÓA HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.2.1 | **Xem tất cả khóa học** | Danh sách toàn bộ courses: public, personal. | `GET /api/v1/admin/courses` | Admin |
| 4.2.2 | **Xem chi tiết khóa học** | Thông tin đầy đủ: content, modules, lessons | `GET /api/v1/admin/courses/{id}` | Admin |
| 4.2.3 | **Tạo khóa học** | Tạo khóa học mới cho hệ thống. | `POST /api/v1/admin/courses` | Admin |
| 4.2.4 | **Chỉnh sửa bất kỳ khóa học** | Sửa nội dung, cấu trúc của mọi khóa học (kể cả personal). | `PUT /api/v1/admin/courses/{id}` | Admin |
| 4.2.5 | **Xóa khóa học** | Xóa bất kỳ khóa học nào. | `DELETE /api/v1/admin/courses/{id}` | Admin |
| 4.2.6 | **Xem thống kê khóa học** | Số lượt enroll| `GET /api/v1/admin/courses/{id}/stats` | Admin |

---

### 4.3 NHÓM CHỨC NĂNG: QUẢN LÝ LỚP HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.3.1 | **Xem tất cả lớp học** | Danh sách toàn bộ classes từ mọi giảng viên. | `GET /api/v1/admin/classes` | Admin |
| 4.3.2 | **Xem chi tiết lớp học** | Thông tin: giảng viên, học viên, khóa học, tiến độ. | `GET /api/v1/admin/classes/{id}` | Admin |
| 4.3.3 | **Xóa lớp học** | Xóa bất kỳ lớp nào. | `DELETE /api/v1/admin/classes/{id}` | Admin |
| 4.3.4 | **Quản lý học viên trong lớp** | Thêm/xóa học viên bất kỳ. | `POST/DELETE /api/v1/admin/classes/{id}/students` | Admin |

---

### 4.4 NHÓM CHỨC NĂNG: DASHBOARD & ANALYTICS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.4.1 | **Dashboard admin tổng quan** | Số users, courses, classes| `GET /api/v1/admin/dashboard` | Admin |
| 4.4.2 | **Thống kê người dùng** | Số lượng theo role | `GET /api/v1/admin/analytics/users` | Admin |
| 4.4.3 | **Thống kê khóa học** | Top courses | `GET /api/v1/admin/analytics/courses` | Admin |

---

## 5. CHỨC NĂNG CHUNG (COMMON)

### 5.1 NHÓM CHỨC NĂNG: TÌM KIẾM & LỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 5.1.1 | **Tìm kiếm toàn hệ thống** | Search courses, users, classes. Full-text search. | `GET /api/v1/search` | All roles |
| 5.1.2 | **Filter theo category** | Lọc khóa học theo danh mục. | `GET /api/v1/search/filter` | All roles |

---

