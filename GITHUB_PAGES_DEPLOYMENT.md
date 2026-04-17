# Deployment Guide

Your Document Intelligence RAG system is ready to deploy! Here's how to get it live:

## 1. Deploy Frontend to GitHub Pages

The frontend (HTML/CSS/JS) is already in the `docs/` folder.

**Step 1:** Go to your GitHub repo → Settings → Pages
**Step 2:** Under "Build and deployment", select:
- Source: `Deploy from a branch`
- Branch: `master`
- Folder: `/docs`

**Step 3:** Click Save. Your frontend will be live at:
```
https://ss889.github.io/voice/
```

---

## 2. Deploy Backend API to Render (Free)

The FastAPI backend needs to run somewhere. **Render** has a free tier and is perfect for this.

### Option A: Deploy via Render Dashboard (Easiest)

1. **Sign up** at https://render.com (free tier available)

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo (ss889/voice)
   - Name: `voice-rag-api`
   - Environment: `Python 3.10`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free (for testing)

3. **Add Environment Variables:**
   - Click "Environment"
   - Add key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (sk-proj-...)
   - Click "Save"

4. **Deploy:**
   - Render will auto-deploy when you push to GitHub
   - Your API will be at: `https://voice-rag-api.onrender.com` (example)

### Option B: Deploy via render.yaml (Automatic)

A `render.yaml` file in the repo root automates setup. See `render.yaml` in this repo.

---

## 3. Connect Frontend to Backend

Once your backend is deployed, update the API URL in the frontend:

**In GitHub Pages (docs/index.html):**
- Find this line: `const API_BASE_URL = localStorage.getItem('apiUrl') || 'http://localhost:8000';`
- The frontend will try to use localStorage first (for user customization)
- If deployed to Render, it will auto-detect

**Or:** Users can set the API URL via browser console:
```javascript
localStorage.setItem('apiUrl', 'https://your-api.onrender.com');
location.reload();
```

---

## 4. Enable CORS on Backend

The frontend (on GitHub Pages) calls the backend (on Render). CORS must be enabled.

This is already configured in `src/main.py`. If you see CORS errors, ensure:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Full Architecture

```
┌─────────────────────────┐
│  GitHub Pages           │
│  (ss889.github.io/voice)│  ← Frontend: HTML/CSS/JS
│                         │
│  Calls →→→→→→→→→→→→→→→→→┼─────────────────┐
└─────────────────────────┘                 │
                                            │
                              ┌─────────────▼──────────┐
                              │  Render                │
                              │  (FastAPI Backend)     │
                              │                        │
                              │  /upload               │
                              │  /query                │
                              │  /evaluate             │
                              │  /stats                │
                              └────────────────────────┘
                                      │
                                      │ Uses
                                      ▼
                              ┌─────────────────────┐
                              │  OpenAI API         │
                              │  - Embeddings       │
                              │  - Evaluation       │
                              └─────────────────────┘
                              
                              + Optional: Qdrant Vector DB
                              (or use in-memory MockVectorStore)
```

---

## Testing Locally First

Before deploying, test locally:

```bash
# Terminal 1: Start API
cd c:\Users\saber\voice\document_intelligence
python -m uvicorn src.main:app --reload

# Terminal 2: Open frontend
# Open file:///c:/Users/saber/voice/document_intelligence/docs/index.html
```

Update the API URL in the browser to `http://localhost:8000` if needed.

---

## Troubleshooting

### "Backend not available"
- Check that your Render service is running (green icon on Render dashboard)
- Verify API URL is correct: https://voice-rag-api.onrender.com (adjust name)
- Check CORS is enabled in src/main.py

### "Upload fails"
- Ensure OPENAI_API_KEY is set in Render environment variables
- Check Render logs: go to your service → Logs

### "Embeddings slow"
- This is normal for OpenAI API (~200ms per request)
- Batch processing included: up to 100 texts at once
- Use Vercel: https://vercel.com for API (free tier, good for Python)

---

## Next Steps

1. ✅ Push to GitHub (already done)
2. ⏳ Enable GitHub Pages (see Step 1 above)
3. ⏳ Deploy to Render (see Step 2 above)
4. ⏳ Test end-to-end
5. ⏳ Share link with others!

---

## Quick Links

- **Frontend**: https://ss889.github.io/voice/
- **Code**: https://github.com/ss889/voice
- **Backend** (after deployment): https://voice-rag-api.onrender.com (example)

---

**Questions?** Check the backend logs on Render or test locally first.
