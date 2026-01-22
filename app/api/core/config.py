import os
from dotenv import load_dotenv

# Loading env. variables
load_dotenv()

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

# Groq Configuration - REQUIRED
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. "
        "Please set it before running the application. "
        "You can get your API key from https://console.groq.com/"
    )

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
LLM_MODEL = os.getenv("LLM_MODEL")

# Vector store configuration
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION"))  # Dimension of embedding model
