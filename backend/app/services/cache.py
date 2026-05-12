"""PhishGuard — Upstash Redis Cache Service.

HTTP-based Redis cache with TTL and Bloom filter sync.
"""

import json
from typing import Optional, Dict
import structlog

from app.core.limiter import get_redis

logger = structlog.get_logger()

CACHE_TTL = 3600  # 1 hour


async def cache_get(key: str) -> Optional[Dict]:
    """Get cached scan result by URL hash."""
    try:
        redis = get_redis()
        if redis is None:
            return None
        cached = redis.get(f"scan:{key}")
        if cached:
            logger.debug("cache_hit", key=key)
            return json.loads(cached)
    except Exception as e:
        logger.warning("cache_get_failed", error=str(e))
    return None


async def cache_set(key: str, value: Dict, ttl: int = CACHE_TTL) -> None:
    """Cache a scan result with TTL."""
    try:
        redis = get_redis()
        if redis is None:
            return
        redis.set(f"scan:{key}", json.dumps(value, default=str), ex=ttl)
        logger.debug("cache_set", key=key, ttl=ttl)
    except Exception as e:
        logger.warning("cache_set_failed", error=str(e))


async def cache_delete(key: str) -> None:
    """Remove a cached result."""
    try:
        redis = get_redis()
        if redis is None:
            return
        redis.delete(f"scan:{key}")
    except Exception as e:
        logger.warning("cache_delete_failed", error=str(e))


async def add_to_bloom_filter(url: str) -> None:
    """Add a malicious URL to the set in Redis."""
    try:
        redis = get_redis()
        if redis is None:
            return
        redis.sadd("bloom:malicious_urls", url)
    except Exception as e:
        logger.warning("bloom_add_failed", error=str(e))


async def check_bloom_filter(url: str) -> bool:
    """Check if URL is in the set (known malicious)."""
    try:
        redis = get_redis()
        if redis is None:
            return False
        return redis.sismember("bloom:malicious_urls", url)
    except Exception as e:
        logger.warning("bloom_check_failed", error=str(e))
        return False


async def get_bloom_filter_urls() -> list:
    """Get all URLs in the Bloom filter for extension sync."""
    try:
        redis = get_redis()
        if redis is None:
            return []
        urls = redis.smembers("bloom:malicious_urls")
        return list(urls) if urls else []
    except Exception as e:
        logger.warning("bloom_get_failed", error=str(e))
        return []
