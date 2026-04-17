from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_text(file_path: str) -> List[Dict]:
    """Parse text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        logger.info(f"Parsed text file: {len(text)} characters")
        if not text.strip():
            logger.warning(f"Text file is empty: {file_path}")
            return []
        return [{"page_num": 1, "text": text, "source": Path(file_path).name}]
    except Exception as e:
        logger.error(f"Error parsing text file {file_path}: {e}")
        return []

def parse_pdf(file_path: str) -> List[Dict]:
    """Parse PDF file."""
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    pages.append({
                        "page_num": i,
                        "text": text,
                        "source": Path(file_path).name
                    })
        logger.info(f"Parsed {len(pages)} pages from {Path(file_path).name}")
        return pages
    except ImportError:
        logger.error("pdfplumber not installed. Run: pip install pdfplumber")
        return []
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return []

def parse_document(file_path: str) -> List[Dict]:
    """Parse document based on file extension."""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return parse_pdf(file_path)
    elif file_ext == '.txt':
        return parse_text(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_ext}")
        return []
