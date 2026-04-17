from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def chunk_text(text: str, metadata: Dict, chunk_size: int = 512, chunk_overlap: int = 100) -> List[Dict]:
    """
    Chunk text with overlap, respecting sentence boundaries.
    
    Args:
        text: Text to chunk
        metadata: Metadata to include in each chunk (source, page_num, etc.)
        chunk_size: Character size of each chunk
        chunk_overlap: Character overlap between chunks
        
    Returns:
        List of chunk dictionaries with text and metadata
    """
    chunks = []
    start = 0
    chunk_index = 0
    
    if not text or not text.strip():
        return chunks
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Find sentence boundary if not at end
        if end < len(text):
            # Look for sentence boundaries in the last portion of the chunk
            for sep in [". ", "! ", "? ", "\n\n", "\n"]:
                last_sep = text.rfind(sep, start + chunk_size // 2, end)
                if last_sep != -1:
                    end = last_sep + len(sep)
                    break
        
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "chunk_index": chunk_index,
                **metadata
            })
            chunk_index += 1
        
        # Move start position, accounting for overlap
        start = end - chunk_overlap if end < len(text) else len(text)
    
    # Add total_chunks metadata to all chunks
    total_chunks = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total_chunks
    
    logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
    return chunks
