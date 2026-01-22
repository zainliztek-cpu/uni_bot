import streamlit as st
from services.api_client import send_query, send_query_with_agents, get_uploaded_documents, delete_document, create_new_session, clear_session_history, get_all_sessions, get_session_history, save_message_to_session
import json

# Page Configuration
st.set_page_config(
    page_title="Chat with your Document | GenAI Assistant",
    layout="wide"
)

# Custom CSS for chat interface
st.markdown("""
    <style>
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
    }
    
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-left: 5%;
        width: 95%;
        text-align: right;
    }
    
    .assistant-message {
        background: #f0f7ff;
        color: #2c3e50;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-right: 5%;
        width: 95%;
        border-left: 4px solid #1f77b4;
    }
    
    .reasoning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .mode-selector {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>Chat with Your Document</h1>", unsafe_allow_html=True)

st.markdown("""
Ask any question about the documents you've uploaded. The AI will search through your 
documents and provide intelligent, grounded answers.
""")

# Session State Initialization (MUST be before any references)
if "session_id" not in st.session_state:
    response = create_new_session()
    if response and "session_id" in response:
        st.session_state.session_id = response["session_id"]
    else:
        st.session_state.session_id = "default_session"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your AI document assistant. Upload a document and ask me anything about it!",
            "type": "normal"
        }
    ]

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if "show_sessions" not in st.session_state:
    st.session_state.show_sessions = False

# Session and Document Management Section
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Session Management")
    
    # Session Controls
    session_col1, session_col2, session_col3 = st.columns([1, 1, 1])
    
    with session_col1:
        if st.button("New Session"):
            response = create_new_session()
            if response and "session_id" in response:
                st.session_state.session_id = response["session_id"]
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "New session started! Ready to chat.",
                        "type": "normal"
                    }
                ]
                st.success(f"New session created!")
                st.rerun()
    
    with session_col2:
        if st.button("All Sessions"):
            st.session_state.show_sessions = not st.session_state.show_sessions
            st.rerun()
    
    with session_col3:
        if st.button("Clear Chat"):
            clear_session_history(st.session_state.session_id)
            st.session_state.messages = []
            st.success("Chat history cleared!")
            st.rerun()
    
    st.info(f"Current Session: {st.session_state.session_id[:12]}...")
    
    # Show sessions list if toggled
    if st.session_state.show_sessions:
        st.subheader("Switch Sessions")
        sessions_response = get_all_sessions()
        if sessions_response and "sessions" in sessions_response:
            sessions = sessions_response["sessions"]
            if sessions:
                for session in sessions:
                    sess_id = session["session_id"]
                    msg_count = session["message_count"]
                    last_accessed = session["last_accessed"][:10] if session["last_accessed"] else "Unknown"
                    
                    col_select, col_info = st.columns([2, 2])
                    with col_select:
                        if st.button(f"{sess_id[:8]}... ({msg_count} messages)", key=f"session_{sess_id}"):
                            # Switch to this session
                            st.session_state.session_id = sess_id
                            history_response = get_session_history(sess_id)
                            if history_response and "history" in history_response:
                                st.session_state.messages = history_response["history"]
                            st.success(f"Switched to session: {sess_id[:12]}...")
                            st.rerun()
                    with col_info:
                        st.caption(f"Last: {last_accessed}")
            else:
                st.info("No previous sessions found.")
        else:
            st.warning("Could not fetch sessions.")

with col2:
    st.subheader("Uploaded Documents")
    
    # Refresh documents
    if st.button("Refresh Documents"):
        st.rerun()
    
    # Get documents
    docs_response = get_uploaded_documents()
    if docs_response and "documents" in docs_response:
        documents = docs_response["documents"]
        if documents:
            st.info(f"Total documents: {len(documents)}")
            
            # Select document for filtering
            doc_names = [doc["filename"] for doc in documents]
            selected_doc = st.selectbox(
                "Filter queries by document (optional):",
                ["All Documents"] + doc_names,
                key="document_filter"
            )
            
            if selected_doc != "All Documents":
                st.session_state.selected_document = selected_doc
            else:
                st.session_state.selected_document = None
            
            # Show document management section in expander
            with st.expander("Manage Documents"):
                for doc in documents:
                    col_name, col_delete = st.columns([3, 1])
                    with col_name:
                        st.text(f"{doc['filename']}")
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{doc['id']}"):
                            delete_document(doc["id"])
                            st.success(f"Deleted: {doc['filename']}")
                            st.rerun()
        else:
            st.warning("No documents uploaded yet. Please upload a document first!")
    else:
        st.warning("Could not fetch documents. Check if the server is running.")

st.markdown("---")

# Query Mode Selection
st.markdown("### Select Query Mode")
col1, col2 = st.columns(2)

# 1. Define your variables first
session_id = st.session_state.session_id
document_name = st.session_state.selected_document

# 2. Use the columns
with col1:
    simple_rag = st.checkbox(
        "📊 Simple RAG Mode", 
        value=True, 
        help=f"Fast, direct answers for {document_name}"
    )

with col2:
    agent_mode = st.checkbox(
        "🧠 Multi-Agent Reasoning", 
        value=False, 
        help="Detailed analysis with planning and reasoning"
    )

if simple_rag and agent_mode:
    st.warning("Select only one mode at a time")
    simple_rag = False
    agent_mode = False

# Display Chat History
st.markdown("### Conversation")
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        if message.get("type") == "agent_reasoning":
            # Display reasoning details
            st.markdown(f"<div class='assistant-message'><strong>🤖 Assistant (Multi-Agent Mode):</strong><br>{message['content']}</div>", unsafe_allow_html=True)
            if "reasoning" in message:
                with st.expander("📊 View Reasoning Details"):
                    st.write(message.get("reasoning", ""))
        else:
            st.markdown(f"<div class='assistant-message'><strong> Assistant:</strong><br>{message['content']}</div>", unsafe_allow_html=True)

# Chat Input
st.markdown("---")
st.markdown("### Send Your Question")

user_query = st.chat_input(
    "Ask a question about your document...",
    key="chat_input"
)

if user_query and user_query.strip():
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })
    # Save user message to backend session
    save_message_to_session(st.session_state.session_id, "user", user_query)
    st.session_state.query_count += 1
    
    # Display user message immediately
    st.markdown(f"<div class='user-message'><strong>You:</strong> {user_query}</div>", unsafe_allow_html=True)
    
    # Get assistant's response
    with st.spinner("Thinking..."):
        try:
            if agent_mode:
                # Multi-agent reasoning
                response = send_query_with_agents(user_query, session_id=st.session_state.session_id, document_name=st.session_state.selected_document)
                
                if response:
                    answer = response.get("answer", "No response")
                    reasoning = response.get("reasoning", "")
                    
                    st.markdown(f"<div class='assistant-message'><strong> Assistant (Multi-Agent):</strong><br>{answer}</div>", unsafe_allow_html=True)
                    
                    # Show reasoning in expander
                    with st.expander("View Analysis & Reasoning"):
                        if response.get("plan"):
                            st.subheader("Planning Phase")
                            st.write(response.get("plan"))
                        if reasoning:
                            st.subheader("Reasoning Phase")
                            st.write(reasoning)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "reasoning": reasoning,
                        "type": "agent_reasoning"
                    })
                    # Save assistant message to backend session
                    save_message_to_session(st.session_state.session_id, "assistant", answer)
                else:
                    error_msg = "Could not get a response from the agent. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "type": "normal"
                    })
                    save_message_to_session(st.session_state.session_id, "assistant", error_msg)
            else:
                # Simple RAG mode
                response = send_query(user_query, session_id=st.session_state.session_id, document_name=st.session_state.selected_document)
                
                if response and "answer" in response:
                    answer = response["answer"]
                    st.markdown(f"<div class='assistant-message'><strong> Assistant:</strong><br>{answer}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "type": "normal"
                    })
                    # Save assistant message to backend session
                    save_message_to_session(st.session_state.session_id, "assistant", answer)
                else:
                    error_msg = "Sorry, I could not get a response. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "type": "normal"
                    })
                    save_message_to_session(st.session_state.session_id, "assistant", error_msg)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "type": "normal"
            })

# Sidebar with Statistics and Help
with st.sidebar:
    # st.markdown("### Chat Statistics")
    # st.metric("Total Queries", st.session_state.query_count)
    # st.metric("Messages in Chat", len(st.session_state.messages))
    
    st.markdown("---")
    
    st.markdown("### How to Use")
    st.markdown("""
    1. **Upload Document**: Go to Document Ingestion page
    2. **Ask Questions**: Type your question in the chat
    3. **Choose Mode**:
       - **Simple RAG**: Fast answers
       - **Multi-Agent**: Detailed reasoning
    4. **View Details**: Expand boxes for more info
    """)
    
    st.markdown("---")
    
    st.markdown("### Query Tips")
    st.markdown("""
    -  Be specific in your questions
    -  Ask about document content
    -  Use clear language
    -  Avoid very broad questions
    -  Don't expect external knowledge
    """)
    
    st.markdown("---")
    
    # Clear Chat Button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Chat cleared! Start fresh with a new question.",
                "type": "normal"
            }
        ]
        st.session_state.query_count = 0
        st.rerun()
