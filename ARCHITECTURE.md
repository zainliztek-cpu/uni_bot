# Architecture Overview - GenAI Document Assistant

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Chat Page       │  │  Document Page   │                 │
│  ├──────────────────┤  ├──────────────────┤                 │
│  │ • Sessions       │  │ • Upload         │                 │
│  │ • Documents      │  │ • Validate       │                 │
│  │ • Queries        │  │ • Error Handle   │                 │
│  │ • Context Filter │  │ • Feedback       │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                               │
│  ┌──────────────────────────────────────────────┐            │
│  │    API Client (api_client.py)                │            │
│  ├──────────────────────────────────────────────┤            │
│  │ • send_query()          • create_new_session │            │
│  │ • send_query_with_agents()  • clear_session  │            │
│  │ • upload_document()     • get_documents      │            │
│  │ • delete_document()                          │            │
│  └──────────────────────────────────────────────┘            │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────┐            │
│  │    Router (rag_router.py)                    │            │
│  ├──────────────────────────────────────────────┤            │
│  │ POST   /api/ingest                           │            │
│  │ POST   /api/query                            │            │
│  │ POST   /api/query/agents                     │            │
│  │ GET    /api/documents                        │            │
│  │ DELETE /api/documents/{id}                   │            │
│  │ POST   /api/chat/new_session                 │            │
│  │ DELETE /api/chat/clear_session/{id}          │            │
│  └──────────────────────────────────────────────┘            │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────┐            │
│  │    API Handlers (rag_api.py)                 │            │
│  ├──────────────────────────────────────────────┤            │
│  │ • ingest_document()       • get_documents()  │            │
│  │ • get_query_response()    • delete_document()│            │
│  │ • get_query_response_with_agents()           │            │
│  │ • create_new_chat_session()                  │            │
│  │ • clear_chat_session_history()               │            │
│  └──────────────────────────────────────────────┘            │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────┐            │
│  │    RAG Service (rag_service.py)              │            │
│  ├──────────────────────────────────────────────┤            │
│  │ Core Methods:                                │            │
│  │ • ingest_document()                          │            │
│  │ • generate_answer()                          │            │
│  │ • generate_answer_with_agents()              │            │
│  │                                              │            │
│  │ Session Management:                          │            │
│  │ • start_new_session()                        │            │
│  │ • clear_session_history()                    │            │
│  │                                              │            │
│  │ Document Management:                         │            │
│  │ • get_uploaded_documents()                   │            │
│  │ • delete_document()                          │            │
│  │ • _load_existing_document_metadata()         │            │
│  │                                              │            │
│  │ Storage:                                     │            │
│  │ • chat_history (defaultdict)                 │            │
│  │ • document_metadata (dict)                   │            │
│  │ • content_hashes (dict)                      │            │
│  └──────────────────────────────────────────────┘            │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │ ChromaDB   │   │ LangChain  │   │ Groq LLM   │
    │ (Vector    │   │ (Processing│   │ (Inference)│
    │  Store)    │   │  & Agents) │   │            │
    └────────────┘   └────────────┘   └────────────┘
```

---

## Data Flow Diagrams

### 1. Document Upload with Duplicate Prevention Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User Uploads Document (Frontend)                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ API Client: upload_document()                               │
│ POST /api/ingest (file)                                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend: ingest_document()                                  │
│ • Validate file type                                        │
│ • Store in temporary directory                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ RAGService: ingest_document(file_path, filename)            │
│ • Load document by type (PDF/TXT/CSV/XLSX)                  │
│ • Split into chunks (500 chars, 50 overlap)                 │
│ • Calculate SHA-256 content hash                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Hash Check   │
                    └──────────────┘
                      /         \
                    YES          NO
                    /               \
                   ▼                 ▼
            ┌──────────────┐  ┌──────────────┐
            │REJECT (409)  │  │ PROCEED      │
            │Duplicate     │  │              │
            └──────────────┘  └──────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ • Create unique doc_id       │
                    │ • Add metadata to chunks     │
                    │ • Store in ChromaDB          │
                    │ • Store in document_metadata │
                    │ • Store in content_hashes    │
                    └──────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ Return Success (200)         │
                    │ • filename                   │
                    │ • chunks_ingested count      │
                    └──────────────────────────────┘
```

### 2. Session-Based Query Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User Query with Session & Document Context (Frontend)       │
│ • query: "What is the main point?"                          │
│ • session_id: "abc-123-def"                                 │
│ • document_name: "report.pdf" (optional)                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ API Client: send_query() / send_query_with_agents()         │
│ POST /api/query (with session_id & document_name)           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend: get_query_response()                               │
│ • Extract query, session_id, document_name                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ RAGService: generate_answer()                               │
│ • Check if document_name provided                           │
└─────────────────────────────────────────────────────────────┘
                           │
                    ┌──────────────┐
                    │ Filter?      │
                    └──────────────┘
                      /         \
                    YES          NO
                    /               \
                   ▼                 ▼
        ┌──────────────────────┐ ┌─────────────────────┐
        │ Filter Query:        │ │ Search All:         │
        │ metadata={           │ │ similarity_search   │
        │  "filename":         │ │ (query, k=4)        │
        │  document_name       │ │                     │
        │ }                    │ └─────────────────────┘
        └──────────────────────┘
                   \               /
                    \             /
                     ▼           ▼
                    ┌──────────────────────────────┐
                    │ Retrieve k=4 chunks          │
                    │ with similarity scores       │
                    └──────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ Build context from chunks    │
                    │ Construct LLM prompt         │
                    └──────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ Generate Answer with Groq    │
                    │ temperature=0.7              │
                    └──────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ Track in chat_history        │
                    │ [session_id] = [messages]    │
                    └──────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │ Return Answer to Frontend    │
                    │ {"answer": "The main..."}    │
                    └──────────────────────────────┘
```

### 3. Session Management Flow

```
New Session Creation:
┌──────────────────────┐
│ Click "Start New     │
│ Session" (Frontend)  │
└──────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ API: create_new_session()        │
│ POST /api/chat/new_session       │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ RAGService.start_new_session()   │
│ • Generate UUID session_id       │
│ • Initialize empty chat_history  │
│ • Store in memory                │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Return session_id to Frontend    │
│ Store in session_state           │
└──────────────────────────────────┘


Clear Session:
┌──────────────────────────────────┐
│ Click "Clear Chat History"       │
│ (Frontend, current session_id)   │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ API: clear_session_history()     │
│ DELETE /api/chat/clear_session   │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ RAGService.clear_session_history │
│ • Clear chat_history[session_id] │
│ • Preserve session_id            │
└──────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Confirm to Frontend              │
│ Refresh chat messages            │
└──────────────────────────────────┘
```

---

## Database Schema

### ChromaDB Collection Structure

```
Collection: "documents"

Each chunk document:
{
  "id": "auto-generated-by-chroma",
  "embedding": [vector array],
  "metadatas": {
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "report.pdf",
    "content_hash": "sha256_hash_here",
    "source": "/path/to/file",
    "row": 0
  },
  "documents": "chunk text content...",
  "uris": null,
  "data": null
}
```

### In-Memory Storage (RAGService)

```python
# Session-based chat history
chat_history: {
  "session-id-1": [
    {"role": "user", "content": "Question 1"},
    {"role": "assistant", "content": "Answer 1"},
    ...
  ],
  "session-id-2": [...]
}

# Document metadata tracking
document_metadata: {
  "doc-uuid-1": {
    "filename": "report.pdf",
    "content_hash": "sha256_hash"
  },
  "doc-uuid-2": {...}
}

# Content hash → filename mapping for duplicate detection
content_hashes: {
  "sha256_hash": "report.pdf",
  ...
}
```

---

## API Endpoints Summary

### Document Management
```
POST   /api/ingest
       Upload and ingest a new document
       Returns: {filename, chunks_ingested, message}

GET    /api/documents
       List all uploaded documents
       Returns: {documents: [{id, filename}, ...]}

DELETE /api/documents/{document_id}
       Delete a document by ID
       Returns: {message: "Document deleted"}
```

### Query Processing
```
POST   /api/query
       Simple RAG query with session and document filtering
       Params: query, session_id, document_name (optional)
       Returns: {answer: "..."}

POST   /api/query/agents
       Multi-agent reasoning query
       Params: query, session_id, document_name (optional)
       Returns: {answer: "...", plan: "...", reasoning: "..."}
```

### Session Management
```
POST   /api/chat/new_session
       Create a new chat session
       Returns: {session_id: "uuid"}

DELETE /api/chat/clear_session/{session_id}
       Clear chat history for a session
       Returns: {message: "Chat history cleared"}
```

---

## Key Components

### Frontend Components
- **Chat Page**: Session management, document filtering, query interface
- **Document Ingestion**: Upload, validation, duplicate detection
- **API Client**: Communication with backend, error handling

### Backend Components
- **RAGService**: Core business logic, document and session management
- **API Handlers**: HTTP request processing
- **Router**: Endpoint definitions and routing

### External Services
- **ChromaDB**: Vector storage and retrieval
- **LangChain**: Document loading, text splitting, agent orchestration
- **Groq**: LLM for answer generation
- **HuggingFace**: Embeddings generation

---

## Error Handling Strategy

```
HTTP Status Codes:
├─ 200 OK: Successful operation
├─ 400 Bad Request: Invalid input (empty query, unsupported file)
├─ 404 Not Found: Document not found (delete non-existent doc)
├─ 409 Conflict: Duplicate document detected
└─ 500 Internal Server Error: Unexpected server errors

Frontend Feedback:
├─ Success: Green checkmark with confirmation message
├─ Warning: Yellow alert with guidance
├─ Error: Red error box with reason and suggestions
└─ Info: Blue info box with additional context
```

---

## Performance Considerations

### Optimization Points
1. **Duplicate Detection**: O(1) hash lookup instead of full content comparison
2. **Document Filtering**: Metadata-based filtering reduces search space
3. **Session Tracking**: In-memory storage for fast access
4. **Chunk Caching**: ChromaDB handles caching
5. **Lazy Loading**: Documents loaded only when needed

### Scalability Limitations (Current)
- In-memory storage: Session data lost on restart
- No distributed caching: Single instance only
- No batch operations: One document at a time
- Linear metadata loading: All documents loaded on startup

---

**Architecture Version**: 1.0
**Last Updated**: January 22, 2026
