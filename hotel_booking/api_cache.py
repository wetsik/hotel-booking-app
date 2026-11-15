"""Redis cache for hotel room availability (P08).

PostgreSQL is the source of truth.
Redis stores search results for 30 seconds.
Booking and cancellation never read the cache.
"""

from __future__ import annotations

from typing import Protocol

from redis import Redis

TTL_SECONDS = 30
VERSION_KEY = "availability:version"


class KeyValueStore(Protocol):
    """Operations required from the cache storage."""

    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...

    def increment(self, key: str) -> None: ...


class RedisKeyValueStore:
    """Adapter for Redis commands."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def get(self, key: str) -> str | None:
        return self._redis.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._redis.set(key, value, ex=ttl_seconds)

    def increment(self, key: str) -> None:
        self._redis.incr(key)


class AvailabilityCache:
    """Cache of free room numbers for a selected date range."""

    def __init__(self, store: KeyValueStore) -> None:
        self._store = store

    def key(self, check_in: str, check_out: str) -> str:
        version = self._store.get(VERSION_KEY) or "0"
        return f"availability:v{version}:{check_in}:{check_out}"

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, room_numbers: str) -> None:
        self._store.set(key, room_numbers, TTL_SECONDS)

    def invalidate(self) -> None:
        """Increment the version after availability changes."""
        self._store.increment(VERSION_KEY)
