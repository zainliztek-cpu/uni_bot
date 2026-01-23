# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn uvicorn

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health-check', timeout=5)"

# Run the application with gunicorn and uvicorn
# Single worker for free tier (512MB RAM), increased timeouts for model loading
# --timeout 600s: Models (HF embeddings) need 5+ min to load on first request
# --workers 1: Prevent duplicate model loading in multiple processes (saves ~260MB RAM)
# --max-requests 100: Recycle worker periodically to prevent memory bloat
# Note: uvicorn.workers.UvicornWorker uses 1 thread by default, but we ensure it explicitly
CMD ["gunicorn", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "600", "--graceful-timeout", "60", "--max-requests", "100", "--max-requests-jitter", "20", "--threads", "1", "main:app"]
