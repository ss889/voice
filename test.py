#!/usr/bin/env python
"""Test script for Document Intelligence Pipeline"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from src.config.settings import settings
        print("✓ Config settings")
        
        from src.document.parser import parse_text, parse_document
        print("✓ Document parser")
        
        from src.document.chunker import chunk_text
        print("✓ Document chunker")
        
        from src.vector.client import VectorStore
        print("✓ Vector store")
        
        from src.vector.embeddings import embed_text
        print("✓ Embeddings")
        
        from src.vector.search import RAGSearch
        print("✓ RAG search")
        
        from src.document.loader import DocumentLoader
        print("✓ Document loader")
        
        from src.evaluation.judge import evaluate_batch
        print("✓ Judge/evaluation")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_parser():
    """Test document parser"""
    print("\nTesting document parser...")
    from src.document.parser import parse_text
    
    # Create a test file
    test_file = Path("temp_test.txt")
    test_file.write_text("This is a test document.\nIt has multiple paragraphs.\nFor testing purposes.")
    
    try:
        result = parse_text(str(test_file))
        assert len(result) > 0
        assert "text" in result[0]
        assert "source" in result[0]
        print("✓ Text parsing works")
        return True
    except Exception as e:
        print(f"✗ Parser test failed: {e}")
        return False
    finally:
        test_file.unlink()

def test_chunker():
    """Test document chunker"""
    print("\nTesting document chunker...")
    from src.document.chunker import chunk_text
    
    long_text = """
    This is a test document for chunking.
    It has multiple sentences separated by periods.
    Each sentence is relatively short.
    We want to test the chunking algorithm.
    It should respect sentence boundaries.
    And maintain proper metadata.
    Including source and page number information.
    For each chunk that is created.
    Let's add more content here.
    To make sure we have enough text for multiple chunks.
    """ * 10
    
    metadata = {"source": "test.txt", "page_num": 1}
    
    try:
        chunks = chunk_text(long_text, metadata, chunk_size=512, chunk_overlap=100)
        assert len(chunks) > 1
        assert all("text" in c for c in chunks)
        assert all("chunk_index" in c for c in chunks)
        assert all("total_chunks" in c for c in chunks)
        print(f"✓ Chunking works ({len(chunks)} chunks created)")
        return True
    except Exception as e:
        print(f"✗ Chunker test failed: {e}")
        return False

def test_settings():
    """Test settings loading"""
    print("\nTesting settings...")
    from src.config.settings import settings
    
    try:
        assert settings.EMBEDDING_MODEL == "text-embedding-3-small"
        assert settings.EMBEDDING_DIMENSION == 1536
        assert settings.CHUNK_SIZE == 512
        print("✓ Settings loaded correctly")
        return True
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Document Intelligence Pipeline - Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Settings", test_settings),
        ("Parser", test_parser),
        ("Chunker", test_chunker),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
