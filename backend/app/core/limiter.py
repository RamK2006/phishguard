"""PhishGuard — Redis Token-Bucket Rate Limiter.

Enforces per-client rate limits using Redis.
Extension clients: 100 req/min. Analysts: 1000 req/min.
"""

import time
from typing import Optional
from fastapi import Request, HTTPException, status
import redis.asyncio as aioredis
import structlog

from app.core.config import settings

logger = structlog.get_logger()

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create async Redis connection."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
    return _redis_client


async def close_redis():
    """Close Redis connection on shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def check_rate_limit(request: Request) -> None:
    """Token-bucket rate limiter.

    Identifies client by Extension-Key header (extension) or user ID (analyst).
    Raises 429 if rate limit exceeded.
    """
    redis = await get_redis()

    # Determine client identity and limit
    extension_key = request.headers.get("Extension-Key")
    if extension_key:
        client_id = f"ext:{extension_key}"
        max_requests = settings.rate_limit_extension
    else:
        # Use IP as fallback identifier
        client_id = f"ip:{request.client.host if request.client else 'unknown'}"
        max_requests = settings.rate_limit_analyst

    key = f"ratelimit:{client_id}"
    window = 60  # 1 minute window

    try:
        pipe = redis.pipeline()
        now = time.time()
        window_start = now - window

        # Remove expired entries
        await pipe.zremrangebyscore(key, 0, window_start)
        # Count current window
        await pipe.zcard(key)
        # Add current request
        await pipe.zadd(key, {str(now): now})
        # Set expiry on key
        await pipe.expire(key, window)

        results = await pipe.execute()
        request_count = results[1]

        if request_count >= max_requests:
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id,
                count=request_count,
                limit=max_requests,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {max_requests} requests per minute.",
                headers={"Retry-After": "60"},
            )
    except HTTPException:
        raise
    except Exception as e:
        # Fail open — don't block requests if Redis is down
        logger.error("rate_limit_check_failed", error=str(e))
