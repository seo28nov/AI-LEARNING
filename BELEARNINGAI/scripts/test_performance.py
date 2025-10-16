"""
Performance Testing Script

Test hiệu suất hệ thống:
- Response time các endpoints
- Database query performance
- Concurrent user handling
- Vector search performance
- Memory usage

Run: python scripts/test_performance.py
"""
import asyncio
import logging
import time
import statistics
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceTester:
    """Performance Testing"""
    
    def __init__(self):
        self.results = {}
    
    def record_metric(self, test: str, metric: str, value: float, unit: str = "ms"):
        """Ghi metric"""
        if test not in self.results:
            self.results[test] = {}
        self.results[test][metric] = {"value": value, "unit": unit}
    
    async def test_api_response_times(self) -> bool:
        """Test 1: API Response Times"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: API Response Times")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # Setup: Tạo user và course
                logger.info("\nSetup: Tạo test data...")
                
                # Đăng ký student
                await client.post(
                    "/auth/register",
                    json={
                        "email": "perf_student@test.com",
                        "password": "Student123!",
                        "full_name": "Perf Student",
                        "role": "student"
                    }
                )
                
                login = await client.post(
                    "/auth/login",
                    json={
                        "email": "perf_student@test.com",
                        "password": "Student123!"
                    }
                )
                token = login.json()["access_token"]
                
                # Đăng ký instructor
                await client.post(
                    "/auth/register",
                    json={
                        "email": "perf_instructor@test.com",
                        "password": "Instructor123!",
                        "full_name": "Perf Instructor",
                        "role": "instructor"
                    }
                )
                
                instructor_login = await client.post(
                    "/auth/login",
                    json={
                        "email": "perf_instructor@test.com",
                        "password": "Instructor123!"
                    }
                )
                instructor_token = instructor_login.json()["access_token"]
                
                # Tạo course
                course_response = await client.post(
                    "/courses",
                    headers={"Authorization": f"Bearer {instructor_token}"},
                    json={
                        "title": "Performance Test Course",
                        "description": "Test course",
                        "level": "beginner",
                        "category": "programming",
                        "status": "published"
                    }
                )
                course_id = course_response.json()["id"]
                
                # Test endpoints
                endpoints = [
                    ("GET", "/courses", None, None),
                    ("GET", f"/courses/{course_id}", None, None),
                    ("POST", "/enrollments", {"course_id": course_id}, token),
                    ("GET", "/users/me", None, token),
                ]
                
                for method, path, body, auth_token in endpoints:
                    logger.info(f"\nTesting {method} {path}")
                    
                    times = []
                    for _ in range(10):  # 10 lần đo
                        start = time.time()
                        
                        headers = {}
                        if auth_token:
                            headers["Authorization"] = f"Bearer {auth_token}"
                        
                        if method == "GET":
                            _ = await client.get(path, headers=headers)
                        elif method == "POST":
                            _ = await client.post(path, json=body, headers=headers)
                        
                        elapsed = (time.time() - start) * 1000  # ms
                        times.append(elapsed)
                    
                    avg_time = statistics.mean(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    logger.info(f"  Avg: {avg_time:.1f}ms")
                    logger.info(f"  Min: {min_time:.1f}ms")
                    logger.info(f"  Max: {max_time:.1f}ms")
                    
                    test_name = f"{method} {path}"
                    self.record_metric(test_name, "avg", avg_time, "ms")
                    self.record_metric(test_name, "min", min_time, "ms")
                    self.record_metric(test_name, "max", max_time, "ms")
                    
                    # Check performance thresholds
                    if avg_time < 100:
                        logger.info("  Status: EXCELLENT (<100ms)")
                    elif avg_time < 300:
                        logger.info("  Status: GOOD (<300ms)")
                    elif avg_time < 1000:
                        logger.info("  Status: ACCEPTABLE (<1s)")
                    else:
                        logger.warning("  Status: SLOW (>1s)")
                
                return True
                
        except Exception as e:
            logger.error(f"Test 1 failed: {e}")
            return False
    
    async def test_concurrent_requests(self) -> bool:
        """Test 2: Concurrent Request Handling"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: Concurrent Request Handling")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            
            async def make_request(client_num: int):
                """Tạo 1 request"""
                async with AsyncClient(transport=transport, base_url="http://test") as client:  
                    start = time.time()
                    _ = await client.get("/courses")
                    elapsed = (time.time() - start) * 1000
                    return elapsed            # Test với số concurrent requests tăng dần
            concurrent_levels = [1, 5, 10, 20]
            
            for num_concurrent in concurrent_levels:
                logger.info(f"\nTest với {num_concurrent} concurrent requests")
                
                start = time.time()
                tasks = [make_request(i) for i in range(num_concurrent)]
                times = await asyncio.gather(*tasks)
                total_time = (time.time() - start) * 1000
                
                avg_time = statistics.mean(times)
                throughput = num_concurrent / (total_time / 1000)  # requests/sec
                
                logger.info(f"  Total time: {total_time:.1f}ms")
                logger.info(f"  Avg per request: {avg_time:.1f}ms")
                logger.info(f"  Throughput: {throughput:.1f} req/s")
                
                test_name = f"Concurrent {num_concurrent}"
                self.record_metric(test_name, "avg_time", avg_time, "ms")
                self.record_metric(test_name, "throughput", throughput, "req/s")
            
            return True
            
        except Exception as e:
            logger.error(f"Test 2 failed: {e}")
            return False
    
    async def test_database_performance(self) -> bool:
        """Test 3: Database Query Performance"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: Database Query Performance")
        logger.info("="*70)
        
        try:
            from models.models import Course
            from beanie import init_beanie
            from motor.motor_asyncio import AsyncIOMotorClient
            from config.config import settings
            
            # Kết nối database
            logger.info("\nKết nối MongoDB...")
            client = AsyncIOMotorClient(settings.mongodb_url)
            await init_beanie(
                database=client[settings.mongodb_database],
                document_models=[Course]
            )
            
            # Test 3.1: Insert performance
            logger.info("\nTest 3.1: Insert performance")
            
            insert_times = []
            for i in range(10):
                start = time.time()
                
                course = Course(
                    title=f"Performance Test Course {i}",
                    description="Test course",
                    instructor_id="test-instructor",
                    level="beginner",
                    status="published",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                await course.insert()
                
                elapsed = (time.time() - start) * 1000
                insert_times.append(elapsed)
            
            avg_insert = statistics.mean(insert_times)
            logger.info(f"  Avg insert time: {avg_insert:.1f}ms")
            
            self.record_metric("DB Insert", "avg", avg_insert, "ms")
            
            # Test 3.2: Query performance
            logger.info("\nTest 3.2: Query performance")
            
            query_times = []
            for _ in range(10):
                start = time.time()
                courses = await Course.find().to_list()
                elapsed = (time.time() - start) * 1000
                query_times.append(elapsed)
            
            avg_query = statistics.mean(query_times)
            logger.info(f"  Avg query time: {avg_query:.1f}ms")
            logger.info(f"  Records: {len(courses)}")
            
            self.record_metric("DB Query", "avg", avg_query, "ms")
            
            # Cleanup
            await Course.find().delete()
            
            return True
            
        except Exception as e:
            logger.error(f"Test 3 failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_vector_search_performance(self) -> bool:
        """Test 4: Vector Search Performance"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: Vector Search Performance")
        logger.info("="*70)
        
        try:
            from services.embedding_service import embedding_service
            from services.vector_service import vector_service
            
            # Tạo test vectors
            logger.info("\nSetup: Tạo test vectors...")
            num_vectors = 100
            
            texts = [f"Test document number {i} about Python programming" for i in range(num_vectors)]
            
            # Test embedding generation speed
            logger.info("\nTest 4.1: Embedding generation")
            start = time.time()
            embeddings = await embedding_service.generate_embeddings_batch(texts)
            embed_time = (time.time() - start) * 1000
            
            embed_per_sec = num_vectors / (embed_time / 1000)
            logger.info(f"  Total time: {embed_time:.1f}ms")
            logger.info(f"  Speed: {embed_per_sec:.1f} embeddings/sec")
            
            self.record_metric("Embedding Generation", "speed", embed_per_sec, "emb/s")
            
            # Upsert vectors
            logger.info("\nTest 4.2: Vector upsert")
            vectors = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                vectors.append({
                    "id": f"perf-vec-{i}",
                    "values": embedding,
                    "metadata": {"text": text}
                })
            
            start = time.time()
            await vector_service.upsert_vectors(vectors, namespace="performance")
            upsert_time = (time.time() - start) * 1000
            
            logger.info(f"  Time: {upsert_time:.1f}ms")
            logger.info(f"  Speed: {num_vectors/(upsert_time/1000):.1f} vectors/sec")
            
            self.record_metric("Vector Upsert", "time", upsert_time, "ms")
            
            # Test search performance
            logger.info("\nTest 4.3: Vector search")
            
            query = "Python programming tutorial"
            query_embedding = await embedding_service.generate_query_embedding(query)
            
            search_times = []
            for _ in range(20):
                start = time.time()
                _ = await vector_service.search(
                    query_vector=query_embedding,
                    top_k=10,
                    namespace="courses"
                )
                elapsed = time.time() - start
                search_times.append(elapsed)
            
            avg_search = statistics.mean(search_times)
            min_search = min(search_times)
            max_search = max(search_times)
            
            logger.info(f"  Avg: {avg_search:.1f}ms")
            logger.info(f"  Min: {min_search:.1f}ms")
            logger.info(f"  Max: {max_search:.1f}ms")
            
            self.record_metric("Vector Search", "avg", avg_search, "ms")
            
            # Cleanup
            await vector_service.reset_collection("performance")
            
            # Performance assessment
            if avg_search < 50:
                logger.info("\n  Performance: EXCELLENT")
            elif avg_search < 100:
                logger.info("\n  Performance: GOOD")
            elif avg_search < 200:
                logger.info("\n  Performance: ACCEPTABLE")
            else:
                logger.warning("\n  Performance: NEEDS OPTIMIZATION")
            
            return True
            
        except Exception as e:
            logger.error(f"Test 4 failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_large_dataset_handling(self) -> bool:
        """Test 5: Large Dataset Handling"""
        logger.info("\n" + "="*70)
        logger.info("TEST 5: Large Dataset Handling")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # Setup instructor
                await client.post(
                    "/auth/register",
                    json={
                        "email": "large_data_instructor@test.com",
                        "password": "Instructor123!",
                        "full_name": "Large Data Instructor",
                        "role": "instructor"
                    }
                )
                
                login = await client.post(
                    "/auth/login",
                    json={
                        "email": "large_data_instructor@test.com",
                        "password": "Instructor123!"
                    }
                )
                token = login.json()["access_token"]
                
                # Test với course có nhiều chapters/lessons
                logger.info("\nTest 5.1: Course với nhiều chapters")
                
                num_chapters = 5
                lessons_per_chapter = 10
                
                chapters = []
                for i in range(num_chapters):
                    lessons = []
                    for j in range(lessons_per_chapter):
                        lessons.append({
                            "title": f"Lesson {j+1}",
                            "content": f"Content for lesson {j+1} " * 50,  # ~500 chars
                            "order": j+1,
                            "duration_minutes": 15
                        })
                    
                    chapters.append({
                        "title": f"Chapter {i+1}",
                        "description": f"Description for chapter {i+1}",
                        "order": i+1,
                        "lessons": lessons
                    })
                
                start = time.time()
                response = await client.post(
                    "/courses",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "title": "Large Course",
                        "description": "Course with many lessons",
                        "level": "beginner",
                        "category": "programming",
                        "status": "published",
                        "chapters": chapters
                    }
                )
                create_time = (time.time() - start) * 1000
                
                logger.info(f"  Chapters: {num_chapters}")
                logger.info(f"  Lessons per chapter: {lessons_per_chapter}")
                logger.info(f"  Total lessons: {num_chapters * lessons_per_chapter}")
                logger.info(f"  Create time: {create_time:.1f}ms")
                
                self.record_metric("Large Course Create", "time", create_time, "ms")
                
                if response.status_code == 201:
                    course_id = response.json()["id"]
                    
                    # Test retrieve time
                    start = time.time()
                    _ = await client.get(f"/courses/{course_id}")
                    retrieve_time = (time.time() - start) * 1000
                    
                    logger.info(f"  Retrieve time: {retrieve_time:.1f}ms")
                    
                    self.record_metric("Large Course Retrieve", "time", retrieve_time, "ms")
                
                return True
                
        except Exception as e:
            logger.error(f"Test 5 failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """In tổng kết performance"""
        logger.info("\n" + "="*70)
        logger.info("PERFORMANCE TESTING SUMMARY")
        logger.info("="*70)
        
        for test_name, metrics in self.results.items():
            logger.info(f"\n{test_name}:")
            for metric_name, data in metrics.items():
                logger.info(f"  {metric_name}: {data['value']:.2f} {data['unit']}")
        
        # Performance ratings
        logger.info("\n" + "="*70)
        logger.info("PERFORMANCE RATINGS")
        logger.info("="*70)
        
        # Check API response times
        api_metrics = [k for k in self.results.keys() if k.startswith("GET") or k.startswith("POST")]
        if api_metrics:
            avg_api_time = statistics.mean([
                self.results[k]["avg"]["value"] for k in api_metrics if "avg" in self.results[k]
            ])
            logger.info(f"\nAPI Response Time: {avg_api_time:.1f}ms")
            if avg_api_time < 100:
                logger.info("  Rating: EXCELLENT")
            elif avg_api_time < 300:
                logger.info("  Rating: GOOD")
            else:
                logger.info("  Rating: NEEDS IMPROVEMENT")
        
        # Check vector search
        if "Vector Search" in self.results:
            search_time = self.results["Vector Search"]["avg"]["value"]
            logger.info(f"\nVector Search: {search_time:.1f}ms")
            if search_time < 50:
                logger.info("  Rating: EXCELLENT")
            elif search_time < 100:
                logger.info("  Rating: GOOD")
            else:
                logger.info("  Rating: ACCEPTABLE")
        
        logger.info("\n" + "="*70)


async def main():
    """Chạy performance tests"""
    logger.info("\n" + "="*70)
    logger.info("PERFORMANCE TESTING")
    logger.info("Test API response times, concurrency, database, vector search")
    logger.info("="*70)
    
    tester = PerformanceTester()
    
    tests = [
        tester.test_api_response_times,
        tester.test_concurrent_requests,
        tester.test_database_performance,
        tester.test_vector_search_performance,
        tester.test_large_dataset_handling
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            logger.error(f"Test crashed: {e}")
    
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
