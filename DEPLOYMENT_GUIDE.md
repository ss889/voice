# Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (Streamlit Dashboard / CLI / External Systems)             │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────▼──────┐
         │  FastAPI     │ (Port 8000)
         │  REST API    │
         └───────┬──────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌────▼─────┐  ┌──▼────┐
│Document│  │  Vector   │  │ LLM   │
│Pipeline│  │  Store    │  │ Judge │
└────────┘  └───┬──────┘  └───────┘
                │
            ┌───▼──────┐
            │  Qdrant  │ (Port 6333)
            │  Vector  │
            │   DB     │
            └──────────┘
```

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 2GB Disk (for Qdrant data)
- Docker (for Qdrant)

### Recommended
- Python 3.11+
- 8GB RAM
- 10GB Disk
- Docker with 4GB memory allocation

## Installation Steps

### 1. Clone/Setup
```bash
cd document_intelligence
```

### 2. Environment Setup
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 3. Start Qdrant (Required)
```bash
docker-compose up -d

# Verify it's running
curl http://localhost:6333/health
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Start API Server
```bash
# Terminal 1
python -m uvicorn src.main:app --reload --port 8000
```

### 6. Start Streamlit Dashboard
```bash
# Terminal 2
streamlit run dashboard/app.py
```

### 7. Access Dashboard
Open browser to: http://localhost:8501

---

## Usage Examples

### Via Dashboard (Easiest)
1. Go to Upload tab
2. Select a .txt or .pdf file
3. Click "Ingest"
4. Go to Search tab
5. Enter query and click "Search"
6. Go to Evaluate tab to see quality scores

### Via API (Programmatic)

**Ingest Document:**
```bash
curl -X POST \
  -F "file=@sample_docs/vector_databases.txt" \
  http://localhost:8000/ingest
```

**Query Documents:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "What are vector databases?", "k": 5}' \
  http://localhost:8000/query
```

**Evaluate Retrieval:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "How does semantic search work?", "k": 3}' \
  http://localhost:8000/evaluate
```

**Get Stats:**
```bash
curl http://localhost:8000/stats
```

**Clear Collection:**
```bash
curl -X DELETE http://localhost:8000/clear
```

### Via Python (Programmatic)

```python
from src.vector.client import VectorStore
from src.document.loader import DocumentLoader
from src.vector.search import RAGSearch
from src.vector import embeddings
from src.config.settings import settings

# Initialize
vector_store = VectorStore()
loader = DocumentLoader(vector_store)

# Ingest document
result = loader.load_document("sample_docs/vector_databases.txt")
print(f"Ingested {result['chunks_indexed']} chunks")

# Search
rag_search = RAGSearch(vector_store, embeddings)
results = rag_search.search("What are vector databases?", k=5)
for result in results['results']:
    print(f"Score: {result['score']:.3f} - {result['text'][:100]}...")
```

---

## Docker Compose Details

### Qdrant Service

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT_API_KEY=test_key
```

**Port**: 6333 (HTTP API)  
**Data**: Persisted in `qdrant_storage` volume  
**API Key**: `test_key` (configurable)

### Managing Qdrant

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs qdrant

# Reset data
docker-compose down -v
docker-compose up -d

# Access console
curl http://localhost:6333/docs  # Swagger UI
```

---

## Configuration

### Environment Variables (.env)

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...              # Required

# Qdrant Configuration
QDRANT_HOST=localhost              # Default: localhost
QDRANT_PORT=6333                   # Default: 6333
QDRANT_API_KEY=test_key            # Default: test_key

# Feature Configuration (in src/config/settings.py)
CHUNK_SIZE=512                     # Character size of chunks
CHUNK_OVERLAP=100                  # Character overlap between chunks
DEFAULT_K=5                        # Default number of results
```

### Code Configuration (src/config/settings.py)

```python
from src.config.settings import settings

settings.EMBEDDING_MODEL          # "text-embedding-3-small"
settings.EMBEDDING_DIMENSION      # 1536
settings.QDRANT_COLLECTION_NAME   # "documents"
settings.JUDGE_MODEL              # "gpt-4o-mini"
```

---

## Troubleshooting

### "Connection refused to Qdrant"
```bash
# Check if Qdrant is running
docker-compose ps

# If not running, start it
docker-compose up -d

# Test connection
curl http://localhost:6333/health
```

### "OPENAI_API_KEY not set"
```bash
# Check .env file exists
ls -la .env

# Add key if missing
echo "OPENAI_API_KEY=sk-..." >> .env
```

### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or with upgrade
pip install --upgrade -r requirements.txt
```

### "Port 6333 already in use"
```bash
# Find and stop the process
lsof -i :6333
kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Slow embeddings
```bash
# Use batch processing (automatic)
# Reduce batch size in src/vector/embeddings.py if needed
```

### API crashes
```bash
# Check logs
python -m uvicorn src.main:app --reload --port 8000

# Enable debug
# Set logging level in src/main.py
logging.basicConfig(level=logging.DEBUG)
```

---

## Performance Tuning

### Faster Embeddings
- Qdrant automatically batches embeddings
- Max batch size: 100 (OpenAI limit)
- Larger batches = faster per-document but higher latency

### Faster Search
- Qdrant optimizes automatically
- Use HNSW index (default)
- Typical search: <50ms

### Reduce Memory
- Process documents one at a time
- Clear collection between batches
- Use streaming for large files

### Batch Processing
```python
from src.document.loader import DocumentLoader

# Load directory of documents
results = loader.load_directory("./documents")
```

---

## Production Deployment

### Option 1: Docker Deployment
```bash
# Build app container
docker build -t doc-intelligence .

# Run with Qdrant
docker-compose up -d

# Run app in container
docker run -p 8000:8000 --env-file .env doc-intelligence
```

### Option 2: Cloud Deployment
```bash
# Deploy to AWS/GCP/Azure
# 1. Use managed Qdrant (Qdrant Cloud)
# 2. Update QDRANT_HOST in .env
# 3. Deploy API to serverless (Lambda, Cloud Run)
# 4. Deploy Streamlit to app hosting
```

### Option 3: Kubernetes
```bash
# Create k8s manifests
# Deploy Qdrant StatefulSet
# Deploy API as Deployment
# Expose via Service
```

---

## Monitoring & Logging

### Application Logs
```python
# Logs are printed to console
# Configure in src/main.py
import logging
logging.basicConfig(level=logging.INFO)
```

### Vector DB Health
```bash
# Check Qdrant status
curl http://localhost:6333/health

# Get collection stats
curl http://localhost:6333/collections/documents
```

### API Health
```bash
# Health check endpoint
curl http://localhost:8000/health
```

---

## Scaling Considerations

### Single Node
- Works for up to ~100K documents
- Max latency increase as collection grows

### Multi-Node
- Deploy Qdrant in cluster mode
- Use load balancer for API
- Add caching layer (Redis)

### Cloud Scale
- Use Qdrant Cloud (managed)
- Use serverless API (Lambda)
- Use CDN for static assets

---

## Security Considerations

### Current State
- API is open (no authentication)
- Qdrant has test API key
- No rate limiting

### For Production
1. Add API key authentication
2. Use strong Qdrant API key
3. Add rate limiting
4. Use HTTPS/TLS
5. Add CORS configuration
6. Enable audit logging

### Example: Add API Key Auth
```python
from fastapi import Header, HTTPException

@app.post("/query")
async def query_documents(
    query: str,
    k: int = 5,
    x_api_key: str = Header(...)
):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of implementation
```

---

## Support & Debugging

### View Logs
```bash
# FastAPI logs
# Terminal 1: python -m uvicorn ... (shows logs)

# Qdrant logs
docker-compose logs qdrant

# Streamlit logs
# Terminal 2: streamlit run ... (shows logs)
```

### Test Components
```bash
# Test parser
python -m src.document.parser

# Test chunker
python -m src.document.chunker

# Test embeddings
python -m src.vector.embeddings

# Run all tests
python test.py
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add breakpoints
import pdb; pdb.set_trace()
```

---

## Next Steps

1. **Try It Out**
   - Run dashboard with sample documents
   - Test search and evaluation

2. **Integrate**
   - Add to your application
   - Use API endpoints or MCP tools

3. **Extend**
   - Add more document formats
   - Implement custom evaluation metrics
   - Add authentication

4. **Deploy**
   - Choose hosting platform
   - Set up monitoring
   - Configure backups

---

**For questions or issues, refer to README.md and source code documentation.**
