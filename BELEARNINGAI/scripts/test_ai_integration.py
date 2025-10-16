"""
Test AI Integration - Course & Quiz Generation

Script test các chức năng AI:
1. Course generation với Google AI
2. Quiz generation tự động
3. Performance benchmarks
4. RAG ON vs RAG OFF comparison
5. Embedding generation speed

Run: python scripts/test_ai_integration.py
"""
import asyncio
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIIntegrationTester:
    """Test AI integration features"""
    
    def __init__(self):
        self.results = []
    
    def record_result(self, test_name: str, passed: bool, details: str = ""):
        """Ghi lại kết quả test"""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow()
        })
    
    async def test_google_ai_connection(self) -> bool:
        """Test 1: Kết nối Google AI API"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: Google AI API Connection")
        logger.info("="*70)
        
        try:
            from services.ai_service import ai_service
            
            logger.info("Đang kiểm tra kết nối Google AI...")
            
            # Test basic text generation
            prompt = "Viết 1 câu giới thiệu ngắn về Python"
            start_time = time.time()
            
            response = await ai_service.generate_text(prompt)
            
            elapsed = time.time() - start_time
            
            logger.info(f"Phản hồi: {response[:100]}...")
            logger.info(f"Thời gian phản hồi: {elapsed:.2f}s")
            
            success = len(response) > 0
            self.record_result(
                "Google AI Connection",
                success,
                f"Response time: {elapsed:.2f}s"
            )
            
            if success:
                logger.info("PASSED - Google AI API hoạt động tốt")
            else:
                logger.error("FAILED - Không nhận được phản hồi từ API")
            
            return success
            
        except Exception as e:
            logger.error(f"FAILED - Lỗi: {e}")
            self.record_result("Google AI Connection", False, str(e))
            return False
    
    async def test_course_content_generation(self) -> bool:
        """Test 2: Generate course content với AI"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: AI Course Content Generation")
        logger.info("="*70)
        
        try:
            from services.ai_service import ai_service
            
            logger.info("Đang tạo nội dung bài học với AI...")
            
            # Test generate lesson content
            topic = "Python Variables and Data Types"
            level = "beginner"
            
            prompt = f"""
            Tạo nội dung bài học về "{topic}" cho người mới học (level: {level}).
            Bao gồm:
            - Giới thiệu khái niệm
            - Ví dụ cụ thể
            - Code examples
            - Tóm tắt
            
            Độ dài: khoảng 300-500 từ.
            """
            
            start_time = time.time()
            content = await ai_service.generate_text(prompt)
            elapsed = time.time() - start_time
            
            logger.info(f"\nNội dung được tạo ({len(content)} ký tự):")
            logger.info(content[:300] + "...")
            logger.info(f"\nThời gian tạo: {elapsed:.2f}s")
            logger.info(f"Tốc độ: {len(content)/elapsed:.0f} ký tự/giây")
            
            # Kiểm tra chất lượng content
            success = (
                len(content) >= 300 and
                topic.lower() in content.lower() and
                len(content.split()) >= 50
            )
            
            self.record_result(
                "Course Content Generation",
                success,
                f"{len(content)} chars, {elapsed:.2f}s"
            )
            
            if success:
                logger.info("\nPASSED - Nội dung được tạo đầy đủ và chất lượng")
            else:
                logger.warning("\nFAILED - Nội dung không đủ tiêu chuẩn")
            
            return success
            
        except Exception as e:
            logger.error(f"FAILED - Lỗi: {e}")
            self.record_result("Course Content Generation", False, str(e))
            return False
    
    async def test_quiz_generation(self) -> bool:
        """Test 3: Tạo quiz tự động với AI"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: AI Quiz Generation")
        logger.info("="*70)
        
        try:
            from services.ai_service import ai_service
            import json
            
            logger.info("Đang tạo quiz với AI...")
            
            topic = "Python Lists"
            num_questions = 3
            
            prompt = f"""
            Tạo {num_questions} câu hỏi trắc nghiệm về "{topic}".
            Format JSON như sau:
            {{
                "questions": [
                    {{
                        "question": "Câu hỏi?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Giải thích"
                    }}
                ]
            }}
            
            Chỉ trả về JSON, không có text khác.
            """
            
            start_time = time.time()
            response = await ai_service.generate_text(prompt)
            elapsed = time.time() - start_time
            
            logger.info(f"Thời gian tạo: {elapsed:.2f}s")
            
            # Parse JSON
            try:
                # Clean response (remove markdown code blocks if any)
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                
                quiz_data = json.loads(clean_response)
                questions = quiz_data.get("questions", [])
                
                logger.info(f"\nĐã tạo {len(questions)} câu hỏi:")
                for i, q in enumerate(questions, 1):
                    logger.info(f"\n{i}. {q['question']}")
                    logger.info(f"   Đáp án đúng: {q['correct_answer']}")
                
                success = len(questions) == num_questions
                
                self.record_result(
                    "Quiz Generation",
                    success,
                    f"{len(questions)} questions, {elapsed:.2f}s"
                )
                
                if success:
                    logger.info("\nPASSED - Quiz được tạo đúng format và số lượng")
                else:
                    logger.warning(f"\nFAILED - Tạo được {len(questions)}/{num_questions} câu")
                
                return success
                
            except json.JSONDecodeError as e:
                logger.error(f"FAILED - Không parse được JSON: {e}")
                logger.error(f"Response: {response[:200]}")
                self.record_result("Quiz Generation", False, "JSON parse error")
                return False
            
        except Exception as e:
            logger.error(f"FAILED - Lỗi: {e}")
            self.record_result("Quiz Generation", False, str(e))
            return False
    
    async def test_embedding_performance(self) -> bool:
        """Test 4: Đo tốc độ embedding generation"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: Embedding Generation Performance")
        logger.info("="*70)
        
        try:
            from services.embedding_service import embedding_service
            
            # Test 1: Single embedding
            logger.info("\nTest 4.1: Single Embedding Speed")
            text = "Python is a high-level programming language"
            
            times = []
            for i in range(5):
                start = time.time()
                _ = await embedding_service.generate_embedding(text)
                elapsed = time.time() - start
                times.append(elapsed)
                logger.info(f"  Run {i+1}: {elapsed*1000:.0f}ms")
            
            avg_single = sum(times) / len(times)
            logger.info(f"Trung bình: {avg_single*1000:.0f}ms")
            
            # Test 2: Batch embedding
            logger.info("\nTest 4.2: Batch Embedding Speed")
            texts = [
                "Python programming language",
                "JavaScript web development",
                "SQL database queries",
                "HTML markup language",
                "CSS styling"
            ]
            
            start = time.time()
            _ = await embedding_service.generate_embeddings_batch(texts)
            elapsed = time.time() - start
            
            logger.info(f"  {len(texts)} texts: {elapsed*1000:.0f}ms")
            logger.info(f"  Trung bình: {elapsed/len(texts)*1000:.0f}ms/text")
            
            # So sánh batch vs single
            logger.info("\nSo sánh:")
            logger.info(f"  Single: {avg_single*1000:.0f}ms")
            logger.info(f"  Batch:  {elapsed/len(texts)*1000:.0f}ms")
            speedup = avg_single / (elapsed/len(texts))
            logger.info(f"  Batch nhanh hơn: {speedup:.1f}x")
            
            # Success nếu batch nhanh hơn single
            success = speedup > 1.0
            
            self.record_result(
                "Embedding Performance",
                success,
                f"Batch {speedup:.1f}x faster"
            )
            
            if success:
                logger.info("\nPASSED - Batch embedding hiệu quả hơn")
            else:
                logger.warning("\nWARNING - Batch không nhanh hơn single")
            
            return success
            
        except Exception as e:
            logger.error(f"FAILED - Lỗi: {e}")
            self.record_result("Embedding Performance", False, str(e))
            return False
    
    async def test_rag_comparison(self) -> bool:
        """Test 5: So sánh RAG ON vs RAG OFF"""
        logger.info("\n" + "="*70)
        logger.info("TEST 5: RAG ON vs RAG OFF Comparison")
        logger.info("="*70)
        
        try:
            from models.models import Course, CourseChapter, Lesson, ChatDocument
            from services.course_indexing_service import course_indexing_service
            from services.chat_service import build_context
            from beanie import init_beanie
            from motor.motor_asyncio import AsyncIOMotorClient
            from config.config import settings
            
            # Kết nối database
            logger.info("Đang kết nối MongoDB...")
            client = AsyncIOMotorClient(settings.mongodb_url)
            await init_beanie(
                database=client[settings.mongodb_database],
                document_models=[Course, ChatDocument]
            )
            
            # Tạo test course
            logger.info("Đang tạo test course...")
            test_course = Course(
                title="AI Testing Course",
                description="Course để test RAG",
                instructor_id="test-instructor",
                level="beginner",
                status="published",
                chapters=[
                    CourseChapter(
                        title="Python Fundamentals",
                        description="Python basics",
                        order=1,
                        lessons=[
                            Lesson(
                                title="Python History",
                                content="Python được tạo bởi Guido van Rossum vào năm 1991. Nó là ngôn ngữ lập trình bậc cao, thông dịch, với cú pháp rõ ràng và dễ đọc.",
                                order=1,
                                duration_minutes=10
                            )
                        ]
                    )
                ],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await test_course.insert()
            
            # Index course
            logger.info("Đang index course...")
            index_result = await course_indexing_service.index_course(test_course)
            logger.info(f"Đã index {index_result['chunks_indexed']} chunks")
            
            # Tạo chat session
            chat = ChatDocument(
                user_id="test-user",
                course_id=str(test_course.id),
                title="Test Chat",
                messages=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await chat.insert()
            
            query = "Ai tạo ra Python?"
            
            # Test WITHOUT RAG
            logger.info("\nTest 5.1: WITHOUT RAG")
            logger.info(f"Câu hỏi: {query}")
            
            start = time.time()
            context_no_rag = await build_context(
                chat=chat,
                use_rag=False,
                user_id="test-user",
                user_message=query
            )
            time_no_rag = time.time() - start
            
            logger.info(f"  Context length: {len(context_no_rag)} chars")
            logger.info(f"  Build time: {time_no_rag*1000:.0f}ms")
            
            # Test WITH RAG
            logger.info("\nTest 5.2: WITH RAG")
            logger.info(f"Câu hỏi: {query}")
            
            start = time.time()
            context_with_rag = await build_context(
                chat=chat,
                use_rag=True,
                user_id="test-user",
                user_message=query
            )
            time_with_rag = time.time() - start
            
            logger.info(f"  Context length: {len(context_with_rag)} chars")
            logger.info(f"  Build time: {time_with_rag*1000:.0f}ms")
            
            # So sánh
            logger.info("\nSo sánh:")
            logger.info(f"  RAG OFF: {len(context_no_rag)} chars, {time_no_rag*1000:.0f}ms")
            logger.info(f"  RAG ON:  {len(context_with_rag)} chars, {time_with_rag*1000:.0f}ms")
            logger.info(f"  RAG thêm: {len(context_with_rag) - len(context_no_rag)} chars")
            
            # Kiểm tra RAG có thêm context không
            has_relevant_content = "guido" in context_with_rag.lower()
            logger.info(f"  Có nội dung liên quan: {has_relevant_content}")
            
            success = (
                len(context_with_rag) > len(context_no_rag) and
                has_relevant_content
            )
            
            self.record_result(
                "RAG Comparison",
                success,
                f"+{len(context_with_rag) - len(context_no_rag)} chars"
            )
            
            # Cleanup
            logger.info("\nDọn dẹp...")
            await course_indexing_service.delete_course_index(test_course.id)
            await test_course.delete()
            await chat.delete()
            
            if success:
                logger.info("\nPASSED - RAG thêm context liên quan")
            else:
                logger.warning("\nFAILED - RAG không cải thiện context")
            
            return success
            
        except Exception as e:
            logger.error(f"FAILED - Lỗi: {e}")
            import traceback
            traceback.print_exc()
            self.record_result("RAG Comparison", False, str(e))
            return False
    
    async def test_large_content_indexing(self) -> bool:
        """Test 6: Index content lớn và đo performance"""
        logger.info("\n" + "="*70)
        logger.info("TEST 6: Large Content Indexing Performance")
        logger.info("="*70)
        
        try:
            from services.embedding_service import embedding_service
            from services.vector_service import vector_service
            
            # Tạo content lớn (giả lập 1 course với nhiều lessons)
            num_chunks = 20
            logger.info(f"Đang tạo {num_chunks} chunks content...")
            
            chunks = []
            for i in range(num_chunks):
                chunks.append(
                    f"Lesson {i+1}: Python programming concept number {i+1}. "
                    f"This lesson covers important topics in Python development. "
                    f"Students will learn about variables, functions, classes, and modules. "
                    f"The content includes practical examples and exercises."
                )
            
            # Test embedding generation
            logger.info("\nTest 6.1: Embedding Generation")
            start = time.time()
            embeddings = await embedding_service.generate_embeddings_batch(chunks)
            embed_time = time.time() - start
            
            logger.info(f"  Thời gian: {embed_time:.2f}s")
            logger.info(f"  Tốc độ: {num_chunks/embed_time:.1f} chunks/s")
            
            # Test vector upsert
            logger.info("\nTest 6.2: Vector Upsert")
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vectors.append({
                    "id": f"perf-test-{i}",
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "chunk_index": i
                    }
                })
            
            start = time.time()
            _ = await vector_service.upsert_vectors(vectors, namespace="performance-test")
            upsert_time = time.time() - start
            logger.info(f"  Thời gian: {upsert_time:.2f}s")
            logger.info(f"  Tốc độ: {num_chunks/upsert_time:.1f} vectors/s")
            
            # Test search speed
            logger.info("\nTest 6.3: Search Speed")
            query = "Python programming lessons"
            query_embedding = await embedding_service.generate_query_embedding(query)
            
            search_times = []
            for i in range(5):
                start = time.time()
                _ = await vector_service.search(
                    query_vector=query_embedding,
                    top_k=5,
                    namespace="performance-test"
                )
                elapsed = time.time() - start
                search_times.append(elapsed)
                logger.info(f"  Search {i+1}: {elapsed*1000:.0f}ms")
            
            avg_search = sum(search_times) / len(search_times)
            logger.info(f"  Trung bình: {avg_search*1000:.0f}ms")
            
            # Tổng kết
            total_time = embed_time + upsert_time
            logger.info("\nTổng kết:")
            logger.info(f"  Embedding: {embed_time:.2f}s")
            logger.info(f"  Upsert: {upsert_time:.2f}s")
            logger.info(f"  Search avg: {avg_search*1000:.0f}ms")
            logger.info(f"  Tổng thời gian index: {total_time:.2f}s")
            
            # Success nếu search < 100ms
            success = avg_search < 0.1
            
            self.record_result(
                "Large Content Indexing",
                success,
                f"{num_chunks} chunks, search {avg_search*1000:.0f}ms"
            )
            
            # Cleanup
            logger.info("\nDọn dẹp...")
            await vector_service.reset_collection("performance-test")
            
            if success:
                logger.info("\nPASSED - Performance tốt")
            else:
                logger.warning("\nWARNING - Search hơi chậm")
            
            return success
            
        except Exception as e:
            logger.error(f"FAILED - Lỗi: {e}")
            self.record_result("Large Content Indexing", False, str(e))
            return False
    
    def print_summary(self):
        """In tổng kết kết quả"""
        logger.info("\n" + "="*70)
        logger.info("TỔNG KẾT")
        logger.info("="*70)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        for result in self.results:
            status = "PASSED" if result["passed"] else "FAILED"
            logger.info(f"{status:8} - {result['test']:40} {result['details']}")
        
        logger.info("="*70)
        logger.info(f"Kết quả: {passed}/{total} tests PASSED")
        
        if passed == total:
            logger.info("\nTất cả tests đều PASSED! AI integration hoạt động tốt.")
        else:
            logger.warning(f"\n{total - passed} test(s) FAILED. Cần kiểm tra lại.")
        
        logger.info("="*70)


async def main():
    """Chạy tất cả tests"""
    logger.info("\n" + "="*70)
    logger.info("AI INTEGRATION TESTING")
    logger.info("Test các chức năng AI: Generation, Performance, RAG")
    logger.info("="*70)
    
    tester = AIIntegrationTester()
    
    tests = [
        tester.test_google_ai_connection,
        tester.test_course_content_generation,
        tester.test_quiz_generation,
        tester.test_embedding_performance,
        tester.test_rag_comparison,
        tester.test_large_content_indexing
    ]
    
    for test_func in tests:
        try:
            await test_func()
        except Exception as e:
            logger.error(f"Test crashed: {e}")
            import traceback
            traceback.print_exc()
    
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
