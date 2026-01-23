# Render Deployment Instructions (Refactored for Stability)

## Pre-Deployment Checklist

### ✅ Local Testing (Highly Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your GROQ API key
echo "GROQ_API_KEY=your-api-key-here" > .env

# 3. Run the backend
python main.py
# Backend runs on http://localhost:8000

# 4. In another terminal, run the frontend
streamlit run frontend/app.py
# Frontend runs on http://localhost:8501

# 5. Test health endpoint
curl http://localhost:8000/health-check
# Should return: {"status": "ok", ...}

# 6. Test debug endpoint
curl http://localhost:8000/api/debug/status
# Should return: {"api_key_present": true, "llm_initialized": false, ...}

# 7. Upload a small PDF (wait 5-10 min for first API call to load models)
curl -X POST http://localhost:8000/api/ingest_document \
  -F "file=@small_test.pdf"

# 8. If successful, you're ready to deploy!
```

### ❌ Common Local Issues

**Issue:** "Module not found" errors
```bash
Solution: 
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Issue:** "GROQ_API_KEY not set"
```bash
Solution:
# Create .env file in project root with:
GROQ_API_KEY=gsk_xxxxx...
# Or export: export GROQ_API_KEY="gsk_xxxxx..."
```

**Issue:** "First request takes too long (5+ min)"
```
✓ EXPECTED! Models loading for the first time.
  - Embedding model: 2-5 minutes
  - This only happens once
  - Check logs: you should see "[Embeddings] Loading..."
  - Subsequent requests: ~1-2 seconds
```

---

## Render Deployment Steps

### 1. **Create Render Account & Connect GitHub**
- Visit: https://render.com
- Sign up / Log in
- Connect your GitHub account
- Give Render permission to access your repo

### 2. **Set Environment Variables (CRITICAL!)**

Go to Render Dashboard → Select your service → Environment

Add these environment variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `GROQ_API_KEY` | `gsk_xxxxx...` | Get from https://console.groq.com/ |
| `PYTHON_VERSION` | `3.11` | Optional, explicitly set Python version |

⚠️ **DO NOT commit .env file to git** - .gitignore already prevents this

### 3. **Create New Web Service on Render**

1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. Configure:
   - **Name:** `genai-rag-backend` (or your preference)
   - **Environment:** `Docker`
   - **Branch:** `main` (or your branch)
   - **Build Command:** (leave blank - Docker handles it)
   - **Start Command:** (leave blank - Docker handles it)
4. **Plan:** Select "Free" tier
5. Click "Create Web Service"

### 4. **Deploy Backend**

Render will automatically:
1. Pull your code from GitHub
2. Build Docker image (~3-5 min)
3. Start container with Gunicorn + Uvicorn

**First Deployment Timeline:**
- Build: 3-5 minutes
- Container start: <5 seconds
- Health check passes: Immediately
- First API request: 5-10 minutes (models load)

### 5. **Verify Backend is Running**

After deployment completes:

```bash
# Check health endpoint
curl https://your-backend-url.onrender.com/health-check
# Should return: {"status": "ok", ...}

# Check debug status
curl https://your-backend-url.onrender.com/api/debug/status
# Service not yet initialized (that's OK, will initialize on first request)

# Try uploading a file (expect 5+ min wait)
curl -X POST https://your-backend-url.onrender.com/api/ingest_document \
  -F "file=@small_test.pdf"
```

### 6. **Deploy Frontend on Streamlit Cloud**

1. Visit: https://streamlit.io/cloud
2. Sign up with GitHub
3. Click "New app"
4. Configure:
   - **Repository:** Select your repo
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`
5. Advanced settings:
   - **Environment variables:**
     - `BACKEND_API_URL=https://your-backend-url.onrender.com`

6. Click "Deploy"

### 7. **Verify Frontend Connection**

1. Open your Streamlit app URL
2. Go to Chat with Document
3. Try uploading a PDF
4. If successful → Backend and Frontend communicating! ✓

---

## Monitoring & Troubleshooting

### ✅ Healthy Symptoms

```
Log Messages (Good):
[RAGService] Initializing container (models deferred)...
[RAGService] ✓ Container ready (models will load on first request)
[Embeddings] Loading HuggingFaceEmbeddings model...
[Embeddings] ✓ Model loaded successfully
[VectorStore] Loading ChromaDB...
[VectorStore] ✓ ChromaDB loaded
[Agent] Initializing AgentOrchestrator...
[Agent] ✓ AgentOrchestrator initialized
✓ Worker alive

Memory Usage (Good):
- Container memory: 400-500MB (stable)
- No OOM kills
- Worker processes don't crash
- No "Memory limit exceeded" errors
```

### ❌ Unhealthy Symptoms

```
Log Messages (Bad):
[Embeddings] ❌ Failed to load: ...
GROQ_API_KEY not set
502 Bad Gateway
Worker timeout
Worker died unexpectedly

Memory Issues (Bad):
- Container memory: 800MB+ (exceeds 512MB limit)
- Worker OOM killed
- "Killed" message in logs
- Service keeps restarting

Fix:
1. Check GROQ_API_KEY is set in Render environment
2. Wait 10 minutes after first deploy (model loading)
3. Check Render logs for specific error: "Render Dashboard → View logs"
4. Verify Dockerfile is correct: "gunicorn ... --workers 1 ..."
```

### 📊 Real-Time Monitoring

```bash
# Watch logs in real-time
# Go to Render Dashboard → Select service → Logs

# Common patterns to look for:
✓ "Worker alive" = healthy
✗ "Worker timeout" = models taking too long to load
✗ "OOM killer" = memory exceeded
✓ "Ingestion successful" = document upload working
```

---

## Performance Expectations

| Action | Time | Notes |
|--------|------|-------|
| Container startup | <5 sec | Instant |
| Health check response | <100 ms | Always fast |
| First API request | 5-10 min | Models loading (one-time) |
| Subsequent requests | 1-2 sec | Models cached |
| Document upload | 10-30 sec | Depends on PDF size |
| Query response | 2-5 sec | LLM inference time |

---

## Cost Summary

**Render Free Tier:**
- ✓ 1 Web Service (backend)
- ✓ Auto-sleep after 15 min inactivity
- ✓ Wakes up on request (cold start 5s)
- ✓ $0/month

**Streamlit Cloud Free Tier:**
- ✓ 1 App (frontend)
- ✓ 1GB RAM per app
- ✓ $0/month

**Groq API (Used for LLM):**
- ✓ Free tier: 4,000 requests/minute limit
- ✓ No credit card required
- ✓ $0/month for personal use

**Total Cost:** $0/month ✓

---

## Updating Your Code

After deploying, when you update code:

```bash
# 1. Make changes locally
# 2. Test locally
python main.py
streamlit run frontend/app.py

# 3. Commit and push
git add .
git commit -m "Your commit message"
git push

# 4. Render auto-deploys (check dashboard for status)
# 5. Streamlit auto-reloads (should be instant)
```

---

## Support & Debugging

### If Backend Still Crashes

1. **Check logs:** Render Dashboard → Select service → Logs
2. **Copy error message** and search in REFACTORING_SUMMARY.md
3. **Common fixes:**
   - ✓ Ensure GROQ_API_KEY is set
   - ✓ Wait 10 min after first deploy
   - ✓ Verify Dockerfile has `--workers 1`
   - ✓ Check file/query size limits

### If Frontend Can't Connect to Backend

1. **Verify BACKEND_API_URL** is correct in Streamlit settings
2. **Check backend is running:** curl https://your-backend-url/health-check
3. **CORS issues?** Check Render logs for CORS errors
4. **Firewall?** Render apps are public by default

### Need Help?

- **FastAPI docs:** http://localhost:8000/docs (local) or https://your-backend-url/docs (remote)
- **Render support:** https://render.com/docs
- **Streamlit docs:** https://docs.streamlit.io
- **Groq API docs:** https://console.groq.com/docs

---

## Success Criteria

✅ Deployment successful when:
1. Backend health check returns `{"status": "ok"}`
2. First request takes 5-10 min (models loading)
3. Subsequent requests take 1-2 sec (fast)
4. Can upload PDFs and query them
5. No 502 errors or worker crashes
6. Memory stays below 512MB
7. Logs show models loading on first request, then working

🎉 **Everything working? Great! Your RAG chatbot is live on Render.**

