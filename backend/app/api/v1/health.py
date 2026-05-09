"""PhishGuard — Health & Metrics Endpoints.

GET /health, GET /metrics, GET /stream/scans (SSE)
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST,
)
import asyncio
import json
from datetime import datetime
import structlog

from app.services.ml_inference import is_model_loaded

logger = structlog.get_logger()

router = APIRouter(tags=["health"])

# ─── Prometheus Metrics ───
SCAN_COUNT = Counter("scan_risk_level_total", "Total scans by risk level", ["risk_level"])
HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])
HTTP_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"])
ML_INFERENCE_DURATION = Histogram("ml_inference_duration_seconds", "ML inference duration", ["model_name"])
CACHE_HITS = Counter("cache_hits_total", "Cache hits")
CACHE_MISSES = Counter("cache_misses_total", "Cache misses")
FALSE_POSITIVE_REPORTS = Counter("false_positive_reports_total", "False positive reports")
MODEL_ACCURACY = Gauge("model_accuracy_gauge", "Current model accuracy")


@router.get("/health")
async def health_check():
    """Health check endpoint — verifies all downstream dependencies."""
    checks = {}

    # Database
    try:
        from app.db.session import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:100]}"

    # Redis
    try:
        from app.core.limiter import get_redis
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:100]}"

    # Qdrant
    try:
        from qdrant_client import QdrantClient
        from app.core.config import settings
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=5)
        client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"error: {str(e)[:100]}"

    # ML Model
    checks["ml_model"] = "loaded" if is_model_loaded() else "not_loaded (heuristic mode)"

    all_ok = all(v == "ok" or v.startswith("loaded") or "heuristic" in v for v in checks.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return StreamingResponse(
        iter([generate_latest()]),
        media_type=CONTENT_TYPE_LATEST,
    )


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
