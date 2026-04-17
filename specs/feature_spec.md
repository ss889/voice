# Feature Spec: Document Intelligence Pipeline

## What We're Building
A production-ready RAG pipeline that ingests documents, chunks them intelligently, stores in a vector database, and evaluates retrieval quality.

## Core Features

### 1. Document Ingestion
**What it does:** Parse PDFs and text files, extract content with metadata.

**Requirements:**
- Support PDF (via pdfplumber) and .txt files
- Extract: text content, page number, source filename
- Handle encoding issues gracefully (utf-8 with fallback)

**Why this matters:** Document parsing is the foundation. If this breaks, everything breaks.

**Success criteria:**
- Successfully parses 3 sample documents
- Preserves page numbers and source attribution
- No silent failures on malformed files

### 2. Semantic Chunking
**What it does:** Split documents into chunks that preserve meaning.

**Requirements:**
- Default chunk size: 512 tokens (good balance for OpenAI embeddings)
- Overlap: 100 tokens (20% - prevents context loss at boundaries)
- Respect sentence boundaries when possible
- Metadata per chunk: chunk_index, total_chunks, source_doc, page_num

**Chunking strategy:**
```
1. Split by character count (512 chars)
2. Look backwards for sentence boundary (. ! ? \n)
3. If found within last 256 chars, use that as split point
4. Add overlap from previous chunk
```

**Why this matters:** Bad chunking = bad retrieval. I've seen systems fail because chunks cut off mid-sentence.

**Success criteria:**
- All text preserved (no gaps between chunks)
- Average chunk size within 400-600 char range
- Sentence boundaries respected >80% of time

### 3. Vector Database (Qdrant)
**What it does:** Store embeddings and enable semantic search.

**Requirements:**
- Use Qdrant (open source, runs locally)
- Collection name: "documents"
- Vector config: 1536 dimensions (OpenAI), Cosine distance
- Payload schema: source_doc, page_num, chunk_index, total_chunks, text

**Qdrant setup:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

volumes:
  qdrant_storage:
```

**Why this matters:** Vector DB is your retrieval engine. Qdrant is fast, free, and production-proven.

**Success criteria:**
- Qdrant starts in Docker without errors
- Collection created with correct config
- Upsert and search operations <100ms

### 4. Embedding Pipeline
**What it does:** Convert text to vectors using OpenAI embeddings.

**Requirements:**
- Use OpenAI `text-embedding-3-small` (cheap, good quality)
- Batch embedding for efficiency (max 100 texts per call)
- Same model for documents AND queries (critical!)

**Why this matters:** Embedding model choice affects retrieval quality significantly. Using different models for docs vs queries = broken retrieval.

**Success criteria:**
- Embeddings generated successfully
- Vector dimension matches Qdrant config (1536)
- Batch processing works

### 5. RAG Query Pipeline
**What it does:** Search for relevant chunks given a query.

**Requirements:**
- Embed query using same model as documents
- Retrieve top-k chunks (default k=5)
- Return: text, similarity score, source attribution

**Response format:**
```json
{
  "query": "What are vector databases?",
  "results": [
    {
      "text": "Vector databases store embeddings...",
      "score": 0.89,
      "source": "vector_db_guide.pdf",
      "page_num": 3,
      "chunk_index": 7
    }
  ],
  "retrieval_time_ms": 45
}
```

**Why this matters:** This is what users see. Fast, accurate retrieval is the product.

**Success criteria:**
- Query returns relevant results
- Scores are meaningful (higher = more relevant)
- Source attribution is clear
- Latency <100ms

### 6. LLM-as-a-Judge Evaluation
**What it does:** Evaluate retrieval quality using an LLM.

**Requirements:**
- Implement Context Relevance metric (is retrieved chunk relevant to query?)
- Use GPT-4o-mini (cheap, fast, good enough for evaluation)
- Temperature = 0 (deterministic scoring)
- Structured JSON output with reasoning

**Judge prompt:**
```
You are evaluating retrieval quality for a RAG system.

Query: {query}

Retrieved Chunk: {chunk}

Rate the relevance of this chunk to the query:
1 = Completely irrelevant
2 = Somewhat related but not useful
3 = Moderately relevant, some useful info
4 = Highly relevant, directly addresses query
5 = Perfect match, exactly what's needed

Respond in JSON:
{
  "score": 1-5,
  "reasoning": "brief explanation",
  "key_matches": ["specific matching concepts"]
}
```

**Why this matters:** You can't improve what you don't measure. Evaluation catches problems before they hit users.

**Success criteria:**
- Evaluation produces consistent scores
- Reasoning is explainable
- Runs in <2 seconds per query

### 7. MCP Server
**What it does:** Expose tools for integration.

**Requirements:**
- 5 tools: ingest_document, query_documents, evaluate_retrieval, get_stats, delete_document
- Clear input/output schemas
- Error handling with informative messages

**Why this matters:** MCP is your differentiator. Shows you understand modern AI integration patterns.

### 8. Streamlit Dashboard
**What it does:** Visual interface for the pipeline.

**Requirements:**
- 4 tabs: Upload, Search, Evaluate, Analytics
- Upload: File uploader, ingest button, progress indicator
- Search: Query input, results display with scores
- Evaluate: Run evaluation, view scores and reasoning
- Analytics: Stats (docs, chunks, avg scores), query history

**Why this matters:** Dashboard makes the system demoable. Interviewers can see it work.

## File Structure
```
document_intelligence/
├── specs/
│   ├── feature_spec.md
│   ├── qa_feature_spec.md
│   ├── sprint_doc.md
│   ├── qa_sprint_doc.md
│   └── qa_implementation.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── mcp_server.py
│   ├── document/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── chunker.py
│   │   └── loader.py
│   ├── vector/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── embeddings.py
│   │   └── search.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── judge.py
│   │   └── metrics.py
│   └── config/
│       └── settings.py
├── dashboard/
│   └── app.py
├── sample_docs/
│   ├── sample_1.txt
│   └── sample_2.txt
├── docker-compose.yml
├── requirements.txt
└── README.md
```
