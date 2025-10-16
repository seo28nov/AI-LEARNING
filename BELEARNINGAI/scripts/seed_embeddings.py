"""
Script để index tất cả courses vào FAISS Vector Database.

Script này:
1. Load tất cả courses từ MongoDB
2. Sử dụng CourseIndexingService để chunk và embed
3. Upsert embeddings vào FAISS Vector Database
4. In thống kê kết quả

Usage:
    python scripts/seed_embeddings.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from config.config import get_settings
from models.models import CourseDocument
from services.course_indexing_service import course_indexing_service


async def init_db():
    """Khởi tạo kết nối database."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[CourseDocument]
    )
    
    return client


async def seed_embeddings():
    """Index tất cả courses vào FAISS Vector Database."""
    print("\n" + "="*60)
    print("  INDEX COURSES TO FAISS VECTOR DATABASE")
    print("="*60)
    
    # Khởi tạo database
    client = await init_db()
    
    try:
        # Lấy tất cả courses
        print("\n📚 Loading courses from MongoDB...")
        courses = await CourseDocument.find_all().to_list()
        
        if not courses:
            print("⚠️  Không có courses nào trong database!")
            print("💡 Chạy: python scripts/initial_data.py trước")
            return
        
        print(f"✅ Tìm thấy {len(courses)} courses")
        
        # Index từng course
        total_chunks = 0
        total_vectors = 0
        successful = 0
        failed = 0
        
        print("\n🔄 Bắt đầu indexing...")
        print("-" * 60)
        
        for i, course in enumerate(courses, 1):
            try:
                print(f"\n[{i}/{len(courses)}] Indexing: {course.title}")
                
                # Convert Beanie Document to Pydantic model
                # CourseIndexingService expects a Course model
                course_dict = course.dict()
                course_dict["id"] = str(course.id)
                
                # Index course
                result = await course_indexing_service.index_course(course)
                
                # Thống kê
                chunks = result.get("chunks_created", 0)
                vectors = result.get("vectors_stored", 0)
                
                total_chunks += chunks
                total_vectors += vectors
                successful += 1
                
                print(f"  ✅ Success: {chunks} chunks, {vectors} vectors")
                
            except Exception as e:
                failed += 1
                print(f"  ❌ Failed: {str(e)}")
                continue
        
        # Tổng kết
        print("\n" + "="*60)
        print("  📊 INDEXING SUMMARY")
        print("="*60)
        print(f"Total Courses: {len(courses)}")
        print(f"Successful:    {successful}")
        print(f"Failed:        {failed}")
        print(f"Total Chunks:  {total_chunks}")
        print(f"Total Vectors: {total_vectors}")
        print("="*60)
        
        if successful > 0:
            print("\n✅ Indexing completed successfully!")
            print("\n💡 Bây giờ có thể test RAG chat:")
            print("   - Chạy app: uvicorn app.main:app")
            print("   - Test endpoint: POST /api/v1/chat")
        else:
            print("\n❌ Không có course nào được index!")
        
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        raise
    finally:
        client.close()


async def verify_vectordb():
    """Verify FAISS Vector Database đã có embeddings chưa."""
    print("\n🔍 Verifying FAISS Vector Database...")
    
    try:
        from services.vector_service import vector_service
        
        if vector_service is None:
            print("❌ Vector service not initialized")
            return
        
        # Get collection stats
        stats = await vector_service.get_collection_stats("courses")
        count = stats.get("count", 0)
        
        print(f"✅ FAISS Vector Database contains {count} vectors")
        
        if count > 0:
            print("✅ FAISS Vector Database is ready for RAG queries!")
        else:
            print("⚠️  FAISS Vector Database is empty. Run indexing first.")
        
    except Exception as e:
        print(f"❌ Error verifying FAISS Vector Database: {e}")
if __name__ == "__main__":
    print("\n🚀 Starting embedding seeding process...\n")
    
    # Run seeding
    asyncio.run(seed_embeddings())
    
    # Verify
    asyncio.run(verify_vectordb())
    
    print("\n✅ Done!\n")
