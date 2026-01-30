"""
Rate Limit Decorator for Endpoint-Level Rate Limiting

Allows fine-grained rate limiting on specific API endpoints.
"""

from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from typing import Optional
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def rate_limit(limit: int, window: int = 3600, key_prefix: str = None):
    """
    Rate limit decorator for individual endpoints

    Args:
        limit: Max requests allowed in time window
        window: Time window in seconds (default: 1 hour)
        key_prefix: Custom cache key prefix for this endpoint
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                identifier = f"user:{request.user.id}"
            else:
                ip = request.META.get("REMOTE_ADDR", "unknown")
                identifier = f"ip:{ip}"

            func_name = func.__name__
            cache_key = f"rl:{key_prefix or func_name}:{identifier}"

            current = cache.get(cache_key, 0)

            if current >= limit:
                logger.warning(
                    f"Rate limit exceeded for {identifier} "
                    f"on endpoint {func_name} (limit: {limit}/{window}s)"
                )
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {limit} requests per {window}s allowed",
                        "retry_after": window,
                    },
                    status=429,
                )

            cache.set(cache_key, current + 1, window)

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def cache_response(ttl: int = 300, key_prefix: str = None):
    """
    Cache API responses in Redis

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Custom cache key prefix
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method != "GET":
                return func(request, *args, **kwargs)

            cache_key = _generate_cache_key(
                func.__name__,
                request.GET.dict(),
                request.user.id
                if hasattr(request, "user") and request.user.is_authenticated
                else None,
                key_prefix,
            )

            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                response = JsonResponse(cached)
                response["X-Cache"] = "HIT"
                return response

            response = func(request, *args, **kwargs)

            try:
                response_data = json.loads(response.content)
                cache.set(cache_key, response_data, ttl)
                logger.debug(f"Cache set: {cache_key} (ttl: {ttl}s)")
                response["X-Cache"] = "MISS"
            except (json.JSONDecodeError, AttributeError):
                pass

            return response

        return wrapper

    return decorator


def _generate_cache_key(
    func_name: str, params: dict, user_id: Optional[int] = None, prefix: str = None
) -> str:
    """Generate unique cache key for response caching"""
    key_data = {
        "func": func_name,
        "params": sorted(params.items()) if params else [],
        "user": user_id,
    }

    key_hash = hashlib.md5(
        json.dumps(key_data, sort_keys=True, default=str).encode()
    ).hexdigest()

    if prefix:
        return f"cache:{prefix}:{key_hash}"
    else:
        return f"cache:{func_name}:{key_hash}"


class EndpointRateLimit:
    """
    Endpoint-specific rate limits configuration

    Usage:
        ENDPOINT_RATE_LIMITS = {
            'market_overview': {'limit': 100, 'window': 3600},
            'market_indices': {'limit': 200, 'window': 3600},
            'asset_search': {'limit': 50, 'window': 3600},
            'portfolio_create': {'limit': 20, 'window': 3600},
        }
    """

    DEFAULT_LIMITS = {
        "GET": {"limit": 1000, "window": 3600},
        "POST": {"limit": 100, "window": 3600},
        "PUT": {"limit": 100, "window": 3600},
        "DELETE": {"limit": 50, "window": 3600},
    }

    ENDPOINT_LIMITS = {
        "market_overview": {"limit": 100, "window": 3600},
        "market_indices": {"limit": 200, "window": 3600},
        "market_data": {"limit": 150, "window": 3600},
        "asset_search": {"limit": 50, "window": 3600},
        "asset_detail": {"limit": 300, "window": 3600},
        "portfolio_list": {"limit": 100, "window": 3600},
        "portfolio_create": {"limit": 20, "window": 3600},
        "portfolio_update": {"limit": 50, "window": 3600},
        "watchlist_add": {"limit": 30, "window": 3600},
        "alert_create": {"limit": 20, "window": 3600},
        "news_fetch": {"limit": 100, "window": 3600},
    }

    @classmethod
    def get_limit(cls, endpoint_name: str, method: str = "GET") -> dict:
        """Get rate limit config for an endpoint"""
        if endpoint_name in cls.ENDPOINT_LIMITS:
            return cls.ENDPOINT_LIMITS[endpoint_name]
        return cls.DEFAULT_LIMITS.get(method, cls.DEFAULT_LIMITS["GET"])
