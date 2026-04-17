import os
import json
from openai import OpenAI
from typing import Dict
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def evaluate_context_relevance(query: str, chunk: str) -> Dict:
    """
    Evaluate the relevance of a chunk to a query using LLM-as-a-Judge.
    
    Returns a score 1-5 with reasoning.
    """
    prompt = f"""You are evaluating retrieval quality for a RAG system.

Query: {query}

Retrieved Chunk: {chunk}

Rate the relevance of this chunk to the query on a scale of 1-5:
1 = Completely irrelevant - no connection to the query
2 = Somewhat related but not useful - tangentially related
3 = Moderately relevant - some useful information
4 = Highly relevant - directly addresses the query
5 = Perfect match - exactly what's needed

Respond in JSON format with:
- score: integer 1-5
- reasoning: brief explanation of your rating
- key_matches: list of 2-3 specific matching concepts"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure we have the required fields
        return {
            "score": int(result.get("score", 3)),
            "reasoning": result.get("reasoning", ""),
            "key_matches": result.get("key_matches", [])
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in evaluation: {e}")
        return {
            "score": 3,
            "reasoning": "Evaluation failed - JSON parsing error",
            "key_matches": []
        }
    except Exception as e:
        logger.error(f"Error in evaluate_context_relevance: {e}")
        return {
            "score": 3,
            "reasoning": f"Evaluation failed - {str(e)}",
            "key_matches": []
        }

def evaluate_batch(query: str, chunks: list) -> Dict:
    """Evaluate multiple chunks for a single query (synchronous wrapper)."""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    evaluations = []
    scores = []
    
    for chunk in chunks:
        result = loop.run_until_complete(evaluate_context_relevance(query, chunk))
        evaluations.append(result)
        scores.append(result["score"])
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "query": query,
        "evaluations": evaluations,
        "num_chunks": len(chunks),
        "average_score": round(avg_score, 2),
        "scores": scores
    }
