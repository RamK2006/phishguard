"""PhishGuard — Redis-backed Data Store.

Replaces SQLAlchemy/PostgreSQL with Upstash Redis for serverless deployment.
Stores scan events as JSON in Redis with TTL.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
import structlog

from app.core.limiter import get_redis

logger = structlog.get_logger()

# TTL for scan events: 30 days
SCAN_TTL = 30 * 24 * 3600


async def store_scan_event(scan_data: Dict[str, Any]) -> None:
    """Store a scan event in Redis."""
    try:
        redis = get_redis()
        if redis is None:
            return

        scan_id = scan_data.get("scan_id", str(uuid.uuid4()))

        # Store individual scan
        redis.set(
            f"scan_event:{scan_id}",
            json.dumps(scan_data, default=str),
            ex=SCAN_TTL,
        )

        # Add to recent scans list (capped at 1000)
        redis.lpush("scan_events:recent", scan_id)
        redis.ltrim("scan_events:recent", 0, 999)

        # Increment counters
        risk_level = scan_data.get("risk_level", "safe")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        redis.incr(f"stats:total:{today}")
        redis.expire(f"stats:total:{today}", 90 * 86400)
        redis.incr(f"stats:{risk_level}:{today}")
        redis.expire(f"stats:{risk_level}:{today}", 90 * 86400)

    except Exception as e:
        logger.error("store_scan_event_failed", error=str(e))


async def get_scan_event(scan_id: str) -> Optional[Dict]:
    """Get a specific scan event."""
    try:
        redis = get_redis()
        if redis is None:
            return None
        data = redis.get(f"scan_event:{scan_id}")
        return json.loads(data) if data else None
    except Exception as e:
        logger.error("get_scan_event_failed", error=str(e))
        return None


async def get_recent_scans(page: int = 1, limit: int = 20) -> Dict:
    """Get paginated recent scans."""
    try:
        redis = get_redis()
        if redis is None:
            return {"scans": [], "total": 0, "page": page, "limit": limit, "pages": 0}

        start = (page - 1) * limit
        end = start + limit - 1

        scan_ids = redis.lrange("scan_events:recent", start, end)
        total = redis.llen("scan_events:recent") or 0

        scans = []
        for scan_id in (scan_ids or []):
            data = redis.get(f"scan_event:{scan_id}")
            if data:
                scans.append(json.loads(data))

        return {
            "scans": scans,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 0,
        }
    except Exception as e:
        logger.error("get_recent_scans_failed", error=str(e))
        return {"scans": [], "total": 0, "page": page, "limit": limit, "pages": 0}


async def get_summary_stats(days: int = 7) -> Dict:
    """Get scan summary statistics from Redis counters."""
    try:
        redis = get_redis()
        if redis is None:
            return _empty_stats(days)

        from datetime import timedelta
        total = 0
        malicious = 0
        suspicious = 0
        safe = 0

        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            t = redis.get(f"stats:total:{date}")
            m = redis.get(f"stats:malicious:{date}")
            s = redis.get(f"stats:suspicious:{date}")
            sf = redis.get(f"stats:safe:{date}")
            total += int(t) if t else 0
            malicious += int(m) if m else 0
            suspicious += int(s) if s else 0
            safe += int(sf) if sf else 0

        return {
            "period_days": days,
            "total_scans": total,
            "malicious": malicious,
            "suspicious": suspicious,
            "safe": safe,
            "malicious_rate": round(malicious / max(total, 1) * 100, 2),
            "avg_latency_ms": 0,
        }
    except Exception as e:
        logger.error("get_summary_stats_failed", error=str(e))
        return _empty_stats(days)


async def store_feedback(feedback_data: Dict) -> None:
    """Store feedback in Redis."""
    try:
        redis = get_redis()
        if redis is None:
            return
        feedback_id = feedback_data.get("feedback_id", str(uuid.uuid4()))
        redis.set(
            f"feedback:{feedback_id}",
            json.dumps(feedback_data, default=str),
            ex=SCAN_TTL,
        )
    except Exception as e:
        logger.error("store_feedback_failed", error=str(e))


def _empty_stats(days: int) -> Dict:
    return {
        "period_days": days,
        "total_scans": 0,
        "malicious": 0,
        "suspicious": 0,
        "safe": 0,
        "malicious_rate": 0.0,
        "avg_latency_ms": 0,
    }
