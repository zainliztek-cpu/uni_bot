# 🚀 Quick Start Guide

## Prerequisites

- Python 3.11+
- Git
- Groq API Key (free from https://console.groq.com/)

## Local Development Setup

### Step 1: Clone and Setup Environment

```bash
# Navigate to project directory
cd genai-Capstone-doc-Assistant

# Create .env file from template
cp .env.example .env
```

### Step 2: Add Your Groq API Key

Edit `.env` file and add your API key:

```bash
# Open .env with your editor
# Windows: notepad .env
# Mac/Linux: nano .env

# Replace this line:
GROQ_API_KEY=your_groq_api_key_here

# With your actual Groq API key:
GROQ_API_KEY=gsk_abcd1234...
```

**How to get your Groq API Key:**
1. Go to https://console.groq.com/
2. Sign up (free account)
3. Create a new API key
4. Copy and paste it into `.env`

### Step 3: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
pip install -r requirements.txt
cd ..
```

### Step 4: Run Locally

**Option A: Run both services with Docker Compose (Recommended)**

```bash
# Make sure Docker is running
docker-compose up --build

# Services will be available at:
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

**Option B: Run backend and frontend separately**

Terminal 1 - Backend:
```bash
# From project root
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
streamlit run app.py
```

### Step 5: Test the Connection

1. Open frontend: http://localhost:8501
2. Check "System Status" section
3. Click "Check API Status"
4. You should see: ✅ "Everything is working perfectly!"

---

## ⚠️ Important: Git and Environment Variables

### Why .env is in .gitignore

The `.gitignore` file prevents `.env` from being committed to Git because:
- ✅ Keeps your API keys secure
- ✅ Prevents accidental exposure on GitHub
- ✅ Each environment (dev, staging, production) has its own keys

### Verify Before Pushing to Git

```bash
# Check what will be committed
git status

# Verify .env is NOT in the list
# If .env is listed, STOP and fix it:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

---

## Deployment on Render & Streamlit

### Backend (Render)

1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. On Render Dashboard:
   - Add environment variable: `GROQ_API_KEY=your_key_here`
   - Other variables are optional (use defaults)

### Frontend (Streamlit)

1. On Streamlit Cloud Dashboard:
   - Go to App Settings → Secrets
   - Add: `BACKEND_API_URL=https://your-backend.onrender.com`

---

## Troubleshooting

### Error: "GROQ_API_KEY environment variable is not set"

**Solution:**
```bash
# Make sure .env file exists in project root
ls -la .env  # Mac/Linux
dir .env    # Windows

# Make sure it has your API key
cat .env    # Mac/Linux
type .env   # Windows
```

### Error: "Could not connect to backend"

1. Check backend is running:
   ```bash
   curl http://localhost:8000/health-check
   ```

2. Check frontend can see backend URL:
   - Open browser console (F12)
   - Check Network tab for API calls
   - Verify BACKEND_API_URL environment variable

### Error: "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or in frontend directory
cd frontend
pip install -r requirements.txt
```

---

## Environment Variables Reference

### Required

| Variable | Purpose | Example |
|----------|---------|---------|
| `GROQ_API_KEY` | Groq LLM API Key | `gsk_...` |

### Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `CHROMA_DB_PATH` | `./chroma_data` | Vector DB location |
| `EMBEDDING_MODEL` | `BAAI/bge-large-en-v1.5` | Embedding model |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | LLM model name |
| `BACKEND_API_URL` | `http://localhost:8000` | Backend URL (frontend only) |

---

## File Structure After Setup

```
genai-Capstone-doc-Assistant/
├── .env                    # ← Your local secrets (NOT in git)
├── .env.example            # ← Template (in git)
├── .gitignore              # ← Prevents .env from being tracked
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── main.py
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile.streamlit
│   ├── .streamlit/
│   │   └── config.toml
│   ├── pages/
│   └── services/
├── app/
│   └── api/
│       ├── core/
│       │   └── config.py   # ← Reads GROQ_API_KEY from .env
│       ├── services/
│       └── agents/
└── chroma_data/
```

---

## Next Steps

1. ✅ Set up .env with your Groq API key
2. ✅ Test locally with `docker-compose up`
3. ✅ Push to GitHub
4. ✅ Deploy on Render (backend)
5. ✅ Deploy on Streamlit Cloud (frontend)

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
