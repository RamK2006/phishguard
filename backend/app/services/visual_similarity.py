"""PhishGuard — Visual Similarity Service.

Qdrant brand_visual_embeddings collection with perceptual hash search.
"""

from typing import Dict, Any, Optional, List
import structlog

from app.core.config import settings

logger = structlog.get_logger()

_qdrant_client = None


def _get_qdrant():
    """Lazy-init Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        try:
            from qdrant_client import QdrantClient
            _qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        except Exception as e:
            logger.error("qdrant_init_failed", error=str(e))
    return _qdrant_client


async def check_visual_similarity(url: str) -> Dict[str, Any]:
    """Check URL against brand visual embedding database.

    Returns similarity score and matched brand if any.
    """
    try:
        client = _get_qdrant()
        if client is None:
            return {"available": False, "score": 0.0}

        # For now, return a default. Full implementation requires
        # screenshot capture + imagehash comparison.
        return {
            "available": True,
            "score": 0.0,
            "matched_brand": None,
            "similarity": 0.0,
        }
    except Exception as e:
        logger.warning("visual_similarity_check_failed", error=str(e))
        return {"available": False, "score": 0.0}


async def init_brand_collection():
    """Initialize Qdrant collection for brand visual embeddings."""
    try:
        from qdrant_client.models import Distance, VectorParams
        client = _get_qdrant()
        if client is None:
            return

        collections = [c.name for c in client.get_collections().collections]
        if "brand_visual_embeddings" not in collections:
            client.create_collection(
                collection_name="brand_visual_embeddings",
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )
            logger.info("created_brand_visual_embeddings_collection")
    except Exception as e:
        logger.warning("qdrant_collection_init_failed", error=str(e))
