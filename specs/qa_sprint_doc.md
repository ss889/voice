# QA Checklist for Sprint Doc

## Feasibility
- [x] All dependencies available (qdrant-client, openai, pdfplumber, streamlit, fastapi, mcp, python-dotenv)
- [x] Time estimates realistic: 15+10+10+15+10+10+10+5+5 = 90 min ✓
- [x] No blocking external services (Qdrant runs locally in Docker, OpenAI API available)

## Vector DB
- [x] Qdrant Docker setup is simple and reliable
- [x] Collection config will use Cosine distance and 1536 dimensions
- [x] Error handling noted for connection failures

## Chunking
- [x] Chunk size (512 chars) appropriate for context
- [x] Overlap (100 chars) is 20% as specified
- [x] Sentence boundary handling is specified

## Evaluation
- [x] Judge model specified (GPT-4o-mini)
- [x] Temperature = 0 for determinism
- [x] Structured output format defined

## MCP
- [x] All 5 tools specified with clear functionality
- [x] Tool schemas are simple and implementable

## Implementation Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Qdrant Docker won't start | Check docker status; can test with in-memory mode first |
| PDF parsing fails | Have text files as fallback; handle encoding gracefully |
| OpenAI rate limit | Add retry logic with exponential backoff |
| FastAPI startup issues | Keep endpoints minimal; test one at a time |
| Streamlit complexity | Use simple widgets first; iterate on design |
| MCP tool errors | Test each tool individually before integration |

## Task Ordering
- [x] Setup first (prerequisites for everything)
- [x] Parser before Chunker (need documents)
- [x] Chunker before Vector Store (need chunks)
- [x] Vector Store before Loader (need store to load into)
- [x] Loader before API (API depends on full pipeline)
- [x] Judge and Dashboard can be done in parallel

## Dependencies Between Tasks
- Setup (Task 1) → All others depend on this
- Parser (Task 2) → Required by Loader (Task 5)
- Chunker (Task 3) → Required by Loader (Task 5)
- Vector Store (Task 4) → Required by Loader (Task 5)
- Loader (Task 5) → Aggregates Tasks 2-4
- API (Task 6) → Uses Loader output
- Judge (Task 7) → Independent, can run in parallel
- MCP (Task 8) → Uses API endpoints
- Dashboard (Task 9) → Uses API endpoints

## Approved: YES ✓

**Sign-off:** Sprint doc is feasible within 90-minute window. Task breakdown is logical with clear dependencies. All deliverables are defined and measurable. Ready to implement.

**Key Success Factors:**
1. Start Docker immediately
2. Test each module independently before integration
3. Use provided code templates to save time
4. If stuck, simplify (e.g., text files only, single embedding, etc.)
5. Prioritize working > perfect
