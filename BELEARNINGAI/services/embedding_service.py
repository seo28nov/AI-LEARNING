"""
Embedding Service - Generate embeddings sử dụng Google AI.

Service này chịu trách nhiệm:
1. Generate embeddings cho course content (documents)
2. Generate embeddings cho user queries
3. Batch processing để tối ưu API calls
"""
from typing import List
import logging
import asyncio

import google.generativeai as genai
from config.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service để generate text embeddings với Google AI."""
    
    # Constants
    EMBEDDING_MODEL = "models/embedding-001"  # Google AI embedding model
    EMBEDDING_DIMENSION = 768  # Dimension của embedding vector
    MAX_BATCH_SIZE = 100  # Google AI giới hạn 100 texts/request
    
    def __init__(self):
        """
        Khởi tạo Embedding Service.
        
        Cấu hình Google AI API key và model.
        """
        try:
            # Cấu hình Google AI
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            
            logger.info("✅ Embedding Service đã sẵn sàng với Google AI")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo Embedding Service: {e}")
            raise
    
    async def generate_embedding(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """
        Generate embedding cho một đoạn text.
        
        Args:
            text: Text cần generate embedding
            task_type: Loại task:
                - "retrieval_document": Cho nội dung khóa học (documents)
                - "retrieval_query": Cho câu hỏi tìm kiếm (queries)
                - "semantic_similarity": Cho so sánh tương đồng
                
        Returns:
            List of floats (vector embedding với 768 dimensions)
            
        Example:
            >>> embedding_service = EmbeddingService()
            >>> vector = await embedding_service.generate_embedding("Python là ngôn ngữ lập trình")
            >>> len(vector)
            768
        """
        try:
            # Validate input
            if not text or not text.strip():
                logger.warning("⚠️ Text rỗng, trả về zero vector")
                return [0.0] * self.EMBEDDING_DIMENSION
            
            # Truncate text nếu quá dài (Google AI limit ~10k tokens)
            text = text[:10000]
            
            # Generate embedding
            result = genai.embed_content(
                model=self.EMBEDDING_MODEL,
                content=text,
                task_type=task_type
            )
            
            embedding = result["embedding"]
            
            logger.debug(f"✅ Generated embedding: {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Lỗi generate embedding: {e}")
            # Trả về zero vector thay vì raise exception
            return [0.0] * self.EMBEDDING_DIMENSION
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        task_type: str = "retrieval_document"
    ) -> List[List[float]]:
        """
        Generate embeddings cho nhiều texts (batch processing).
        
        Tự động chia thành batches nhỏ để tránh vượt quá API limit.
        
        Args:
            texts: List of texts cần generate embeddings
            task_type: Loại task (retrieval_document hoặc retrieval_query)
            
        Returns:
            List of embedding vectors
            
        Example:
            >>> texts = ["Text 1", "Text 2", "Text 3"]
            >>> embeddings = await embedding_service.generate_embeddings_batch(texts)
            >>> len(embeddings)
            3
        """
        try:
            if not texts:
                logger.warning("⚠️ Texts list rỗng")
                return []
            
            logger.info(f"📊 Bắt đầu generate embeddings cho {len(texts)} texts")
            
            all_embeddings = []
            
            # Chia thành batches
            for i in range(0, len(texts), self.MAX_BATCH_SIZE):
                batch = texts[i:i + self.MAX_BATCH_SIZE]
                
                # Filter ra empty texts
                valid_texts = [t for t in batch if t and t.strip()]
                
                if not valid_texts:
                    # Nếu batch toàn empty, thêm zero vectors
                    all_embeddings.extend(
                        [[0.0] * self.EMBEDDING_DIMENSION] * len(batch)
                    )
                    continue
                
                # Truncate texts
                truncated_texts = [t[:10000] for t in valid_texts]
                
                try:
                    # Generate embeddings cho batch
                    result = genai.embed_content(
                        model=self.EMBEDDING_MODEL,
                        content=truncated_texts,
                        task_type=task_type
                    )
                    
                    # Extract embeddings
                    batch_embeddings = result["embedding"]
                    
                    # Nếu chỉ có 1 text, wrap thành list
                    if isinstance(batch_embeddings[0], float):
                        batch_embeddings = [batch_embeddings]
                    
                    all_embeddings.extend(batch_embeddings)
                    
                    logger.info(f"✅ Batch {i // self.MAX_BATCH_SIZE + 1}: {len(batch_embeddings)} embeddings")
                    
                    # Delay nhỏ để tránh rate limiting
                    if i + self.MAX_BATCH_SIZE < len(texts):
                        await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ Lỗi batch {i // self.MAX_BATCH_SIZE + 1}: {e}")
                    # Thêm zero vectors cho batch bị lỗi
                    all_embeddings.extend(
                        [[0.0] * self.EMBEDDING_DIMENSION] * len(batch)
                    )
            
            logger.info(f"✅ Hoàn thành generate {len(all_embeddings)} embeddings")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"❌ Lỗi generate embeddings batch: {e}")
            # Trả về zero vectors
            return [[0.0] * self.EMBEDDING_DIMENSION] * len(texts)
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding cho search query.
        
        Đây là helper function với task_type="retrieval_query" đã set sẵn.
        
        Args:
            query: Câu hỏi/query từ user
            
        Returns:
            Embedding vector
            
        Example:
            >>> query = "Python list comprehension là gì?"
            >>> embedding = await embedding_service.generate_query_embedding(query)
        """
        return await self.generate_embedding(query, task_type="retrieval_query")
    
    async def generate_document_embedding(self, text: str) -> List[float]:
        """
        Generate embedding cho document/content.
        
        Đây là helper function với task_type="retrieval_document" đã set sẵn.
        
        Args:
            text: Nội dung document
            
        Returns:
            Embedding vector
        """
        return await self.generate_embedding(text, task_type="retrieval_document")
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Tính cosine similarity giữa 2 embeddings.
        
        Args:
            embedding1: Vector embedding thứ nhất
            embedding2: Vector embedding thứ hai
            
        Returns:
            Similarity score từ 0 đến 1 (1 là giống nhất)
            
        Example:
            >>> emb1 = await embedding_service.generate_embedding("Python")
            >>> emb2 = await embedding_service.generate_embedding("Java")
            >>> similarity = embedding_service.compute_similarity(emb1, emb2)
        """
        try:
            # Cosine similarity = dot product / (norm1 * norm2)
            import math
            
            # Dot product
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            
            # Norms
            norm1 = math.sqrt(sum(a * a for a in embedding1))
            norm2 = math.sqrt(sum(b * b for b in embedding2))
            
            # Avoid division by zero
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Cosine similarity
            similarity = dot_product / (norm1 * norm2)
            
            # Clamp to [0, 1]
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"❌ Lỗi compute similarity: {e}")
            return 0.0
    
    async def test_connection(self) -> bool:
        """
        Test xem có thể kết nối và generate embedding không.
        
        Returns:
            True nếu test thành công, False nếu thất bại
        """
        try:
            logger.info("🧪 Testing Embedding Service...")
            
            # Test với text đơn giản
            test_text = "This is a test."
            embedding = await self.generate_embedding(test_text)
            
            # Verify embedding
            if len(embedding) == self.EMBEDDING_DIMENSION:
                logger.info("✅ Embedding Service test thành công!")
                return True
            else:
                logger.error(f"❌ Embedding dimension sai: {len(embedding)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Embedding Service test thất bại: {e}")
            return False


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Khởi tạo embedding service duy nhất
try:
    embedding_service = EmbeddingService()
    logger.info("✅ Embedding Service singleton đã được khởi tạo")
except Exception as e:
    logger.error(f"❌ Không thể khởi tạo Embedding Service: {e}")
    embedding_service = None
