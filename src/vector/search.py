from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)

class RAGSearch:
    def __init__(self, vector_store, embeddings_module):
        self.vector_store = vector_store
        self.embeddings = embeddings_module
    
    def search(self, query: str, k: int = 5) -> Dict:
        """Search for relevant chunks given a query."""
        try:
            start_time = time.time()
            
            # Embed the query
            query_vector = self.embeddings.embed_text(query)
            if not query_vector:
                return {
                    "query": query,
                    "results": [],
                    "retrieval_time_ms": 0,
                    "error": "Failed to embed query"
                }
            
            # Search vector store
            results = self.vector_store.search(query_vector, k=k)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return {
                "query": query,
                "results": results,
                "retrieval_time_ms": round(retrieval_time_ms, 2),
                "num_results": len(results)
            }
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return {
                "query": query,
                "results": [],
                "retrieval_time_ms": 0,
                "error": str(e)
            }
