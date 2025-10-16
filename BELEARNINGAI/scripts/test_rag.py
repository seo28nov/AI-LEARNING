"""
Test RAG (Retrieval-Augmented Generation) System

Script này test toàn bộ RAG pipeline:
1. Embedding generation
2. Course indexing
3. Vector search
4. Chat với RAG

Run: python scripts/test_rag.py
"""
import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_embedding_service():
    """Test 1: Embedding Service"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Embedding Service")
    logger.info("="*70)
    
    try:
        from services.embedding_service import embedding_service
        
        # Test connection
        logger.info("📡 Testing Google AI connection...")
        success = await embedding_service.test_connection()
        
        if not success:
            logger.error("❌ Embedding service test failed!")
            return False
        
        logger.info("✅ Embedding service working!")
        
        # Test single embedding
        logger.info("\n📝 Testing single embedding generation...")
        text = "Python là ngôn ngữ lập trình high-level"
        embedding = await embedding_service.generate_embedding(text)
        
        logger.info(f"   Embedding dimension: {len(embedding)}")
        logger.info(f"   First 5 values: {embedding[:5]}")
        
        assert len(embedding) == 768, "Wrong embedding dimension!"
        
        # Test batch embeddings
        logger.info("\n📝 Testing batch embedding generation...")
        texts = [
            "Python list comprehension",
            "JavaScript async/await",
            "SQL JOIN operations"
        ]
        embeddings = await embedding_service.generate_embeddings_batch(texts)
        
        logger.info(f"   Generated {len(embeddings)} embeddings")
        assert len(embeddings) == 3, "Batch generation failed!"
        
        logger.info("✅ TEST 1 PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 1 FAILED: {e}")
        return False


async def test_vector_service():
    """Test 2: Vector Service (ChromaDB)"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Vector Service (ChromaDB)")
    logger.info("="*70)
    
    try:
        from services.vector_service import vector_service
        from services.embedding_service import embedding_service
        
        # Test collection stats
        logger.info("📊 Checking ChromaDB connection...")
        stats = await vector_service.get_collection_stats("test")
        logger.info(f"   Collection: {stats['name']}")
        logger.info(f"   Current vectors: {stats['count']}")
        
        # Test upsert
        logger.info("\n📝 Testing vector upsert...")
        
        # Generate test embeddings
        test_texts = [
            "Python is a programming language",
            "JavaScript is used for web development",
            "SQL is for database queries"
        ]
        
        embeddings = await embedding_service.generate_embeddings_batch(test_texts)
        
        # Prepare vectors
        vectors = []
        for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
            vectors.append({
                "id": f"test-vector-{i}",
                "values": embedding,
                "metadata": {
                    "text": text,
                    "title": f"Test {i+1}",
                    "content_type": "test"
                }
            })
        
        # Upsert
        result = await vector_service.upsert_vectors(vectors, namespace="test")
        
        logger.info(f"   Upserted: {result['upserted_count']} vectors")
        assert result["success"], "Upsert failed!"
        
        # Test search
        logger.info("\n🔍 Testing vector search...")
        query_text = "programming languages"
        query_embedding = await embedding_service.generate_query_embedding(query_text)
        
        results = await vector_service.search(
            query_vector=query_embedding,
            top_k=2,
            namespace="test"
        )
        
        logger.info(f"   Query: '{query_text}'")
        logger.info(f"   Found: {len(results)} results")
        
        for i, result in enumerate(results, 1):
            logger.info(f"   [{i}] Score: {result['score']:.3f}")
            logger.info(f"       Text: {result['metadata']['text']}")
        
        assert len(results) > 0, "Search returned no results!"
        
        # Cleanup
        logger.info("\n🗑️ Cleaning up test data...")
        await vector_service.reset_collection("test")
        
        logger.info("✅ TEST 2 PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 2 FAILED: {e}")
        return False


async def test_course_indexing():
    """Test 3: Course Indexing Service"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Course Indexing Service")
    logger.info("="*70)
    
    try:
        from models.models import Course, CourseChapter, Lesson
        from services.course_indexing_service import course_indexing_service
        from beanie import init_beanie
        from motor.motor_asyncio import AsyncIOMotorClient
        from config.config import settings
        
        # Init database
        logger.info("📡 Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.mongodb_url)
        await init_beanie(
            database=client[settings.mongodb_database],
            document_models=[Course]
        )
        logger.info("✅ MongoDB connected")
        
        # Create test course
        logger.info("\n📝 Creating test course...")
        
        test_course = Course(
            title="Python Fundamentals - Test Course",
            description="A comprehensive course about Python programming fundamentals",
            instructor_id="test-instructor",
            level="beginner",
            status="published",
            chapters=[
                CourseChapter(
                    title="Chapter 1: Introduction to Python",
                    description="Learn the basics of Python programming language",
                    order=1,
                    lessons=[
                        Lesson(
                            title="What is Python?",
                            content="""Python is a high-level, interpreted programming language. 
                            It was created by Guido van Rossum and first released in 1991. 
                            Python emphasizes code readability with significant indentation. 
                            It supports multiple programming paradigms including procedural, 
                            object-oriented, and functional programming.""",
                            order=1,
                            duration_minutes=15
                        ),
                        Lesson(
                            title="Python Variables and Data Types",
                            content="""Variables in Python don't need explicit declaration. 
                            Python has several built-in data types: int, float, str, bool, list, 
                            tuple, dict, and set. You can assign values using the = operator. 
                            Example: x = 10, name = "John", numbers = [1, 2, 3]""",
                            order=2,
                            duration_minutes=20
                        )
                    ]
                ),
                CourseChapter(
                    title="Chapter 2: Control Flow",
                    description="Learn about if statements, loops, and control structures",
                    order=2,
                    lessons=[
                        Lesson(
                            title="If Statements and Conditions",
                            content="""Python uses if, elif, and else for conditional execution. 
                            Syntax: if condition: statement. Indentation is crucial. 
                            Comparison operators: ==, !=, <, >, <=, >=. 
                            Logical operators: and, or, not.""",
                            order=1,
                            duration_minutes=25
                        )
                    ]
                )
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await test_course.insert()
        logger.info(f"✅ Created course: {test_course.id}")
        
        # Index course
        logger.info("\n📦 Indexing course...")
        result = await course_indexing_service.index_course(test_course)
        
        logger.info(f"   Success: {result['success']}")
        logger.info(f"   Chunks indexed: {result['chunks_indexed']}")
        
        assert result["success"], "Indexing failed!"
        assert result["chunks_indexed"] > 0, "No chunks indexed!"
        
        # Test search
        logger.info("\n🔍 Testing course content search...")
        
        test_queries = [
            "What is Python programming language?",
            "Python variables and data types",
            "if statements in Python"
        ]
        
        for query in test_queries:
            logger.info(f"\n   Query: '{query}'")
            
            results = await course_indexing_service.search_course_content(
                query=query,
                course_id=str(test_course.id),
                top_k=2
            )
            
            logger.info(f"   Results: {len(results)}")
            
            for i, result in enumerate(results, 1):
                logger.info(f"   [{i}] Score: {result['score']:.3f}")
                logger.info(f"       Title: {result['title']}")
                logger.info(f"       Text: {result['text'][:80]}...")
        
        # Cleanup
        logger.info("\n🗑️ Cleaning up...")
        await course_indexing_service.delete_course_index(test_course.id)
        await test_course.delete()
        
        logger.info("✅ TEST 3 PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_rag_chat():
    """Test 4: RAG Chat Integration"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: RAG Chat Integration")
    logger.info("="*70)
    
    try:
        from models.models import Course, CourseChapter, Lesson, ChatDocument
        from services.course_indexing_service import course_indexing_service
        from services.chat_service import build_context
        from beanie import init_beanie
        from motor.motor_asyncio import AsyncIOMotorClient
        from config.config import settings
        
        # Init database
        logger.info("📡 Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.mongodb_url)
        await init_beanie(
            database=client[settings.mongodb_database],
            document_models=[Course, ChatDocument]
        )
        
        # Create and index test course
        logger.info("\n📝 Creating and indexing test course...")
        
        test_course = Course(
            title="JavaScript Basics",
            description="Learn JavaScript programming",
            instructor_id="test-instructor",
            level="beginner",
            status="published",
            chapters=[
                CourseChapter(
                    title="Introduction",
                    description="JavaScript fundamentals",
                    order=1,
                    lessons=[
                        Lesson(
                            title="What is JavaScript?",
                            content="JavaScript is a programming language for web development. It runs in browsers and Node.js.",
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
        
        # Index
        result = await course_indexing_service.index_course(test_course)
        logger.info(f"✅ Indexed {result['chunks_indexed']} chunks")
        
        # Create chat session
        logger.info("\n💬 Creating chat session...")
        
        chat = ChatDocument(
            user_id="test-user",
            course_id=str(test_course.id),
            title="Test Chat",
            messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await chat.insert()
        
        # Test context building WITHOUT RAG
        logger.info("\n🔍 Testing context building WITHOUT RAG...")
        context_no_rag = await build_context(
            chat=chat,
            use_rag=False,
            user_id="test-user",
            user_message="What is JavaScript?"
        )
        
        logger.info(f"   Context length (no RAG): {len(context_no_rag)} chars")
        
        # Test context building WITH RAG
        logger.info("\n🔍 Testing context building WITH RAG...")
        context_with_rag = await build_context(
            chat=chat,
            use_rag=True,
            user_id="test-user",
            user_message="What is JavaScript?"
        )
        
        logger.info(f"   Context length (with RAG): {len(context_with_rag)} chars")
        logger.info("\n   Context preview:")
        logger.info(f"   {context_with_rag[:300]}...")
        
        # Verify RAG context is longer (contains retrieved chunks)
        assert len(context_with_rag) > len(context_no_rag), "RAG context should be longer!"
        assert "JavaScript" in context_with_rag, "Context should contain relevant content!"
        
        # Cleanup
        logger.info("\n🗑️ Cleaning up...")
        await course_indexing_service.delete_course_index(test_course.id)
        await test_course.delete()
        await chat.delete()
        
        logger.info("✅ TEST 4 PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "🚀"*35)
    logger.info("  RAG SYSTEM TESTING")
    logger.info("🚀"*35 + "\n")
    
    tests = [
        ("Embedding Service", test_embedding_service),
        ("Vector Service (ChromaDB)", test_vector_service),
        ("Course Indexing", test_course_indexing),
        ("RAG Chat Integration", test_rag_chat)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} - {test_name}")
    
    logger.info("="*70)
    logger.info(f"Result: {passed}/{total} tests passed")
    logger.info("="*70 + "\n")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! RAG system is working correctly.")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} test(s) failed. Please fix before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
