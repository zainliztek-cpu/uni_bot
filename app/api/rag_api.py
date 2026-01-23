from fastapi import UploadFile, File, Form, HTTPException
import os
import tempfile
from app.api.services.rag_service import RAGService

# Global service instance - starts as None, initialized on first use
_rag_service = None
_service_lock = None

def get_rag_service():
    """
    Lazy loading singleton for RAGService.
    Initializes only on first use, not on app startup.
    This prevents 502 errors from model loading timeouts on Render.
    """
    global _rag_service
    
    # If already initialized, return it
    if _rag_service is not None:
        return _rag_service
    
    # Initialize on first use
    print("[RAGService] Initializing on first API call...")
    _rag_service = RAGService()
    print("[RAGService] Successfully initialized and cached")
    return _rag_service

# Document Ingestion
async def ingest_document(file: UploadFile = File(...)):
    # Validate file type
    supported_types = {".pdf", ".txt", ".csv", ".xlsx", ".xls"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in supported_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Supported formats: PDF, TXT, CSV, XLSX, XLS"
        )
    
    # Create a temporary directory to store the file
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file.filename)

        # Write the uploaded file to ingest the document
        with open(file_path, "wb") as f:
            f.write(await file.read())

        try:
            # Call the service to ingest the document
            rag_service = get_rag_service()
            num_chunks = rag_service.ingest_document(file_path, file.filename)
            print("Number of Chunks: ", num_chunks)
            return {
                "message": "Document ingested successfully",
                "filename": file.filename,
                "chunks_ingested": num_chunks
            }
        except ValueError as ve:
            raise HTTPException(status_code=409, detail=f"Duplicate document: {str(ve)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

# Query Logic
async def get_query_response(query: str = Form(...), session_id: str = Form(...), document_name: str = Form(None)):
    """
    Handles a query from the user, calls the RAG service to generate an answer,
    and returns the answer along with source documents.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        rag_service = get_rag_service()
        answer = rag_service.generate_answer(query, session_id, document_name=document_name)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")


# Agent-based Query Logic
async def get_query_response_with_agents(query: str = Form(...), session_id: str = Form(...), document_name: str = Form(None)):
    """
    Handles a query using multi-agent reasoning pipeline.
    Uses Planner, Retriever, Reasoning, and Response agents.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        rag_service = get_rag_service()
        result = rag_service.generate_answer_with_agents(query, session_id, document_name=document_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer with agents: {str(e)}")

# Document Management Endpoints
async def get_documents():
    """Returns a list of all uploaded documents."""
    try:
        rag_service = get_rag_service()
        documents = rag_service.get_uploaded_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

async def delete_document(document_id: str):
    """Deletes a document by its ID."""
    try:
        rag_service = get_rag_service()
        rag_service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

# Chat Session Management Endpoints
async def create_new_chat_session():
    """Creates a new chat session and returns the session ID."""
    try:
        rag_service = get_rag_service()
        session_id = rag_service.start_new_session()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create new session: {str(e)}")

async def clear_chat_session_history(session_id: str):
    """Clears the chat history for a specific session."""
    try:
        rag_service = get_rag_service()
        rag_service.clear_session_history(session_id)
        return {"message": f"Chat history for session {session_id} cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear session history: {str(e)}")

async def get_all_sessions():
    """Returns a list of all sessions."""
    try:
        rag_service = get_rag_service()
        sessions = rag_service.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")

async def get_session_history(session_id: str):
    """Returns the chat history for a specific session."""
    try:
        rag_service = get_rag_service()
        history = rag_service.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")

async def save_message_to_session(session_id: str = Form(...), message: str = Form(...), role: str = Form(...)):
    """Saves a message to a session's chat history."""
    try:
        rag_service = get_rag_service()
        rag_service.add_message_to_session(session_id, role, message)
        return {"message": "Message saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")
