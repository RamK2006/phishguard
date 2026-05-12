"""PhishGuard — Health & Metrics Endpoints.

GET /health, GET /stream/scans (SSE), GET /bloom/sync
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime
import structlog

from app.services.ml_inference import is_model_loaded

logger = structlog.get_logger()

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint — verifies all downstream dependencies."""
    checks = {}

    # Redis
    try:
        from app.core.limiter import get_redis
        redis = get_redis()
        if redis:
            redis.ping()
            checks["redis"] = "ok"
        else:
            checks["redis"] = "not_configured"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:100]}"

    # ML Model
    checks["ml_model"] = "loaded" if is_model_loaded() else "not_loaded (heuristic mode)"

    # Gemini API
    from app.core.config import settings
    checks["gemini_api"] = "configured" if settings.gemini_api_key else "not_configured"

    all_ok = all(
        v in ("ok", "configured", "not_configured") or "loaded" in v or "heuristic" in v
        for v in checks.values()
    )

    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stream/scans")
async def stream_scans():
    """SSE endpoint for real-time scan events."""
    async def event_generator():
        while True:
            event_data = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/bloom/sync")
async def bloom_sync():
    """Endpoint for extension to sync Bloom filter data."""
    from app.services.cache import get_bloom_filter_urls
    urls = await get_bloom_filter_urls()
    return {"urls": urls, "count": len(urls)}
