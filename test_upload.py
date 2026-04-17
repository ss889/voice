#!/usr/bin/env python
"""Test document upload locally."""

import sys
import os
from pathlib import Path

# Set up environment
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from src.document.parser import parse_document
from src.document.chunker import chunk_text
from src.config.settings import settings

def test_document(file_path):
    """Test parsing and chunking a document."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📄 Testing: {file_path.name}")
    print(f"📏 File size: {file_path.stat().st_size} bytes")
    
    # Parse
    print("\n1️⃣  Parsing...")
    pages = parse_document(str(file_path))
    print(f"✓ Got {len(pages)} pages")
    
    if not pages:
        print("❌ No content parsed!")
        return
    
    for i, page in enumerate(pages):
        text = page.get('text', '')
        print(f"  Page {i+1}: {len(text)} characters")
        if not text.strip():
            print(f"  ⚠️  Page {i+1} is empty!")
    
    # Chunk
    print("\n2️⃣  Chunking...")
    total_chunks = 0
    for page in pages:
        text = page.get('text', '')
        if not text.strip():
            continue
        
        metadata = {'source': file_path.name, 'page_num': page.get('page_num', 1)}
        chunks = chunk_text(text, metadata, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        print(f"✓ Created {len(chunks)} chunks from {len(text)} chars")
        total_chunks += len(chunks)
    
    print(f"\n✅ Total chunks: {total_chunks}")
    
    if total_chunks == 0:
        print("❌ No chunks created! Check the file content and chunking settings.")

if __name__ == '__main__':
    # Test with sample files
    test_files = [
        'sample_docs/vector_databases.txt',
        'sample_docs/rag_systems.txt',
    ]
    
    for test_file in test_files:
        test_document(test_file)
