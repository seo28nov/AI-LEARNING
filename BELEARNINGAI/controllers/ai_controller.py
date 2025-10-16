"""Controller cho các endpoint AI."""
from schemas.ai import AIChatRequest, AIChatResponse, AIContentRequest, AIContentResponse
from services.ai_service import chat_with_ai, generate_course_from_prompt


async def handle_ai_course_generation(payload: AIContentRequest) -> AIContentResponse:
    return await generate_course_from_prompt(payload)


async def handle_ai_chat(payload: AIChatRequest) -> AIChatResponse:
    return await chat_with_ai(payload)


async def handle_ai_quiz_generation(payload: dict, user_id: str) -> dict:
    """Sinh quiz bằng AI."""
    from services.quiz_service import generate_quiz_with_ai
    from fastapi import HTTPException, status
    
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic is required"
        )
    
    return await generate_quiz_with_ai(
        topic=topic,
        course_id=payload.get("course_id"),
        chapter_id=payload.get("chapter_id"),
        num_questions=payload.get("num_questions", 10),
        difficulty=payload.get("difficulty", "medium"),
        user_id=user_id
    )


async def handle_ai_course_recommendations(user_id: str, payload: dict = None) -> dict:
    """Gợi ý khóa học bằng AI dựa trên lịch sử và preferences."""
    from services.recommendation_service import recommend_for_user
    
    category = payload.get("category") if payload else None
    
    recommendations = await recommend_for_user(
        user_id=user_id,
        category=category
    )
    
    return recommendations


async def handle_ai_learning_path(user_id: str, payload: dict) -> dict:
    """Tạo lộ trình học cá nhân hóa bằng AI."""
    from services.recommendation_service import build_learning_path
    from fastapi import HTTPException, status
    
    goal = payload.get("goal")
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Learning goal is required"
        )
    
    current_level = payload.get("current_level", "beginner")
    interests = payload.get("interests", [])
    
    path = await build_learning_path(
        user_id=user_id,
        goal=goal,
        current_level=current_level,
        interests=interests
    )
    
    return {
        "user_id": user_id,
        "goal": goal,
        "learning_path": path,
        "estimated_duration": f"{len(path) * 4} weeks"  # Giả sử mỗi step 4 tuần
    }


async def handle_ai_content_enhance(payload: dict) -> dict:
    """Cải thiện nội dung bằng AI."""
    import google.generativeai as genai
    from config.config import settings
    from fastapi import HTTPException, status
    
    content = payload.get("content")
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    enhancement_type = payload.get("type", "improve")  # improve, simplify, expand
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompts = {
        "improve": f"Cải thiện nội dung sau cho rõ ràng và dễ hiểu hơn:\n\n{content}",
        "simplify": f"Đơn giản hóa nội dung sau cho người mới bắt đầu:\n\n{content}",
        "expand": f"Mở rộng và giải thích chi tiết hơn nội dung sau:\n\n{content}"
    }
    
    prompt = prompts.get(enhancement_type, prompts["improve"])
    response = model.generate_content(prompt)
    
    return {
        "original": content,
        "enhanced": response.text,
        "type": enhancement_type
    }
