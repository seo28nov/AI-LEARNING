"""
Course Indexing Service - Index nội dung khóa học vào vector database.

Service này chịu trách nhiệm:
1. Extract text từ course content (title, description, chapters, lessons)
2. Chunk text thành các đoạn nhỏ (với overlap để giữ context)
3. Generate embeddings cho mỗi chunk
4. Store embeddings vào vector database
5. Update/reindex khi course thay đổi
"""
from typing import List, Dict, Optional, Any
import logging
import re
from datetime import datetime

from beanie import PydanticObjectId
from models.models import CourseDocument
from services.embedding_service import embedding_service
from services.vector_service import vector_service

logger = logging.getLogger(__name__)


class CourseIndexingService:
    """Service để index course content vào vector database."""
    
    # Constants
    CHUNK_SIZE = 500  # Số từ mỗi chunk
    CHUNK_OVERLAP = 100  # Số từ overlap giữa các chunks
    NAMESPACE = "courses"  # Namespace trong vector DB
    
    def __init__(self):
        """Khởi tạo Course Indexing Service."""
        logger.info("✅ Course Indexing Service đã sẵn sàng")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean và normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (giữ lại dấu câu cơ bản)
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        # Strip
        text = text.strip()
        
        return text
    
    def _split_into_chunks(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Chia text thành các chunks với overlap.
        
        Args:
            text: Text cần chia
            chunk_size: Số từ mỗi chunk (default: CHUNK_SIZE)
            overlap: Số từ overlap (default: CHUNK_OVERLAP)
            
        Returns:
            List of text chunks
            
        Example:
            >>> text = "Python is a programming language. It is easy to learn."
            >>> chunks = self._split_into_chunks(text, chunk_size=5, overlap=2)
        """
        if not text:
            return []
        
        chunk_size = chunk_size or self.CHUNK_SIZE
        overlap = overlap or self.CHUNK_OVERLAP
        
        # Split thành words
        words = text.split()
        
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            # Lấy chunk
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            # Move start pointer (trừ overlap)
            start = end - overlap
            
            # Nếu còn ít từ hơn overlap, lấy hết
            if len(words) - end < overlap:
                break
        
        return chunks
    
    async def _extract_course_content(self, course: CourseDocument) -> List[Dict[str, Any]]:
        """
        Extract tất cả nội dung text từ course.
        
        Args:
            course: Course object
            
        Returns:
            List of content dicts với fields:
                - text: Nội dung text
                - title: Tiêu đề của chunk
                - course_id: ID của course
                - chapter_id: ID của chapter (nếu có)
                - lesson_id: ID của lesson (nếu có)
                - content_type: Loại content (overview, chapter, lesson)
        """
        contents = []
        
        try:
            # 1. Course overview (title + description)
            overview_text = f"{course.title}\n\n{course.description or ''}"
            overview_text = self._clean_text(overview_text)
            
            if overview_text:
                contents.append({
                    "text": overview_text,
                    "title": course.title,
                    "course_id": str(course.id),
                    "chapter_id": None,
                    "lesson_id": None,
                    "content_type": "overview"
                })
            
            # 2. Chapters và Lessons
            if course.chapters:
                for chapter in course.chapters:
                    # Chapter content
                    chapter_text = f"{chapter.title}\n\n{chapter.description or ''}"
                    chapter_text = self._clean_text(chapter_text)
                    
                    if chapter_text:
                        contents.append({
                            "text": chapter_text,
                            "title": f"{course.title} - {chapter.title}",
                            "course_id": str(course.id),
                            "chapter_id": str(chapter.id),
                            "lesson_id": None,
                            "content_type": "chapter"
                        })
                    
                    # Lessons trong chapter
                    if chapter.lessons:
                        for lesson in chapter.lessons:
                            lesson_text = f"{lesson.title}\n\n{lesson.content or ''}"
                            lesson_text = self._clean_text(lesson_text)
                            
                            if lesson_text:
                                contents.append({
                                    "text": lesson_text,
                                    "title": f"{course.title} - {chapter.title} - {lesson.title}",
                                    "course_id": str(course.id),
                                    "chapter_id": str(chapter.id),
                                    "lesson_id": str(lesson.id),
                                    "content_type": "lesson"
                                })
            
            logger.info(f"📄 Extracted {len(contents)} content pieces from course {course.id}")
            
            return contents
            
        except Exception as e:
            logger.error(f"❌ Lỗi extract course content: {e}")
            return []
    
    async def _chunk_content(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chia các content thành chunks nhỏ hơn.
        
        Args:
            contents: List of content dicts
            
        Returns:
            List of chunked content dicts
        """
        chunked_contents = []
        
        for content in contents:
            text = content["text"]
            
            # Split into chunks
            chunks = self._split_into_chunks(text)
            
            # Nếu chỉ có 1 chunk, giữ nguyên
            if len(chunks) == 1:
                chunked_contents.append(content)
            else:
                # Tạo multiple chunks
                for i, chunk_text in enumerate(chunks):
                    chunk_dict = content.copy()
                    chunk_dict["text"] = chunk_text
                    chunk_dict["chunk_index"] = i
                    chunk_dict["total_chunks"] = len(chunks)
                    chunked_contents.append(chunk_dict)
        
        logger.info(f"📊 Chunked into {len(chunked_contents)} total chunks")
        
        return chunked_contents
    
    async def index_course(self, course: CourseDocument) -> Dict[str, Any]:
        """
        Index một course vào vector database.
        
        Workflow:
        1. Extract content từ course
        2. Chunk content thành các đoạn nhỏ
        3. Generate embeddings cho mỗi chunk
        4. Store vào vector database
        
        Args:
            course: Course object cần index
            
        Returns:
            Dict với kết quả:
                - success: True/False
                - course_id: ID của course
                - chunks_indexed: Số chunks đã index
                - message: Thông báo
        """
        try:
            logger.info(f"🚀 Bắt đầu index course: {course.id} - {course.title}")
            
            # 1. Extract content
            contents = await self._extract_course_content(course)
            
            if not contents:
                logger.warning(f"⚠️ Course {course.id} không có content để index")
                return {
                    "success": False,
                    "course_id": str(course.id),
                    "chunks_indexed": 0,
                    "message": "No content to index"
                }
            
            # 2. Chunk content
            chunked_contents = await self._chunk_content(contents)
            
            # 3. Generate embeddings
            texts = [c["text"] for c in chunked_contents]
            embeddings = await embedding_service.generate_embeddings_batch(
                texts,
                task_type="retrieval_document"
            )
            
            # 4. Prepare vectors cho vector database
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunked_contents, embeddings)):
                vector = {
                    "id": f"{course.id}_chunk_{i}",
                    "values": embedding,
                    "metadata": {
                        "course_id": chunk["course_id"],
                        "chapter_id": chunk.get("chapter_id"),
                        "lesson_id": chunk.get("lesson_id"),
                        "content_type": chunk["content_type"],
                        "title": chunk["title"],
                        "text": chunk["text"][:1000],  # Giới hạn text trong metadata
                        "chunk_index": chunk.get("chunk_index", 0),
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                }
                vectors.append(vector)
            
            # 5. Upsert vào vector database
            upsert_result = await vector_service.upsert_vectors(vectors, namespace=self.NAMESPACE)
            
            # Log kết quả upsert để debug
            logger.info(f"✅ Đã index {len(vectors)} chunks cho course {course.id}")
            logger.debug(f"Upsert result: {upsert_result}")
            
            return {
                "success": True,
                "course_id": str(course.id),
                "chunks_indexed": len(vectors),
                "message": "Course indexed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi index course {course.id}: {e}")
            return {
                "success": False,
                "course_id": str(course.id),
                "chunks_indexed": 0,
                "message": f"Error: {str(e)}"
            }
    
    async def reindex_course(self, course_id: PydanticObjectId) -> Dict[str, Any]:
        """
        Reindex một course (xóa index cũ và tạo lại).
        
        Args:
            course_id: ID của course
            
        Returns:
            Dict với kết quả
        """
        try:
            logger.info(f"🔄 Reindex course: {course_id}")
            
            # 1. Xóa index cũ
            await self.delete_course_index(course_id)
            
            # 2. Load course từ database
            course = await CourseDocument.get(course_id)
            
            if not course:
                logger.error(f"❌ Không tìm thấy course {course_id}")
                return {
                    "success": False,
                    "course_id": str(course_id),
                    "message": "Course not found"
                }
            
            # 3. Index lại
            result = await self.index_course(course)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Lỗi reindex course {course_id}: {e}")
            return {
                "success": False,
                "course_id": str(course_id),
                "message": f"Error: {str(e)}"
            }
    
    async def delete_course_index(self, course_id: PydanticObjectId) -> Dict[str, Any]:
        """
        Xóa index của một course khỏi vector database.
        
        Args:
            course_id: ID của course
            
        Returns:
            Dict với kết quả
        """
        try:
            logger.info(f"🗑️ Xóa index của course: {course_id}")
            
            # Delete by filter
            delete_result = await vector_service.delete_by_filter(
                filter_dict={"course_id": str(course_id)},
                namespace=self.NAMESPACE
            )
            
            logger.info(f"✅ Đã xóa index của course {course_id}")
            logger.debug(f"Delete result: {delete_result}")
            
            return {
                "success": True,
                "course_id": str(course_id),
                "message": "Course index deleted"
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi xóa course index {course_id}: {e}")
            return {
                "success": False,
                "course_id": str(course_id),
                "message": f"Error: {str(e)}"
            }
    
    async def search_course_content(
        self,
        query: str,
        course_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search content trong courses.
        
        Args:
            query: Query string từ user
            course_id: Optional - chỉ search trong course này
            top_k: Số kết quả trả về
            
        Returns:
            List of search results với:
                - text: Nội dung
                - title: Tiêu đề
                - course_id: ID course
                - score: Similarity score
                
        Example:
            >>> results = await indexing_service.search_course_content(
            ...     "Python list comprehension",
            ...     top_k=3
            ... )
        """
        try:
            logger.info(f"🔍 Search: '{query}' (top_k={top_k})")
            
            # 1. Generate query embedding
            query_embedding = await embedding_service.generate_query_embedding(query)
            
            # 2. Build filter
            filter_dict = None
            if course_id:
                filter_dict = {"course_id": course_id}
            
            # 3. Search trong vector database
            results = await vector_service.search(
                query_vector=query_embedding,
                top_k=top_k,
                namespace=self.NAMESPACE,
                filter_dict=filter_dict
            )
            
            # 4. Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result["metadata"].get("text", ""),
                    "title": result["metadata"].get("title", ""),
                    "course_id": result["metadata"].get("course_id"),
                    "chapter_id": result["metadata"].get("chapter_id"),
                    "lesson_id": result["metadata"].get("lesson_id"),
                    "content_type": result["metadata"].get("content_type"),
                    "score": result.get("score", 0.0)
                })
            
            logger.info(f"✅ Tìm thấy {len(formatted_results)} kết quả")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Lỗi search content: {e}")
            return []
    
    async def index_all_courses(self) -> Dict[str, Any]:
        """
        Index tất cả courses trong database.
        
        Dùng cho initial setup hoặc bulk reindex.
        
        Returns:
            Dict với thống kê:
                - total_courses: Tổng số courses
                - indexed: Số courses đã index thành công
                - failed: Số courses bị lỗi
                - total_chunks: Tổng số chunks đã index
        """
        try:
            logger.info("🚀 Bắt đầu index tất cả courses...")
            
            # Load tất cả courses
            courses = await CourseDocument.find_all().to_list()
            
            total_courses = len(courses)
            indexed_count = 0
            failed_count = 0
            total_chunks = 0
            
            for course in courses:
                result = await self.index_course(course)
                
                if result["success"]:
                    indexed_count += 1
                    total_chunks += result["chunks_indexed"]
                else:
                    failed_count += 1
            
            logger.info(f"✅ Hoàn thành index: {indexed_count}/{total_courses} courses")
            
            return {
                "total_courses": total_courses,
                "indexed": indexed_count,
                "failed": failed_count,
                "total_chunks": total_chunks
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi index all courses: {e}")
            return {
                "total_courses": 0,
                "indexed": 0,
                "failed": 0,
                "total_chunks": 0,
                "error": str(e)
            }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Khởi tạo course indexing service duy nhất
course_indexing_service = CourseIndexingService()
logger.info("✅ Course Indexing Service singleton đã được khởi tạo")
