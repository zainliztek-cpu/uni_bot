# GenAI Document Assistant - Complete Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Agent Workflow](#agent-workflow)
3. [API Usage](#api-usage)
4. [Limitations and Assumptions](#limitations-and-assumptions)
5. [Security Considerations](#security-considerations)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Layer                                │
├─────────────────────────────────────────────────────────────────────┤
│  Frontend (Streamlit Cloud)                                         │
│  - Document Ingestion Page                                          │
│  - Chat Interface                                                   │
│  - Document Management                                              │
│  - Session History                                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS REST API
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                      API Layer (FastAPI)                            │
├─────────────────────────────────────────────────────────────────────┤
│  Render Container (Production)                                      │
│  - Route: /api/ingest                                               │
│  - Route: /api/query                                                │
│  - Route: /api/query/agents                                         │
│  - Route: /api/documents                                            │
│  - Route: /api/chat/sessions                                        │
│  - Route: /health-check                                             │
└────────────────────────┬────────────────────────────────────────────┘
                         │ In-Process
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                  Service Layer (RAGService)                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Document         │  │ Embedding        │  │ LLM Query        │  │
│  │ Processing       │  │ Generation       │  │ Generation       │  │
│  │ - PDF loader     │  │ - HuggingFace    │  │ - Groq LLM       │  │
│  │ - TXT loader     │  │   BAAI embedder  │  │ - Multi-agent    │  │
│  │ - CSV loader     │  │ - 1024 dims      │  │   orchestrator   │  │
│  │ - Excel loader   │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│           │                    │                      │             │
└───────────┼────────────────────┼──────────────────────┼─────────────┘
            │                    │                      │
┌───────────▼────────────────────▼──────────────────────▼─────────────┐
│                    Data Layer                                       │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Vector Store     │  │ Chat History     │  │ Document Meta    │  │
│  │ (ChromaDB)       │  │ (In-Memory)      │  │ (In-Memory)      │  │
│  │ - Documents      │  │ - Session ID → [ │  │ - Doc ID → Name  │  │
│  │ - Embeddings     │  │   Messages]      │  │ - Content Hash   │  │
│  │ - Metadata       │  │ - Role: user/ai  │  │ - Filename       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. **Frontend (Streamlit Cloud)**
- **Location**: `frontend/app.py`
- **Pages**:
  - `app.py` - Landing page with system info
  - `pages/Document_Ingestion.py` - Upload documents
  - `pages/Chat_with_your_document.py` - Query interface
- **Features**:
  - Real-time API communication
  - Session management
  - Multi-document chat
  - Response streaming

#### 2. **API Layer (FastAPI on Render)**
- **Location**: `main.py` + `app/api/`
- **Endpoints**:
  ```
  POST /api/ingest              - Upload document
  POST /api/query               - Simple RAG query
  POST /api/query/agents        - Multi-agent query
  GET  /api/documents           - List documents
  DELETE /api/documents/{id}    - Remove document
  POST /api/chat/new_session    - Create session
  GET  /api/chat/sessions       - List sessions
  GET  /api/chat/sessions/{id}  - Get chat history
  POST /api/chat/sessions/{id}/message - Save message
  DELETE /api/chat/clear_session/{id}  - Clear history
  GET  /health-check            - Server status
  GET  /api/debug/status        - Service status
  ```

#### 3. **RAG Service**
- **Location**: `app/api/services/rag_service.py`
- **Functions**:
  - Document ingestion & chunking
  - Embedding generation (HuggingFace)
  - Vector search (ChromaDB)
  - Answer generation (Groq LLM)
  - Session management
  - Duplicate detection

#### 4. **Agent Orchestrator**
- **Location**: `app/api/agents/agents.py`
- **Agents**:
  - `PlannerAgent` - Breaks down queries
  - `RetrieverAgent` - Fetches relevant docs
  - `ReasoningAgent` - Synthesizes information
  - `ResponseAgent` - Generates final answer

#### 5. **Data Storage**
- **ChromaDB**: Vector embeddings (persistent on Render disk)
- **In-Memory**: Chat history, document metadata, sessions
- **Limitation**: Data lost on Render restart (free tier)

---

## Agent Workflow

### Simple RAG Mode (Non-Agent)

```
User Query
    ↓
[1] Embed Query
    ├─ Convert text to 1024-dim vector
    ├─ Model: BAAI/bge-large-en-v1.5
    ↓
[2] Search Vector Store
    ├─ Find 4 most similar chunks
    ├─ Return with similarity scores
    ↓
[3] Create Prompt
    ├─ Add system context
    ├─ Add retrieved chunks
    ├─ Add user query
    ↓
[4] Generate Response
    ├─ Model: Groq llama-3.3-70b-versatile
    ├─ Temperature: 0.7
    ↓
[5] Save to Session History
    └─ Store user query + AI response
    
Response to User
```

### Multi-Agent Mode

```
User Query
    ↓
[1] PLANNER AGENT
    ├─ Analyze query: "What is document about?"
    ├─ Generate sub-questions:
    │  • "What are main topics?"
    │  • "What specific details needed?"
    │  • "What context required?"
    ↓
[2] RETRIEVER AGENT (Parallel for each sub-question)
    ├─ For each sub-question:
    │  ├─ Generate embedding
    │  ├─ Search vector DB (top-5 results)
    │  └─ Return ranked chunks
    ├─ Combine all results
    └─ De-duplicate similar chunks
    ↓
[3] REASONING AGENT
    ├─ Analyze retrieved chunks
    ├─ Identify relationships
    ├─ Build knowledge graph
    ├─ Determine key facts
    ├─ Assess answer confidence
    ↓
[4] RESPONSE AGENT
    ├─ Synthesize reasoning
    ├─ Generate comprehensive answer
    ├─ Add source attribution
    ├─ Format with confidence levels
    ↓
[5] Save to Session
    └─ Store full reasoning + response
    
Multi-Agent Response to User
```

### Document Processing Pipeline

```
Upload Document
    ↓
[1] Validate
    ├─ Check file type (.pdf, .txt, .csv, .xlsx, .xls)
    ├─ Check duplicate (content hash)
    ├─ Create temp directory
    ↓
[2] Load Content
    ├─ PDF → PyPDFLoader
    ├─ TXT → TextLoader
    ├─ CSV → CSVLoader
    └─ Excel → CSVLoader (via pandas)
    ↓
[3] Chunk Text
    ├─ Splitter: RecursiveCharacterTextSplitter
    ├─ Chunk size: 1000 chars
    ├─ Overlap: 200 chars
    ├─ Preserve structure
    ↓
[4] Generate Embeddings
    ├─ Model: BAAI/bge-large-en-v1.5
    ├─ Batch process chunks
    ├─ Generate 1024-dim vectors
    ↓
[5] Store in ChromaDB
    ├─ Insert embeddings
    ├─ Add chunk metadata
    ├─ Index for search
    ├─ Store document ID mapping
    ↓
[6] Return to User
    └─ Chunks ingested count
    
Document Ready for Queries
```

---

## API Usage

### Authentication
- No authentication required (public API)
- Frontend URL must be configured in backend for CORS

### Headers Required
```
Content-Type: application/json (for POST with JSON)
Content-Type: multipart/form-data (for file uploads)
```

### 1. Document Ingestion

**Endpoint**: `POST /api/ingest`

**Request**:
```bash
curl -X POST "https://backend.onrender.com/api/ingest" \
  -F "file=@document.pdf"
```

**Response (200 OK)**:
```json
{
  "message": "Document ingested successfully",
  "filename": "document.pdf",
  "chunks_ingested": 45
}
```

**Error Cases**:
- 400: Unsupported file type
- 409: Duplicate document
- 500: Processing error

---

### 2. Simple Query

**Endpoint**: `POST /api/query`

**Request**:
```bash
curl -X POST "https://backend.onrender.com/api/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What is the main topic?&session_id=abc123&document_name=document.pdf"
```

**Parameters**:
- `query` (string, required): Question to ask
- `session_id` (string, required): Chat session ID
- `document_name` (string, optional): Specific document to query

**Response (200 OK)**:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "text": "...",
      "similarity": 0.92,
      "source": "document.pdf - page 1"
    }
  ],
  "confidence": 0.85
}
```

---

### 3. Multi-Agent Query

**Endpoint**: `POST /api/query/agents`

**Request**:
```bash
curl -X POST "https://backend.onrender.com/api/query/agents" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=Complex question?&session_id=abc123"
```

**Response (200 OK)**:
```json
{
  "answer": "Comprehensive answer...",
  "reasoning": {
    "plan": ["Sub-question 1", "Sub-question 2"],
    "key_findings": ["Finding 1", "Finding 2"],
    "confidence": 0.88
  },
  "sources": [
    {
      "text": "...",
      "similarity": 0.95,
      "source": "document.pdf - section 2"
    }
  ]
}
```

---

### 4. Document Management

**List Documents**:
```bash
GET /api/documents
```

**Response**:
```json
{
  "documents": [
    {
      "id": "doc_1",
      "filename": "report.pdf",
      "chunks": 42,
      "uploaded": "2026-01-23T10:30:00Z"
    }
  ]
}
```

**Delete Document**:
```bash
DELETE /api/documents/{document_id}
```

---

### 5. Session Management

**Create Session**:
```bash
POST /api/chat/new_session
```

**Response**:
```json
{
  "session_id": "abc123def456"
}
```

**Get All Sessions**:
```bash
GET /api/chat/sessions
```

**Response**:
```json
{
  "sessions": [
    {
      "id": "abc123def456",
      "created": "2026-01-23T10:30:00Z",
      "message_count": 5
    }
  ]
}
```

**Get Session History**:
```bash
GET /api/chat/sessions/{session_id}
```

**Response**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is this about?",
      "timestamp": "2026-01-23T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "This is about...",
      "timestamp": "2026-01-23T10:30:05Z"
    }
  ]
}
```

**Save Message**:
```bash
POST /api/chat/sessions/{session_id}/message
  ?message=User message&role=user
```

**Clear Session**:
```bash
DELETE /api/chat/clear_session/{session_id}
```

---

### 6. Health & Status

**Health Check**:
```bash
GET /health-check
```

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.2",
  "environment": "production",
  "uptime_seconds": 3600,
  "note": "RAG service initializes on first API call"
}
```

**Debug Status** (check if models loaded):
```bash
GET /api/debug/status
```

**Response**:
```json
{
  "api_key_present": true,
  "llm_initialized": true,
  "embeddings_initialized": true,
  "vector_store_ready": true,
  "status": "ALL SYSTEMS OPERATIONAL",
  "error": null,
  "uptime_seconds": 600
}
```

---

## Limitations and Assumptions

### Limitations

#### 1. **Memory Constraints**
- **Render Free Tier**: 512MB RAM
- Single worker deployment (no parallel processing)
- In-memory session history lost on restart
- Max batch size for embeddings: 32

#### 2. **Storage**
- **ChromaDB**: Stored on Render ephemeral filesystem
- Data lost on restart (no persistent backup)
- Recommendation: Upgrade to Render Disk or use managed DB
- Max documents: Limited by available disk space (~1GB)

#### 3. **Model Constraints**
- **Embedding Model**: Fixed to BAAI/bge-large-en-v1.5 (1024 dims)
- **LLM**: Fixed to Groq llama-3.3-70b (no model switching)
- **Context Window**: ~4096 tokens (max document context)
- **Latency**: First request triggers model loading (5-10min cold start)

#### 4. **Processing**
- **File Size**: Recommended max 50MB per file
- **Chunk Size**: 1000 characters with 200 char overlap (fixed)
- **Max Chunks per Query**: 4 retrieved chunks
- **Query Timeout**: 600 seconds

#### 5. **Concurrent Users**
- Single worker = sequential processing
- No request queuing (requests may timeout)
- Recommended max: 5-10 concurrent users
- Production deployment needed for higher load

#### 6. **Features Not Supported**
- Real-time collaboration
- Document versioning
- User authentication
- Role-based access control
- Encryption at rest
- API rate limiting
- Request logging/monitoring

### Assumptions

#### 1. **Document Quality**
- Documents are in English
- Text is extractable (not scanned images)
- Content is relevant and well-structured
- No audio or video content

#### 2. **Query Assumptions**
- Questions are in English
- Queries are related to uploaded documents
- Expected answer is within document scope
- Queries are not adversarial

#### 3. **Data Assumptions**
- Users upload unique documents
- Sessions don't persist across deployments
- Document content doesn't change during session
- No versioning of documents

#### 4. **Performance Assumptions**
- Network latency: 100-500ms
- Model loading: 5-10 minutes (first request)
- Query processing: 5-30 seconds
- Embedding generation: 100ms per chunk

#### 5. **Usage Assumptions**
- Single user per session (no multi-user sessions)
- User completes one query before starting another
- Session lifetime: 24 hours (optional cleanup)
- Max documents per session: 50

---

## Security Considerations

### Current Security Posture

#### ✅ Implemented

1. **Environment Variables**
   - GROQ_API_KEY stored as environment variable (not in code)
   - API keys not committed to git
   - .gitignore prevents secret leakage

2. **CORS Configuration**
   - FastAPI CORS middleware can be configured
   - Prevents unauthorized domain access
   - Currently allows all origins (development mode)

3. **File Upload Validation**
   - File type whitelist (.pdf, .txt, .csv, .xlsx, .xls)
   - No arbitrary code execution
   - Temporary files deleted after processing

4. **Input Validation**
   - Query length limits
   - File size limits (recommended 50MB max)
   - Content type validation

---

#### ⚠️ Recommendations for Production

1. **Authentication & Authorization**
   ```python
   # Add JWT token validation
   from fastapi.security import HTTPBearer, HTTPAuthCredential
   
   security = HTTPBearer()
   
   @app.post("/api/query")
   async def query(request: Request, credentials: HTTPAuthCredential = Depends(security)):
       # Verify JWT token
       # Extract user ID
       # Validate permissions
   ```

2. **API Rate Limiting**
   ```python
   # Add slowapi rate limiter
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/query")
   @limiter.limit("10/minute")
   async def query(...):
       pass
   ```

3. **Data Encryption**
   - Use TLS 1.3 for transit
   - Encrypt sensitive data at rest
   - Hash user identifiers

4. **Logging & Monitoring**
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   
   # Log all API calls with user context
   # Don't log sensitive data (API keys, document content)
   # Monitor for anomalies
   ```

5. **Database Security**
   - Use managed PostgreSQL instead of SQLite
   - Enable encryption at rest
   - Restrict network access
   - Regular backups

6. **CORS Configuration** (Production)
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourfrontend.streamlit.app"],  # Specific domain
       allow_credentials=True,
       allow_methods=["GET", "POST", "DELETE"],
       allow_headers=["*"],
   )
   ```

7. **Secrets Management**
   - Use AWS Secrets Manager or similar
   - Rotate keys regularly
   - Never commit secrets
   - Use separate keys per environment

8. **Document Security**
   - Validate document source
   - Scan for malware
   - Implement document versioning
   - Access control per document

---

### Security Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| API Key Exposure | Unauthorized LLM usage | Store in env vars, rotate keys |
| Unauthorized Access | Data breach | Add JWT authentication |
| DDoS Attacks | Service unavailability | Rate limiting, load balancing |
| Document Injection | Malicious content | Input validation, content filtering |
| Memory Overflow | Service crash | Request size limits |
| Data Loss | Information lost | Regular backups, managed storage |
| Model Hijacking | Wrong responses | Validate API responses |
| SQL Injection | DB compromise | Use ORM, parameterized queries |

---

### Deployment Security Checklist

- [ ] GROQ_API_KEY set in production environment
- [ ] CORS restricted to known domains
- [ ] TLS certificate valid and updated
- [ ] Rate limiting configured
- [ ] Request logging enabled
- [ ] Error messages don't expose internals
- [ ] File upload validation enabled
- [ ] Database backups configured
- [ ] Security headers set (X-Frame-Options, CSP, etc.)
- [ ] Dependencies audited for vulnerabilities
- [ ] User authentication implemented
- [ ] Encryption at rest enabled
- [ ] Regular security scanning scheduled

---

### API Security Headers (Recommended)

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## Environment Variables Reference

### Required
```
GROQ_API_KEY=gsk_your_api_key_here
```

### Optional (with defaults)
```
CHROMA_DB_PATH=./chroma_data
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
LLM_MODEL=llama-3.3-70b-versatile
VECTOR_DIMENSION=1024
BACKEND_API_URL=http://localhost:8000 (frontend only)
```

---

## Troubleshooting

### Common Issues

**502 Bad Gateway**
- Check GROQ_API_KEY is set
- Verify backend has enough memory
- Check request timeout (should be 600s)

**Timeout on first request**
- Expected on Render free tier (cold start)
- Models need 5-10 minutes to load initially
- Subsequent requests should be faster

**Out of Memory**
- Single worker deployment limits requests
- Clear old sessions manually
- Consider upgrading to paid Render plan

**Documents not found**
- ChromaDB may have restarted (data lost)
- Re-upload documents if needed
- Consider persistent storage

---

**Last Updated**: January 23, 2026
**Version**: 1.0.2
