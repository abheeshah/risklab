"""Diskcache wrapper with TTL."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from diskcache import Cache

from app.core.config import get_settings

_cache: Cache | None = None


def get_cache() -> Cache:
    global _cache
    if _cache is None:
        settings = get_settings()
        path = Path(settings.cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        _cache = Cache(str(path))
    return _cache


def cache_get(key: str) -> Any | None:
    return get_cache().get(key, default=None)


def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    settings = get_settings()
    expire = settings.cache_ttl_seconds if ttl is None else ttl
    get_cache().set(key, value, expire=expire)


def cache_ok() -> bool:
    try:
        c = get_cache()
        probe_key = "__health_probe__"
        c.set(probe_key, True, expire=60)
        ok = c.get(probe_key) is True
        c.delete(probe_key)
        return ok
    except Exception:
        return False


def reset_cache_for_tests() -> None:
    """Close and clear the singleton (tests only)."""
    global _cache
    if _cache is not None:
        _cache.close()
        _cache = None
