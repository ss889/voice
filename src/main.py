from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import logging
from typing import List
from pathlib import Path

from src.config.settings import settings
from src.vector.search import RAGSearch
from src.document.loader import DocumentLoader
from src.evaluation.judge import evaluate_batch
from src.vector import embeddings as embeddings_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request bodies
class QueryRequest(BaseModel):
    query: str
    k: int = 5

class EvaluateRequest(BaseModel):
    query: str
    k: int = 5

# Initialize components
vector_store = None
try:
    from src.vector.client import VectorStore
    vector_store = VectorStore(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        vector_size=settings.EMBEDDING_DIMENSION
    )
    logger.info("✓ Using Qdrant vector store (Docker)")
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
    except Exception as e2:
        logger.error(f"Failed to initialize any vector store: {e2}")
        vector_store = None

document_loader = DocumentLoader(vector_store) if vector_store else None
rag_search = RAGSearch(vector_store, embeddings_module) if vector_store else None

app = FastAPI(title="Document Intelligence Pipeline")

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
    return {"status": "ok"}

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document and process it."""
    if not vector_store or not document_loader:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())  # Ensure file is written to disk
            tmp_path = tmp_file.name
        
        # File context closes here - ensure it's fully written
        # Load and process document
        result = document_loader.load_document(tmp_path)
        
        # Clean up
        try:
            os.remove(tmp_path)
        except:
            pass  # File might already be deleted
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in ingest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query the document collection."""
    if not rag_search:
        raise HTTPException(status_code=503, detail="RAG search not initialized")
    
    try:
        result = rag_search.search(request.query, k=request.k)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate")
async def evaluate_retrieval(request: EvaluateRequest):
    """Evaluate retrieval quality for a query."""
    if not rag_search:
        raise HTTPException(status_code=503, detail="RAG search not initialized")
    
    try:
        # Get search results
        search_result = rag_search.search(request.query, k=request.k)
        results = search_result.get("results", [])
        
        if not results:
            return JSONResponse(content={
                "query": request.query,
                "message": "No results found to evaluate",
                "average_score": 0
            })
        
        # Extract chunk texts
        chunks = [result["text"] for result in results]
        
        # Evaluate
        evaluation = evaluate_batch(request.query, chunks)
        
        # Combine with search results
        for i, result in enumerate(results):
            if i < len(evaluation["evaluations"]):
                result["evaluation"] = evaluation["evaluations"][i]
        
        return JSONResponse(content={
            "query": request.query,
            "results": results,
            "average_relevance_score": evaluation["average_score"],
            "retrieval_time_ms": search_result.get("retrieval_time_ms", 0)
        })
    except Exception as e:
        logger.error(f"Error in evaluate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get collection statistics."""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        stats = vector_store.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_collection():
    """Clear the collection."""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        vector_store.clear()
        return JSONResponse(content={"status": "success", "message": "Collection cleared"})
    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
