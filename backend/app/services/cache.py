"""PhishGuard — Redis Cache Service.

Async Redis cache with TTL and Bloom filter sync.
"""

import json
from typing import Optional, Any, Dict
import structlog

from app.core.limiter import get_redis

logger = structlog.get_logger()

CACHE_TTL = 3600  # 1 hour


async def cache_get(key: str) -> Optional[Dict]:
    """Get cached scan result by URL hash."""
    try:
        redis = await get_redis()
        cached = await redis.get(f"scan:{key}")
        if cached:
            logger.debug("cache_hit", key=key)
            return json.loads(cached)
    except Exception as e:
        logger.warning("cache_get_failed", error=str(e))
    return None


async def cache_set(key: str, value: Dict, ttl: int = CACHE_TTL) -> None:
    """Cache a scan result with TTL."""
    try:
        redis = await get_redis()
        await redis.set(f"scan:{key}", json.dumps(value, default=str), ex=ttl)
        logger.debug("cache_set", key=key, ttl=ttl)
    except Exception as e:
        logger.warning("cache_set_failed", error=str(e))


async def cache_delete(key: str) -> None:
    """Remove a cached result."""
    try:
        redis = await get_redis()
        await redis.delete(f"scan:{key}")
    except Exception as e:
        logger.warning("cache_delete_failed", error=str(e))


async def add_to_bloom_filter(url: str) -> None:
    """Add a malicious URL to the Bloom filter set in Redis."""
    try:
        redis = await get_redis()
        await redis.sadd("bloom:malicious_urls", url)
    except Exception as e:
        logger.warning("bloom_add_failed", error=str(e))


async def check_bloom_filter(url: str) -> bool:
    """Check if URL is in the Bloom filter (known malicious)."""
    try:
        redis = await get_redis()
        return await redis.sismember("bloom:malicious_urls", url)
    except Exception as e:
        logger.warning("bloom_check_failed", error=str(e))
        return False


async def get_bloom_filter_urls() -> list:
    """Get all URLs in the Bloom filter for extension sync."""
    try:
        redis = await get_redis()
        urls = await redis.smembers("bloom:malicious_urls")
        return list(urls)
    except Exception as e:
        logger.warning("bloom_get_failed", error=str(e))
        return []
