# Deployment Guide: GenAI Document Assistant

This guide will help you deploy the backend on **Render** and the frontend on **Streamlit Cloud** with proper inter-service communication.

## Prerequisites

- GitHub account (for version control)
- Render account (free tier available at render.com)
- Streamlit Cloud account (free tier available at share.streamlit.io)
- Docker installed locally (for testing)

## Architecture Overview

```
┌─────────────────────────────┐
│   Streamlit Frontend        │
│  (Streamlit Cloud)          │
└────────────┬────────────────┘
             │ HTTPS API Calls
             │
┌────────────▼────────────────┐
│   FastAPI Backend           │
│   (Render Docker)           │
│   - Document Processing     │
│   - RAG Query Engine        │
│   - Session Management      │
└─────────────────────────────┘
```

## Part 1: Backend Deployment on Render

### Step 1: Prepare Your Repository

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/genai-doc-assistant.git
   git push -u origin main
   ```

2. Verify these files are in your repo:
   - `Dockerfile` ✓
   - `.dockerignore` ✓
   - `render.yaml` ✓
   - `requirements.txt` ✓
   - `main.py` ✓

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository and branch
5. Configure the deployment:
   - **Name:** `genai-doc-assistant-backend`
   - **Environment:** `Docker`
   - **Region:** `Oregon` (or closest to you)
   - **Branch:** `main`
   - **Build Command:** (leave empty if using Dockerfile)
   - **Start Command:** (leave empty if using Dockerfile)

6. Add Environment Variables (click "Add from file" or add individually):
   - Key: `PYTHON_VERSION` → Value: `3.11`
   - Key: `PORT` → Value: `8000`
   - Add any API keys or secrets your RAG system needs (GROQ_API_KEY, etc.)

7. Click **"Create Web Service"**

**Expected Deployment Time:** 5-10 minutes

### Step 3: Get Your Backend URL

Once deployed, Render will provide you with a URL like:
```
https://genai-doc-assistant-backend.onrender.com
```

Save this URL - you'll need it for the frontend configuration.

---

## Part 2: Frontend Deployment on Streamlit Cloud

### Step 1: Prepare Frontend Requirements

1. Create `frontend/.streamlit/config.toml` ✓ (already created)
2. Create `frontend/requirements.txt` ✓ (already created)

### Step 2: Create `.streamlit/secrets.toml` for Local Testing

Create `frontend/.streamlit/secrets.toml`:

```toml
# Local development
BACKEND_API_URL = "http://localhost:8000"
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub repository
4. Configure deployment:
   - **Repository:** Select your repo
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`

5. Click **"Deploy!"**

### Step 4: Configure Environment Variables in Streamlit Cloud

1. In Streamlit Cloud dashboard, go to **"App settings"** (gear icon)
2. Click on **"Secrets"** tab
3. Add your environment variable:

   ```
   BACKEND_API_URL = "https://genai-doc-assistant-backend.onrender.com"
   ```

4. Save and wait for app to redeploy (~1-2 minutes)

---

## Part 3: Enable Cross-Service Communication

### Backend (Render) Configuration

Your FastAPI backend should allow requests from the Streamlit frontend. If you need to add CORS:

Update `main.py` to include CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG System API",
    description="An API for document ingestion and querying using a RAG system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify: ["https://your-streamlit-app.streamlit.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend (Streamlit) Configuration

The frontend is already configured to:
- Read `BACKEND_API_URL` from environment variables
- Fall back to `http://localhost:8000` for local development
- Use this URL for all API calls

---

## Testing the Deployment

### Test Backend Health Check

```bash
curl https://genai-doc-assistant-backend.onrender.com/health-check
```

Expected response:
```json
{
  "status": "ok",
  "version": "1.0.2",
  "environment": "production",
  "uptime_seconds": 1234
}
```

### Test Frontend Connection

1. Visit your Streamlit app URL
2. Go to the "System Status" section
3. Click "Check API Status"
4. If successful, you'll see: "Everything is working perfectly!"

---

## Troubleshooting

### Backend not starting on Render

1. Check Render logs: Dashboard → Select your service → Logs
2. Common issues:
   - Missing dependencies: Add to `requirements.txt`
   - Port binding: Ensure port 8000 is exposed
   - Environment variables: Verify all required keys are set

### Frontend can't connect to backend

1. Verify backend URL in Streamlit secrets
2. Check browser console for network errors (F12)
3. Ensure backend CORS allows Streamlit domain
4. Test with curl: `curl BACKEND_API_URL/health-check`

### Timeout issues

- Backend file uploads: Increase timeout in `frontend/services/api_client.py`
- Render cold starts: Free tier may have 50-second startup delay
- Consider upgrading to paid tier for production

### Database/Storage Issues

- ChromaDB data is currently stored locally
- For production, consider:
  - Moving to cloud storage (AWS S3, Google Cloud Storage)
  - Using managed vector database (Pinecone, Weaviate, Milvus)
  - Implementing persistent volume in Render

---

## Manual Deployment Steps (Alternative)

If you prefer not to use deployment files:

### Render - Manual Docker Deployment

1. In Render dashboard, select your service
2. Go to "Environment"
3. Ensure Docker is selected
4. Set port to 8000
5. Render will automatically detect and use your Dockerfile

### Streamlit - Manual Deployment

```bash
# Local test
cd frontend
streamlit run app.py

# The deploy to Streamlit Cloud by linking your GitHub repo
```

---

## Environment Variables Summary

### Backend (Render)

```
PYTHON_VERSION=3.11
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
# Add any API keys your RAG system needs
GROQ_API_KEY=your_api_key_here
```

### Frontend (Streamlit)

```
BACKEND_API_URL=https://genai-doc-assistant-backend.onrender.com
```

---

## Performance Optimization Tips

### For Render Backend

1. Use paid tier for faster cold starts
2. Enable "Auto-scaling" for consistent performance
3. Implement caching for frequently accessed documents
4. Monitor logs for bottlenecks

### For Streamlit Frontend

1. Use `@st.cache_data` for API responses
2. Implement session state management
3. Optimize large document uploads with streaming

---

## Monitoring & Maintenance

### Monitor Backend Health

```bash
# Check every 5 minutes
curl -X GET https://genai-doc-assistant-backend.onrender.com/health-check
```

### View Logs

- **Render:** Dashboard → Logs tab
- **Streamlit:** Dashboard → App logs

### Update Deployment

To deploy new changes:

```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

Both services will automatically redeploy (with Render taking 5-10 minutes).

---

## Cleanup & Cost Management

### Free Tier Limits

- **Render:** 750 hours/month, auto-sleep after 15 min inactivity
- **Streamlit:** Unlimited apps but single app per project limit

### Cost Optimization

- Use free tiers for development/testing
- Upgrade only services that need it
- Monitor usage in both dashboards

---

## Next Steps

1. ✅ Deploy backend on Render
2. ✅ Deploy frontend on Streamlit Cloud
3. ✅ Configure environment variables
4. ✅ Test end-to-end communication
5. Optional: Set up monitoring/alerting
6. Optional: Configure custom domains

For issues or questions, check:
- [Render Docs](https://render.com/docs)
- [Streamlit Docs](https://docs.streamlit.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)
