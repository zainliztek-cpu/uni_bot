# 🔧 Deployment Troubleshooting Guide

## Problem: Health Check Passes but Features Don't Work

If you see "Everything is working perfectly!" but:
- ❌ Document uploading fails
- ❌ LLM queries don't work  
- ❌ Features are broken

The issue is likely: **GROQ_API_KEY is not set in Render environment variables**

---

## Quick Fix

### Step 1: Check Render Environment Variables

1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your backend service: `genai-doc-assistant-backend`
3. Click **"Settings"** (or **"Environment"**)
4. Look for these variables:

**✅ Required:**
```
GROQ_API_KEY = gsk_your_actual_key_here
```

**If GROQ_API_KEY is missing or says `gsk_...` (placeholder):**
- This is your problem! The LLM won't work without it.

### Step 2: Get Your Groq API Key

1. Go to https://console.groq.com/
2. Sign in with your account
3. Create new API key (or copy existing one)
4. Copy the full key (starts with `gsk_`)

### Step 3: Add to Render

1. In Render dashboard settings
2. Find the **Environment** or **Env Vars** section
3. Add/Update:
   - **Key:** `GROQ_API_KEY`
   - **Value:** `gsk_your_full_key_here`
4. Click **Save**
5. Service will auto-restart (takes 2-5 minutes)

### Step 4: Verify It Works

**Test health endpoint:**
```bash
curl https://your-backend.onrender.com/health-check
```

**Test debug endpoint:**
```bash
curl https://your-backend.onrender.com/api/debug/status
```

If you see `"llm_initialized": true` and `"api_key_present": true`, it worked!

---

## Complete Render Environment Variables Checklist

Add these to your Render service settings:

```
PYTHON_VERSION = 3.11
GROQ_API_KEY = gsk_your_actual_key_here (REQUIRED!)
CHROMA_DB_PATH = ./chroma_data (optional, has default)
EMBEDDING_MODEL = BAAI/bge-large-en-v1.5 (optional, has default)
LLM_MODEL = llama-3.3-70b-versatile (optional, has default)
```

**Only GROQ_API_KEY is absolutely required.**

---

## Step-by-Step Render Setup

### 1. Open Render Dashboard

Visit: https://dashboard.render.com/

### 2. Select Your Service

Click on **`genai-doc-assistant-backend`**

### 3. Go to Settings

- Look for a **Settings** tab or **Environment** section
- Click it

### 4. Add Environment Variables

Click **"Add Environment Variable"** (or edit if already exists)

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `gsk_abc123...` (your real key) |
| `CHROMA_DB_PATH` | `./chroma_data` |
| `EMBEDDING_MODEL` | `BAAI/bge-large-en-v1.5` |
| `LLM_MODEL` | `llama-3.3-70b-versatile` |

### 5. Save and Wait

- Click **Save**
- Service will restart automatically
- Wait 2-5 minutes for restart

### 6. Check Logs

While it restarts, check **Logs** tab:
- Look for "RAG service initialized successfully"
- If you see errors, screenshot them for debugging

---

## Verify the Fix

### Test 1: Check Server is Running
```bash
curl https://your-backend.onrender.com/
```

**Expected:**
```json
{"message": "API is running"}
```

### Test 2: Check Health
```bash
curl https://your-backend.onrender.com/health-check
```

**Expected:**
```json
{
  "status": "ok",
  "version": "1.0.2",
  "environment": "production",
  "uptime_seconds": 123
}
```

### Test 3: Check Debug Status (NEW!)
```bash
curl https://your-backend.onrender.com/api/debug/status
```

**Expected if working:**
```json
{
  "api_key_present": true,
  "llm_initialized": true,
  "embeddings_initialized": true,
  "vector_store_ready": true,
  "status": "ALL SYSTEMS OPERATIONAL"
}
```

**If you see `"api_key_present": false`:**
- Your GROQ_API_KEY is not set!
- Go back to Step 1 and add it

---

## Check Render Logs for Errors

1. Open your Render service
2. Click **"Logs"** tab
3. Look for error messages

**Common errors:**

### Error: "GROQ_API_KEY environment variable is not set"
**Solution:** Add GROQ_API_KEY to Render env vars (see above)

### Error: "InvalidRequestError: Error code: 401"
**Solution:** Your GROQ_API_KEY is invalid or expired
- Go to https://console.groq.com/ 
- Create a new API key
- Update in Render env vars

### Error: "ModuleNotFoundError"
**Solution:** Missing Python package
- Check `requirements.txt` includes all packages
- Redeploy by pushing to GitHub

### Error: "ConnectionError" for ChromaDB
**Solution:** Render restart needed
- Wait 5 minutes
- Manually restart in Render dashboard if needed

---

## Streamlit Frontend Verification

### Test Connection to Backend

1. Open your Streamlit app
2. Scroll to **"System Status"** section
3. Click **"Check API Status"**

**If it says "Backend API is not accessible":**
- Verify backend URL is correct in Streamlit Secrets
- In Streamlit Cloud Dashboard:
  - Click **⚙️ App settings**
  - Go to **Secrets** tab
  - Check: `BACKEND_API_URL = https://your-backend.onrender.com`

---

## Complete Verification Checklist

- [ ] GROQ_API_KEY is set in Render env vars (not a placeholder)
- [ ] Backend has restarted (check "Updated" time in Render)
- [ ] Render logs show "RAG service initialized successfully"
- [ ] `curl /api/debug/status` shows all TRUE
- [ ] Streamlit backend URL is correct
- [ ] Streamlit can reach backend (no network errors)
- [ ] Can upload documents
- [ ] Can query documents
- [ ] LLM generates responses

---

## Still Not Working?

### Debug by Checking Render Logs

```bash
# SSH into your Render service and check:
ps aux | grep python
env | grep GROQ

# Or check logs in Render dashboard under "Logs" tab
```

### Check File Permissions

Make sure `chroma_data` directory is writable:
```bash
ls -la chroma_data/
```

### Restart Services

**Restart Backend:**
1. Render Dashboard → Service → Manual Restart
2. Wait 2-5 minutes

**Restart Frontend:**
1. Streamlit Cloud → App → Reboot app

### Test Locally First

Before assuming deployed version is broken:

```bash
# Local test
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
python -m uvicorn main:app --reload
# In another terminal: curl http://localhost:8000/api/debug/status
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Everything is perfect" but no uploads | GROQ_API_KEY not set | Add to Render env vars |
| 500 error on upload | Missing dependencies | Check requirements.txt |
| "Invalid API key" error | Wrong/expired key | Get new key from groq.com |
| Timeout on upload | File too large or cold start | Upgrade Render plan |
| Streamlit can't reach backend | Wrong URL or CORS issue | Check secrets in Streamlit Cloud |
| ChromaDB errors | Disk space or permissions | Restart Render service |

---

## Next Steps

1. **Immediately:** Add GROQ_API_KEY to Render env vars
2. **Wait:** 5 minutes for service to restart
3. **Test:** Run debug status check (see above)
4. **Verify:** Upload document and query it
5. **Monitor:** Check Render logs if issues occur

---

## Get Help

If still not working, provide:
1. Output of: `curl https://your-backend.onrender.com/api/debug/status`
2. Last 50 lines from Render logs
3. Browser console errors (F12)
4. Screenshot of Render env vars (mask API key)

**Remember:** The health check only verifies the server is running, not that all services are initialized! Use the debug endpoint to verify everything is actually working.
