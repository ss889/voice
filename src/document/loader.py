from pathlib import Path
from typing import List, Dict
import logging
from .parser import parse_document
from .chunker import chunk_text
from ..vector.embeddings import embed_batch
from ..vector.client import VectorStore
from ..config.settings import settings

logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def load_document(self, file_path: str) -> Dict:
        """Load, parse, chunk, and embed a document."""
        try:
            file_path = str(file_path)
            logger.info(f"Loading document: {file_path}")
            
            # Parse document
            pages = parse_document(file_path)
            logger.info(f"Parsed {len(pages)} pages")
            if not pages:
                logger.warning(f"No content parsed from {file_path}")
                return {"status": "error", "message": "Failed to parse document"}
            
            total_chunks = 0
            source_name = Path(file_path).name
            
            # Process each page
            for page_idx, page_data in enumerate(pages):
                page_num = page_data.get("page_num", 1)
                text = page_data.get("text", "")
                logger.info(f"Page {page_idx+1}: {len(text)} characters")
                
                # Chunk the text
                metadata = {
                    "source": source_name,
                    "page_num": page_num,
                }
                chunks = chunk_text(text, metadata, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                logger.info(f"Created {len(chunks)} chunks from page {page_idx+1}")
                
                if not chunks:
                    logger.warning(f"No chunks created for page {page_idx+1}")
                    continue
                
                # Embed chunks
                chunk_texts = [chunk["text"] for chunk in chunks]
                logger.info(f"Embedding {len(chunk_texts)} chunks...")
                embeddings = embed_batch(chunk_texts, settings.EMBEDDING_MODEL)
                logger.info(f"Got {len(embeddings) if embeddings else 0} embeddings")
                
                if not embeddings or len(embeddings) != len(chunks):
                    logger.error(f"Embedding count mismatch for {source_name}: expected {len(chunks)}, got {len(embeddings) if embeddings else 0}")
                    continue
                
                # Prepare payloads (without text for storage efficiency)
                payloads = []
                for chunk in chunks:
                    payload = {k: v for k, v in chunk.items() if k != "text"}
                    payload["text"] = chunk["text"]  # Keep text for retrieval
                    payloads.append(payload)
                
                # Upsert to vector store
                self.vector_store.upsert(embeddings, payloads)
                total_chunks += len(chunks)
            
            logger.info(f"Successfully loaded {source_name} with {total_chunks} chunks")
            return {
                "status": "success",
                "source": source_name,
                "chunks_indexed": total_chunks,
                "pages_processed": len(pages)
            }
        except Exception as e:
            logger.error(f"Error loading document: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def load_directory(self, directory: str) -> List[Dict]:
        """Load all documents from a directory."""
        results = []
        dir_path = Path(directory)
        
        for file_path in dir_path.glob("*.*"):
            if file_path.suffix.lower() in [".txt", ".pdf"]:
                result = self.load_document(str(file_path))
                results.append(result)
        
        logger.info(f"Loaded {len(results)} documents from {directory}")
        return results
