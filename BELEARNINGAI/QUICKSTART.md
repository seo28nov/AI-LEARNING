# 🚀 Quick Start Guide - BeLearning AI

> **5 phút setup** | **Ready for testing** | **Updated: 2025-10-16**

## Prerequisites

- Python 3.11+
- MongoDB running (local hoặc Atlas)
- Google AI API key

---

## Step 1: Clone & Setup (2 phút)

```powershell
# Clone repo
cd BELEARNINGAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configuration (1 phút)

```powershell
# Copy environment file
copy .env.example .env

# Edit .env với text editor
notepad .env  # Windows
# nano .env   # Linux
```

**Minimum required:**
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=belearning_db
GOOGLE_API_KEY=your-google-ai-api-key-here
JWT_SECRET_KEY=any-random-string-for-development
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

**Get Google AI API Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Create new key
3. Copy vào `.env`

---

## Step 3: Health Check (30 giây)

```powershell
python scripts/health_check.py
```

**Expected output:**
```
✅ PASS - Imports
✅ PASS - Configuration
✅ PASS - MongoDB
✅ PASS - ChromaDB
✅ PASS - Google AI
✅ PASS - Services

🎉 ALL CHECKS PASSED! System is healthy.
```

---

## Step 4: Initialize Database (1 phút)

```powershell
# Create initial data
python scripts/initial_data.py

# Create database indexes
python scripts/create_indexes.py
```

---

## Step 5: Start Server (30 giây)

```powershell
uvicorn app.main:app --reload
```

**Server running at:**
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs ⭐
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

## ✅ Verify Installation

### Test 1: Health Endpoint

```powershell
curl http://localhost:8000/health
```

Expected: `{"status": "healthy"}`

### Test 2: API Docs

Open browser: http://localhost:8000/docs

Should see interactive Swagger UI với 100+ endpoints.

### Test 3: Register User

```powershell
# PowerShell
$body = @{
    email = "test@example.com"
    password = "Test123!"
    full_name = "Test User"
    role = "student"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/register" -Method POST -Body $body -ContentType "application/json"
```

Expected: User created successfully.

---

## 🧪 Run Tests (Optional - 5 phút)

```powershell
# Test RAG system
python scripts/test_rag.py

# Expected: 4/4 tests PASSED
```

---

## 📚 What's Next?

### Phase 2: Testing (40 phút)

1. **Integration Tests** - Run `test_rag.py`
2. **Manual Tests** - Use Swagger UI
3. **User Flows** - Test Admin/Instructor/Student workflows

### Phase 3: Development

1. **Frontend Integration** - Connect React/Next.js
2. **Custom Features** - Add your features
3. **Production Deployment** - Follow `DEPLOYMENT.md`

---

## 🔧 Troubleshooting

### Issue: MongoDB connection failed

**Solution:**
```powershell
# Start MongoDB service
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
```

Hoặc use MongoDB Atlas (cloud):
1. Sign up: https://www.mongodb.com/cloud/atlas
2. Get connection string
3. Update `MONGODB_URL` in `.env`

### Issue: Google AI API error

**Check:**
- API key is correct in `.env`
- Key has not expired
- Within quota (60 requests/minute free tier)

### Issue: Import errors

**Solution:**
```powershell
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue: ChromaDB permission error

**Solution:**
```powershell
# Windows: Recreate directory
Remove-Item -Recurse -Force .\chroma_db
New-Item -ItemType Directory .\chroma_db
```

---

## 📖 Documentation

- **README.md** - Comprehensive overview
- **SETUP_GUIDE.md** - Detailed setup instructions
- **CHROMADB_RAG_GUIDE.md** - RAG system guide
- **ARCHITECTURE.md** - System architecture
- **DEPLOYMENT.md** - Production deployment

---

## 💡 Quick Tips

### Development Workflow

```powershell
# Terminal 1: Run server
uvicorn app.main:app --reload

# Terminal 2: Run tests
pytest

# Terminal 3: MongoDB shell (if needed)
mongosh
```

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Register user via `/auth/register`
4. Login via `/auth/login` → copy token
5. Paste token in "Authorize" dialog
6. Now can test protected endpoints!

### Testing RAG

```powershell
# 1. Create course via API
# 2. Index course
# 3. Create chat session
# 4. Send message with use_rag=true
# 5. AI will answer based on course content!
```

---

## ✅ Success Criteria

You're ready to proceed if:

- [ ] Health check passes
- [ ] Server starts without errors
- [ ] Can access Swagger UI
- [ ] Can register and login user
- [ ] Can create a course
- [ ] (Optional) RAG tests pass

---

## 🎯 Next Steps

### Option A: Start Testing (Recommended)
```powershell
# Follow Phase 2 testing guide
python scripts/test_rag.py
```

### Option B: Start Development
- Read `ARCHITECTURE.md` for system overview
- Check `docs/` for detailed guides
- Start building your features!

### Option C: Deploy to Production
- Follow `DEPLOYMENT.md`
- Setup Docker
- Configure cloud services

---

## 📞 Need Help?

1. **Check Documentation** - `docs/` folder
2. **Run Health Check** - `python scripts/health_check.py`
3. **Check Logs** - Look for error messages
4. **Common Issues** - See Troubleshooting section above

---

## 🎉 Congratulations!

You've successfully set up BeLearning AI platform! 

The system is now ready for:
- ✅ Development
- ✅ Testing
- ✅ Integration with frontend
- ✅ Further customization

**Enjoy building! 🚀**

---

**Last Updated**: 2025-10-16  
**Version**: 2.0  
**Status**: Production Ready
