from fastapi import APIRouter, UploadFile, File, Form
from app.api import rag_api

# Creating an APIRouter instance
router = APIRouter()

# Define the endpoints
@router.post("/ingest", summary="Ingest a document (PDF, TXT, CSV, XLSX, XLS)")
async def ingest_endpoint(file: UploadFile = File(...)):
    return await rag_api.ingest_document(file)

@router.post("/query", summary="Query the ingested document using simple RAG")
async def query_endpoint(query: str = Form(...), session_id: str = Form(...), document_name: str = Form(None)):
    return await rag_api.get_query_response(query, session_id, document_name)

@router.post("/query/agents", summary="Query using multi-agent reasoning pipeline")
async def query_agents_endpoint(query: str = Form(...), session_id: str = Form(...), document_name: str = Form(None)):
    return await rag_api.get_query_response_with_agents(query, session_id, document_name)

@router.get("/documents", summary="Get list of all uploaded documents")
async def get_documents_endpoint():
    return await rag_api.get_documents()

@router.delete("/documents/{document_id}", summary="Delete a document by ID")
async def delete_document_endpoint(document_id: str):
    return await rag_api.delete_document(document_id)

@router.post("/chat/new_session", summary="Create a new chat session")
async def create_session_endpoint():
    return await rag_api.create_new_chat_session()

@router.get("/chat/sessions", summary="Get all sessions")
async def get_sessions_endpoint():
    return await rag_api.get_all_sessions()

@router.get("/chat/sessions/{session_id}", summary="Get chat history for a specific session")
async def get_session_history_endpoint(session_id: str):
    return await rag_api.get_session_history(session_id)

@router.post("/chat/sessions/{session_id}/message", summary="Save a message to session history")
async def save_message_endpoint(session_id: str, message: str = Form(...), role: str = Form(...)):
    return await rag_api.save_message_to_session(session_id, message, role)

@router.delete("/chat/clear_session/{session_id}", summary="Clear chat history for a session")
async def clear_session_endpoint(session_id: str):
    return await rag_api.clear_chat_session_history(session_id)
