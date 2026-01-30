"""
Cache Invalidation Service

Smart cache invalidation for different data types.
"""

from django.core.cache import cache
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class CacheInvalidator:
    """Manage cache invalidation for different data types"""

    TRACKED_KEYS = {
        "market_overview": [],
        "market_indices": [],
        "asset_detail": [],
        "asset_search": [],
        "portfolio": [],
        "watchlist": [],
        "alerts": [],
        "news": [],
    }

    @staticmethod
    def invalidate_asset(symbol: str):
        """Invalidate all caches related to an asset"""
        patterns = [
            f"cache:asset_detail:*",
            f"cache:asset_search:*",
            f"cache:portfolio:*",
            f"cache:watchlist:*",
        ]

        for pattern in patterns:
            CacheInvalidator._invalidate_pattern(pattern)

        logger.info(f"Invalidated caches for asset: {symbol}")

    @staticmethod
    def invalidate_market_data():
        """Invalidate all market-related caches"""
        patterns = [
            "cache:market_*",
            "cache:asset_search:*",
        ]

        for pattern in patterns:
            CacheInvalidator._invalidate_pattern(pattern)

        CacheInvalidator.TRACKED_KEYS["market_overview"] = []
        CacheInvalidator.TRACKED_KEYS["market_indices"] = []

        logger.info("Invalidated all market data caches")

    @staticmethod
    def invalidate_user_data(user_id: int):
        """Invalidate all user-specific caches"""
        patterns = [
            f"cache:portfolio:*user_{user_id}*",
            f"cache:watchlist:*user_{user_id}*",
            f"cache:alerts:*user_{user_id}*",
        ]

        for pattern in patterns:
            CacheInvalidator._invalidate_pattern(pattern)

        logger.info(f"Invalidated user caches: user_{user_id}")

    @staticmethod
    def invalidate_news():
        """Invalidate all news caches"""
        CacheInvalidator._invalidate_pattern("cache:news_*")
        CacheInvalidator.TRACKED_KEYS["news"] = []
        logger.info("Invalidated news caches")

    @staticmethod
    def invalidate_portfolio(portfolio_id: int, user_id: int):
        """Invalidate portfolio-related caches"""
        patterns = [
            f"cache:portfolio:{portfolio_id}",
            f"cache:portfolio:*user_{user_id}*",
        ]

        for pattern in patterns:
            CacheInvalidator._invalidate_pattern(pattern)

        logger.info(f"Invalidated portfolio caches: {portfolio_id}")

    @staticmethod
    def track_cache_key(category: str, key: str):
        """Track a cache key for later invalidation"""
        if category not in CacheInvalidator.TRACKED_KEYS:
            CacheInvalidator.TRACKED_KEYS[category] = []
        CacheInvalidator.TRACKED_KEYS[category].append(key)

    @staticmethod
    def _invalidate_pattern(pattern: str):
        """Invalidate all keys matching a pattern"""
        try:
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
                logger.debug(f"Invalidated {len(keys)} keys matching: {pattern}")
        except Exception as e:
            logger.warning(f"Failed to invalidate pattern {pattern}: {e}")

    @staticmethod
    def cleanup_stale_entries(max_keys: int = 1000):
        """Clean up tracked keys that are no longer valid"""
        for category, keys in CacheInvalidator.TRACKED_KEYS.items():
            valid_keys = []
            for key in keys:
                try:
                    if cache.get(key):
                        valid_keys.append(key)
                    else:
                        logger.debug(f"Removing stale key: {key}")
                except Exception:
                    pass

            CacheInvalidator.TRACKED_KEYS[category] = valid_keys[:max_keys]


class SmartCache:
    """
    Smart caching with automatic invalidation tracking
    """

    def __init__(self, category: str):
        self.category = category
        self.invalidator = CacheInvalidator()

    def get(self, key: str):
        """Get value from cache"""
        return cache.get(key)

    def set(self, key: str, value, ttl: int = 300):
        """Set value in cache and track it"""
        cache.set(key, value, ttl)
        self.invalidator.track_cache_key(self.category, key)

    def delete(self, key: str):
        """Delete from cache"""
        cache.delete(key)

    def invalidate_all(self):
        """Invalidate all cached values in this category"""
        if self.category in CacheInvalidator.TRACKED_KEYS:
            for key in CacheInvalidator.TRACKED_KEYS[self.category]:
                cache.delete(key)
            CacheInvalidator.TRACKED_KEYS[self.category] = []


def get_smart_cache(category: str) -> SmartCache:
    """Factory function for smart cache instances"""
    return SmartCache(category)
