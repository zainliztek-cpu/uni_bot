# 🚨 IMMEDIATE ACTION: Fix Your Deployment

Your deployment is reporting everything works but features are broken. This almost certainly means **GROQ_API_KEY is missing from Render environment variables**.

## The Problem

- ✅ Health check passes (server is running)
- ❌ Document upload fails
- ❌ LLM doesn't respond
- ❌ No useful error messages

**Root cause:** GROQ_API_KEY environment variable is not set on Render.

---

## ⚡ QUICK FIX (Do This Now!)

### Step 1: Open Your Render Service

1. Go to: https://dashboard.render.com/
2. Click on your service: **`genai-doc-assistant-backend`**

### Step 2: Add the Missing Environment Variable

1. Look for **"Environment"** section in the left sidebar
2. Click on it
3. Click **"Add Environment Variable"**
4. Fill in:
   - **Key:** `GROQ_API_KEY`
   - **Value:** (Get from step 3 below)

### Step 3: Get Your Groq API Key

1. Go to: https://console.groq.com/
2. Log in (create account if needed - free!)
3. Click **"API Keys"** in sidebar
4. Create a new key or copy existing one
5. Copy the full key (starts with `gsk_`)

### Step 4: Paste and Save

- Paste your `gsk_...` key into the Value field
- Click **"Save"**
- Wait 2-5 minutes for service to restart

---

## ✅ Verify It's Fixed

### Test 1: Check Debug Status

Run this command:

```bash
curl https://your-render-url.onrender.com/api/debug/status
```

Replace `your-render-url` with your actual Render URL.

**Good response:**
```json
{
  "api_key_present": true,
  "llm_initialized": true,
  "embeddings_initialized": true,
  "vector_store_ready": true,
  "status": "ALL SYSTEMS OPERATIONAL"
}
```

**Bad response (your current issue):**
```json
{
  "api_key_present": false,
  "llm_initialized": false,
  "status": "SOME SYSTEMS FAILED",
  "error": "GROQ_API_KEY environment variable is not set..."
}
```

### Test 2: Try Uploading a Document

1. Open your Streamlit frontend
2. Go to **"Document Ingestion"** page
3. Upload a small PDF or text file
4. Should now work!

---

## 📋 All Required Environment Variables

Add these to your Render service (in Environment section):

| Key | Value | Required? |
|-----|-------|-----------|
| `GROQ_API_KEY` | `gsk_your_key_here` | ✅ YES |
| `CHROMA_DB_PATH` | `./chroma_data` | ❌ No (has default) |
| `EMBEDDING_MODEL` | `BAAI/bge-large-en-v1.5` | ❌ No (has default) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | ❌ No (has default) |

**Only GROQ_API_KEY is absolutely required to make it work.**

---

## Step-by-Step With Screenshots

### Screenshot Guide:

**1. Open Render Dashboard**
```
Go to: https://dashboard.render.com/
Look for your service in the list
```

**2. Click Your Service**
```
Service name: genai-doc-assistant-backend
Click on it
```

**3. Find Environment Section**
```
Left sidebar → "Environment" (or scroll to find it)
Click Environment
```

**4. Add Variable**
```
Button: "Add Environment Variable" (or + sign)
Click it
```

**5. Enter Variable**
```
Key field: GROQ_API_KEY
Value field: gsk_... (your actual key from groq.com)
```

**6. Save**
```
Click "Save" button
Service will restart automatically
```

---

## 🔍 Diagnose Further (If Still Not Working)

### Check Render Logs

1. In your Render service page
2. Click **"Logs"** tab
3. Look for any error messages
4. Share the last 10 error lines if you're still stuck

### Check Render Restart Status

1. Go to Render service page
2. Look at **"Updated"** timestamp
3. Should show recent time (within last 5 minutes)
4. If old, it didn't restart - click **"Restart service"** manually

### Verify API Key Format

Your Groq API key should:
- Start with `gsk_`
- Be at least 50 characters long
- Not have spaces or special characters (except underscore)

If it doesn't look right, create a new key at https://console.groq.com/

---

## Common Mistakes

❌ **Mistake:** Pasting only part of the key
- **Fix:** Use full key from groq.com console

❌ **Mistake:** Setting key to placeholder like `gsk_...`
- **Fix:** Use your real key, not the example

❌ **Mistake:** Not waiting for service to restart
- **Fix:** Wait 2-5 minutes, then test

❌ **Mistake:** Wrong variable name (like `GROQ_KEY` instead of `GROQ_API_KEY`)
- **Fix:** Use exact name: `GROQ_API_KEY`

---

## Test Your Groq Key Locally

Before deploying, test locally:

```bash
# Create/edit .env file
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# Run backend
python -m uvicorn main:app --reload

# In another terminal, test debug endpoint
curl http://localhost:8000/api/debug/status

# Should show all TRUE values
```

---

## Still Broken?

Provide this information and I can help:

1. Run:
   ```bash
   curl https://your-render-url.onrender.com/api/debug/status
   ```
   Paste the response

2. Take screenshot of Render Environment variables (mask the key with `gsk_...xxx`)

3. Copy last 20 lines from Render Logs

Then we can debug the exact issue.

---

## Summary

1. ✅ Get Groq API key from https://console.groq.com/
2. ✅ Add it to Render as `GROQ_API_KEY` env var
3. ✅ Wait 2-5 minutes for restart
4. ✅ Test with `curl .../api/debug/status`
5. ✅ Try uploading a document

That's it! Should work now.
