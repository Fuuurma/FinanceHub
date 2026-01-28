"""
API Mixins Module
Provides reusable mixins for rate limiting, caching, and logging.
"""
from functools import wraps
from django.core.cache import cache
from utils.helpers.logger.logger import get_logger
from utils.constants.api import RATE_LIMITS, CACHE_TTLS

logger = get_logger(__name__)


class RateLimitMixin:
    """Mixin providing rate limiting for endpoints."""

    @staticmethod
    def ratelimited(rate: str = None, key: str = 'ip'):
        """Decorator factory for rate limiting endpoints."""
        from django_ratelimit.decorators import ratelimit
        rate = rate or RATE_LIMITS['default']
        return ratelimit(key=key, rate=rate, block=True)


class CacheMixin:
    """Mixin providing caching utilities for endpoints."""

    @staticmethod
    def cached(ttl: int = None, key_prefix: str = ''):
        """Decorator factory for caching endpoint results with auto key generation."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = f"{key_prefix}:{func.__name__}:{str(args)[:100]}:{str(kwargs)[:100]}"
                cached = cache.get(cache_key)
                if cached:
                    return cached

                result = await func(*args, **kwargs)
                cache.set(cache_key, result, ttl or CACHE_TTLS['default'])
                return result
            return wrapper
        return decorator


class APIMixin(RateLimitMixin, CacheMixin):
    """Combined mixin for common API patterns."""

    @property
    def log(self):
        """Lazy logger property."""
        return logger


class CachedAPI:
    """Class-based decorator for endpoints requiring caching."""

    def __init__(self, ttl: int = None, key_prefix: str = ''):
        self.ttl = ttl or CACHE_TTLS['default']
        self.key_prefix = key_prefix

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{self.key_prefix}:{func.__name__}"
            cached = cache.get(cache_key)
            if cached:
                return cached

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, self.ttl)
            return result
        return wrapper


class RateLimited:
    """Class-based decorator for endpoints requiring rate limiting."""

    def __init__(self, rate: str = None, key: str = 'ip'):
        from django_ratelimit.decorators import ratelimit
        self.rate = rate or RATE_LIMITS['default']
        self.decorator = ratelimit(key=key, rate=self.rate, block=True)

    def __call__(self, func):
        return self.decorator(func)
