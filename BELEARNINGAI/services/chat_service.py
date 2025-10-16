"""Dịch vụ chat AI với Google GenAI và RAG."""
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict

from fastapi import HTTPException, status
import google.generativeai as genai

from config.config import get_settings
from models.models import (
    ChatDocument,
    UserDocument,
    CourseDocument,
    UploadDocument
)
from services.course_indexing_service import course_indexing_service

logger = logging.getLogger(__name__)
settings = get_settings()


async def create_chat_session(
    user_id: str,
    course_id: Optional[str] = None,
    title: str = "New Chat"
) -> dict:
    """Tạo phiên chat mới.
    
    Args:
        user_id: ID người dùng
        course_id: ID khóa học (nếu chat về khóa học cụ thể)
        title: Tiêu đề chat
        
    Returns:
        Thông tin session
    """
    # Kiểm tra user
    user = await UserDocument.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )
    
    # Nếu có course_id, kiểm tra course
    if course_id:
        course = await CourseDocument.get(course_id)
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khóa học không tồn tại"
            )
    
    now = datetime.now(timezone.utc)
    chat_doc = ChatDocument(
        user_id=user_id,
        course_id=course_id,
        title=title,
        messages=[],
        created_at=now,
        updated_at=now
    )
    
    await chat_doc.insert()
    
    return {
        "id": str(chat_doc.id),
        "user_id": chat_doc.user_id,
        "course_id": chat_doc.course_id,
        "title": chat_doc.title,
        "created_at": chat_doc.created_at
    }


async def send_message(
    session_id: str,
    user_id: str,
    message: str,
    use_rag: bool = False
) -> dict:
    """Gửi tin nhắn và nhận phản hồi từ AI.
    
    Với RAG enabled, AI sẽ sử dụng nội dung từ course để trả lời chính xác hơn.
    
    Args:
        session_id: ID phiên chat
        user_id: ID người dùng
        message: Nội dung tin nhắn
        use_rag: Sử dụng RAG với course content (vector search)
        
    Returns:
        Tin nhắn và phản hồi từ AI
    """
    try:
        # Lấy chat session
        chat = await ChatDocument.get(session_id)
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session không tồn tại"
            )
        
        # Kiểm tra quyền
        if chat.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập chat này"
            )
        
        # Thêm tin nhắn user vào history
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Tạo context cho AI (với RAG nếu enabled)
        context = await build_context(chat, use_rag, user_id, message)
        
        # Gọi AI để lấy phản hồi
        ai_response = await generate_ai_response(message, context, chat.messages)
        
        # Thêm phản hồi AI vào history
        ai_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Lưu vào database
        chat.messages.append(user_message)
        chat.messages.append(ai_message)
        chat.updated_at = datetime.now(timezone.utc)
        await chat.save()
        
        logger.info(f"✅ Chat message processed: session={session_id}, use_rag={use_rag}")
        
        return {
            "session_id": session_id,
            "user_message": user_message,
            "ai_message": ai_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi send_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi xử lý tin nhắn"
        )


async def build_context(
    chat: ChatDocument,
    use_rag: bool,
    user_id: str,
    user_message: str = ""
) -> str:
    """Xây dựng context cho AI.
    
    Với RAG enabled, sử dụng vector search để tìm relevant content từ course.
    
    Args:
        chat: Chat document
        use_rag: Có sử dụng RAG không
        user_id: ID người dùng
        user_message: Tin nhắn của user (để search relevant content)
        
    Returns:
        Context string cho AI
    """
    context_parts = []
    
    try:
        # 1. Nếu chat về khóa học cụ thể
        if chat.course_id:
            course = await CourseDocument.get(chat.course_id)
            if course:
                context_parts.append("=== THÔNG TIN KHÓA HỌC ===")
                context_parts.append(f"Khóa học: {course.title}")
                context_parts.append(f"Mô tả: {course.description}")
                context_parts.append("")
                
                # 2. Nếu sử dụng RAG - tìm relevant content bằng vector search
                if use_rag and user_message:
                    logger.info(f"🔍 RAG: Searching relevant content for: '{user_message[:50]}...'")
                    
                    try:
                        # Search trong course content
                        search_results = await course_indexing_service.search_course_content(
                            query=user_message,
                            course_id=str(chat.course_id),
                            top_k=3  # Lấy top 3 relevant chunks
                        )
                        
                        if search_results:
                            context_parts.append("=== NỘI DUNG LIÊN QUAN ===")
                            for i, result in enumerate(search_results, 1):
                                context_parts.append(f"\n[Đoạn {i}] {result['title']}")
                                context_parts.append(f"(Độ liên quan: {result['score']:.2f})")
                                context_parts.append(result['text'])
                            context_parts.append("")
                            
                            logger.info(f"✅ RAG: Found {len(search_results)} relevant chunks")
                        else:
                            logger.warning("⚠️ RAG: No relevant content found")
                            
                    except Exception as e:
                        logger.error(f"❌ RAG search error: {e}")
                        # Fallback: không dùng RAG
                        context_parts.append("(Không tìm thấy nội dung liên quan)")
                
                # 3. Fallback: Thêm chapter info nếu không dùng RAG
                elif course.chapters:
                    context_parts.append("=== CHƯƠNG TRÌNH HỌC ===")
                    for i, chapter in enumerate(course.chapters[:5], 1):
                        context_parts.append(f"{i}. {chapter.title}")
                        if chapter.description:
                            context_parts.append(f"   {chapter.description[:100]}...")
                    context_parts.append("")
        
        # 4. Thêm tài liệu upload (nếu user có)
        uploads = await UploadDocument.find(
            UploadDocument.user_id == user_id
        ).limit(3).to_list()
        
        if uploads:
            context_parts.append("=== TÀI LIỆU THAM KHẢO ===")
            for upload in uploads:
                context_parts.append(f"- {upload.file_name}")
                if upload.extracted_text:
                    preview = upload.extracted_text[:300]
                    context_parts.append(f"  {preview}...")
            context_parts.append("")
        
        final_context = "\n".join(context_parts)
        
        logger.debug(f"📝 Context built: {len(final_context)} chars, RAG={use_rag}")
        
        return final_context
        
    except Exception as e:
        logger.error(f"❌ Error building context: {e}")
        return ""


async def generate_ai_response(
    message: str,
    context: str,
    history: List[Dict]
) -> str:
    """Tạo phản hồi từ Google GenAI.
    
    Args:
        message: Tin nhắn người dùng
        context: Context từ khóa học/tài liệu (với RAG)
        history: Lịch sử chat
        
    Returns:
        Phản hồi từ AI
    """
    if not settings.google_ai_api_key:
        logger.warning("⚠️ Google AI API key chưa được cấu hình")
        return "Xin lỗi, AI service chưa được cấu hình. Vui lòng thêm GOOGLE_AI_API_KEY vào .env"
    
    try:
        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Xây dựng system prompt
        system_prompt = """Bạn là trợ lý AI thông minh cho nền tảng học tập trực tuyến BeLearning.

NHIỆM VỤ:
- Trả lời câu hỏi về khóa học, lập trình, và các chủ đề học tập
- Giải thích khái niệm một cách dễ hiểu, có ví dụ thực tế
- Dựa vào CONTEXT được cung cấp để trả lời chính xác
- Nếu thông tin trong CONTEXT, ưu tiên sử dụng nó
- Nếu không có trong CONTEXT, sử dụng kiến thức chung
- Động viên và hỗ trợ người học một cách thân thiện

QUY TẮC:
- Trả lời bằng tiếng Việt rõ ràng, dễ hiểu
- Đưa ra code examples khi phù hợp
- Luôn kiểm tra CONTEXT trước khi trả lời
- Nếu không chắc chắn, hãy thừa nhận và gợi ý tài liệu tham khảo
- Format câu trả lời đẹp mắt với markdown"""
        
        # Thêm context nếu có
        if context:
            system_prompt += f"\n\n=== CONTEXT ===\n{context}\n=== END CONTEXT ==="
        
        # Xây dựng lịch sử chat (giới hạn 10 tin nhắn gần nhất)
        chat_history = []
        recent_messages = history[-10:] if len(history) > 10 else history
        
        for msg in recent_messages:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({
                "role": role,
                "parts": [msg["content"]]
            })
        
        # Tạo chat với history
        chat = model.start_chat(history=chat_history)
        
        # Gửi tin nhắn với system prompt
        full_prompt = f"{system_prompt}\n\n=== QUESTION ===\n{message}"
        
        logger.info(f"🤖 Generating AI response (context: {len(context)} chars)")
        
        response = chat.send_message(full_prompt)
        
        logger.info(f"✅ AI response generated ({len(response.text)} chars)")
        
        return response.text
        
    except Exception as e:
        logger.error(f"❌ Error generating AI response: {e}")
        return f"Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu: {str(e)}"


async def get_chat_history(
    session_id: str,
    user_id: str
) -> dict:
    """Lấy lịch sử chat.
    
    Args:
        session_id: ID phiên chat
        user_id: ID người dùng
        
    Returns:
        Lịch sử chat
    """
    chat = await ChatDocument.get(session_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session không tồn tại"
        )
    
    # Kiểm tra quyền
    if chat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chat này"
        )
    
    return {
        "id": str(chat.id),
        "title": chat.title,
        "course_id": chat.course_id,
        "messages": chat.messages,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at
    }


async def list_user_chats(
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[dict], int]:
    """Lấy danh sách chat sessions của user.
    
    Args:
        user_id: ID người dùng
        skip: Bỏ qua
        limit: Giới hạn
        
    Returns:
        Tuple (chats, total)
    """
    query = ChatDocument.find(ChatDocument.user_id == user_id)
    total = await query.count()
    chats = await query.sort(-ChatDocument.updated_at).skip(skip).limit(limit).to_list()
    
    chat_list = []
    for chat in chats:
        # Lấy tin nhắn cuối cùng
        last_message = chat.messages[-1] if chat.messages else None
        
        chat_list.append({
            "id": str(chat.id),
            "title": chat.title,
            "course_id": chat.course_id,
            "message_count": len(chat.messages),
            "last_message": last_message,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        })
    
    return chat_list, total


async def delete_chat_session(
    session_id: str,
    user_id: str
) -> bool:
    """Xóa chat session.
    
    Args:
        session_id: ID phiên chat
        user_id: ID người dùng
        
    Returns:
        True nếu thành công
    """
    chat = await ChatDocument.get(session_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session không tồn tại"
        )
    
    # Kiểm tra quyền
    if chat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa chat này"
        )
    
    await chat.delete()
    return True


async def update_chat_title(
    session_id: str,
    user_id: str,
    new_title: str
) -> dict:
    """Cập nhật tiêu đề chat.
    
    Args:
        session_id: ID phiên chat
        user_id: ID người dùng
        new_title: Tiêu đề mới
        
    Returns:
        Thông tin chat
    """
    chat = await ChatDocument.get(session_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session không tồn tại"
        )
    
    # Kiểm tra quyền
    if chat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật chat này"
        )
    
    chat.title = new_title
    chat.updated_at = datetime.now(timezone.utc)
    await chat.save()
    
    return {
        "id": str(chat.id),
        "title": chat.title,
        "updated_at": chat.updated_at
    }


async def generate_course_content(
    topic: str,
    level: str = "beginner",
    num_chapters: int = 5
) -> dict:
    """Tạo nội dung khóa học tự động bằng AI.
    
    Args:
        topic: Chủ đề khóa học
        level: Trình độ
        num_chapters: Số chương
        
    Returns:
        Nội dung khóa học
    """
    if not settings.google_ai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service chưa được cấu hình"
        )
    
    try:
        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Tạo cấu trúc khóa học về {topic} cho người học ở trình độ {level}.
        
        Yêu cầu:
        - Tạo {num_chapters} chương học
        - Mỗi chương có tiêu đề, mô tả, và nội dung chi tiết
        - Ước tính thời gian học cho mỗi chương
        - Thêm các bài tập thực hành
        
        Trả về JSON format:
        {{
          "title": "Tiêu đề khóa học",
          "description": "Mô tả khóa học",
          "level": "{level}",
          "chapters": [
            {{
              "title": "Tên chương",
              "description": "Mô tả chương",
              "duration_minutes": 60,
              "content": "Nội dung chi tiết",
              "learning_objectives": ["Mục tiêu 1", "Mục tiêu 2"],
              "exercises": ["Bài tập 1", "Bài tập 2"]
            }}
          ]
        }}
        
        Chỉ trả về JSON, không text giải thích.
        """
        
        response = model.generate_content(prompt)
        content_json = response.text.strip()
        
        # Parse JSON
        if content_json.startswith("```json"):
            content_json = content_json[7:-3].strip()
        elif content_json.startswith("```"):
            content_json = content_json[3:-3].strip()
        
        course_content = json.loads(content_json)
        return course_content
        
    except Exception as e:
        print(f"Error generating course content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo nội dung khóa học"
        )


# Aliases for backward compatibility with controller
start_chat_session = create_chat_session
get_user_chat_sessions = list_user_chats
