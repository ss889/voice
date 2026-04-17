"""
Dependency Injection Container - Centralizes service initialization.
Eliminates global state and improves testability.
"""
import logging
from typing import Optional

from src.config.settings import settings
from src.document.loader import DocumentLoader
from src.vector.search import RAGSearch
from src.vector import embeddings as embeddings_module

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Container for managing service dependencies."""
    
    def __init__(self):
        self._vector_store: Optional[object] = None
        self._document_loader: Optional[DocumentLoader] = None
        self._rag_search: Optional[RAGSearch] = None
    
    @property
    def vector_store(self):
        """Lazily initialize and return vector store."""
        if self._vector_store is None:
            self._vector_store = self._create_vector_store()
        return self._vector_store
    
    @property
    def document_loader(self) -> Optional[DocumentLoader]:
        """Get document loader (depends on vector store)."""
        if self._document_loader is None and self.vector_store is not None:
            self._document_loader = DocumentLoader(self.vector_store)
        return self._document_loader
    
    @property
    def rag_search(self) -> Optional[RAGSearch]:
        """Get RAG search (depends on vector store)."""
        if self._rag_search is None and self.vector_store is not None:
            self._rag_search = RAGSearch(self.vector_store, embeddings_module)
        return self._rag_search
    
    @property
    def is_ready(self) -> bool:
        """Check if all services are initialized."""
        return (self.vector_store is not None and 
                self.document_loader is not None and 
                self.rag_search is not None)
    
    @staticmethod
    def _create_vector_store():
        """Create vector store with fallback support."""
        try:
            from src.vector.client import VectorStore
            vector_store = VectorStore(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vector_size=settings.EMBEDDING_DIMENSION
            )
            logger.info("✓ Using Qdrant vector store (Docker)")
            return vector_store
        except Exception as e:
            logger.warning(f"Qdrant unavailable: {e}")
            logger.info("Falling back to in-memory mock vector store")
            try:
                from src.vector.mock_client import MockVectorStore
                vector_store = MockVectorStore(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vector_size=settings.EMBEDDING_DIMENSION
                )
                logger.info("✓ Using MockVectorStore (in-memory, demo mode)")
                return vector_store
            except Exception as e2:
                logger.error(f"Failed to initialize any vector store: {e2}")
                return None


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get or create the global service container."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container():
    """Reset container (useful for testing)."""
    global _container
    _container = None
