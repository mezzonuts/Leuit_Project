"""In-memory caching layer for performance optimization."""
from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# In-memory cache: key -> (value, timestamp, ttl_seconds)
_cache: dict[str, tuple[Any, float, float]] = {}
DEFAULT_TTL = 300  # 5 minutes


def get_cache(key: str) -> Any | None:
    """Get value from cache. Returns None if expired or missing."""
    if key not in _cache:
        return None

    value, timestamp, ttl = _cache[key]
    if time.time() - timestamp > ttl:
        del _cache[key]
        return None

    return value


def set_cache(key: str, value: Any, ttl: float = DEFAULT_TTL) -> None:
    """Set value in cache with TTL."""
    _cache[key] = (value, time.time(), ttl)
    logger.debug(f"Cache set: {key} (ttl={ttl}s)")


def invalidate_cache(prefix: str | None = None) -> int:
    """Invalidate cache entries. If prefix given, only matching keys."""
    if prefix is None:
        count = len(_cache)
        _cache.clear()
        return count

    keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
    for k in keys_to_delete:
        del _cache[k]

    return len(keys_to_delete)


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    now = time.time()
    active = sum(1 for _, ts, ttl in _cache.values() if now - ts < ttl)
    expired = len(_cache) - active
    return {
        "total_entries": len(_cache),
        "active_entries": active,
        "expired_entries": expired,
        "hit_rate": "N/A",  # Would need hit/miss counters
    }
