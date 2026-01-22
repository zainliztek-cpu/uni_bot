from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.schema import Document
from langchain_core.documents import Document
import os
import pandas as pd
from app.api.agents.agents import AgentOrchestrator
import uuid
import json
from collections import defaultdict
import hashlib

# Import all configurations
from app.api.core.config import (
    CHROMA_DB_PATH,
    GROQ_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
)

class RAGService:
    def __init__(self):
        print("---Initializing RAG Service with ChromaDB and Groq---")

        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        # Initialize the chat model 
        self.llm = ChatGroq(
            model=LLM_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.7
        )

        # Initialize the langchain vector store with ChromaDB
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DB_PATH,
            collection_name="documents",
        )
        print("RAG service initialized successfully")
        
        # Initialize Agent Orchestrator for multi-agent reasoning
        self.agent_orchestrator = AgentOrchestrator(self.llm, self.vector_store, k=4)

        # Initialize in-memory storage for chat history (session_id -> list of messages)
        self.chat_history = defaultdict(list)
        # Initialize in-memory storage for document metadata (id -> filename)
        self.document_metadata = {}
        # Initialize in-memory storage for content hashes (content_hash -> filename)
        self.content_hashes = {}
        # Initialize session registry to track all sessions with timestamps
        self.session_registry = {}  # session_id -> {created_at, last_accessed}
        # Load existing document metadata from ChromaDB on startup
        self._load_existing_document_metadata()
        # Load existing sessions on startup
        self._load_existing_sessions()

    def _validate_file(self, file_path: str, file_type: str) -> bool:
        """Validate file exists and has correct extension"""
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        valid_types = {"pdf", "txt", "csv", "xlsx", "xls"}
        if file_type.lower() not in valid_types:
            raise ValueError(f"Unsupported file type: {file_type}. Supported: {valid_types}")
        
        return True

    def _load_pdf(self, file_path: str):
        """Load PDF file"""
        loader = PyPDFLoader(file_path)
        return loader.load()

    def _load_txt(self, file_path: str):
        """Load TXT file"""
        loader = TextLoader(file_path)
        return loader.load()

    def _load_csv(self, file_path: str):
        """Load CSV file using pandas"""
        loader = CSVLoader(file_path)
        return loader.load()

    def _load_excel(self, file_path: str):
        """Load Excel file using pandas"""
        excel_file = pd.read_excel(file_path)
        documents = []
        for index, row in excel_file.iterrows():
            content = "\n".join([f"{col}: {val}" for col, val in row.items()])
            doc = Document(page_content=content, metadata={"source": file_path, "row": index})
            documents.append(doc)
        return documents

    def _get_file_type(self, file_path: str) -> str:
        """Extract file type from path"""
        _, ext = os.path.splitext(file_path)
        return ext.lower().lstrip('.')

    def _load_document_by_type(self, file_path: str, file_type: str):
        """Load document based on file type"""
        if file_type == "pdf":
            return self._load_pdf(file_path)
        elif file_type == "txt":
            return self._load_txt(file_path)
        elif file_type == "csv":
            return self._load_csv(file_path)
        elif file_type in ["xlsx", "xls"]:
            return self._load_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    # This is the method you are adding
    def ingest_document(self, file_path: str, filename: str):
        print(f"Starting ingestion for document: {file_path}")

        # Calculate content hash to check for duplicates FIRST
        with open(file_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()

        if content_hash in self.content_hashes:
            raise ValueError(f"Document '{filename}' with same content already exists.")

        # Get and validate file type
        file_type = self._get_file_type(file_path)
        self._validate_file(file_path, file_type)

        # Load the document
        documents = self._load_document_by_type(file_path, file_type)
        print(f"Loaded {len(documents)} document pages")

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs_chunks = text_splitter.split_documents(documents)
        
        # Assign a unique document ID and add metadata to each chunk
        document_id = str(uuid.uuid4())
        for chunk in docs_chunks:
            chunk.metadata["document_id"] = document_id
            chunk.metadata["filename"] = filename
            chunk.metadata["content_hash"] = content_hash
        print("docs_chunks: ", docs_chunks[0])
        chunk_count = len(docs_chunks)
        print(f"Split document into {len(docs_chunks)} chunks")

        # Ingest chunk into the vector store
        try:
            print("---Ingesting document chunks into ChromaDB---")
            self.vector_store.add_documents(docs_chunks)
            print("Document ingested successfully")
            
            # Store document metadata
            self.document_metadata[document_id] = {"filename": filename, "content_hash": content_hash}
            self.content_hashes[content_hash] = filename
            
            return len(docs_chunks)
        except Exception as e:
            print(f"Error during ingestion:{e}")
            raise

    # This is the method you are adding
    def generate_answer(self, query: str, session_id: str, k: int = 4, document_name: str = None):
        """
        Generates an answer to a query using the RAG pipeline.
        
        Args:
            query (str): The user's question.
            k (int): The number of relevant documents to retrieve.

        Returns:
            A dictionary containing the answer and the source documents.
        """
        print(f"Received query: '{query}'")

        # Retrieve the relevant documents from the vector store
        if document_name:
            # Filter by document name using metadata
            # This assumes your ChromaDB metadata can be queried this way.
            # If not, you might need to retrieve all and then filter in-memory.
            print(f"Searching for {k} relevant documents within document: '{document_name}'..")
            # This is a simplified filter. Actual implementation might vary based on ChromaDB's capabilities.
            search_results = self.vector_store.similarity_search_with_score(
                query, k=k, filter={"filename": document_name}
            )
        else:
            print(f"Searching for {k} relevant documents across all documents..")
            search_results = self.vector_store.similarity_search_with_score(query, k=k)
        print(search_results)
        if not search_results:
            print("No relevant documents found")
            return {"answer": "No relevant information in the provided documents", "source_documents": []}

        # Construct the context and prepare the prompt
        context = "/n/n---/n/n".join([doc.page_content for doc, score in search_results])
        print("Context: ", context)

        prompt = (
            "You are a helpful AI assistant. Use the following context from a document to answer the question. "
            "If you don't know the answer, just say that you don't know, don't try to make up an answer.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )

        print("Generating answer with LLM...")
        try:
            response = self.llm.invoke(prompt)
            # Handle different response types
            if hasattr(response, 'content'):
                answer_text = response.content
            else:
                answer_text = str(response)
            return {"answer": answer_text}
        except Exception as e:
            print(f"Error generating answer: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_answer_with_agents(self, query: str, session_id: str, document_name: str = None):
        """
        Generates an answer using multi-agent reasoning pipeline.
        Uses Planner, Retriever, Reasoning, and Response agents.
        
        Args:
            query (str): The user's question.
        
        Returns:
            A dictionary containing the answer, plan, and reasoning process.
        """
        print(f"Received query for agent-based reasoning: '{query}'")
        
        try:
            result = self.agent_orchestrator.execute(query, session_id, document_name)
            return result
        except Exception as e:
            print(f"Error in agent-based reasoning: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _load_existing_document_metadata(self):
        """Loads existing document metadata from ChromaDB on startup."""
        print("Loading existing document metadata from ChromaDB...")
        try:
            # Retrieve all documents from the collection with their metadata
            collection_results = self.vector_store._collection.get(include=['metadatas'])
            
            if not collection_results or not collection_results.get('metadatas'):
                print("No documents found in ChromaDB collection.")
                return
            
            # Use a set to track unique document IDs to avoid duplicates
            loaded_doc_ids = set()
            
            for metadata in collection_results['metadatas']:
                if not metadata:
                    continue
                    
                doc_id = metadata.get("document_id")
                filename = metadata.get("filename")
                content_hash = metadata.get("content_hash")
                
                # Only load each document once (documents have multiple chunks)
                if doc_id and filename and content_hash and doc_id not in loaded_doc_ids:
                    self.document_metadata[doc_id] = {"filename": filename, "content_hash": content_hash}
                    self.content_hashes[content_hash] = filename
                    loaded_doc_ids.add(doc_id)
            
            print(f"Loaded {len(self.document_metadata)} existing documents from ChromaDB.")
        except Exception as e:
            print(f"Error loading existing document metadata: {e}")
            print("Continuing with empty document metadata. New documents can still be ingested.")

    def get_uploaded_documents(self):
        """Returns a list of uploaded documents with their IDs and filenames."""
        return [{"id": doc_id, "filename": metadata["filename"]} for doc_id, metadata in self.document_metadata.items()]

    def delete_document(self, document_id: str):
        """Deletes a document from the vector store and metadata storage."""
        if document_id not in self.document_metadata:
            raise ValueError(f"Document with ID {document_id} not found.")

        try:
            # Delete from ChromaDB
            # ChromaDB's delete method can take a list of IDs to delete.
            # We need to find all chunk IDs associated with this document_id.
            # This requires querying ChromaDB for chunks that have this document_id in their metadata.
            
            # A more efficient way if ChromaDB supported direct deletion by metadata field.
            # For now, we'll retrieve all relevant chunks and delete them by their unique IDs.
            
            # First, find all chunk IDs associated with the document_id
            # This is a simplified approach, assuming document_id is directly searchable in metadata
            
            # This needs to be done carefully. ChromaDB's delete by `where` clause on metadata
            # is more appropriate here if available. Otherwise, we'd need to retrieve and then delete by IDs.
            
            # Assuming `delete` can filter by metadata:
            self.vector_store._collection.delete(where={"document_id": document_id})
            
            # Remove from in-memory metadata
            content_hash = self.document_metadata[document_id]["content_hash"]
            del self.content_hashes[content_hash]
            del self.document_metadata[document_id]
            print(f"Document {document_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            raise

    def start_new_session(self) -> str:
        """Generates and returns a new session ID."""
        from datetime import datetime
        session_id = str(uuid.uuid4())
        self.chat_history[session_id] = []  # Initialize empty chat history for the new session
        self.session_registry[session_id] = {
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        print(f"New session started with ID: {session_id}")
        return session_id

    def clear_session_history(self, session_id: str):
        """Clears the chat history for a given session ID."""
        if session_id in self.chat_history:
            self.chat_history[session_id].clear()
            print(f"Chat history cleared for session: {session_id}")
        else:
            print(f"No chat history found for session: {session_id}")

    def get_all_sessions(self) -> list:
        """Returns a list of all sessions with their metadata."""
        from datetime import datetime
        sessions = []
        for session_id, metadata in self.session_registry.items():
            sessions.append({
                "session_id": session_id,
                "created_at": metadata.get("created_at"),
                "last_accessed": metadata.get("last_accessed"),
                "message_count": len(self.chat_history.get(session_id, []))
            })
        # Sort by last_accessed in descending order (most recent first)
        sessions.sort(key=lambda x: x["last_accessed"], reverse=True)
        return sessions

    def get_session_history(self, session_id: str) -> list:
        """Returns the chat history for a specific session."""
        from datetime import datetime
        if session_id in self.session_registry:
            # Update last_accessed timestamp
            self.session_registry[session_id]["last_accessed"] = datetime.now().isoformat()
        return self.chat_history.get(session_id, [])

    def add_message_to_session(self, session_id: str, role: str, content: str):
        """Adds a message to a session's chat history."""
        from datetime import datetime
        # Initialize session if it doesn't exist
        if session_id not in self.session_registry:
            self.session_registry[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat()
            }
        if session_id not in self.chat_history:
            self.chat_history[session_id] = []
        
        # Add message to history
        message = {
            "role": role,
            "content": content
        }
        self.chat_history[session_id].append(message)
        
        # Update last_accessed timestamp
        self.session_registry[session_id]["last_accessed"] = datetime.now().isoformat()
        print(f"Message added to session {session_id}: {role}")

    def _load_existing_sessions(self):
        """Loads existing sessions from chat_history on startup."""
        print("Loading existing sessions...")
        try:
            # Sessions are stored in memory, so they exist as long as the service is running
            # This method is a placeholder for future persistence features
            print(f"Session management system ready. Sessions will be in memory.")
        except Exception as e:
            print(f"rror initializing session system: {e}")
# This line creates a single, shared instance of the service when the module is imported.
try:
    rag_service_instance = RAGService()
except Exception as e:
    print(f"Warning: Failed to initialize RAG Service at import time: {e}")
    print("Service will be initialized on first use")
    rag_service_instance = None
