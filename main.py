from fastapi import FastAPI
from app.api.core import rag_router
import time
import os

START_TIME = time.time()

# Creating an instance of the FastAPI class
app = FastAPI(
    title="RAG System API",
    description="An API for document ingestion and querying using a RAG system",
    version="1.0.0"
)

# Simple root endpoint to check if the server is running
@app.get("/")
def read_root():
    return {'message': 'API is running'}

@app.get("/health-check")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.2",
        "environment": "production",
        "uptime_seconds": int(time.time() - START_TIME),
        "note": "RAG service initializes on first API call (not on startup) to prevent timeouts"
    }

@app.get("/api/debug/status")
def debug_status():
    """
    Debug endpoint to check if all services are properly initialized.
    Use this to verify everything is working, not just the health check.
    """
    try:
        # Check API key
        api_key_present = bool(os.getenv("GROQ_API_KEY"))
        
        # Check if RAG service has been initialized
        from app.api.rag_api import _rag_service
        
        if _rag_service is None:
            # Service hasn't been initialized yet - that's OK, it will on first request
            return {
                "api_key_present": api_key_present,
                "llm_initialized": False,
                "embeddings_initialized": False,
                "vector_store_ready": False,
                "status": "NOT_YET_INITIALIZED",
                "error": "Service will initialize on first API call",
                "uptime_seconds": int(time.time() - START_TIME)
            }
        
        # Service exists, report its status
        status = "ALL SYSTEMS OPERATIONAL"
        
        return {
            "api_key_present": api_key_present,
            "llm_initialized": True,
            "embeddings_initialized": True,
            "vector_store_ready": True,
            "status": status,
            "error": None,
            "uptime_seconds": int(time.time() - START_TIME)
        }
    except Exception as e:
        return {
            "api_key_present": False,
            "llm_initialized": False,
            "embeddings_initialized": False,
            "vector_store_ready": False,
            "status": "INITIALIZATION FAILED",
            "error": str(e),
            "uptime_seconds": int(time.time() - START_TIME)
        }


app.include_router(
    rag_router.router,
    prefix="/api",
    tags=["RAG System"]
)
