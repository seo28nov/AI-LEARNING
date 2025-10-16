"""Dịch vụ quản lý quiz và bài tập."""
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict

from fastapi import HTTPException, status
import google.generativeai as genai

from config.config import get_settings
from models.models import (
    QuizDocument,
    QuizQuestion,
    CourseDocument,
    UserDocument,
    UserRole,
    EnrollmentDocument
)


settings = get_settings()


async def create_quiz(
    course_id: str,
    chapter_id: str,
    title: str,
    description: str,
    questions: List[Dict],
    instructor_id: str,
    time_limit: Optional[int] = None,
    passing_score: float = 70.0
) -> dict:
    """Tạo quiz mới cho chapter.
    
    Args:
        course_id: ID khóa học
        chapter_id: ID chapter
        title: Tiêu đề quiz
        description: Mô tả
        questions: Danh sách câu hỏi
        instructor_id: ID giảng viên
        time_limit: Giới hạn thời gian (phút)
        passing_score: Điểm đạt (%)
        
    Returns:
        Thông tin quiz vừa tạo
    """
    # Kiểm tra course
    course = await CourseDocument.get(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra quyền (owner hoặc admin)
    instructor = await UserDocument.get(instructor_id)
    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor không tồn tại"
        )
    
    if course.created_by != instructor_id and instructor.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tạo quiz cho khóa học này"
        )
    
    # Chuyển đổi questions sang QuizQuestion
    quiz_questions = []
    for q in questions:
        quiz_questions.append(QuizQuestion(
            question=q.get("question", ""),
            options=q.get("options", []),
            correct_answer=q.get("correct_answer", 0),
            explanation=q.get("explanation", "")
        ))
    
    # Tạo quiz
    now = datetime.now(timezone.utc)
    quiz_doc = QuizDocument(
        course_id=course_id,
        chapter_id=chapter_id,
        title=title,
        description=description,
        questions=quiz_questions,
        time_limit=time_limit,
        passing_score=passing_score,
        created_at=now,
        updated_at=now
    )
    
    await quiz_doc.insert()
    
    return {
        "id": str(quiz_doc.id),
        "course_id": quiz_doc.course_id,
        "chapter_id": quiz_doc.chapter_id,
        "title": quiz_doc.title,
        "description": quiz_doc.description,
        "question_count": len(quiz_doc.questions),
        "time_limit": quiz_doc.time_limit,
        "passing_score": quiz_doc.passing_score,
        "created_at": quiz_doc.created_at
    }


async def generate_quiz_with_ai(
    topic: str,
    difficulty: str = "intermediate",
    num_questions: int = 5
) -> List[Dict]:
    """Tạo câu hỏi quiz bằng Google GenAI.
    
    Args:
        topic: Chủ đề quiz
        difficulty: Độ khó
        num_questions: Số câu hỏi
        
    Returns:
        List câu hỏi với format [{question, options, correct_answer, explanation}]
    """
    if not settings.google_ai_api_key:
        # Fallback: câu hỏi mẫu
        return [
            {
                "question": f"Câu hỏi {i+1} về {topic}",
                "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
                "correct_answer": 0,
                "explanation": "Giải thích đáp án"
            }
            for i in range(num_questions)
        ]
    
    try:
        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Tạo {num_questions} câu hỏi trắc nghiệm về {topic} ở mức độ {difficulty}.
        
        Trả về JSON format:
        [
          {{
            "question": "Câu hỏi chi tiết",
            "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
            "correct_answer": 0,
            "explanation": "Giải thích tại sao đáp án này đúng"
          }}
        ]
        
        Chỉ trả về JSON array, không text giải thích.
        """
        
        response = model.generate_content(prompt)
        questions_json = response.text.strip()
        
        # Parse JSON
        if questions_json.startswith("```json"):
            questions_json = questions_json[7:-3].strip()
        elif questions_json.startswith("```"):
            questions_json = questions_json[3:-3].strip()
        
        questions = json.loads(questions_json)
        return questions
        
    except Exception as e:
        print(f"Error generating quiz: {e}")
        # Fallback
        return [
            {
                "question": f"Câu hỏi {i+1} về {topic}",
                "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
                "correct_answer": 0,
                "explanation": "Giải thích đáp án"
            }
            for i in range(num_questions)
        ]


async def get_quiz_by_id(quiz_id: str, user_id: str) -> dict:
    """Lấy thông tin quiz (không bao gồm đáp án đúng).
    
    Args:
        quiz_id: ID quiz
        user_id: ID người dùng
        
    Returns:
        Thông tin quiz
    """
    quiz = await QuizDocument.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra enrollment
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == quiz.course_id
    )
    
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa đăng ký khóa học này"
        )
    
    # Loại bỏ correct_answer và explanation khỏi questions
    safe_questions = []
    for q in quiz.questions:
        safe_questions.append({
            "question": q.question,
            "options": q.options
        })
    
    return {
        "id": str(quiz.id),
        "course_id": quiz.course_id,
        "chapter_id": quiz.chapter_id,
        "title": quiz.title,
        "description": quiz.description,
        "questions": safe_questions,
        "time_limit": quiz.time_limit,
        "passing_score": quiz.passing_score
    }


async def submit_quiz(
    quiz_id: str,
    user_id: str,
    answers: List[int]
) -> dict:
    """Nộp bài quiz và chấm điểm.
    
    Args:
        quiz_id: ID quiz
        user_id: ID người dùng
        answers: Danh sách đáp án (index)
        
    Returns:
        Kết quả quiz với điểm số và giải thích
    """
    quiz = await QuizDocument.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra enrollment
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == quiz.course_id
    )
    
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa đăng ký khóa học này"
        )
    
    # Chấm điểm
    correct_count = 0
    results = []
    
    for i, question in enumerate(quiz.questions):
        user_answer = answers[i] if i < len(answers) else -1
        is_correct = user_answer == question.correct_answer
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_index": i,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation
        })
    
    score = (correct_count / len(quiz.questions)) * 100 if quiz.questions else 0
    passed = score >= quiz.passing_score
    
    # Lưu điểm vào enrollment
    quiz_key = f"{quiz.chapter_id}_{quiz_id}"
    if quiz_key not in enrollment.quiz_scores or score > enrollment.quiz_scores.get(quiz_key, 0):
        enrollment.quiz_scores[quiz_key] = score
        enrollment.last_accessed = datetime.now(timezone.utc)
        await enrollment.save()
    
    return {
        "quiz_id": quiz_id,
        "score": round(score, 2),
        "correct_count": correct_count,
        "total_questions": len(quiz.questions),
        "passed": passed,
        "passing_score": quiz.passing_score,
        "results": results
    }


async def list_course_quizzes(
    course_id: str,
    user_id: str
) -> List[dict]:
    """Lấy danh sách quiz của khóa học.
    
    Args:
        course_id: ID khóa học
        user_id: ID người dùng
        
    Returns:
        List quiz
    """
    # Kiểm tra enrollment
    enrollment = await EnrollmentDocument.find_one(
        EnrollmentDocument.user_id == user_id,
        EnrollmentDocument.course_id == course_id
    )
    
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa đăng ký khóa học này"
        )
    
    quizzes = await QuizDocument.find(QuizDocument.course_id == course_id).to_list()
    
    quiz_list = []
    for quiz in quizzes:
        # Lấy điểm cao nhất (nếu có)
        quiz_key = f"{quiz.chapter_id}_{str(quiz.id)}"
        best_score = enrollment.quiz_scores.get(quiz_key)
        
        quiz_list.append({
            "id": str(quiz.id),
            "chapter_id": quiz.chapter_id,
            "title": quiz.title,
            "description": quiz.description,
            "question_count": len(quiz.questions),
            "time_limit": quiz.time_limit,
            "passing_score": quiz.passing_score,
            "best_score": best_score,
            "passed": best_score >= quiz.passing_score if best_score is not None else False
        })
    
    return quiz_list


async def update_quiz(
    quiz_id: str,
    update_data: dict,
    instructor_id: str
) -> dict:
    """Cập nhật quiz.
    
    Args:
        quiz_id: ID quiz
        update_data: Dữ liệu cập nhật
        instructor_id: ID giảng viên
        
    Returns:
        Thông tin quiz sau cập nhật
    """
    quiz = await QuizDocument.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra quyền
    course = await CourseDocument.get(quiz.course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    instructor = await UserDocument.get(instructor_id)
    if course.created_by != instructor_id and instructor.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật quiz này"
        )
    
    # Các trường được phép update
    allowed_fields = {
        "title", "description", "time_limit", "passing_score"
    }
    
    for field, value in update_data.items():
        if field in allowed_fields and hasattr(quiz, field):
            setattr(quiz, field, value)
    
    quiz.updated_at = datetime.now(timezone.utc)
    await quiz.save()
    
    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "time_limit": quiz.time_limit,
        "passing_score": quiz.passing_score,
        "updated_at": quiz.updated_at
    }


async def delete_quiz(quiz_id: str, instructor_id: str) -> bool:
    """Xóa quiz.
    
    Args:
        quiz_id: ID quiz
        instructor_id: ID giảng viên
        
    Returns:
        True nếu thành công
    """
    quiz = await QuizDocument.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra quyền
    course = await CourseDocument.get(quiz.course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    instructor = await UserDocument.get(instructor_id)
    if course.created_by != instructor_id and instructor.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa quiz này"
        )
    
    await quiz.delete()
    return True


async def get_quiz_analytics(
    quiz_id: str,
    instructor_id: str
) -> dict:
    """Lấy thống kê quiz (cho instructor).
    
    Args:
        quiz_id: ID quiz
        instructor_id: ID giảng viên
        
    Returns:
        Thống kê quiz
    """
    quiz = await QuizDocument.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz không tồn tại"
        )
    
    # Kiểm tra quyền
    course = await CourseDocument.get(quiz.course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    instructor = await UserDocument.get(instructor_id)
    if course.created_by != instructor_id and instructor.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem analytics"
        )
    
    # Lấy tất cả enrollments của course
    enrollments = await EnrollmentDocument.find(
        EnrollmentDocument.course_id == quiz.course_id
    ).to_list()
    
    quiz_key = f"{quiz.chapter_id}_{quiz_id}"
    
    total_attempts = 0
    total_score = 0
    passed_count = 0
    
    for enrollment in enrollments:
        if quiz_key in enrollment.quiz_scores:
            score = enrollment.quiz_scores[quiz_key]
            total_attempts += 1
            total_score += score
            if score >= quiz.passing_score:
                passed_count += 1
    
    avg_score = total_score / total_attempts if total_attempts > 0 else 0
    pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        "quiz_id": quiz_id,
        "title": quiz.title,
        "total_attempts": total_attempts,
        "average_score": round(avg_score, 2),
        "pass_rate": round(pass_rate, 2),
        "passed_count": passed_count,
        "failed_count": total_attempts - passed_count
    }


async def get_quiz_attempts(quiz_id: str, user_id: str) -> list:
    """Lấy lịch sử làm quiz của user."""
    # For now, return empty list - needs QuizAttempt model
    return []


async def get_quiz_statistics(quiz_id: str) -> dict:
    """Thống kê quiz - alias cho get_quiz_analytics."""
    return await get_quiz_analytics(quiz_id)


# Alias cho controller
list_quizzes_by_course = list_course_quizzes
submit_quiz_attempt = submit_quiz

