import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "test_key")
    QDRANT_COLLECTION_NAME = "documents"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 100
    DEFAULT_K = 5
    JUDGE_MODEL = "gpt-4o-mini"

settings = Settings()
