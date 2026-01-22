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
        "uptime_seconds": int(time.time() - START_TIME)
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
        
        # Try to initialize RAG service
        from app.api.services.rag_service import RAGService
        try:
            rag_service = RAGService()
            llm_initialized = True
            embeddings_initialized = True
            vector_store_ready = True
            error_message = None
        except Exception as e:
            llm_initialized = False
            embeddings_initialized = False
            vector_store_ready = False
            error_message = str(e)
        
        status = "ALL SYSTEMS OPERATIONAL" if all([
            api_key_present,
            llm_initialized,
            embeddings_initialized,
            vector_store_ready
        ]) else "SOME SYSTEMS FAILED"
        
        return {
            "api_key_present": api_key_present,
            "llm_initialized": llm_initialized,
            "embeddings_initialized": embeddings_initialized,
            "vector_store_ready": vector_store_ready,
            "status": status,
            "error": error_message,
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
