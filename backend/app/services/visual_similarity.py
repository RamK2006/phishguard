"""PhishGuard — Visual Similarity Service.

Placeholder for brand visual similarity detection.
Runs without Qdrant in serverless mode.
"""

from typing import Dict, Any
import structlog

logger = structlog.get_logger()


async def check_visual_similarity(url: str) -> Dict[str, Any]:
    """Check URL against brand visual embedding database.

    Returns similarity score and matched brand if any.
    In serverless mode, returns a default (no Qdrant available).
    """
    try:
        return {
            "available": False,
            "score": 0.0,
            "matched_brand": None,
            "similarity": 0.0,
        }
    except Exception as e:
        logger.warning("visual_similarity_check_failed", error=str(e))
        return {"available": False, "score": 0.0}


async def init_brand_collection():
    """No-op in serverless mode."""
    pass
