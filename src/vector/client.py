from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 collection_name: str = "documents", vector_size: int = 1536):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        try:
            self.client = QdrantClient(host=host, port=port)
            logger.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
        
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Created collection '{self.collection_name}'")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise
    
    def upsert(self, vectors: List[List[float]], payloads: List[Dict], ids: Optional[List[int]] = None) -> bool:
        """Upsert vectors and payloads into the collection."""
        try:
            if ids is None:
                # Get current count to generate new IDs
                stats = self.client.get_collection(self.collection_name)
                ids = list(range(int(stats.vectors_count), int(stats.vectors_count) + len(vectors)))
            
            points = [
                PointStruct(id=id, vector=vec, payload=payload)
                for id, vec, payload in zip(ids, vectors, payloads)
            ]
            
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Upserted {len(points)} vectors")
            return True
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            return False
    
    def search(self, query_vector: List[float], k: int = 5, score_threshold: float = 0.0) -> List[Dict]:
        """Search for similar vectors."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=k,
                score_threshold=score_threshold,
                with_payload=True
            )
            
            search_results = []
            for result in results:
                payload = result.payload
                search_results.append({
                    "text": payload.get("text", ""),
                    "score": result.score,
                    "source": payload.get("source", ""),
                    "page_num": payload.get("page_num", 1),
                    "chunk_index": payload.get("chunk_index", 0),
                    "total_chunks": payload.get("total_chunks", 0),
                })
            
            logger.info(f"Found {len(search_results)} results")
            return search_results
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get collection statistics."""
        try:
            collection = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vectors_count": collection.vectors_count,
                "vector_size": self.vector_size,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def delete_by_source(self, source: str) -> bool:
        """Delete all vectors from a specific source file."""
        try:
            from qdrant_client.models import FieldCondition, MatchValue
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=self.client.models.FilterSelector(
                    filter=self.client.models.Filter(
                        must=[
                            FieldCondition(
                                key="source",
                                match=MatchValue(value=source)
                            )
                        ]
                    )
                ),
            )
            logger.info(f"Deleted vectors from source: {source}")
            return True
        except Exception as e:
            logger.error(f"Error deleting by source '{source}': {e}")
            return False
    
    def clear(self):
        """Clear the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
            logger.info("Cleared collection")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
