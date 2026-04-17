import os
from openai import OpenAI
from typing import List
import logging

logger = logging.getLogger(__name__)

# Initialize client lazily when needed
_client = None

def get_client():
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY not configured")
        _client = OpenAI(api_key=api_key)
    return _client

def embed_text(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Embed a single text."""
    try:
        client = get_client()
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error embedding text: {e}")
        return []

def embed_batch(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """Embed a batch of texts efficiently."""
    if not texts:
        return []
    
    # OpenAI API has a limit on batch size, so we process in chunks
    max_batch_size = 100
    all_embeddings = []
    
    try:
        client = get_client()
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
        logger.error(f"Error embedding batch: {e}", exc_info=True)
        return []
