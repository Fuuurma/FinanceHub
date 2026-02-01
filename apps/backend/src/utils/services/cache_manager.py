import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass, field

from django.core.cache import cache as django_cache
from django.utils import timezone
from django.db import connection
from django.db.utils import InterfaceError
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class CacheLevel(Enum):
    L1_MEMORY = 1
    L2_REDIS = 2
    L3_DATABASE = 3


@dataclass
class CacheEntry:
    key: str
    value: Any
    level: CacheLevel
    created_at: datetime = field(default_factory=timezone.now)
    expires_at: Optional[datetime] = None
    hit_count: int = 0
    size_bytes: int = 0

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    def age_seconds(self) -> int:
        return int((timezone.now() - self.created_at).total_seconds())

    def ttl_seconds(self) -> int:
        if self.expires_at is None:
            return -1
        return max(0, int((self.expires_at - timezone.now()).total_seconds()))


class CacheStatistics:
    def __init__(self):
        self.hits: int = 0
        self.misses: int = 0
        self.evolutions: int = 0
        self.writes: int = 0
        self.deletes: int = 0
        self.errors: int = 0
        self.level_stats: Dict[str, Dict] = {
            "L1_MEMORY": {"hits": 0, "misses": 0, "size_bytes": 0},
            "L2_REDIS": {"hits": 0, "misses": 0},
            "L3_DATABASE": {"hits": 0, "misses": 0},
        }
        self.key_stats: Dict[str, Dict] = {}

    def record_hit(self, level: CacheLevel, key: str):
        self.hits += 1
        level_name = level.name
        self.level_stats[level_name]["hits"] += 1

        if key not in self.key_stats:
            self.key_stats[key] = {"hits": 0, "misses": 0}
        self.key_stats[key]["hits"] += 1

    def record_miss(self, level: CacheLevel, key: str):
        self.misses += 1
        level_name = level.name
        self.level_stats[level_name]["misses"] += 1

        if key not in self.key_stats:
            self.key_stats[key] = {"hits": 0, "misses": 0}
        self.key_stats[key]["misses"] += 1

    def record_evolution(self):
        self.evolutions += 1

    def record_write(self):
        self.writes += 1

    def record_delete(self):
        self.deletes += 1

    def record_error(self):
        self.errors += 1

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def get_summary(self) -> dict:
        level_rates = {}
        for level_name, stats in self.level_stats.items():
            total = stats["hits"] + stats["misses"]
            hit_rate = stats["hits"] / total if total > 0 else 0.0
            level_rates[level_name] = {
                "hits": stats["hits"],
                "misses": stats["misses"],
                "hit_rate": hit_rate,
            }

        return {
            "total_hits": self.hits,
            "total_misses": self.misses,
            "hit_rate": self.get_hit_rate(),
            "evolutions": self.evolutions,
            "writes": self.writes,
            "deletes": self.deletes,
            "errors": self.errors,
            "level_stats": level_rates,
            "top_keys": sorted(
                self.key_stats.items(),
                key=lambda x: x[1]["hits"] + x[1]["misses"],
                reverse=True,
            )[:20],
        }


class CacheManager:
    def __init__(
        self,
        l1_max_size: int = 1000,
        l1_max_bytes: int = 50_000_000,
        l2_default_ttl: int = 300,
        l3_default_ttl: int = 3600,
    ):
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_max_size = l1_max_size
        self.l1_max_bytes = l1_max_bytes
        self.l2_default_ttl = l2_default_ttl
        self.l3_default_ttl = l3_default_ttl
        self.statistics = CacheStatistics()
        self._lock = asyncio.Lock()

    @staticmethod
    def _generate_key(prefix: str, *args, **kwargs) -> str:
        key_parts = [prefix]

        for arg in args:
            key_parts.append(str(arg))

        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:32]

    @staticmethod
    def _serialize(value: Any) -> str:
        try:
            return json.dumps(value, default=str)
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"Failed to serialize value: {e}")
            raise

    @staticmethod
    def _deserialize(value: str) -> Any:
        try:
            return json.loads(value)
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"Failed to deserialize value: {e}")
            raise

    def _calculate_size(self, value: Any) -> int:
        try:
            serialized = self._serialize(value)
            return len(serialized.encode("utf-8"))
        except Exception:
            return 0

    async def _evict_l1(self):
        while (
            len(self.l1_cache) >= self.l1_max_size
            or self._get_l1_size_bytes() >= self.l1_max_bytes
        ):
            if not self.l1_cache:
                break

            oldest_key = min(
                self.l1_cache.keys(), key=lambda k: self.l1_cache[k].created_at
            )

            entry = self.l1_cache.pop(oldest_key)
            self.l1_cache[oldest_key] = entry
            self.statistics.record_evolution()
            logger.debug(f"Evicted L1 cache entry: {oldest_key}")

    def _get_l1_size_bytes(self) -> int:
        return sum(entry.size_bytes for entry in self.l1_cache.values())

    async def get(self, prefix: str, *args, default: Any = None, **kwargs) -> Any:
        cache_key = self._generate_key(prefix, *args, **kwargs)

        async with self._lock:
            entry = self.l1_cache.get(cache_key)

            if entry and not entry.is_expired():
                entry.hit_count += 1
                self.statistics.record_hit(CacheLevel.L1_MEMORY, cache_key)
                return entry.value

            self.statistics.record_miss(CacheLevel.L1_MEMORY, cache_key)

        try:
            cached_value = django_cache.get(cache_key)

            if cached_value is not None:
                self.statistics.record_hit(CacheLevel.L2_REDIS, cache_key)

                value = self._deserialize(cached_value)

                await self._promote_to_l1(cache_key, value)

                return value

            self.statistics.record_miss(CacheLevel.L2_REDIS, cache_key)

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"L2 cache error: {e}")
            self.statistics.record_error()

        try:
            from assets.models.historic.prices import AssetPricesHistoric

            if prefix == "asset_price":
                symbol = args[0] if args else kwargs.get("symbol")
                if symbol:
                    record = await asyncio.to_thread(
                        AssetPricesHistoric.objects.filter(asset__symbol=symbol)
                        .order_by("-timestamp")
                        .first
                    )

                    if record:
                        self.statistics.record_hit(CacheLevel.L3_DATABASE, cache_key)
                        value = {
                            "open": record.open,
                            "high": record.high,
                            "low": record.low,
                            "close": record.close,
                            "volume": record.volume,
                            "timestamp": record.timestamp.isoformat(),
                        }

                        await self._promote_to_l1(cache_key, value)
                        await self.set(
                            prefix,
                            *args,
                            value=value,
                            ttl=self.l3_default_ttl,
                            **kwargs,
                        )

                        return value

            self.statistics.record_miss(CacheLevel.L3_DATABASE, cache_key)

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"L3 cache error: {e}")
            self.statistics.record_error()

        return default

    async def set(
        self, prefix: str, *args, value: Any, ttl: Optional[int] = None, **kwargs
    ) -> bool:
        cache_key = self._generate_key(prefix, *args, **kwargs)
        size_bytes = self._calculate_size(value)

        if ttl is None:
            ttl = self.l2_default_ttl

        expires_at = timezone.now() + timedelta(seconds=ttl)

        async with self._lock:
            await self._evict_l1()

            self.l1_cache[cache_key] = CacheEntry(
                key=cache_key,
                value=value,
                level=CacheLevel.L1_MEMORY,
                expires_at=expires_at,
                size_bytes=size_bytes,
            )

            self.statistics.record_write()

        try:
            serialized = self._serialize(value)
            django_cache.set(cache_key, serialized, timeout=ttl)
            return True

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"Failed to set cache value: {e}")
            self.statistics.record_error()
            return False

    async def delete(self, prefix: str, *args, **kwargs) -> bool:
        cache_key = self._generate_key(prefix, *args, **kwargs)

        async with self._lock:
            if cache_key in self.l1_cache:
                del self.l1_cache[cache_key]
                self.statistics.record_delete()

        try:
            django_cache.delete(cache_key)
            return True
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"Failed to delete cache value: {e}")
            self.statistics.record_error()
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        count = 0

        async with self._lock:
            keys_to_delete = [key for key in self.l1_cache.keys() if pattern in key]

            for key in keys_to_delete:
                del self.l1_cache[key]
                count += 1
                self.statistics.record_delete()

        try:
            from django.core.cache import cache

            if hasattr(cache, "delete_pattern"):
                cache.delete_pattern(pattern)
            else:
                logger.warning("Cache backend doesn't support pattern deletion")

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"Failed to invalidate cache pattern: {e}")
            self.statistics.record_error()

        return count

    async def warm_cache(self, warm_data: Dict[str, Tuple[Any, int]]) -> int:
        warmed = 0

        for cache_key, (value, ttl) in warm_data.items():
            try:
                await self.set("warm", cache_key, value=value, ttl=ttl)
                warmed += 1
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
                logger.error(f"Failed to warm cache for key {cache_key}: {e}")

        logger.info(f"Warmed {warmed}/{len(warm_data)} cache entries")
        return warmed

    async def clear_all(self):
        async with self._lock:
            self.l1_cache.clear()

        try:
            django_cache.clear()
            logger.info("Cleared all cache levels")
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, CacheError) as e:
            logger.error(f"Failed to clear cache: {e}")
            self.statistics.record_error()

    async def get_statistics(self) -> dict:
        async with self._lock:
            l1_stats = {
                "size": len(self.l1_cache),
                "max_size": self.l1_max_size,
                "size_bytes": self._get_l1_size_bytes(),
                "max_bytes": self.l1_max_bytes,
            }

        try:
            l2_info = (
                django_cache._cache.info if hasattr(django_cache._cache, "info") else {}
            )
        except Exception:
            l2_info = {}

        return {
            "l1_memory": l1_stats,
            "l2_redis": l2_info,
            "statistics": self.statistics.get_summary(),
        }

    async def _promote_to_l1(self, cache_key: str, value: Any):
        async with self._lock:
            await self._evict_l1()

            self.l1_cache[cache_key] = CacheEntry(
                key=cache_key,
                value=value,
                level=CacheLevel.L1_MEMORY,
                size_bytes=self._calculate_size(value),
            )


_cache_manager_instance: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance
