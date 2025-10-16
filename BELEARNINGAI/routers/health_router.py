"""Router health check và RAG system monitoring."""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/vectordb",
    response_model=dict,
    summary="Kiểm tra Vector Database connection",
    description="Kiểm tra xem FAISS Vector Database có hoạt động không và có bao nhiêu vectors"
)
async def check_vectordb() -> Dict[str, Any]:
    """
    Endpoint kiểm tra Vector Database health.
    
    Returns:
        Dict với status và thông tin Vector Database
    """
    try:
        from services.vector_service import vector_service
        
        if vector_service is None:
            raise Exception("Vector service not initialized")
        
        # Get collection stats
        stats = await vector_service.get_collection_stats("courses")
        vector_count = stats.get("count", 0)
        
        return {
            "status": "healthy",
            "service": "FAISS Vector Database",
            "connected": True,
            "vector_count": vector_count,
            "collection": "courses",
            "message": f"FAISS Vector Database hoạt động bình thường với {vector_count} vectors"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "FAISS Vector Database",
            "connected": False,
            "error": str(e),
            "message": "FAISS Vector Database không hoạt động"
        }


@router.get(
    "/embeddings",
    response_model=dict,
    summary="Kiểm tra Embedding Service",
    description="Kiểm tra xem Google AI Embedding service có hoạt động không"
)
async def check_embeddings() -> Dict[str, Any]:
    """
    Endpoint kiểm tra Embedding Service health.
    
    Returns:
        Dict với status và thông tin embedding service
    """
    try:
        from services.embedding_service import embedding_service
        
        # Test generate embedding với text ngắn
        test_text = "Test embedding service"
        embedding = await embedding_service.generate_embedding(
            text=test_text,
            task_type="retrieval_query"
        )
        
        # Kiểm tra embedding dimension
        dimension = len(embedding) if embedding else 0
        expected_dimension = 768
        
        is_healthy = dimension == expected_dimension
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "Google AI Embeddings",
            "connected": True,
            "embedding_dimension": dimension,
            "expected_dimension": expected_dimension,
            "model": "models/embedding-001",
            "message": "Embedding service hoạt động bình thường" if is_healthy else "Embedding dimension không đúng"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Google AI Embeddings",
            "connected": False,
            "error": str(e),
            "message": "Embedding service không hoạt động"
        }


@router.get(
    "/rag-stats",
    response_model=dict,
    summary="Thống kê RAG system",
    description="Thống kê tổng quan về RAG system: số courses indexed, số vectors, etc."
)
async def get_rag_stats() -> Dict[str, Any]:
    """
    Endpoint lấy thống kê RAG system.
    
    Returns:
        Dict với các thống kê RAG
    """
    try:
        from services.vector_service import vector_service
        from models.models import CourseDocument
        
        # Get Vector Database stats
        if vector_service is None:
            raise Exception("Vector service not initialized")
            
        stats = await vector_service.get_collection_stats("courses")
        vector_count = stats.get("count", 0)
        
        # Get MongoDB stats
        total_courses = await CourseDocument.find_all().count()
        published_courses = await CourseDocument.find(
            CourseDocument.is_published
        ).count()
        
        # Estimate average chunks per course
        avg_chunks_per_course = vector_count / total_courses if total_courses > 0 else 0
        
        return {
            "status": "healthy",
            "rag_system": {
                "vectordb": {
                    "total_vectors": vector_count,
                    "collection": "courses",
                    "engine": "FAISS"
                },
                "mongodb": {
                    "total_courses": total_courses,
                    "published_courses": published_courses,
                    "unpublished_courses": total_courses - published_courses
                },
                "indexing": {
                    "indexed_courses": total_courses,  # Assume all are indexed if vectors exist
                    "avg_chunks_per_course": round(avg_chunks_per_course, 2),
                    "total_chunks": vector_count
                }
            },
            "message": "RAG system hoạt động bình thường"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy RAG stats: {str(e)}"
        )


@router.get(
    "/",
    response_model=dict,
    summary="Health check tổng quan",
    description="Kiểm tra tất cả services: MongoDB, FAISS Vector DB, Embeddings"
)
async def overall_health() -> Dict[str, Any]:
    """
    Endpoint health check tổng quan.
    
    Returns:
        Dict với status tất cả services
    """
    # Check Vector Database
    vectordb_status = await check_vectordb()
    
    # Check Embeddings
    embeddings_status = await check_embeddings()
    
    # Check MongoDB
    try:
        from models.models import CourseDocument
        await CourseDocument.find_one()
        mongodb_status = {
            "status": "healthy",
            "service": "MongoDB",
            "connected": True,
            "message": "MongoDB hoạt động bình thường"
        }
    except Exception as e:
        mongodb_status = {
            "status": "unhealthy",
            "service": "MongoDB",
            "connected": False,
            "error": str(e),
            "message": "MongoDB không hoạt động"
        }
    
    # Determine overall status
    all_healthy = all([
        vectordb_status.get("status") == "healthy",
        embeddings_status.get("status") == "healthy",
        mongodb_status.get("status") == "healthy"
    ])
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": {
            "mongodb": mongodb_status,
            "vectordb": vectordb_status,
            "embeddings": embeddings_status
        },
        "message": "Tất cả services hoạt động bình thường" if all_healthy else "Một số services gặp vấn đề"
    }
