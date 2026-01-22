# 🎯 Your Action Checklist - Fix Your Deployment NOW

## What's Wrong
You deployed successfully but:
- ❌ Document uploads fail
- ❌ LLM doesn't work
- ✅ Health check says "everything is perfect"

**Reason:** GROQ_API_KEY is missing in Render environment variables

---

## ✅ STEP-BY-STEP FIX

### ⏱️ Time needed: 5-10 minutes

### Step 1: Get Your Groq API Key (2 min)

1. Open: https://console.groq.com/
2. Sign in (create free account if needed)
3. Go to **API Keys** section
4. Copy your key (looks like: `gsk_abc123...`)
   - If no keys exist, click **"Create API Key"**
5. Keep this key visible for Step 3

### Step 2: Open Render Dashboard (1 min)

1. Go to: https://dashboard.render.com/
2. Log in with your account
3. Click your service: **`genai-doc-assistant-backend`**

### Step 3: Add Environment Variable (2 min)

1. In the service page, find **"Environment"** in left sidebar
2. Click on **"Environment"**
3. Click **"Add Environment Variable"** button
4. Fill in the form:
   - **Key:** `GROQ_API_KEY` (exact spelling!)
   - **Value:** Paste your key from Step 1 (the one starting with `gsk_`)
5. Click **"Save"**

### Step 4: Wait for Restart (3 min)

- Service will restart automatically
- You'll see a spinner/loading status
- Wait until it says **"live"** or **"running"**
- Don't close the page

### Step 5: Test It Works (1 min)

**Open a terminal and run:**

```bash
curl https://your-render-url.onrender.com/api/debug/status
```

Replace `your-render-url` with your actual Render backend URL.

**You should see:**
```
{
  "api_key_present": true,
  "llm_initialized": true,
  "embeddings_initialized": true,
  "vector_store_ready": true,
  "status": "ALL SYSTEMS OPERATIONAL"
}
```

**If you still see `"api_key_present": false`:**
- Go back to Step 3 and verify the key was saved
- Check the "Updated" timestamp - should be recent
- Try restarting the service manually

### Step 6: Test Frontend Features (2 min)

1. Open your Streamlit app
2. Try uploading a small PDF or text file
3. Try asking a question
4. Should work now! ✅

---

## 📋 Verification Checklist

- [ ] Groq API key copied from console.groq.com
- [ ] Logged into Render dashboard
- [ ] Found the backend service
- [ ] Added GROQ_API_KEY environment variable
- [ ] Pasted the full key (starting with `gsk_`)
- [ ] Clicked Save
- [ ] Waited for service to restart (shows "live")
- [ ] Ran debug status test (shows all TRUE)
- [ ] Tested document upload - works!
- [ ] Tested LLM query - works!

---

## 🔧 If It's Still Not Working

### Test 1: Check Your API Key

Run this:
```bash
curl https://your-render-url.onrender.com/api/debug/status
```

If `"api_key_present": false` → Go back to Step 3, key wasn't saved properly

If `"llm_initialized": false` → API key is invalid/expired
- Get a new one from https://console.groq.com/
- Update it in Render

### Test 2: Check Render Logs

1. In Render service page
2. Click **"Logs"** tab
3. Look for error messages
4. If you see "GROQ_API_KEY environment variable is not set":
   - The variable wasn't saved, repeat Step 3

### Test 3: Manual Service Restart

1. In Render service page
2. Click three-dot menu (⋮)
3. Select **"Restart service"**
4. Wait 2-5 minutes
5. Test again

### Test 4: Check Streamlit Configuration

1. Open your Streamlit Cloud dashboard
2. Find your app
3. Click ⚙️ Settings
4. Go to **"Secrets"** tab
5. Make sure `BACKEND_API_URL` is set to your Render URL
6. Should look like: `https://genai-doc-assistant-backend.onrender.com`

---

## 📞 Emergency Debug Info

If you're stuck, collect this info and share it:

**1. Run this command:**
```bash
curl https://your-backend-url.onrender.com/api/debug/status
```
Copy the full output.

**2. Screenshot from Render:**
- Go to your service
- Take screenshot of Environment variables section (mask the API key with `gsk_...xxx`)

**3. Last 10 lines from Render logs:**
- Go to Logs tab
- Copy the last 10 lines

---

## 🎉 Success Indicators

You'll know it's fixed when:

✅ Debug status shows all `true` values
✅ Can upload a document without error
✅ Can ask questions about the document
✅ Get actual answers from the LLM
✅ No more "Connection refused" errors

---

## Summary

| Step | What | Where | Time |
|------|------|-------|------|
| 1 | Get API key | https://console.groq.com/ | 2 min |
| 2 | Open Render | https://dashboard.render.com/ | 1 min |
| 3 | Add env var | Backend service → Environment | 2 min |
| 4 | Wait restart | Service page (watch status) | 3 min |
| 5 | Test debug | Run curl command | 1 min |
| 6 | Test features | Upload doc + ask question | 2 min |

**Total time: ~10 minutes**

---

**Do this now and your deployment will work!** 🚀
