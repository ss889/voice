# File Directory Guide

## Quick Navigation

### 🚀 START HERE
- **START_HERE.md** - Read this first! Quick overview and checklist
- **README.md** - Full documentation, usage examples, architecture

### 📋 Planning & QA Documents
- **specs/feature_spec.md** - What we're building (detailed requirements)
- **specs/qa_feature_spec.md** - Validation of feature spec ✓
- **specs/sprint_doc.md** - How to build it (90-min sprint plan)
- **specs/qa_sprint_doc.md** - Validation of sprint plan ✓
- **specs/qa_implementation.md** - Final QA and results ✓

### 📊 Project Summaries
- **COMPLETION_SUMMARY.md** - What was delivered in 2.5 hours
- **DEPLOYMENT_GUIDE.md** - How to run in production
- **INTERVIEW_GUIDE.md** - How to talk about this in interviews

### ⚙️ Configuration Files
- **.env.example** - Copy this to .env and add your OpenAI key
- **docker-compose.yml** - Starts Qdrant vector database
- **requirements.txt** - Python dependencies

### 🏃 Quick Start Scripts
- **quickstart.sh** - Linux/Mac setup script
- **quickstart.bat** - Windows setup script
- **test.py** - Unit tests

### 📁 Source Code

#### Core Modules
```
src/
├── config/
│   └── settings.py          ← Configuration management
├── document/
│   ├── parser.py            ← PDF/TXT file parsing
│   ├── chunker.py           ← Semantic chunking with boundaries
│   └── loader.py            ← Full ingestion pipeline
├── vector/
│   ├── client.py            ← Qdrant vector store wrapper
│   ├── embeddings.py        ← OpenAI embedding integration
│   └── search.py            ← RAG retrieval logic
├── evaluation/
│   ├── judge.py             ← LLM-as-a-Judge evaluation
│   └── metrics.py           ← Evaluation metrics (extensible)
├── main.py                  ← FastAPI REST API server
└── mcp_server.py            ← MCP tool definitions
```

### 🎨 User Interface
```
dashboard/
└── app.py                   ← Streamlit dashboard (4 tabs)
```

### 📚 Test Data
```
sample_docs/
├── vector_databases.txt     ← About vector databases
├── rag_systems.txt          ← About RAG systems
└── semantic_search.txt      ← About semantic search
```

---

## File Purposes

### Configuration & Setup
| File | Purpose |
|------|---------|
| .env.example | Template for environment variables |
| requirements.txt | Python package dependencies |
| docker-compose.yml | Docker Qdrant setup |
| settings.py | Centralized config (chunk size, models, etc.) |

### Document Processing
| File | Purpose |
|------|---------|
| parser.py | Parse PDF and TXT files |
| chunker.py | Split text into chunks preserving meaning |
| loader.py | Orchestrate ingestion: parse → chunk → embed → store |

### Vector Search
| File | Purpose |
|------|---------|
| client.py | Qdrant connection and operations |
| embeddings.py | OpenAI embedding calls and batching |
| search.py | Query embedding and result retrieval |

### Evaluation
| File | Purpose |
|------|---------|
| judge.py | LLM-based quality evaluation |
| metrics.py | Place for additional metrics |

### APIs & Integration
| File | Purpose |
|------|---------|
| main.py | FastAPI REST endpoints |
| mcp_server.py | MCP tool definitions for AI integration |

### User Interface
| File | Purpose |
|------|---------|
| app.py | Streamlit dashboard with 4 tabs |

### Testing & Documentation
| File | Purpose |
|------|---------|
| test.py | Unit tests for core modules |
| START_HERE.md | Quick start guide |
| README.md | Full documentation |
| DEPLOYMENT_GUIDE.md | Production deployment instructions |
| INTERVIEW_GUIDE.md | Interview preparation material |

---

## Reading Order by Use Case

### I want to run it immediately
1. START_HERE.md (5 min)
2. quickstart.bat (or quickstart.sh)
3. Try the dashboard

### I want to understand the architecture
1. README.md - Architecture section
2. src/main.py - See the API structure
3. src/document/loader.py - See the pipeline

### I want to understand the code
1. src/config/settings.py - See configuration
2. src/document/parser.py - Start simple (parsing)
3. src/document/chunker.py - Then chunking logic
4. src/vector/embeddings.py - Then embedding
5. src/vector/client.py - Then vector store
6. src/evaluation/judge.py - Then evaluation

### I want to use this in production
1. DEPLOYMENT_GUIDE.md (full instructions)
2. docker-compose.yml (modify for your setup)
3. src/config/settings.py (adjust parameters)
4. INTERVIEW_GUIDE.md (understand tradeoffs)

### I have an interview tomorrow
1. INTERVIEW_GUIDE.md (read everything)
2. COMPLETION_SUMMARY.md (understand what you built)
3. Try running it successfully

### I want to extend this
1. README.md - Extensibility section
2. Look at existing modules as examples
3. src/document/ - Add new document formats
4. src/evaluation/ - Add new metrics
5. dashboard/app.py - Add new tabs

---

## Key Modules & Their Responsibility

### Entry Points
- **src/main.py** - REST API entry point (FastAPI)
- **src/mcp_server.py** - MCP tool entry point
- **dashboard/app.py** - UI entry point (Streamlit)

### Data Pipeline
```
Input File → parser.py → pages
           → chunker.py → chunks
           → embeddings.py → vectors
           → client.py → stored in Qdrant
```

### Query Pipeline
```
Query → embeddings.py → query_vector
      → client.py → search Qdrant
      → results with scores and source
```

### Evaluation Pipeline
```
Query + Results → judge.py → Context Relevance score
                → structured JSON output
                → displayed in dashboard
```

---

## Testing

### Run Unit Tests
```bash
python test.py
```

Tests included:
- Import verification
- Settings loading
- Text parsing
- Chunking logic

### Manual Testing
```bash
# Test API
curl http://localhost:8000/health

# Ingest
curl -X POST -F "file=@sample_docs/vector_databases.txt" \
  http://localhost:8000/ingest

# Query
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What are vector databases?"}' \
  http://localhost:8000/query
```

---

## Customization Points

Want to customize? Here's where to change things:

| What | Where | How |
|------|-------|-----|
| Chunk size | settings.py | Change CHUNK_SIZE (default 512) |
| Embedding model | settings.py | Change EMBEDDING_MODEL |
| Number of results | settings.py | Change DEFAULT_K |
| Judge model | settings.py | Change JUDGE_MODEL |
| Qdrant config | docker-compose.yml | Change ports/volumes |
| New document format | parser.py | Add parse_docx(), etc. |
| New metric | metrics.py | Add new evaluation function |
| New tab in dashboard | app.py | Add with st.tabs() |
| New API endpoint | main.py | Add @app.post() or @app.get() |

---

## Deployment Checklist

Before deploying:
- [ ] .env has OPENAI_API_KEY
- [ ] docker-compose.yml configured for your environment
- [ ] requirements.txt installed
- [ ] tests pass (python test.py)
- [ ] Can ingest sample documents
- [ ] Search returns relevant results
- [ ] Evaluation produces scores

---

## Troubleshooting: Where to Look

| Problem | File to Check |
|---------|--------------|
| Qdrant won't start | docker-compose.yml, DEPLOYMENT_GUIDE.md |
| OpenAI API error | .env, src/config/settings.py |
| Parser failing | src/document/parser.py, test.py |
| Chunking issues | src/document/chunker.py |
| Embedding problems | src/vector/embeddings.py |
| Search not working | src/vector/client.py, src/vector/search.py |
| Evaluation errors | src/evaluation/judge.py |
| Dashboard not connecting | dashboard/app.py, src/main.py |

---

## Documentation Map

```
Project Documentation Hierarchy:

START_HERE.md (Quick overview)
    ├─ README.md (Full documentation)
    │   ├─ Architecture & Design
    │   ├─ Setup Instructions
    │   ├─ API Endpoints
    │   └─ Extensibility
    ├─ DEPLOYMENT_GUIDE.md (Production deployment)
    │   ├─ System Requirements
    │   ├─ Installation Steps
    │   ├─ Usage Examples
    │   ├─ Troubleshooting
    │   └─ Scaling
    ├─ INTERVIEW_GUIDE.md (Interview preparation)
    │   ├─ Elevator Pitch
    │   ├─ 2-Minute Story
    │   ├─ Q&A
    │   └─ Demo Script
    └─ Specs (Design documentation)
        ├─ feature_spec.md (Requirements)
        ├─ sprint_doc.md (Implementation plan)
        └─ qa_*.md files (Validation)
```

---

## Directory Structure

```
document_intelligence/
├── 📄 START_HERE.md                 ← READ THIS FIRST
├── 📄 README.md                     ← Full docs
├── 📄 DEPLOYMENT_GUIDE.md           ← Production guide
├── 📄 INTERVIEW_GUIDE.md            ← Interview prep
├── 📄 COMPLETION_SUMMARY.md         ← What was built
├── 📄 FILE_GUIDE.md                 ← This file
├── specs/                           ← Planning & QA
│   ├── feature_spec.md
│   ├── qa_feature_spec.md
│   ├── sprint_doc.md
│   ├── qa_sprint_doc.md
│   └── qa_implementation.md
├── src/                             ← Source code
│   ├── config/
│   │   └── settings.py
│   ├── document/
│   │   ├── parser.py
│   │   ├── chunker.py
│   │   └── loader.py
│   ├── vector/
│   │   ├── client.py
│   │   ├── embeddings.py
│   │   └── search.py
│   ├── evaluation/
│   │   ├── judge.py
│   │   └── metrics.py
│   ├── main.py
│   └── mcp_server.py
├── dashboard/
│   └── app.py
├── sample_docs/
│   ├── vector_databases.txt
│   ├── rag_systems.txt
│   └── semantic_search.txt
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── test.py
├── quickstart.sh
└── quickstart.bat
```

---

**Everything you need is here. Start with START_HERE.md or README.md.**
