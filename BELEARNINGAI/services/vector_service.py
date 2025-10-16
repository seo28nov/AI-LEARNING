"""
Vector Service - FAISS Implementation cho RAG System.

FAISS được chọn làm vector database cho BeLearning vì:
✅ Local storage - không phụ thuộc cloud, data stays on-premise
✅ Free & open source - không có chi phí định kỳ cho schools
✅ Production ready - được Facebook sử dụng trong production
✅ Privacy friendly - nội dung khóa học là tài sản, cần lưu local
✅ Easy setup - không cần build tools hoặc cấu hình phức tạp
✅ Python native - integration mượt mà với FastAPI
✅ Persistent storage - data không mất khi restart
✅ Extremely fast - nhanh hơn ChromaDB đáng kể

FAISS phù hợp với educational platform vì:
- Scale excellent cho hàng nghìn courses
- Performance vượt trội cho real-time search
- Cost-effective cho institutions
- Self-hosted - full control over data
- No compilation issues trên Windows
"""
import logging

# Import FAISS service
from services.faiss_vector_service import FAISSVectorService

logger = logging.getLogger(__name__)


# Backward compatibility: ChromaVectorService = FAISS
# Để không phá vỡ code cũ có thể đang import ChromaVectorService
ChromaVectorService = FAISSVectorService


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Khởi tạo FAISS vector service duy nhất
try:
    vector_service = FAISSVectorService()
    logger.info("✅ Vector Service (FAISS) singleton initialized")
except Exception as e:
    logger.error(f"❌ Cannot initialize FAISS Vector Service: {e}")
    vector_service = None
