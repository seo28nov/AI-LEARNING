"""Dịch vụ đánh giá năng lực và đề xuất khóa học."""
import json
from datetime import datetime, timezone
from typing import List, Dict

from fastapi import HTTPException, status
import google.generativeai as genai

from config.config import get_settings
from models.models import AssessmentDocument, UserDocument, CourseDocument


settings = get_settings()


async def create_assessment(
    user_id: str,
    category: str,
    assessment_type: str = "skill_test",
    difficulty: str = "beginner"
) -> dict:
    """Tạo bài đánh giá kỹ năng mới.
    
    Args:
        user_id: ID người dùng
        category: Danh mục đánh giá (programming, design, ...)
        assessment_type: Loại đánh giá (skill_test, placement_test)
        difficulty: Độ khó (beginner, intermediate, advanced)
        
    Returns:
        Thông tin bài đánh giá với danh sách câu hỏi
    """
    # Kiểm tra user
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    # Tạo câu hỏi bằng AI
    questions = await generate_questions(category, difficulty)
    
    now = datetime.now(timezone.utc)
    assessment_doc = AssessmentDocument(
        user_id=user_id,
        category=category,
        assessment_type=assessment_type,
        difficulty=difficulty,
        questions=questions,
        answers=[],
        score=0.0,
        level="beginner",
        strengths=[],
        weaknesses=[],
        topics=[],
        recommended_courses=[],
        learning_path=[],
        created_at=now,
        updated_at=now
    )
    
    await assessment_doc.insert()
    
    return {
        "id": str(assessment_doc.id),
        "user_id": assessment_doc.user_id,
        "category": assessment_doc.category,
        "assessment_type": assessment_doc.assessment_type,
        "difficulty": assessment_doc.difficulty,
        "questions": assessment_doc.questions,
        "created_at": assessment_doc.created_at
    }


async def generate_questions(category: str, difficulty: str, num_questions: int = 10) -> List[Dict]:
    """Sử dụng Google GenAI để tạo câu hỏi trắc nghiệm.
    
    Args:
        category: Danh mục kiến thức
        difficulty: Độ khó
        num_questions: Số câu hỏi
        
    Returns:
        List câu hỏi với format [{question, options, correct_answer, topic}]
    """
    if not settings.google_ai_api_key:
        # Fallback: trả về câu hỏi mẫu
        return [
            {
                "question": f"Câu hỏi {i+1} về {category}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": 0,
                "topic": category
            }
            for i in range(num_questions)
        ]
    
    try:
        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Tạo {num_questions} câu hỏi trắc nghiệm về {category} ở mức độ {difficulty}.
        
        Trả về JSON format:
        [
          {{
            "question": "Câu hỏi",
            "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
            "correct_answer": 0,
            "topic": "Chủ đề cụ thể"
          }}
        ]
        
        Chỉ trả về JSON array, không có text giải thích.
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
        print(f"Error generating questions: {e}")
        # Fallback
        return [
            {
                "question": f"Câu hỏi {i+1} về {category}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": 0,
                "topic": category
            }
            for i in range(num_questions)
        ]


async def submit_assessment(
    assessment_id: str,
    user_id: str,
    answers: List[int]
) -> dict:
    """Nộp bài và chấm điểm đánh giá.
    
    Args:
        assessment_id: ID bài đánh giá
        user_id: ID người dùng
        answers: Danh sách đáp án (index)
        
    Returns:
        Kết quả đánh giá với điểm số và phân tích
    """
    assessment = await AssessmentDocument.get(assessment_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài đánh giá không tồn tại"
        )
    
    # Kiểm tra quyền
    if assessment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền nộp bài này"
        )
    
    # Đã nộp rồi
    if assessment.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bài đánh giá đã được nộp"
        )
    
    # Chấm điểm
    score, topics = calculate_score(assessment.questions, answers)
    
    # Xác định level
    level = determine_level(score)
    
    # Phân tích điểm mạnh/yếu
    strengths, weaknesses = analyze_performance(topics)
    
    # Lưu kết quả
    assessment.answers = answers
    assessment.score = score
    assessment.level = level
    assessment.strengths = strengths
    assessment.weaknesses = weaknesses
    assessment.topics = topics
    assessment.updated_at = datetime.now(timezone.utc)
    
    await assessment.save()
    
    # Tạo đề xuất khóa học
    recommended_courses = await get_recommended_courses(
        assessment.category,
        level,
        weaknesses
    )
    
    # Tạo lộ trình học tập
    learning_path = await generate_learning_path(
        assessment.category,
        level,
        topics
    )
    
    # Cập nhật đề xuất
    assessment.recommended_courses = recommended_courses
    assessment.learning_path = learning_path
    await assessment.save()
    
    return {
        "id": str(assessment.id),
        "score": assessment.score,
        "level": assessment.level,
        "strengths": assessment.strengths,
        "weaknesses": assessment.weaknesses,
        "topics": assessment.topics,
        "recommended_courses": assessment.recommended_courses,
        "learning_path": assessment.learning_path,
        "updated_at": assessment.updated_at
    }


def calculate_score(questions: List[Dict], answers: List[int]) -> tuple[float, List[Dict]]:
    """Tính điểm và phân tích theo topic.
    
    Returns:
        Tuple (score, topics) với topics = [{topic, correct, total, mastery_level}]
    """
    correct_count = 0
    topic_stats = {}
    
    for i, question in enumerate(questions):
        correct_answer = question.get("correct_answer", 0)
        user_answer = answers[i] if i < len(answers) else -1
        
        is_correct = user_answer == correct_answer
        if is_correct:
            correct_count += 1
        
        # Thống kê theo topic
        topic = question.get("topic", "general")
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        
        topic_stats[topic]["total"] += 1
        if is_correct:
            topic_stats[topic]["correct"] += 1
    
    # Tính điểm phần trăm
    score = (correct_count / len(questions)) * 100 if questions else 0
    
    # Chuyển topic_stats thành list
    topics = []
    for topic, stats in topic_stats.items():
        mastery = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        if mastery >= 0.8:
            level = "excellent"
        elif mastery >= 0.6:
            level = "good"
        elif mastery >= 0.4:
            level = "fair"
        else:
            level = "poor"
        
        topics.append({
            "topic": topic,
            "correct": stats["correct"],
            "total": stats["total"],
            "mastery_level": level
        })
    
    return score, topics


def determine_level(score: float) -> str:
    """Xác định trình độ dựa trên điểm số."""
    if score >= 80:
        return "advanced"
    elif score >= 60:
        return "intermediate"
    else:
        return "beginner"


def analyze_performance(topics: List[Dict]) -> tuple[List[str], List[str]]:
    """Phân tích điểm mạnh và yếu.
    
    Returns:
        Tuple (strengths, weaknesses)
    """
    strengths = []
    weaknesses = []
    
    for topic_data in topics:
        topic = topic_data["topic"]
        level = topic_data["mastery_level"]
        
        if level in ["excellent", "good"]:
            strengths.append(topic)
        elif level in ["fair", "poor"]:
            weaknesses.append(topic)
    
    return strengths, weaknesses


async def get_recommended_courses(
    category: str,
    level: str,
    weaknesses: List[str]
) -> List[str]:
    """Đề xuất khóa học dựa trên kết quả đánh giá.
    
    Args:
        category: Danh mục
        level: Trình độ hiện tại
        weaknesses: Điểm yếu cần cải thiện
        
    Returns:
        List course IDs
    """
    # Tìm khóa học phù hợp
    query_conditions = [
        CourseDocument.category == category,
        CourseDocument.is_published
    ]
    
    # Ưu tiên level tương ứng hoặc cao hơn 1 bậc
    if level == "beginner":
        query_conditions.append(CourseDocument.level.in_(["beginner", "intermediate"]))
    elif level == "intermediate":
        query_conditions.append(CourseDocument.level.in_(["intermediate", "advanced"]))
    else:
        query_conditions.append(CourseDocument.level == "advanced")
    
    courses = await CourseDocument.find(*query_conditions).limit(5).to_list()
    
    return [str(course.id) for course in courses]


async def generate_learning_path(
    category: str,
    level: str,
    topics: List[Dict]
) -> List[str]:
    """Tạo lộ trình học tập cá nhân hóa bằng AI.
    
    Args:
        category: Danh mục
        level: Trình độ
        topics: Phân tích chủ đề
        
    Returns:
        List bước học (text descriptions)
    """
    if not settings.google_ai_api_key:
        # Fallback: lộ trình cơ bản
        return [
            f"Bước 1: Ôn tập kiến thức cơ bản về {category}",
            f"Bước 2: Thực hành các bài tập {level}",
            "Bước 3: Hoàn thành dự án thực tế"
        ]
    
    try:
        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Chuẩn bị context
        weak_topics = [t["topic"] for t in topics if t["mastery_level"] in ["fair", "poor"]]
        
        prompt = f"""
        Tạo lộ trình học tập cá nhân hóa cho người học {category} ở trình độ {level}.
        
        Điểm yếu cần cải thiện: {', '.join(weak_topics) if weak_topics else 'Không có'}
        
        Trả về JSON array với 5-7 bước học, mỗi bước là string mô tả ngắn gọn:
        ["Bước 1: ...", "Bước 2: ...", ...]
        
        Chỉ trả về JSON array, không text giải thích.
        """
        
        response = model.generate_content(prompt)
        path_json = response.text.strip()
        
        if path_json.startswith("```json"):
            path_json = path_json[7:-3].strip()
        elif path_json.startswith("```"):
            path_json = path_json[3:-3].strip()
        
        learning_path = json.loads(path_json)
        return learning_path
        
    except Exception as e:
        print(f"Error generating learning path: {e}")
        return [
            f"Bước 1: Ôn tập kiến thức cơ bản về {category}",
            f"Bước 2: Thực hành các bài tập {level}",
            "Bước 3: Hoàn thành dự án thực tế"
        ]


async def get_assessment_by_id(assessment_id: str, user_id: str) -> dict:
    """Lấy thông tin chi tiết đánh giá.
    
    Args:
        assessment_id: ID đánh giá
        user_id: ID người dùng
        
    Returns:
        Thông tin đánh giá
    """
    assessment = await AssessmentDocument.get(assessment_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bài đánh giá không tồn tại"
        )
    
    # Kiểm tra quyền
    if assessment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem bài này"
        )
    
    return {
        "id": str(assessment.id),
        "user_id": assessment.user_id,
        "category": assessment.category,
        "assessment_type": assessment.assessment_type,
        "difficulty": assessment.difficulty,
        "questions": assessment.questions,
        "answers": assessment.answers,
        "score": assessment.score,
        "level": assessment.level,
        "strengths": assessment.strengths,
        "weaknesses": assessment.weaknesses,
        "topics": assessment.topics,
        "recommended_courses": assessment.recommended_courses,
        "learning_path": assessment.learning_path,
        "created_at": assessment.created_at,
        "updated_at": assessment.updated_at
    }


async def list_user_assessments(
    user_id: str,
    skip: int = 0,
    limit: int = 10
) -> tuple[List[dict], int]:
    """Lấy danh sách đánh giá của người dùng.
    
    Args:
        user_id: ID người dùng
        skip: Bỏ qua
        limit: Giới hạn
        
    Returns:
        Tuple (assessments, total)
    """
    query = AssessmentDocument.find(AssessmentDocument.user_id == user_id)
    total = await query.count()
    assessments = await query.sort(-AssessmentDocument.created_at).skip(skip).limit(limit).to_list()
    
    assessment_list = []
    for assessment in assessments:
        assessment_list.append({
            "id": str(assessment.id),
            "category": assessment.category,
            "assessment_type": assessment.assessment_type,
            "difficulty": assessment.difficulty,
            "score": assessment.score,
            "level": assessment.level,
            "created_at": assessment.created_at
        })
    
    return assessment_list, total
