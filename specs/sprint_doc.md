# Sprint Doc: Document Intelligence Pipeline MVP

## Goal
Working document RAG pipeline with Qdrant, semantic chunking, and evaluation.

## Time Budget: 90 minutes

### Task 1: Setup (15 min)
- [ ] Create directory structure
- [ ] Create docker-compose.yml
- [ ] Create requirements.txt:
  ```
  qdrant-client
  openai
  pdfplumber
  streamlit
  fastapi
  uvicorn
  mcp
  python-dotenv
  ```
- [ ] Start Qdrant: `docker-compose up -d`
- [ ] Create .env file for OpenAI API key
- [ ] Test Qdrant connection

### Task 2: Document Parser (10 min)
- [ ] src/document/parser.py with parse_pdf() and parse_text()
- [ ] Handle encoding errors gracefully
- [ ] Return list of dicts with page_num, text, source

### Task 3: Chunker (10 min)
- [ ] src/document/chunker.py with chunk_text()
- [ ] Configurable chunk_size and overlap
- [ ] Respect sentence boundaries
- [ ] Add metadata (chunk_index, total_chunks)

### Task 4: Vector Store (15 min)
- [ ] src/vector/client.py - Qdrant wrapper
- [ ] src/vector/embeddings.py - OpenAI embedding
- [ ] src/vector/search.py - retrieval logic
- [ ] Test: ingest → search flow

### Task 5: Document Loader (10 min)
- [ ] src/document/loader.py - full pipeline
- [ ] Load → Parse → Chunk → Embed → Store

### Task 6: FastAPI Server (10 min)
- [ ] src/main.py with endpoints:
  - POST /ingest - upload and process
  - POST /query - RAG search
  - GET /stats - collection stats

### Task 7: LLM Judge (10 min)
- [ ] src/evaluation/judge.py with evaluate_context_relevance()
- [ ] Use GPT-4o-mini, temperature=0
- [ ] Structured JSON output

### Task 8: MCP Server (5 min)
- [ ] src/mcp_server.py with 5 tools
- [ ] Test each tool

### Task 9: Streamlit Dashboard (5 min)
- [ ] dashboard/app.py with 4 tabs
- [ ] Wire to backend

## Definition of Done
- [ ] Can ingest PDF and text files
- [ ] Documents chunked and stored in Qdrant
- [ ] Queries return relevant results
- [ ] Evaluation produces scores
- [ ] MCP tools functional
- [ ] Dashboard works
