"""Module tổng hợp logic khóa học để tái sử dụng."""
from models.models import CourseCreate, LessonContent, ModuleOutline


def build_demo_course() -> CourseCreate:
    """Sinh dữ liệu khóa học mẫu "Con lắc lò xo"."""

    return CourseCreate(
        title="Lý thuyết Con lắc Lò xo",
        description="Nội dung chuẩn hóa từ tài liệu vật lý lớp 11.",
        level="intermediate",
        category="Vật lý",
        estimated_duration_hours=3.5,
        tags=["vat-ly", "dao-dong", "con-lac"],
        modules=[
            ModuleOutline(
                name="Con lắc đơn",
                objectives=[
                    "Nắm cấu tạo và nguyên lý hoạt động",
                    "Áp dụng công thức tính chu kỳ T = 2π√(l/g)",
                ],
                lessons=[
                    LessonContent(
                        title="Cấu tạo con lắc đơn",
                        summary="Trình bày thành phần vật nhỏ khối lượng m treo vào dây dài l không giãn.",
                        duration_minutes=20,
                    ),
                    LessonContent(
                        title="Chu kỳ con lắc đơn",
                        summary="Phân tích công thức T=2π√(l/g) và ý nghĩa từng đại lượng.",
                        duration_minutes=25,
                    ),
                ],
            ),
            ModuleOutline(
                name="Con lắc lò xo",
                objectives=[
                    "Hiểu cấu tạo hệ lò xo - vật",
                    "Tính chu kỳ dựa trên khối lượng và độ cứng",
                ],
                lessons=[
                    LessonContent(
                        title="Cấu tạo con lắc lò xo",
                        summary="Mô tả hệ vật khối lượng m gắn với lò xo độ cứng k, vị trí cân bằng.",
                        duration_minutes=20,
                    ),
                    LessonContent(
                        title="Chu kỳ con lắc lò xo",
                        summary="Giải thích công thức T=2π√(m/k) và ví dụ minh họa.",
                        duration_minutes=25,
                    ),
                ],
            ),
        ],
    )
