# ============================================================================
# Dockerfile for FastAPI + RAG Service on Render Free Tier (512MB RAM)
# Optimized for lazy loading of heavy ML models and memory efficiency
# ============================================================================

# Base image: Python 3.11 slim (smaller than standard, ~160MB)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ============================================================================
# ENVIRONMENT VARIABLES - Optimized for Render Free Tier
# ============================================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    WEB_CONCURRENCY=1 \
    PORT=8000

# ============================================================================
# SYSTEM DEPENDENCIES - Minimal Installation
# Only install build-essential for compiling Python packages with C extensions
# This is needed for torch, transformers, sentence-transformers, etc.
# ============================================================================
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# ============================================================================
# PYTHON DEPENDENCIES - Optimized Installation
# ============================================================================
# Copy requirements.txt first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install dependencies
# Using --no-cache-dir to reduce layer size
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Note: gunicorn and uvicorn are already in requirements.txt
# They provide the ASGI server and worker processes

# ============================================================================
# APPLICATION CODE
# ============================================================================
COPY . .

# ============================================================================
# EXPOSE PORT
# Render automatically reads PORT environment variable
# Expose the port specified in PORT env var (default 8000)
# ============================================================================
EXPOSE 8000

# ============================================================================
# HEALTH CHECK - Fast container liveness probe
# Interval: 30s - Check every 30 seconds
# Timeout: 10s - Give up after 10 seconds
# Start-period: 120s - Wait 2 min before first check (models loading)
# Retries: 3 - Allow 3 consecutive failures before marking unhealthy
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health-check', timeout=5)"

# ============================================================================
# GUNICORN CONFIGURATION - Memory-Optimized for 512MB Render Free Tier
# ============================================================================
# KEY SETTINGS EXPLAINED:
#
# --workers 1
#   CRITICAL: Only 1 worker process to prevent duplicate model loading
#   Each worker = full copy of embeddings (260MB) + ChromaDB cache (100MB)
#   2 workers = 720MB+ total (exceeds 512MB limit, causes OOM)
#   Solution: Single worker handles all requests sequentially
#
# --worker-class uvicorn.workers.UvicornWorker
#   Uses Uvicorn ASGI worker for async request handling
#   Better performance than sync workers for async FastAPI code
#
# --bind 0.0.0.0:8000
#   Listen on all network interfaces on port 8000
#   Required for Render platform routing
#
# --timeout 600
#   Worker timeout = 600 seconds (10 minutes)
#   CRITICAL: HuggingFace embedding model takes 5-10 minutes to load
#   If timeout too short (e.g., 30s), worker dies during model init
#   First request will hang for 5-10 min while models load (expected behavior)
#   Subsequent requests: 1-2 sec (models cached in memory)
#
# --graceful-timeout 60
#   Allow 60 seconds for graceful shutdown
#   Worker finishes current request before stopping
#
# --max-requests 100
#   Recycle worker after 100 requests
#   Prevents memory bloat from long-running requests
#   Worker restarts cleanly without reloading models (they stay in memory)
#
# --max-requests-jitter 20
#   Add random jitter (0-20) to max-requests
#   Prevents all workers restarting simultaneously (thundering herd)
#
# --threads 1
#   Single thread per worker (explicit)
#   Uvicorn handles async I/O internally with event loop
#   Prevents GIL contention and memory overhead from threading
#
# ============================================================================
CMD ["gunicorn", \
     "--workers", "1", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:${PORT}", \
     "--timeout", "600", \
     "--graceful-timeout", "60", \
     "--max-requests", "100", \
     "--max-requests-jitter", "20", \
     "--threads", "1", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "main:app"]

# ============================================================================
# PERSISTENT VOLUME INSTRUCTIONS FOR CHROMADB
# ============================================================================
# ChromaDB persistence on Render:
#
# 1. EPHEMERAL BY DEFAULT:
#    Render free tier has ephemeral filesystem - data lost on restart
#    Every container restart = fresh ChromaDB (documents lost)
#
# 2. ENABLE PERSISTENT DISK (Paid):
#    If you upgrade from free tier to paid:
#    - Add persistent disk in Render dashboard
#    - Mount at /app/chroma_data (configured in config.py)
#    - Restart service to apply persistent disk
#    - Documents will survive container restarts
#
# 3. WORKAROUND FOR FREE TIER:
#    Upload documents on each session (expected workflow)
#    Or use external database (PostgreSQL, MongoDB, etc.)
#
# 4. DIRECTORY CREATION:
#    ChromaDB directory is created automatically in config.py:
#    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
#    Uses: CHROMA_DB_PATH = "./chroma_data" (from config.py)
#
# ============================================================================
