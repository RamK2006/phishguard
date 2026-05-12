"""PhishGuard — Upstash Redis Rate Limiter.

Enforces per-client rate limits using Upstash Redis (HTTP-based).
Extension clients: 100 req/min. Analysts: 1000 req/min.
"""

import time
from typing import Optional
from fastapi import Request, HTTPException, status
import structlog

from app.core.config import settings

logger = structlog.get_logger()

_redis_client = None


def get_redis():
    """Get or create Upstash Redis client."""
    global _redis_client
    if _redis_client is None:
        if settings.upstash_redis_url and settings.upstash_redis_token:
            try:
                from upstash_redis import Redis
                _redis_client = Redis(
                    url=settings.upstash_redis_url,
                    token=settings.upstash_redis_token,
                )
            except Exception as e:
                logger.warning("upstash_redis_init_failed", error=str(e))
    return _redis_client


async def close_redis():
    """No-op for Upstash (HTTP-based, no persistent connection)."""
    pass


async def check_rate_limit(request: Request) -> None:
    """Simple rate limiter using Upstash Redis.

    Identifies client by Extension-Key header (extension) or IP (analyst).
    Raises 429 if rate limit exceeded.
    """
    redis = get_redis()
    if redis is None:
        # Fail open — no Redis configured, skip rate limiting
        return

    # Determine client identity and limit
    extension_key = request.headers.get("Extension-Key")
    if extension_key:
        client_id = f"ext:{extension_key}"
        max_requests = settings.rate_limit_extension
    else:
        client_id = f"ip:{request.client.host if request.client else 'unknown'}"
        max_requests = settings.rate_limit_analyst

    key = f"ratelimit:{client_id}"

    try:
        # Simple counter with TTL
        current = redis.get(key)
        if current is not None and int(current) >= max_requests:
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id,
                count=current,
                limit=max_requests,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {max_requests} requests per minute.",
                headers={"Retry-After": "60"},
            )
        # Increment counter
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        pipe.exec()
    except HTTPException:
        raise
    except Exception as e:
        # Fail open — don't block requests if Redis is down
        logger.error("rate_limit_check_failed", error=str(e))
