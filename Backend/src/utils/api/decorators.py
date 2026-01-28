"""
API Decorators Module
Convenience decorators for rate limiting and caching endpoints.
"""
from functools import wraps
from django.core.cache import cache
from utils.constants.api import RATE_LIMITS, CACHE_TTLS


def cached_endpoint(ttl: int = None, key_prefix: str = ''):
    """
    Decorator for caching endpoint results with auto key generation.

    Args:
        ttl: Cache TTL in seconds (default from CACHE_TTLS['default'])
        key_prefix: Prefix for cache key

    Usage:
        @router.get("/data")
        @cached_endpoint(ttl=300, key_prefix="market")
        async def get_data(request):
            return expensive_computation()
    """
    ttl = ttl or CACHE_TTLS['default']

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}"
            cached = cache.get(cache_key)
            if cached:
                return cached

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def rate_limited_endpoint(rate: str = None, key: str = 'ip'):
    """
    Decorator for rate limiting endpoints.

    Args:
        rate: Rate limit string (e.g., "100/h", "500/h")
        key: Rate limit key type ('ip', 'user', 'header')

    Usage:
        @router.get("/data")
        @rate_limited_endpoint(rate="100/h", key="ip")
        async def get_data(request):
            return {"data": "expensive"}
    """
    from django_ratelimit.decorators import ratelimit
    rate = rate or RATE_LIMITS['default']
    return ratelimit(key=key, rate=rate, block=True)


def api_endpoint(ttl: int = None, rate: str = None, key_prefix: str = ''):
    """
    Combined decorator for rate limiting + caching.

    Args:
        ttl: Cache TTL in seconds
        rate: Rate limit string
        key_prefix: Prefix for cache key

    Usage:
        @router.get("/data")
        @api_endpoint(ttl=300, rate="200/h", key_prefix="analytics")
        async def get_data(request):
            return {"data": "expensive"}
    """
    def decorator(func):
        func = rate_limited_endpoint(rate or RATE_LIMITS['default'])(func)
        func = cached_endpoint(ttl, key_prefix)(func)
        return func
    return decorator


def cached_sync_endpoint(ttl: int = None, key_prefix: str = ''):
    """
    Decorator for caching synchronous endpoint results.

    Use for non-async endpoints that need caching.
    """
    ttl = ttl or CACHE_TTLS['default']

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}"
            cached = cache.get(cache_key)
            if cached:
                return cached

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


class CacheManager:
    """Helper class for manual cache operations."""

    @staticmethod
    def get(key: str):
        """Get value from cache."""
        return cache.get(key)

    @staticmethod
    def set(key: str, value, ttl: int = None):
        """Set value in cache."""
        cache.set(key, value, ttl or CACHE_TTLS['default'])

    @staticmethod
    def delete(key: str):
        """Delete value from cache."""
        cache.delete(key)

    @staticmethod
    def get_or_set(key: str, func, ttl: int = None):
        """Get value from cache or set it using provided function."""
        return cache.get_or_set(key, func, ttl)

    @staticmethod
    def clear_pattern(pattern: str):
        """Clear all keys matching pattern (requires Redis)."""
        # For Redis-backed caches only
        try:
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
        except Exception:
            pass  # Fall back for non-Redis caches
