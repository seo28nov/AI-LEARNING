# 🚀 Deployment Guide - BE Learning AI

Hướng dẫn deploy BE Learning AI lên production.

## Mục lục

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Database Migration](#database-migration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Hardening](#security-hardening)
8. [Backup Strategy](#backup-strategy)

---

## Pre-Deployment Checklist

### Code Review

- [ ] All tests passing: `pytest`
- [ ] No security vulnerabilities: `pip-audit`
- [ ] Code linted: `ruff check app/`
- [ ] Type checking: `mypy app/`
- [ ] Dependencies updated and locked

### Configuration

- [ ] `DEBUG=False` in production `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] CORS configured with actual frontend domains
- [ ] Rate limiting enabled
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] SSL/TLS certificates ready

### Documentation

- [ ] API documentation updated
- [ ] README current
- [ ] Environment variables documented
- [ ] Deployment runbook ready

---

## Environment Configuration

### Production .env

```env
# ========================================
# PRODUCTION SETTINGS
# ========================================
APP_NAME=BE Learning AI
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# ========================================
# SERVER
# ========================================
HOST=0.0.0.0
PORT=8000
WORKERS=4  # (2 * CPU cores) + 1

# ========================================
# DATABASE
# ========================================
MONGODB_URL=mongodb+srv://prod_user:<password>@production-cluster.mongodb.net/
DATABASE_NAME=belearning_prod

# Connection pool settings
MONGODB_MIN_POOL_SIZE=10
MONGODB_MAX_POOL_SIZE=100
MONGODB_SERVER_SELECTION_TIMEOUT=5000

# ========================================
# JWT
# ========================================
SECRET_KEY=<generated-strong-key-64-chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15  # Shorter for production
REFRESH_TOKEN_EXPIRE_DAYS=7

# ========================================
# CORS
# ========================================
ALLOWED_ORIGINS=https://app.belearning.ai,https://www.belearning.ai

# ========================================
# GOOGLE AI
# ========================================
GOOGLE_API_KEY=<production-api-key>

# ========================================
# VECTOR DATABASE
# ========================================
VECTOR_DB=pinecone
PINECONE_API_KEY=<production-key>
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=belearning-prod

# ========================================
# EMAIL
# ========================================
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@belearning.ai
ENABLE_EMAIL=True

# ========================================
# FILE STORAGE
# ========================================
UPLOAD_PROVIDER=s3  # or gcs, azure
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_S3_BUCKET=belearning-uploads
AWS_REGION=us-east-1

# ========================================
# LOGGING
# ========================================
LOG_LEVEL=WARNING
LOG_FILE=/var/log/belearning/app.log
SENTRY_DSN=<sentry-dsn-for-error-tracking>

# ========================================
# SECURITY
# ========================================
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Generate Production SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Docker Deployment

### 1. Dockerfile (Production)

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. docker-compose.yml (Production)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: belearning-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=${MONGODB_URL}
      - DATABASE_NAME=${DATABASE_NAME}
      - SECRET_KEY=${SECRET_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DEBUG=False
    env_file:
      - .env.production
    volumes:
      - ./logs:/var/log/belearning
    networks:
      - belearning-network
    depends_on:
      - mongodb
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mongodb:
    image: mongo:7
    container_name: belearning-mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: ${DATABASE_NAME}
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
      - ./backups:/backups
    networks:
      - belearning-network

  nginx:
    image: nginx:alpine
    container_name: belearning-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - belearning-network
    depends_on:
      - api

volumes:
  mongodb_data:
  mongodb_config:

networks:
  belearning-network:
    driver: bridge
```

### 3. nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name api.belearning.ai;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.belearning.ai;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API proxy
        location / {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check (no rate limit)
        location /health {
            proxy_pass http://api/health;
        }

        # Static files (if any)
        location /static {
            alias /app/static;
            expires 30d;
        }
    }
}
```

### 4. Build & Deploy

```bash
# Build image
docker build -t belearning-api:latest .

# Tag for registry
docker tag belearning-api:latest registry.example.com/belearning-api:latest

# Push to registry
docker push registry.example.com/belearning-api:latest

# Deploy with compose
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f api

# Check status
docker-compose ps
```

---

## Cloud Deployment

### AWS Elastic Beanstalk

#### 1. Install EB CLI

```bash
pip install awsebcli
```

#### 2. Initialize EB

```bash
eb init -p python-3.11 belearning-api --region us-east-1
```

#### 3. Create Environment

```bash
eb create belearning-prod --database.engine mongodb
```

#### 4. Configure Environment Variables

```bash
eb setenv \
  DEBUG=False \
  SECRET_KEY=<key> \
  MONGODB_URL=<url> \
  GOOGLE_API_KEY=<key>
```

#### 5. Deploy

```bash
eb deploy
```

#### 6. Monitor

```bash
eb status
eb logs
eb health
```

### Google Cloud Run

#### 1. Create Dockerfile

(Use Dockerfile from Docker section above)

#### 2. Build & Push

```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/belearning-api

# Deploy
gcloud run deploy belearning-api \
  --image gcr.io/PROJECT_ID/belearning-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=False,SECRET_KEY=<key> \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### Azure Container Instances

```bash
# Create resource group
az group create --name belearning-rg --location eastus

# Create container
az container create \
  --resource-group belearning-rg \
  --name belearning-api \
  --image yourdockerhub/belearning-api:latest \
  --dns-name-label belearning-api \
  --ports 8000 \
  --environment-variables \
    DEBUG=False \
    SECRET_KEY=<key> \
  --cpu 2 \
  --memory 4
```

### Heroku

#### 1. Create Procfile

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
```

#### 2. Deploy

```bash
# Login
heroku login

# Create app
heroku create belearning-api

# Set config
heroku config:set DEBUG=False SECRET_KEY=<key>

# Deploy
git push heroku main

# Scale
heroku ps:scale web=2:standard-2x
```

---

## Database Migration

### MongoDB Atlas Setup

1. **Create Production Cluster**
   - Tier: M10+ (production tier)
   - Region: Same as application
   - Backup: Enabled

2. **Security**
   - Create dedicated user
   - Whitelist application IPs
   - Enable authentication

3. **Performance**
   - Create indexes (see below)
   - Enable profiling
   - Configure alerts

### Create Indexes

```python
# scripts/create_indexes.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def create_indexes():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    await db.users.create_index("is_active")
    
    # Courses
    await db.courses.create_index("instructor_id")
    await db.courses.create_index("category")
    await db.courses.create_index("is_public")
    await db.courses.create_index([("title", "text"), ("description", "text")])
    
    # Enrollments
    await db.enrollments.create_index([("user_id", 1), ("course_id", 1)], unique=True)
    await db.enrollments.create_index("user_id")
    await db.enrollments.create_index("course_id")
    
    # Quizzes
    await db.quizzes.create_index("course_id")
    await db.quizzes.create_index("instructor_id")
    
    # Chat sessions
    await db.chat_sessions.create_index("user_id")
    await db.chat_sessions.create_index("created_at")
    
    print("✅ All indexes created successfully")

if __name__ == "__main__":
    asyncio.run(create_indexes())
```

```bash
python scripts/create_indexes.py
```

---

## Monitoring & Logging

### Sentry Integration

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )
```

### Application Metrics

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### Health Checks

```python
# app/routers/health.py
@router.get("/health")
async def health_check():
    # Check database
    try:
        await ping_database()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    # Check external services
    services = {
        "database": db_status,
        "google_ai": await check_google_ai(),
        "vector_db": await check_vector_db(),
    }
    
    return {
        "status": "healthy" if all(v == "connected" for v in services.values()) else "degraded",
        "services": services,
        "version": settings.APP_VERSION,
    }
```

### Log Aggregation

Use CloudWatch, Datadog, or ELK stack:

```python
# config/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logging.getLogger().addHandler(logHandler)
```

---

## Security Hardening

### 1. Enable Rate Limiting

```python
# middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login():
    ...
```

### 2. Input Validation

```python
# All Pydantic models have validation
class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., max_length=5000)
```

### 3. SQL Injection Prevention

✅ Using MongoDB + Beanie (NoSQL) - not vulnerable to SQL injection

### 4. XSS Prevention

```python
import bleach

def sanitize_html(content: str) -> str:
    return bleach.clean(content, tags=[], strip=True)
```

### 5. HTTPS Only

```python
# app/main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 6. Security Headers

Already configured in nginx.conf

---

## Backup Strategy

### MongoDB Backups

#### Automated Backups (MongoDB Atlas)

- Point-in-time recovery enabled
- Snapshots every 6 hours
- Retention: 7 days

#### Manual Backups

```bash
# Full backup
mongodump --uri="mongodb+srv://..." --out=/backups/$(date +%Y%m%d)

# Restore
mongorestore --uri="mongodb+srv://..." /backups/20240101
```

#### Backup Script

```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

# Backup database
mongodump --uri="$MONGODB_URL" --out="$BACKUP_DIR"

# Compress
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Upload to S3
aws s3 cp "$BACKUP_DIR.tar.gz" s3://belearning-backups/

# Delete local backup
rm "$BACKUP_DIR.tar.gz"

# Keep only last 30 days in S3
aws s3 ls s3://belearning-backups/ | while read -r line; do
    createDate=$(echo $line | awk {'print $1" "$2'})
    createDate=$(date -d "$createDate" +%s)
    olderThan=$(date --date "30 days ago" +%s)
    if [[ $createDate -lt $olderThan ]]; then
        fileName=$(echo $line | awk {'print $4'})
        aws s3 rm s3://belearning-backups/$fileName
    fi
done
```

#### Cron Job

```bash
# Run daily at 2 AM
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## Post-Deployment

### Verification Checklist

- [ ] Application responding: `curl https://api.belearning.ai/health`
- [ ] Database connected
- [ ] SSL certificate valid
- [ ] All endpoints working
- [ ] Logs flowing to monitoring system
- [ ] Backups running
- [ ] Alerts configured

### Monitoring Alerts

Set up alerts for:
- API response time > 1s
- Error rate > 1%
- CPU usage > 80%
- Memory usage > 85%
- Database connections > 80% of pool
- Disk space < 20%

---

## Rollback Plan

### Docker Deployment

```bash
# Tag current version
docker tag belearning-api:latest belearning-api:v1.0.0

# Deploy new version
docker-compose up -d

# If issues, rollback
docker-compose down
docker tag belearning-api:v1.0.0 belearning-api:latest
docker-compose up -d
```

### Cloud Deployment

```bash
# Heroku
heroku releases
heroku rollback v123

# Google Cloud Run
gcloud run services update-traffic belearning-api --to-revisions=belearning-api-00001-xyz=100
```

---

## Support

Deployment issues? Check:
- Application logs
- Server logs
- Database logs
- Monitoring dashboard

Need help? Contact DevOps team or create incident ticket.

---

**Deployment checklist complete? You're ready for production! 🚀**
