"""Mock Qdrant client for testing without Docker"""
from typing import List, Dict, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class MockVectorStore:
    """In-memory vector store for demo/testing"""
    
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 collection_name: str = "documents", vector_size: int = 1536):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.vectors = {}  # id -> vector
        self.payloads = {}  # id -> payload
        self.next_id = 0
        logger.info(f"MockVectorStore initialized (in-memory, no Docker needed)")
    
    def upsert(self, vectors: List[List[float]], payloads: List[Dict], ids: Optional[List[int]] = None) -> bool:
        """Store vectors and payloads"""
        try:
            if ids is None:
                ids = list(range(self.next_id, self.next_id + len(vectors)))
                self.next_id += len(vectors)
            
            for id, vec, payload in zip(ids, vectors, payloads):
                self.vectors[id] = np.array(vec)
                self.payloads[id] = payload
            
            logger.info(f"Upserted {len(vectors)} vectors")
            return True
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            return False
    
    def search(self, query_vector: List[float], k: int = 5, score_threshold: float = 0.0) -> List[Dict]:
        """Search for similar vectors using cosine similarity"""
        try:
            if not self.vectors:
                return []
            
            query_vec = np.array(query_vector)
            query_norm = np.linalg.norm(query_vec)
            
            scores = {}
            for id, vec in self.vectors.items():
                vec_norm = np.linalg.norm(vec)
                if vec_norm == 0 or query_norm == 0:
                    similarity = 0
                else:
                    similarity = np.dot(query_vec, vec) / (query_norm * vec_norm)
                scores[id] = max(0, similarity)  # Cosine can be negative, clamp to [0, 1]
            
            # Get top-k
            top_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
            
            results = []
            for id, score in top_ids:
                if score >= score_threshold:
                    payload = self.payloads[id]
                    results.append({
                        "text": payload.get("text", ""),
                        "similarity": float(score),  # Match frontend expectation
                        "score": float(score),  # Also include for compatibility
                        "source": payload.get("source", ""),
                        "page_num": payload.get("page_num", 1),
                        "chunk_index": payload.get("chunk_index", 0),
                        "total_chunks": payload.get("total_chunks", 0),
                    })
            
            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            return {
                "collection_name": self.collection_name,
                "vectors_count": len(self.vectors),
                "vector_size": self.vector_size,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def clear(self):
        """Clear all vectors"""
        self.vectors.clear()
        self.payloads.clear()
        self.next_id = 0
        logger.info("Cleared all vectors")
