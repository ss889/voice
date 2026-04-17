import os
from openai import OpenAI
from typing import List
import logging
import hashlib
import numpy as np

logger = logging.getLogger(__name__)

# Initialize client lazily when needed
_client = None
_use_fallback = False

def get_client():
    """Get or create OpenAI client."""
    global _client, _use_fallback
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set - using fallback embeddings")
            _use_fallback = True
            return None
        try:
            _client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e} - using fallback embeddings")
            _use_fallback = True
            return None
    return _client

def _create_fallback_embedding(text: str) -> List[float]:
    """Create a deterministic embedding using hash (fallback when OpenAI unavailable)."""
    # Create a deterministic 1536-dim vector from text hash
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    
    # Seed numpy random with hash for reproducibility
    np.random.seed(int.from_bytes(hash_bytes[:8], 'big') % (2**32))
    embedding = np.random.randn(1536).astype(np.float32)
    # Normalize
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return embedding.tolist()

def embed_text(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Embed a single text."""
    try:
        client = get_client()
        if client is None:
            logger.warning(f"Using fallback embedding for text chunk")
            return _create_fallback_embedding(text)
            
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.warning(f"Error embedding text with OpenAI: {e} - using fallback")
        return _create_fallback_embedding(text)

def embed_batch(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """Embed a batch of texts efficiently."""
    if not texts:
        return []
    
    # OpenAI API has a limit on batch size, so we process in chunks
    max_batch_size = 100
    all_embeddings = []
    
    try:
        client = get_client()
        if client is None:
            logger.warning(f"Using fallback embeddings for {len(texts)} texts")
            return [_create_fallback_embedding(text) for text in texts]
            
        logger.info(f"Embedding {len(texts)} texts with model {model}")
        for i in range(0, len(texts), max_batch_size):
            batch = texts[i:i + max_batch_size]
            logger.debug(f"Embedding batch {i//max_batch_size + 1}: {len(batch)} texts")
            response = client.embeddings.create(
                model=model,
                input=batch
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            all_embeddings.extend([item.embedding for item in embeddings])
        
        logger.info(f"Successfully embedded {len(all_embeddings)} texts")
        return all_embeddings
    except Exception as e:
        logger.warning(f"Error embedding batch with OpenAI: {e} - using fallback embeddings")
        return [_create_fallback_embedding(text) for text in texts]
