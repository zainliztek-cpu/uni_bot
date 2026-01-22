# GenAI Doc Assistant - Usage Guide

## Quick Start

### Running the Application

#### Backend (FastAPI)
```bash
cd D:/repo_uni_bot/genai-Capstone-doc-Assistant
python main.py
```

#### Frontend (Streamlit)
```bash
cd D:/repo_uni_bot/genai-Capstone-doc-Assistant/frontend
streamlit run app.py
```

---

## Feature Usage Examples

### 1. Session Management

#### Starting a New Session
```python
# Frontend
- Navigate to "Chat with your Document" page
- Click "🔄 Start New Session" button
- New session ID will be generated automatically
```

#### Clearing Chat History
```python
# Frontend
- Click "🗑️ Clear Chat History" button
- All messages in current session will be removed
- Session ID remains the same
```

#### Backend API
```bash
# Create new session
curl -X POST http://127.0.0.1:8000/api/chat/new_session

# Clear session history
curl -X DELETE http://127.0.0.1:8000/api/chat/clear_session/{session_id}
```

---

### 2. Document Management

#### Uploading a Document
```python
# Frontend
1. Go to "Document Ingestion" page
2. Upload PDF, TXT, CSV, or Excel file
3. System checks for duplicates
4. If unique: Document is ingested and chunks are created
5. If duplicate: Warning message shown
```

#### Viewing Uploaded Documents
```python
# Frontend
1. Navigate to "Chat with your Document" page
2. Document list appears in the right panel
3. See all document names and their IDs
4. Click "Refresh Documents" to update the list
```

#### Deleting a Document
```python
# Frontend
1. In Chat page, expand "📁 Manage Documents"
2. Click "🗑️" button next to document name
3. Document and all its chunks are deleted
4. Verify deletion in refreshed list

# Backend API
curl -X DELETE http://127.0.0.1:8000/api/documents/{document_id}
```

#### Listing All Documents (API)
```bash
curl -X GET http://127.0.0.1:8000/api/documents
```

Response:
```json
{
  "documents": [
    {"id": "uuid-1", "filename": "research_paper.pdf"},
    {"id": "uuid-2", "filename": "notes.txt"}
  ]
}
```

---

### 3. Duplicate Prevention

#### Scenario: User tries to upload same document twice

**First Upload:**
```
✅ Success
- Filename: report.pdf
- Chunks created: 42
- Status: Document ingested successfully
```

**Second Upload (same file):**
```
⚠️ Duplicate Document
- Message: "A document with the same content has already been uploaded"
- Content Hash Match: Already exists in system
- Action: Upload rejected, no new chunks created
```

---

### 4. Context-Aware Querying

#### Without Document Filter
```
Query: "What are the main findings?"
Scope: Searches across ALL uploaded documents
Response: Answers from most relevant documents
```

#### With Document Filter
```
1. Select document from dropdown: "research_paper.pdf"
2. Query: "What are the main findings?"
3. Scope: Searches ONLY in "research_paper.pdf"
4. Response: Answers specific to selected document
```

#### Backend API Example
```bash
# Query all documents
curl -X POST http://127.0.0.1:8000/api/query \
  -d "query=What are the main points?" \
  -d "session_id=abc-123" \
  -d "document_name="

# Query specific document
curl -X POST http://127.0.0.1:8000/api/query \
  -d "query=What are the main points?" \
  -d "session_id=abc-123" \
  -d "document_name=research_paper.pdf"
```

---

### 5. Session-Based Conversation

#### Multi-Turn Conversation with Session Tracking

**Turn 1:**
```
User: "What is the document about?"
Session ID: session-abc-123
Backend: Stores question & answer in chat_history[session-abc-123]
```

**Turn 2:**
```
User: "Can you elaborate on the methodology?"
Session ID: session-abc-123 (same)
Backend: Uses context from previous turn if needed
Response: Follow-up answer with context awareness
```

**Turn 3 (New Session):**
```
User: Clicks "Start New Session"
New Session ID: session-xyz-789
Previous conversation cleared
New conversation history starts fresh
```

---

### 6. Advanced Queries with Multi-Agent Reasoning

#### Simple RAG Mode
```
1. Select "📊 Simple RAG Mode" (default)
2. Query: "Summarize the document"
3. Response: Direct answer from retrieved documents
4. Speed: Fast
```

#### Multi-Agent Reasoning Mode
```
1. Select "🧠 Multi-Agent Reasoning"
2. Query: "What are the implications of this research?"
3. Process:
   - Planning Phase: Agent determines approach
   - Retrieval Phase: Gathers relevant information
   - Reasoning Phase: Analyzes and synthesizes
   - Response Phase: Generates comprehensive answer
4. Speed: Slower but more thorough
5. View Analysis: Expand "📊 View Analysis & Reasoning"
```

---

## Database Interactions

### Document Metadata Storage

#### ChromaDB Storage (Persistent)
```python
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "annual_report_2024.pdf",
  "content_hash": "sha256_hash_value",
  "source": "/temp/annual_report_2024.pdf",
  "row": 0
}
```

#### In-Memory Metadata
```python
RAGService.document_metadata = {
  "550e8400-e29b-41d4-a716-446655440000": {
    "filename": "annual_report_2024.pdf",
    "content_hash": "sha256_hash_value"
  }
}

RAGService.content_hashes = {
  "sha256_hash_value": "annual_report_2024.pdf"
}
```

---

## Common Workflows

### Workflow 1: Single Document, Multiple Questions
```
1. Upload document (Document Ingestion page)
2. Go to Chat page
3. System creates new session automatically
4. Ask multiple questions
5. All answers are contextualized to same document
6. Chat history maintained per session
```

### Workflow 2: Compare Multiple Documents
```
1. Upload Document A
2. Upload Document B
3. Go to Chat page
4. Ask: "What are the key differences?"
   - System searches both documents
   - Provides comparative analysis
5. Switch to Document A filter
6. Ask: "Elaborate on point X"
   - System searches only Document A
```

### Workflow 3: Archive and Fresh Start
```
1. Have multiple documents and conversation history
2. Click "🗑️ Clear Chat History"
   - Chat history cleared
   - Documents remain
   - Session ID same
3. Click "🔄 Start New Session"
   - Fresh session ID
   - Fresh conversation
   - Documents still available
4. Delete old documents via "📁 Manage Documents"
   - Remove from system entirely
```

---

## API Response Examples

### Upload Document
```bash
POST /api/ingest
Content-Type: multipart/form-data

Response (200):
{
  "message": "Document ingested successfully",
  "filename": "report.pdf",
  "chunks_ingested": 42
}

Response (409 - Duplicate):
{
  "detail": "Duplicate document: Document 'report.pdf' with same content already exists."
}
```

### Query with Session
```bash
POST /api/query
Content-Type: application/x-www-form-urlencoded

Payload:
query=What is the summary?&session_id=abc-123&document_name=report.pdf

Response (200):
{
  "answer": "The document discusses..."
}
```

### List Documents
```bash
GET /api/documents

Response (200):
{
  "documents": [
    {
      "id": "doc-uuid-1",
      "filename": "document1.pdf"
    },
    {
      "id": "doc-uuid-2",
      "filename": "document2.txt"
    }
  ]
}
```

### Create Session
```bash
POST /api/chat/new_session

Response (200):
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

---

## Troubleshooting

### Issue: "Could not connect to backend"
**Solution:**
```bash
# Check if backend is running
python main.py

# Verify port 8000 is accessible
netstat -ano | findstr :8000
```

### Issue: "Document upload failed"
**Solution:**
- Check file format (PDF, TXT, CSV, XLSX, XLS)
- Verify file is not corrupted
- Check file size (should be reasonable)
- Backend must be running

### Issue: "Duplicate document rejected"
**Solution:**
- This is expected behavior
- File with same content already exists
- Delete original if you need different version
- Or upload from different location

### Issue: "No relevant documents found"
**Solution:**
- Check if documents are uploaded
- Try a different query format
- Ensure document contains relevant information
- Check selected document filter

### Issue: Session ID not persisting
**Solution:**
- Session is created automatically on page load
- Check browser console for errors
- Refresh page if needed
- Create new session explicitly

---

## Performance Tips

1. **Use Simple RAG Mode for speed**: When fast responses are more important than deep analysis
2. **Filter by document**: Specify document name when searching specific files
3. **Ask specific questions**: More targeted queries = better responses
4. **Clear old sessions**: Frees up memory and improves performance
5. **Delete unused documents**: Reduces search space and improves retrieval speed

---

## Security Notes

- Session IDs are UUIDs (cryptographically secure)
- Content hashing uses SHA-256
- No authentication required (add if needed)
- Document names stored plaintext (consider encryption if sensitive)
- Metadata stored in ChromaDB (consider backup strategy)

---

## Support & Contributing

For issues or feature requests, refer to the project repository.

---

**Last Updated**: January 22, 2026
