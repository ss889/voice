#!/bin/bash
# Quick start script for Document Intelligence Pipeline

set -e

echo "=================================="
echo "Document Intelligence Pipeline"
echo "Quick Start Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "✓ Docker found"

if ! command -v python &> /dev/null; then
    echo "⚠️  Python not found. Install Python 3.8+"
    exit 1
fi
echo "✓ Python found: $(python --version)"

# Create .env file
echo ""
echo "2. Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env file - PLEASE ADD YOUR OPENAI_API_KEY"
    echo "   Edit .env and set: OPENAI_API_KEY=sk-..."
else
    echo "✓ .env file exists"
fi

# Start Qdrant
echo ""
echo "3. Starting Qdrant..."
docker-compose up -d
echo "✓ Qdrant started on port 6333"
sleep 2

# Install dependencies
echo ""
echo "4. Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure you have OPENAI_API_KEY in .env"
echo ""
echo "2. Start the API server (Terminal 1):"
echo "   python -m uvicorn src.main:app --reload --port 8000"
echo ""
echo "3. Start the Streamlit dashboard (Terminal 2):"
echo "   streamlit run dashboard/app.py"
echo ""
echo "4. Then visit http://localhost:8501 to use the dashboard"
echo ""
echo "To test with sample documents:"
echo "   - Go to Upload tab"
echo "   - Select sample_docs/vector_databases.txt"
echo "   - Click Ingest"
echo "   - Try searching in the Search tab"
echo ""
echo "API Examples:"
echo "  Query: curl -X POST -H 'Content-Type: application/json' \\"
echo "           -d '{\"query\": \"What are vector databases?\"}' \\"
echo "           http://localhost:8000/query"
echo ""
