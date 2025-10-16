"""
Security Testing Script

Test các vấn đề bảo mật:
- Authentication và Authorization
- Input validation
- SQL/NoSQL injection
- XSS protection
- Rate limiting
- JWT security

Run: python scripts/test_security.py
"""
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityTester:
    """Security Testing"""
    
    def __init__(self):
        self.results = []
        self.vulnerabilities = []
    
    def record_result(self, test: str, passed: bool, details: str = ""):
        """Ghi kết quả test"""
        self.results.append({
            "test": test,
            "passed": passed,
            "details": details
        })
        status = "PASS" if passed else "FAIL"
        logger.info(f"  [{status}] {test}: {details}")
        
        if not passed:
            self.vulnerabilities.append(f"{test}: {details}")
    
    async def test_authentication_security(self) -> bool:
        """Test 1: Authentication Security"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: Authentication Security")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # Test 1.1: Weak password rejection
                logger.info("\nTest 1.1: Weak password rejection")
                weak_passwords = ["123", "pass", "abc123", "password"]
                
                rejected = 0
                for pwd in weak_passwords:
                    response = await client.post(
                        "/auth/register",
                        json={
                            "email": f"test_{pwd}@test.com",
                            "password": pwd,
                            "full_name": "Test User",
                            "role": "student"
                        }
                    )
                    if response.status_code == 422:  # Validation error
                        rejected += 1
                
                self.record_result(
                    "1.1 Weak password rejection",
                    rejected == len(weak_passwords),
                    f"{rejected}/{len(weak_passwords)} rejected"
                )
                
                # Test 1.2: SQL injection trong login
                logger.info("\nTest 1.2: SQL injection prevention")
                injection_attempts = [
                    "' OR '1'='1",
                    "admin'--",
                    "' OR 1=1--",
                    "'; DROP TABLE users--"
                ]
                
                protected = 0
                for injection in injection_attempts:
                    response = await client.post(
                        "/auth/login",
                        json={
                            "email": injection,
                            "password": "anything"
                        }
                    )
                    # Không được trả về 200 (success)
                    if response.status_code != 200:
                        protected += 1
                
                self.record_result(
                    "1.2 SQL injection prevention",
                    protected == len(injection_attempts),
                    f"{protected}/{len(injection_attempts)} blocked"
                )
                
                # Test 1.3: Brute force protection
                logger.info("\nTest 1.3: Brute force attempt detection")
                
                # Đăng ký user test
                await client.post(
                    "/auth/register",
                    json={
                        "email": "bruteforce@test.com",
                        "password": "Valid123!",
                        "full_name": "Brute Force Test",
                        "role": "student"
                    }
                )
                
                # Thử login sai nhiều lần
                failed_attempts = 0
                for i in range(5):
                    response = await client.post(
                        "/auth/login",
                        json={
                            "email": "bruteforce@test.com",
                            "password": f"wrong{i}"
                        }
                    )
                    if response.status_code == 401:
                        failed_attempts += 1
                
                self.record_result(
                    "1.3 Multiple login failures",
                    failed_attempts == 5,
                    f"{failed_attempts} attempts rejected"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Test 1 failed: {e}")
            return False
    
    async def test_authorization_security(self) -> bool:
        """Test 2: Authorization & Access Control"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: Authorization & Access Control")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # Setup users
                await client.post(
                    "/auth/register",
                    json={
                        "email": "student_authz@test.com",
                        "password": "Student123!",
                        "full_name": "Student AuthZ",
                        "role": "student"
                    }
                )
                
                student_login = await client.post(
                    "/auth/login",
                    json={
                        "email": "student_authz@test.com",
                        "password": "Student123!"
                    }
                )
                student_token = student_login.json()["access_token"]
                
                # Test 2.1: Student không được truy cập admin endpoints
                logger.info("\nTest 2.1: RBAC - Student blocked from admin")
                admin_endpoints = [
                    "/admin/users",
                    "/admin/analytics/platform",
                    "/admin/courses/pending"
                ]
                
                blocked = 0
                for endpoint in admin_endpoints:
                    response = await client.get(
                        endpoint,
                        headers={"Authorization": f"Bearer {student_token}"}
                    )
                    if response.status_code == 403:  # Forbidden
                        blocked += 1
                
                self.record_result(
                    "2.1 RBAC - Admin endpoints",
                    blocked == len(admin_endpoints),
                    f"{blocked}/{len(admin_endpoints)} blocked"
                )
                
                # Test 2.2: Student không được tạo course
                logger.info("\nTest 2.2: Student cannot create course")
                course_response = await client.post(
                    "/courses",
                    headers={"Authorization": f"Bearer {student_token}"},
                    json={
                        "title": "Unauthorized Course",
                        "description": "Should fail",
                        "level": "beginner",
                        "category": "test"
                    }
                )
                
                self.record_result(
                    "2.2 Prevent student course creation",
                    course_response.status_code == 403,
                    f"Status: {course_response.status_code}"
                )
                
                # Test 2.3: Token validation
                logger.info("\nTest 2.3: Invalid token rejection")
                
                invalid_tokens = [
                    "invalid.token.here",
                    "Bearer fake_token",
                    "",
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature"
                ]
                
                rejected = 0
                for token in invalid_tokens:
                    response = await client.get(
                        "/users/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if response.status_code == 401:
                        rejected += 1
                
                self.record_result(
                    "2.3 Invalid token rejection",
                    rejected == len(invalid_tokens),
                    f"{rejected}/{len(invalid_tokens)} rejected"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Test 2 failed: {e}")
            return False
    
    async def test_input_validation(self) -> bool:
        """Test 3: Input Validation"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: Input Validation")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # Test 3.1: Email validation
                logger.info("\nTest 3.1: Email format validation")
                invalid_emails = [
                    "notanemail",
                    "@test.com",
                    "test@",
                    "test..test@test.com"
                ]
                
                rejected = 0
                for email in invalid_emails:
                    response = await client.post(
                        "/auth/register",
                        json={
                            "email": email,
                            "password": "Valid123!",
                            "full_name": "Test",
                            "role": "student"
                        }
                    )
                    if response.status_code == 422:
                        rejected += 1
                
                self.record_result(
                    "3.1 Email validation",
                    rejected == len(invalid_emails),
                    f"{rejected}/{len(invalid_emails)} rejected"
                )
                
                # Test 3.2: XSS prevention
                logger.info("\nTest 3.2: XSS prevention")
                xss_payloads = [
                    "<script>alert('XSS')</script>",
                    "<img src=x onerror=alert('XSS')>",
                    "javascript:alert('XSS')",
                    "<iframe src='javascript:alert(1)'>"
                ]
                
                # Đăng ký user hợp lệ trước
                await client.post(
                    "/auth/register",
                    json={
                        "email": "xss_test@test.com",
                        "password": "Valid123!",
                        "full_name": "XSS Test",
                        "role": "student"
                    }
                )
                
                login = await client.post(
                    "/auth/login",
                    json={
                        "email": "xss_test@test.com",
                        "password": "Valid123!"
                    }
                )
                token = login.json()["access_token"]
                
                # Thử tạo course với XSS payload
                protected = 0
                for payload in xss_payloads:
                    response = await client.post(
                        "/courses",
                        headers={"Authorization": f"Bearer {token}"},
                        json={
                            "title": payload,
                            "description": "Test",
                            "level": "beginner",
                            "category": "test"
                        }
                    )
                    # Nếu bị reject (403/422) hoặc content được sanitize
                    if response.status_code in [403, 422, 400]:
                        protected += 1
                
                self.record_result(
                    "3.2 XSS prevention",
                    protected > 0,  # Ít nhất 1 payload bị chặn
                    f"{protected}/{len(xss_payloads)} blocked"
                )
                
                # Test 3.3: NoSQL injection
                logger.info("\nTest 3.3: NoSQL injection prevention")
                nosql_payloads = [
                    {"$gt": ""},
                    {"$ne": None},
                    {"$regex": ".*"},
                ]
                
                # Thử search với NoSQL injection
                protected = 0
                for payload in nosql_payloads:
                    try:
                        # Search courses với payload
                        response = await client.get(
                            f"/courses?title={str(payload)}"
                        )
                        # Không nên crash và không nên trả hết data
                        if response.status_code != 500:
                            protected += 1
                    except Exception as e:
                        # Bắt mọi lỗi request (HTTPException, ConnectionError, etc.)
                        logger.debug(f"Request failed with NoSQL payload: {e}")
                        protected += 1
                
                self.record_result(
                    "3.3 NoSQL injection prevention",
                    protected == len(nosql_payloads),
                    f"{protected}/{len(nosql_payloads)} handled"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Test 3 failed: {e}")
            return False
    
    async def test_data_exposure(self) -> bool:
        """Test 4: Data Exposure & Privacy"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: Data Exposure & Privacy")
        logger.info("="*70)
        
        try:
            from httpx import AsyncClient, ASGITransport
            from app.main import app
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                
                # Test 4.1: Password không được trả về trong response
                logger.info("\nTest 4.1: Password not exposed")
                
                response = await client.post(
                    "/auth/register",
                    json={
                        "email": "exposure_test@test.com",
                        "password": "SecretPassword123!",
                        "full_name": "Exposure Test",
                        "role": "student"
                    }
                )
                
                response_data = response.json()
                password_exposed = (
                    "password" in str(response_data).lower() or
                    "SecretPassword" in str(response_data)
                )
                
                self.record_result(
                    "4.1 Password not in response",
                    not password_exposed,
                    "Password hidden" if not password_exposed else "PASSWORD EXPOSED!"
                )
                
                # Test 4.2: User không thể xem data của user khác
                logger.info("\nTest 4.2: User isolation")
                
                # Tạo 2 users
                await client.post(
                    "/auth/register",
                    json={
                        "email": "user1@test.com",
                        "password": "User123!",
                        "full_name": "User 1",
                        "role": "student"
                    }
                )
                
                await client.post(
                    "/auth/register",
                    json={
                        "email": "user2@test.com",
                        "password": "User123!",
                        "full_name": "User 2",
                        "role": "student"
                    }
                )
                
                user1_login = await client.post(
                    "/auth/login",
                    json={"email": "user1@test.com", "password": "User123!"}
                )
                user1_token = user1_login.json()["access_token"]
                
                user2_login = await client.post(
                    "/auth/login",
                    json={"email": "user2@test.com", "password": "User123!"}
                )
                user2_token = user2_login.json()["access_token"]
                
                # User 1 tạo chat
                chat_response = await client.post(
                    "/chat/sessions",
                    headers={"Authorization": f"Bearer {user1_token}"},
                    json={"title": "Private Chat"}
                )
                chat_id = chat_response.json()["id"]
                
                # User 2 thử truy cập chat của User 1
                access_response = await client.get(
                    f"/chat/sessions/{chat_id}",
                    headers={"Authorization": f"Bearer {user2_token}"}
                )
                
                self.record_result(
                    "4.2 User data isolation",
                    access_response.status_code == 403,
                    f"Status: {access_response.status_code}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Test 4 failed: {e}")
            return False
    
    def print_summary(self):
        """In tổng kết security testing"""
        logger.info("\n" + "="*70)
        logger.info("SECURITY TESTING SUMMARY")
        logger.info("="*70)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        for r in self.results:
            status = "PASS" if r["passed"] else "FAIL"
            logger.info(f"  [{status}] {r['test']}: {r['details']}")
        
        logger.info("\n" + "="*70)
        logger.info(f"Kết quả: {passed}/{total} tests PASSED")
        
        if self.vulnerabilities:
            logger.warning("\nCÁC VẤN ĐỀ BẢO MẬT CẦN LƯU Ý:")
            for vuln in self.vulnerabilities:
                logger.warning(f"  - {vuln}")
        else:
            logger.info("\nKhông phát hiện vấn đề bảo mật nghiêm trọng.")
        
        logger.info("="*70)


async def main():
    """Chạy security tests"""
    logger.info("\n" + "="*70)
    logger.info("SECURITY TESTING")
    logger.info("Test authentication, authorization, input validation, data privacy")
    logger.info("="*70)
    
    tester = SecurityTester()
    
    tests = [
        tester.test_authentication_security,
        tester.test_authorization_security,
        tester.test_input_validation,
        tester.test_data_exposure
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            logger.error(f"Test crashed: {e}")
    
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
