import streamlit as st
from services.api_client import upload_document
import time

# Page Configuration
st.set_page_config(
    page_title="Document Ingestion | GenAI Assistant",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
    }
    
    h2 {
        color: #2c3e50;
        margin-top: 2rem;
    }
    
    .upload-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1.5rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-text {
        background: #050329;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1> Document Ingestion</h1>", unsafe_allow_html=True)

# Information Box
st.markdown("""
    <div class='info-text'>
    <strong>ℹ️ How it works:</strong> Upload your documents, and our system will process them, 
    extract text, split into semantic chunks, and store in a vector database for intelligent retrieval.
    </div>
""", unsafe_allow_html=True)

# Two Column Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Upload Your Document")
    
    # Supported Formats Info
    st.markdown("""
    **Supported Formats:**
    - **PDF** - Portable Document Format
    - **TXT** - Plain Text Files
    - **CSV** - Comma-Separated Values
    - **XLSX/XLS** - Microsoft Excel
    """)
    
    # File Uploader with drag-and-drop
    uploaded_file = st.file_uploader(
        "Drag and drop your file here or click to browse",
        type=["pdf", "txt", "csv", "xlsx", "xls"],
        help="Maximum file size: 200MB",
        accept_multiple_files=False
    )

with col2:
    st.markdown("### File Info")
    if uploaded_file is not None:
        file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
        st.info(f"""
        **File Details:**
        - Name: {uploaded_file.name}
        - Type: {uploaded_file.type}
        - Size: {file_size:.2f} MB
        """)

# File Upload Processing
if uploaded_file is not None:
    st.markdown("---")
    
    # Processing Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Processing Document...")
    with col2:
        if st.button("Upload & Process", use_container_width=True):
            with st.spinner("Processing your document... This may take a moment."):
                # Add delay for visual effect
                progress_bar = st.progress(0)
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time.sleep(0.01)
                
                # Call the API client function to upload the document
                response = upload_document(uploaded_file)
                
                # Display Results
                if response:
                    st.success("Document Processed Successfully!")
                    
                    # Success Information Box
                    st.markdown(f"""
                    <div class='success-box'>
                    <h3>Ingestion Summary</h3>
                    <p><strong>File:</strong> {response.get('filename')}</p>
                    <p><strong>Chunks Created:</strong> <span style='font-size: 1.5rem; color: #0d47a1;'>{response.get('chunks_ingested')}</span></p>
                    <p><strong>Status:</strong> {response.get('message')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Next Steps
                    st.markdown("""
                    ### Next Steps
                    1. Go to **Chat with your Document** page
                    2. Ask questions about your document
                    3. Get intelligent, context-aware answers
                    """)
                elif response is None:
                    st.error("Upload Failed")
                    st.error("There was an error uploading your document. Please check:")
                    st.markdown("""
                    - File format is supported (PDF, TXT, CSV, XLSX, XLS)
                    - File is not corrupted
                    - Backend server is running
                    - Try with a smaller file
                    """)
                else:
                    # Check if it's a duplicate error
                    if "duplicate" in str(response).lower() or "same content" in str(response).lower():
                        st.warning("Document Already Exists")
                        st.warning("A document with the same content has already been uploaded. To avoid duplication, the system rejected this upload.")
                        st.info("Go to **Chat with your Document** to see all uploaded documents.")
                    else:
                        st.error("Upload Failed")
                        st.error(f"Error: {response}")

# Tips Section
st.markdown("---")
st.markdown("### Tips for Best Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **PDF Files**
    - Clear, readable text
    - Avoid scanned images
    - Well-structured format
    """)

with col2:
    st.markdown("""
    **Text Files**
    - Plain UTF-8 encoding
    - Clear sections
    - Descriptive content
    """)

with col3:
    st.markdown("""
    **Data Files**
    - Consistent formatting
    - Column headers
    - Meaningful values
    """)
