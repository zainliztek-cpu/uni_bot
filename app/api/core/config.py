import os
from dotenv import load_dotenv

# Loading env. variables
load_dotenv()

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")

# Groq Configuration - REQUIRED
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. "
        "Please set it before running the application. "
        "You can get your API key from https://console.groq.com/"
    )

EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
LLM_MODEL = "llama-3.3-70b-versatile"

# Vector store configuration
VECTOR_DIMENSION = 1024  # Dimension of embedding model
