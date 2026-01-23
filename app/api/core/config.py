import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== MEMORY-SAFE CONFIGURATION ====================
# All sizes tuned for Render free tier (512MB RAM with 1 worker)

# ChromaDB Configuration - ephemeral filesystem safe path
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")

# Ensure ChromaDB directory exists but don't create large files upfront
# Note: On Render free tier, this directory is ephemeral and resets on restart
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Groq API Key - REQUIRED for LLM functionality
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. "
        "Please set it before running the application. "
        "Get it from: https://console.groq.com/"
    )

# Model Configuration - using efficient models for memory constraints
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
# llama-3.1-8b-instant: 7B-sized model, faster inference, perfect for RAG
# Alternative models: gemma-7b-it (7B exact), mixtral-8x7b, llama-3.1-70b-versatile
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

# Vector store configuration
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "1024"))

# ==================== MEMORY LIMITS & SAFEGUARDS ====================
# These prevent OOM crashes on free tier

# Maximum file upload size: 20MB (prevents memory bloat from large files)
MAX_UPLOAD_SIZE_MB = 20
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Maximum query length: 1000 characters (prevents token explosion)
MAX_QUERY_LENGTH = 1000

# Embedding batch size: 8 (lower batch = less peak memory usage)
# Standard is 32, but free tier can't handle it simultaneously
EMBEDDING_BATCH_SIZE = 8

# Number of retrieved chunks: 3 (reduced from 4 for lower memory)
# Each chunk + embedding takes ~50KB in memory
MAX_RETRIEVED_CHUNKS = 3

# Session memory limits
MAX_SESSIONS_IN_MEMORY = 50  # Keep at most 50 active sessions
MAX_MESSAGES_PER_SESSION = 100  # Limit message history per session
MAX_DOCUMENTS_IN_MEMORY = 50  # Track max 50 documents metadata

# Chunk configuration for document processing
# Smaller chunks = more tokens but better search accuracy
CHUNK_SIZE = 800  # Reduced from 1000 for memory safety
CHUNK_OVERLAP = 150  # Reduced from 200

# Temperature for LLM responses (0.7 = balanced creativity/consistency)
LLM_TEMPERATURE = 0.7

# Timeout for model initialization (seconds)
# First request loads models, give it 5+ minutes
MODEL_INIT_TIMEOUT = 600
