from fastapi import FastAPI
from app.api.core import rag_router
import time

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


app.include_router(
    rag_router.router,
    prefix="/api",
    tags=["RAG System"]
)
