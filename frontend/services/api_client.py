import requests
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the base URL of FastAPI backend
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000") + "/api"

def upload_document(file):
    """
    Sends a file to the backend's /ingest endpoint.
    Returns the JSON response from the backend if successful, None otherwise.
    """
    ingest_url = f"{BACKEND_URL}/ingest"
    files = {'file': (file.name, file.getvalue(), file.type)}

    try:
        response = requests.post(ingest_url, files=files, timeout=300)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out. The file may be too large. Please try a smaller file.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f" Could not connect to backend. Ensure the server is running at {BACKEND_URL.replace('/api', '')}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred during file upload: {e}")
        return None

def send_query(query_text, session_id=None, document_name=None):
    """
    Sends a query to the backend's /query endpoint (simple RAG mode).
    Returns the JSON response from the backend if successful, None otherwise.
    """
    query_url = f"{BACKEND_URL}/query"
    payload = {'query': query_text}
    
    if session_id:
        payload['session_id'] = session_id
    if document_name:
        payload['document_name'] = document_name

    try:
        response = requests.post(query_url, data=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out. The query took too long. Please try a simpler question.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while sending the query: {e}")
        return None

def send_query_with_agents(query_text, session_id=None, document_name=None):
    """
    Sends a query to the backend's /query/agents endpoint (multi-agent reasoning mode).
    Returns the JSON response from the backend if successful, None otherwise.
    """
    query_url = f"{BACKEND_URL}/query/agents"
    payload = {'query': query_text}
    
    if session_id:
        payload['session_id'] = session_id
    if document_name:
        payload['document_name'] = document_name

    try:
        response = requests.post(query_url, data=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Multi-agent reasoning timed out. This mode requires more processing time. Try simple RAG mode.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred during multi-agent reasoning: {e}")
        return None

def health_check():
    """
    Checks the health of the backend API.
    Returns the JSON response from the backend if successful, None otherwise.
    """
    health_url = f"{BACKEND_URL.replace('/api', '')}/health"

    try:
        response = requests.get(health_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred during health check: {e}")
        return None
def get_uploaded_documents():
    """
    Retrieves the list of uploaded documents from the backend.
    Returns a list of documents with their IDs and filenames.
    """
    documents_url = f"{BACKEND_URL}/documents"
    
    try:
        response = requests.get(documents_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out while fetching documents.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while fetching documents: {e}")
        return None

def delete_document(document_id):
    """
    Deletes a document from the backend.
    Returns the JSON response from the backend if successful, None otherwise.
    """
    delete_url = f"{BACKEND_URL}/documents/{document_id}"
    
    try:
        response = requests.delete(delete_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out while deleting document.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while deleting the document: {e}")
        return None

def create_new_session():
    """
    Creates a new chat session in the backend.
    Returns the session_id if successful, None otherwise.
    """
    session_url = f"{BACKEND_URL}/chat/new_session"
    
    try:
        response = requests.post(session_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out while creating a new session.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while creating a new session: {e}")
        return None

def clear_session_history(session_id):
    """
    Clears the chat history for a specific session.
    Returns the JSON response from the backend if successful, None otherwise.
    """
    clear_url = f"{BACKEND_URL}/chat/clear_session/{session_id}"
    
    try:
        response = requests.delete(clear_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out while clearing session history.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while clearing session history: {e}")
        return None

def get_all_sessions():
    """
    Retrieves a list of all sessions from the backend.
    Returns sessions list if successful, None otherwise.
    """
    sessions_url = f"{BACKEND_URL}/chat/sessions"
    
    try:
        response = requests.get(sessions_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out while fetching sessions.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while fetching sessions: {e}")
        return None

def get_session_history(session_id):
    """
    Retrieves the chat history for a specific session.
    Returns the session history if successful, None otherwise.
    """
    history_url = f"{BACKEND_URL}/chat/sessions/{session_id}"
    
    try:
        response = requests.get(history_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(" Request timed out while fetching session history.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(" Could not connect to backend. Ensure the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f" An error occurred while fetching session history: {e}")
        return None

def save_message_to_session(session_id, role, content):
    """
    Saves a message to a session's chat history.
    Returns the response if successful, None otherwise.
    """
    save_url = f"{BACKEND_URL}/chat/sessions/{session_id}/message"
    payload = {
        'role': role,
        'message': content
    }
    
    try:
        response = requests.post(save_url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        # Silent fail for message saving to avoid disrupting user
        return None
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.RequestException:
        return None