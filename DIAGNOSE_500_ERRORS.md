# 🔍 Diagnosing 500 Errors - Next Steps

## Problem: You're getting 500 Server Errors

This means your backend is receiving the request but something is failing internally.

## Step 1: Check Render Logs

1. Go to: https://dashboard.render.com/
2. Click your backend service: `genai-doc-assistant-backend`
3. Click the **"Logs"** tab
4. Scroll to see the most recent errors

**Look for error messages that mention:**
- `GROQ_API_KEY` - Your API key is still not set!
- `ImportError` - Missing Python package
- `ModuleNotFoundError` - Import issue
- `Connection refused` - Database connection issue

## Step 2: Verify GROQ_API_KEY AGAIN

**99% chance this is your problem:**

1. In Render dashboard
2. Click your service
3. Go to **"Environment"** section
4. Look for `GROQ_API_KEY`
5. Make sure it has a value that starts with `gsk_`

If it's missing or says `gsk_...` (placeholder):
- Get a fresh key from https://console.groq.com/
- Add/update it in Render env vars
- Service will restart automatically

## Step 3: After Render Updates

Once you've:
- Added/updated GROQ_API_KEY
- Waited for service to restart (2-5 minutes)

Test the debug endpoint:
```bash
curl https://your-render-url.onrender.com/api/debug/status
```

If all values are `true`, the backend is ready.

## Step 4: Check Logs More Carefully

After Render restarts, check logs again for any NEW errors.

Common issues in logs:
- `IndexError` or `KeyError` - Wrong data format
- `FileNotFoundError` - Directory permission issue
- `ValueError` - Invalid input data
- `ConnectionError` - Network issue

## Step 5: Test Upload with Debug Info

Try uploading a small text file (just a few words) and immediately:

1. Check Render logs (will show detailed error)
2. Copy the error message
3. Share it so we can fix it

## What I Added to Help

I've added better error logging to the backend. When you push this code and Render redeploys, you'll see much better error messages in the logs.

## Quick Checklist

- [ ] GROQ_API_KEY is set (not placeholder)
- [ ] Render service has restarted (check "Updated" time)
- [ ] Checked Render logs for errors
- [ ] Ran debug status endpoint - all TRUE
- [ ] Tried uploading small test file
- [ ] Checked logs again for error details

## Next: Share Diagnostic Info

Once you've done these steps, if still getting 500 errors:

1. Go to Render logs
2. Copy the last error message (the complete one)
3. Run: `curl https://your-url.onrender.com/api/debug/status`
4. Copy that response too
5. Share both and I can debug exactly what's wrong

The error messages will now be much more detailed!
