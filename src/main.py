from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import tempfile
import logging
from typing import Optional
from pathlib import Path

from src.config.settings import settings
from src.container import get_container
from src.evaluation.judge import evaluate_batch
from src.exceptions import (
    ServiceUnavailableError, DocumentProcessingError, InvalidDocumentError,
    FileSizeExceededError, VectorStoreError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE_MB = 500
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_MIME_TYPES = {"application/pdf", "text/plain"}
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=100, description="Number of results to return (1-100)")

class EvaluateRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=100, description="Number of results to evaluate (1-100)")

# Initialize FastAPI app
app = FastAPI(title="DocQuery - Semantic Document Search")

# Enable CORS for GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (frontend can be anywhere)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    container = get_container()
    return {
        "status": "ok",
        "services_ready": container.is_ready
    }

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document (PDF or TXT) and process it for semantic search."""
    temp_path: Optional[str] = None
    
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            raise InvalidDocumentError(
                f"Unsupported file type: {file_ext}. Supported: {SUPPORTED_EXTENSIONS}"
            )
        
        # Get container and verify services
        container = get_container()
        if not container.is_ready:
            raise ServiceUnavailableError("Document loader or vector store not initialized")
        
        # Read and validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise FileSizeExceededError(
                f"File exceeds {MAX_FILE_SIZE_MB}MB limit (got {len(content) / 1024 / 1024:.1f}MB)"
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            temp_path = tmp_file.name
        
        # Process document
        result = container.document_loader.load_document(temp_path)
        
        if result.get("status") == "error":
            raise DocumentProcessingError(result.get("message", "Unknown parsing error"))
        
        return JSONResponse(content=result)
    
    except InvalidDocumentError as e:
        logger.warning(f"Invalid document: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileSizeExceededError as e:
        logger.warning(f"File size exceeded: {e}")
        raise HTTPException(status_code=413, detail=str(e))
    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except DocumentProcessingError as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in ingest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during document ingestion")
    finally:
        # Cleanup temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {e}")

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query the document collection with semantic search."""
    try:
        container = get_container()
        if not container.rag_search:
            raise ServiceUnavailableError("RAG search service not initialized")
        
        if not request.query.strip():
            raise InvalidDocumentError("Query cannot be empty")
        
        result = container.rag_search.search(request.query, k=request.k)
        return JSONResponse(content=result)
    
    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except InvalidDocumentError as e:
        logger.warning(f"Invalid query: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error in query search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during search")

@app.post("/evaluate")
async def evaluate_retrieval(request: EvaluateRequest):
    """Evaluate retrieval quality for a query."""
    try:
        container = get_container()
        if not container.rag_search:
            raise ServiceUnavailableError("RAG search service not initialized")
        
        if not request.query.strip():
            raise InvalidDocumentError("Query cannot be empty")
        
        # Get search results
        search_result = container.rag_search.search(request.query, k=request.k)
        results = search_result.get("results", [])
        
        if not results:
            return JSONResponse(content={
                "query": request.query,
                "message": "No results found to evaluate",
                "average_score": 0,
                "results": []
            })
        
        # Extract chunk texts and evaluate
        chunks = [result["text"] for result in results]
        try:
            evaluation = evaluate_batch(request.query, chunks)
        except Exception as e:
            logger.warning(f"Evaluation failed: {e} - returning results without scores")
            # Return results without evaluation scores if evaluation fails
            return JSONResponse(content={
                "query": request.query,
                "results": results,
                "average_relevance_score": 0,
                "retrieval_time_ms": search_result.get("retrieval_time_ms", 0),
                "num_results": len(results),
                "evaluation_error": "Evaluation service unavailable"
            })
        
        # Combine results with evaluations
        for i, result in enumerate(results):
            if i < len(evaluation["evaluations"]):
                result["evaluation"] = evaluation["evaluations"][i]
        
        return JSONResponse(content={
            "query": request.query,
            "results": results,
            "average_relevance_score": evaluation["average_score"],
            "retrieval_time_ms": search_result.get("retrieval_time_ms", 0),
            "num_results": len(results)
        })
    
    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except InvalidDocumentError as e:
        logger.warning(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error in evaluate: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during evaluation")

@app.get("/stats")
async def get_stats():
    """Get collection statistics."""
    try:
        container = get_container()
        if not container.vector_store:
            raise ServiceUnavailableError("Vector store not initialized")
        
        stats = container.vector_store.get_stats()
        return JSONResponse(content=stats)
    
    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except VectorStoreError as e:
        logger.error(f"Vector store error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/clear")
async def clear_collection():
    """Clear all documents from the collection."""
    try:
        container = get_container()
        if not container.vector_store:
            raise ServiceUnavailableError("Vector store not initialized")
        
        container.vector_store.clear()
        logger.info("Collection cleared successfully")
        return JSONResponse(content={
            "status": "success",
            "message": "Collection cleared successfully"
        })
    
    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except VectorStoreError as e:
        logger.error(f"Vector store error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Error clearing collection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
