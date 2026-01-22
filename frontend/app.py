import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment or use default
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Page Configuration with custom theme
st.set_page_config(
    page_title="GenAI Doc Assistant | RAG-Bot",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com",
        'About': "GenAI Document Assistant using RAG"
    }
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main background */
    .main {
        padding-top: 2rem;
    }
    
    /* Title styling */
    h1 {
        color: #1f77b4;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    /* Custom container styling */
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #0d47a1;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1> GenAI Doc Assistant</h1>", unsafe_allow_html=True)

# Subtitle
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;'>
        <p><strong>Intelligent Retrieval-Augmented Generation (RAG) System</strong></p>
        <p>Chat with your documents using advanced AI and vector search</p>
    </div>
""", unsafe_allow_html=True)

# Main content with columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-box'>
        <h3> Document Processing</h3>
        <ul>
            <li>Support for PDF, TXT, CSV, Excel files</li>
            <li>Intelligent text chunking & embedding</li>
            <li>Vector database storage (ChromaDB)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <h3> AI-Powered Retrieval</h3>
        <ul>
            <li>Semantic similarity search</li>
            <li>Context-aware responses</li>
            <li>Multi-agent reasoning</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-box' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
        <h3> Interactive Chat</h3>
        <ul>
            <li>Real-time conversation interface</li>
            <li>Conversation history</li>
            <li>Intelligent answer generation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
        <h3> Advanced Features</h3>
        <ul>
            <li>Simple RAG mode</li>
            <li>Multi-agent reasoning</li>
            <li>Source attribution</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Divider
st.markdown("---")

# Getting Started Section
st.markdown("<h2> Getting Started</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### Step 1: Upload Document
    Navigate to the **Document Ingestion** page and upload your document. Supported formats include PDF, TXT, CSV, and Excel files.
    """)

with col2:
    st.markdown("""
    #### Step 2: Ask Questions
    Go to **Chat with your Document** to start asking questions about your uploaded documents.
    """)

with col3:
    st.markdown("""
    #### Step 3: Get Answers
    Receive intelligent, context-aware answers powered by AI and semantic search.
    """)

# Health Check
st.markdown("---")
st.markdown("<h2> System Status</h2>", unsafe_allow_html=True)

try:
    response = requests.get(f"{API_BASE_URL}", timeout=2)
    if response.status_code == 200:
        st.success(" Backend API is running and healthy")
    else:
        st.warning(" Backend API responded with status: " + str(response.status_code))
except Exception as e:
    st.error(" Backend API is not accessible. Please ensure the server is running.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 0.9rem; margin-top: 2rem;'>
        <p>GenAI Document Assistant v1.0 | Built with Streamlit, LangChain & Groq</p>
    </div>
""", unsafe_allow_html=True)

st.title("FastAPI Health Monitor")

if st.button("Check API Status"):
    try:
        API_URL = f"{API_BASE_URL}/health-check"
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            # Highlighting the result for a non-tech user
            st.success(" Everything is working perfectly! You can start using the app.")
        else:
            st.error(f"API returned an error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Is your FastAPI server running?")
