"""Tests for caching layer performance optimization."""
from __future__ import annotations

import time
from collections.abc import Iterator

import pytest

from app.core.cache import (
    get_cache,
    get_cache_stats,
    invalidate_cache,
    set_cache,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> Iterator[None]:
    invalidate_cache()
    yield
    invalidate_cache()


class TestCacheSetGet:
    def test_set_and_get(self) -> None:
        set_cache("test_key", "test_value", ttl=60)
        assert get_cache("test_key") == "test_value"

    def test_get_missing_key(self) -> None:
        assert get_cache("nonexistent_key") is None

    def test_get_expired_key(self) -> None:
        set_cache("expired_key", "value", ttl=0.001)
        time.sleep(0.01)
        assert get_cache("expired_key") is None

    def test_overwrite_existing(self) -> None:
        set_cache("key", "old_value", ttl=60)
        set_cache("key", "new_value", ttl=60)
        assert get_cache("key") == "new_value"

    def test_complex_value(self) -> None:
        data = {"items": [1, 2, 3], "total": 6}
        set_cache("complex", data, ttl=60)
        assert get_cache("complex") == data


class TestCacheInvalidation:
    def test_invalidate_all(self) -> None:
        set_cache("a", 1)
        set_cache("b", 2)
        count = invalidate_cache()
        assert count == 2
        assert get_cache("a") is None
        assert get_cache("b") is None

    def test_invalidate_by_prefix(self) -> None:
        set_cache("valuation_summary", {})
        set_cache("inventory_list", [])
        set_cache("other_key", "value")

        count = invalidate_cache("valuation")
        assert count == 1
        assert get_cache("valuation_summary") is None
        assert get_cache("inventory_list") is not None
        assert get_cache("other_key") is not None


class TestCacheStats:
    def test_stats_structure(self) -> None:
        set_cache("stat_test", "value", ttl=60)
        stats = get_cache_stats()
        assert "total_entries" in stats
        assert "active_entries" in stats
        assert "expired_entries" in stats
        assert stats["total_entries"] >= 1


class TestCachePerformance:
    def test_cache_faster_than_no_cache(self) -> None:
        # Simulate expensive computation
        def expensive_operation() -> int:
            return sum(range(10000))

        # Time without cache
        start = time.perf_counter()
        for _ in range(100):
            result1 = expensive_operation()
        no_cache_time = time.perf_counter() - start

        # Time with cache
        set_cache("perf_test", expensive_operation(), ttl=60)
        start = time.perf_counter()
        for _ in range(100):
            result2 = get_cache("perf_test")
        cache_time = time.perf_counter() - start

        assert result1 == result2
        # Cache should be significantly faster
        assert cache_time < no_cache_time

    def test_cache_hit_consistency(self) -> None:
        value = {"data": [1, 2, 3]}
        set_cache("consistent", value, ttl=60)

        for _ in range(1000):
            assert get_cache("consistent") == value
