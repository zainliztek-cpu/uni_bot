@echo off
REM GenAI Document Assistant - Deployment Quick Start (Windows)
REM This script sets up and validates your deployment configuration

echo.
echo 🚀 GenAI Document Assistant - Deployment Setup
echo =============================================="
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Docker is not installed. Please install Docker Desktop from https://docker.com
    exit /b 1
)

echo ✅ Docker found
echo.

REM Check Git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Git is not installed. Please install Git from https://git-scm.com
    exit /b 1
)

echo ✅ Git found
echo.

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Python is not installed. Please install Python from https://python.org
    exit /b 1
)

echo ✅ Python found
echo.

REM Check files
echo Checking deployment files...
setlocal enabledelayedexpansion

set "files=Dockerfile .dockerignore docker-compose.yml frontend\Dockerfile.streamlit render.yaml DEPLOYMENT_GUIDE.md"

for %%F in (%files%) do (
    if exist "%%F" (
        echo ✅ %%F
    ) else (
        echo ❌ Missing: %%F
    )
)

echo.
echo 📋 Deployment Checklist:
echo ========================
echo.
echo BEFORE DEPLOYING:
echo.
echo 1. GitHub Repository:
echo    [ ] Push code to GitHub
echo    [ ] Verify all files are committed
echo.
echo 2. Environment Variables:
echo    [ ] Gather all API keys (GROQ_API_KEY, etc.)
echo    [ ] Copy .env.example to .env and fill in values
echo.
echo 3. Backend (Render):
echo    [ ] Create account on render.com
echo    [ ] Connect GitHub repository
echo    [ ] Set environment variables in Render dashboard
echo    [ ] Note down the backend URL after deployment
echo.
echo 4. Frontend (Streamlit):
echo    [ ] Create account on share.streamlit.io
echo    [ ] Connect GitHub repository
echo    [ ] Set BACKEND_API_URL in Streamlit Secrets
echo.
echo 5. Testing Locally (Optional):
echo    [ ] Run: docker-compose up
echo    [ ] Test backend: curl http://localhost:8000/health-check
echo    [ ] Test frontend: Open http://localhost:8501
echo.
echo 📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md
echo.
echo 🎯 Quick Links:
echo    Render: https://render.com
echo    Streamlit Cloud: https://share.streamlit.io
echo.
