import requests
import json
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server implementation
class DocumentIntelligenceMCPServer:
    """MCP Server for Document Intelligence Pipeline"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
    
    def ingest_document(self, file_path: str) -> dict:
        """Ingest a document"""
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(f"{self.api_url}/ingest", files=files)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            logger.error(f"Error in ingest_document: {e}")
            return {"error": str(e)}
    
    def query_documents(self, query: str, k: int = 5) -> dict:
        """Query documents"""
        try:
            response = requests.post(
                f"{self.api_url}/query",
                json={"query": query, "k": k}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            logger.error(f"Error in query_documents: {e}")
            return {"error": str(e)}
    
    def evaluate_retrieval(self, query: str, k: int = 5) -> dict:
        """Evaluate retrieval quality"""
        try:
            response = requests.post(
                f"{self.api_url}/evaluate",
                json={"query": query, "k": k}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            logger.error(f"Error in evaluate_retrieval: {e}")
            return {"error": str(e)}
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            logger.error(f"Error in get_stats: {e}")
            return {"error": str(e)}
    
    def delete_document(self, source: str) -> dict:
        """Delete a document (via clear for MVP)"""
        try:
            # For MVP, we clear the entire collection
            # In production, implement filtering by source
            response = requests.delete(f"{self.api_url}/clear")
            
            if response.status_code == 200:
                return {"status": "success", "message": f"Cleared collection (referenced: {source})"}
            else:
                return {"error": response.text}
        except Exception as e:
            logger.error(f"Error in delete_document: {e}")
            return {"error": str(e)}

# Tool definitions for MCP
TOOLS = {
    "ingest_document": {
        "description": "Ingest a document (PDF or TXT) into the system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file"
                }
            },
            "required": ["file_path"]
        }
    },
    "query_documents": {
        "description": "Query documents in the collection",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    "evaluate_retrieval": {
        "description": "Evaluate retrieval quality for a query",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to evaluate"
                },
                "k": {
                    "type": "integer",
                    "description": "Number of chunks to evaluate (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    "get_stats": {
        "description": "Get collection statistics",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    "delete_document": {
        "description": "Delete documents from the collection",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source document name (for MVP, clears entire collection)"
                }
            },
            "required": ["source"]
        }
    }
}

if __name__ == "__main__":
    # Example usage
    server = DocumentIntelligenceMCPServer()
    
    # Test tools
    print("Testing MCP Tools...")
    print("\nTool: get_stats")
    print(json.dumps(server.get_stats(), indent=2))
