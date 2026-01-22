from fastapi import UploadFile, File, Form, HTTPException
import os
import tempfile
import traceback
import logging
from app.api.services.rag_service import RAGService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instance
_rag_service = None

def get_rag_service():
    global _rag_service
    if _rag_service is None:
        try:
            logger.info("Initializing RAG Service...")
            _rag_service = RAGService()
            logger.info("RAG Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Service initialization failed: {str(e)}. Check GROQ_API_KEY is set."
            )
    return _rag_service

# Document Ingestion
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the RAG system."""
    try:
        logger.info(f"Starting document ingestion for: {file.filename}")
        
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
            logger.info(f"Writing file to temporary location: {file_path}")
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
                logger.info(f"File written successfully, size: {len(content)} bytes")

            try:
                # Call the service to ingest the document
                logger.info("Getting RAG service instance...")
                rag_service = get_rag_service()
                logger.info("Calling ingest_document on RAG service...")
                num_chunks = rag_service.ingest_document(file_path, file.filename)
                logger.info(f"Document ingested successfully with {num_chunks} chunks")
                
                return {
                    "message": "Document ingested successfully",
                    "filename": file.filename,
                    "chunks_ingested": num_chunks
                }
            except ValueError as ve:
                logger.warning(f"Duplicate document detected: {str(ve)}")
                raise HTTPException(status_code=409, detail=f"Duplicate document: {str(ve)}")
            except Exception as e:
                logger.error(f"Error during document ingestion: {str(e)}")
                logger.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ingest_document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Query Logic
async def get_query_response(query: str = Form(...), session_id: str = Form(...), document_name: str = Form(None)):
    """
    Handles a query from the user, calls the RAG service to generate an answer,
    and returns the answer along with source documents.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        logger.info(f"Received query: {query}")
        rag_service = get_rag_service()
        logger.info("Calling generate_answer on RAG service...")
        answer = rag_service.generate_answer(query, session_id, document_name=document_name)
        logger.info("Query answered successfully")
        return answer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")


# Agent-based Query Logic
async def get_query_response_with_agents(query: str = Form(...), session_id: str = Form(...), document_name: str = Form(None)):
    """
    Handles a query using multi-agent reasoning pipeline.
    Uses Planner, Retriever, Reasoning, and Response agents.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        logger.info(f"Received agent-based query: {query}")
        rag_service = get_rag_service()
        logger.info("Calling generate_answer_with_agents on RAG service...")
        result = rag_service.generate_answer_with_agents(query, session_id, document_name=document_name)
        logger.info("Agent query answered successfully")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating agent answer: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate answer with agents: {str(e)}")

# Document Management Endpoints
async def get_documents():
    """Returns a list of all uploaded documents."""
    try:
        logger.info("Fetching uploaded documents...")
        rag_service = get_rag_service()
        documents = rag_service.get_uploaded_documents()
        logger.info(f"Retrieved {len(documents)} documents")
        return {"documents": documents}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

async def delete_document(document_id: str):
    """Deletes a document by its ID."""
    try:
        logger.info(f"Deleting document: {document_id}")
        rag_service = get_rag_service()
        rag_service.delete_document(document_id)
        logger.info(f"Document deleted successfully: {document_id}")
        return {"message": f"Document {document_id} deleted successfully"}
    except ValueError as ve:
        logger.warning(f"Document not found: {document_id}")
        raise HTTPException(status_code=404, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

# Chat Session Management Endpoints
async def create_new_chat_session():
    """Creates a new chat session and returns the session ID."""
    try:
        logger.info("Creating new chat session...")
        rag_service = get_rag_service()
        session_id = rag_service.start_new_session()
        logger.info(f"Chat session created: {session_id}")
        return {"session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create new session: {str(e)}")

async def clear_chat_session_history(session_id: str):
    """Clears the chat history for a specific session."""
    try:
        logger.info(f"Clearing chat history for session: {session_id}")
        rag_service = get_rag_service()
        rag_service.clear_session_history(session_id)
        logger.info(f"Chat history cleared for session: {session_id}")
        return {"message": f"Chat history for session {session_id} cleared"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session history: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to clear session history: {str(e)}")

async def get_all_sessions():
    """Returns a list of all sessions."""
    try:
        logger.info("Fetching all sessions...")
        rag_service = get_rag_service()
        sessions = rag_service.get_all_sessions()
        logger.info(f"Retrieved {len(sessions)} sessions")
        return {"sessions": sessions}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")

async def get_session_history(session_id: str):
    """Returns the chat history for a specific session."""
    try:
        logger.info(f"Fetching history for session: {session_id}")
        rag_service = get_rag_service()
        history = rag_service.get_session_history(session_id)
        logger.info(f"Retrieved {len(history)} messages for session: {session_id}")
        return {"session_id": session_id, "history": history}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session history: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")

async def save_message_to_session(session_id: str = Form(...), message: str = Form(...), role: str = Form(...)):
    """Saves a message to a session's chat history."""
    try:
        logger.info(f"Saving message to session: {session_id}, role: {role}")
        rag_service = get_rag_service()
        rag_service.add_message_to_session(session_id, role, message)
        logger.info(f"Message saved to session: {session_id}")
        return {"message": "Message saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving message: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")
