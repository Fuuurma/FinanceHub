import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque

from django.utils import timezone
from django.core.cache import cache
from django.db.models import Avg, Count, Q

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProviderMetrics:
    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    consecutive_failures: int = 0
    health_score: float = 100.0
    
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))
    error_history: deque = field(default_factory=lambda: deque(maxlen=100))


class PerformanceMonitor:
    def __init__(self):
        self.providers: Dict[str, ProviderMetrics] = {}
        self.metrics_buffer: Dict[str, deque] = {}
        self._lock = asyncio.Lock()
        self.running = False
        
        self.latency_threshold_ms = 5000
        self.error_rate_threshold = 0.1
        self.health_check_interval = 60
    
    async def start(self):
        if self.running:
            return
        
        self.running = True
        logger.info("Performance monitor started")
        
        asyncio.create_task(self._background_health_check())
    
    async def stop(self):
        self.running = False
        logger.info("Performance monitor stopped")
    
    async def record_request(
        self,
        provider: str,
        success: bool,
        latency_ms: float,
        rate_limited: bool = False,
        error_type: Optional[str] = None
    ):
        async with self._lock:
            if provider not in self.providers:
                self.providers[provider] = ProviderMetrics(provider_name=provider)
            
            metrics = self.providers[provider]
            
            metrics.total_requests += 1
            metrics.total_latency_ms += latency_ms
            metrics.avg_latency_ms = metrics.total_latency_ms / metrics.total_requests
            
            metrics.latency_history.append(MetricPoint(
                timestamp=timezone.now(),
                value=latency_ms
            ))
            
            if latency_ms < metrics.min_latency_ms:
                metrics.min_latency_ms = latency_ms
            if latency_ms > metrics.max_latency_ms:
                metrics.max_latency_ms = latency_ms
            
            if success:
                metrics.successful_requests += 1
                metrics.last_success = timezone.now()
                metrics.consecutive_failures = 0
            else:
                metrics.failed_requests += 1
                metrics.last_failure = timezone.now()
                metrics.consecutive_failures += 1
                
                metrics.error_history.append(MetricPoint(
                    timestamp=timezone.now(),
                    value=1.0,
                    tags={'error_type': error_type or 'unknown'}
                ))
            
            if rate_limited:
                metrics.rate_limited_requests += 1
            
            metrics.health_score = self._calculate_health_score(metrics)
            
            await self._store_metrics(provider, metrics)
    
    def _calculate_health_score(self, metrics: ProviderMetrics) -> float:
        if metrics.total_requests == 0:
            return 100.0
        
        error_rate = metrics.failed_requests / metrics.total_requests
        
        latency_score = max(0, 100 - (metrics.avg_latency_ms / 100))
        
        error_score = max(0, 100 * (1 - error_rate))
        
        recency_score = 100.0
        if metrics.last_failure:
            time_since_failure = (timezone.now() - metrics.last_failure).total_seconds()
            recency_score = max(0, 100 - (time_since_failure / 3600) * 20)
        
        weight_latency = 0.3
        weight_error = 0.4
        weight_recency = 0.3
        
        health_score = (
            latency_score * weight_latency +
            error_score * weight_error +
            recency_score * weight_recency
        )
        
        return max(0, min(100, health_score))
    
    async def _store_metrics(self, provider: str, metrics: ProviderMetrics):
        try:
            cache_key = f"provider_metrics_{provider}"
            
            data = {
                'provider_name': metrics.provider_name,
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'rate_limited_requests': metrics.rate_limited_requests,
                'avg_latency_ms': metrics.avg_latency_ms,
                'min_latency_ms': metrics.min_latency_ms,
                'max_latency_ms': metrics.max_latency_ms,
                'consecutive_failures': metrics.consecutive_failures,
                'health_score': metrics.health_score,
                'last_success': metrics.last_success.isoformat() if metrics.last_success else None,
                'last_failure': metrics.last_failure.isoformat() if metrics.last_failure else None,
                'updated_at': timezone.now().isoformat()
            }
            
            cache.set(cache_key, data, timeout=300)
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def get_provider_metrics(self, provider: str) -> Optional[Dict]:
        try:
            cache_key = f"provider_metrics_{provider}"
            cached = cache.get(cache_key)
            
            if cached:
                return cached
            
            if provider in self.providers:
                metrics = self.providers[provider]
                return {
                    'provider_name': metrics.provider_name,
                    'total_requests': metrics.total_requests,
                    'successful_requests': metrics.successful_requests,
                    'failed_requests': metrics.failed_requests,
                    'rate_limited_requests': metrics.rate_limited_requests,
                    'avg_latency_ms': metrics.avg_latency_ms,
                    'min_latency_ms': metrics.min_latency_ms,
                    'max_latency_ms': metrics.max_latency_ms,
                    'consecutive_failures': metrics.consecutive_failures,
                    'health_score': metrics.health_score,
                    'error_rate': metrics.failed_requests / metrics.total_requests if metrics.total_requests > 0 else 0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting provider metrics: {e}")
            return None
    
    async def get_all_provider_metrics(self) -> List[Dict]:
        try:
            results = []
            
            for provider in self.providers:
                metrics = await self.get_provider_metrics(provider)
                if metrics:
                    results.append(metrics)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting all provider metrics: {e}")
            return []
    
    async def get_health_scores(self) -> Dict[str, float]:
        try:
            scores = {}
            
            for provider, metrics in self.providers.items():
                scores[provider] = metrics.health_score
            
            return scores
            
        except Exception as e:
            logger.error(f"Error getting health scores: {e}")
            return {}
    
    async def get_slowest_providers(self, limit: int = 5) -> List[Dict]:
        try:
            providers = await self.get_all_provider_metrics()
            
            sorted_providers = sorted(
                providers,
                key=lambda x: x.get('avg_latency_ms', 0),
                reverse=True
            )
            
            return sorted_providers[:limit]
            
        except Exception as e:
            logger.error(f"Error getting slowest providers: {e}")
            return []
    
    async def get_error_prone_providers(self, limit: int = 5) -> List[Dict]:
        try:
            providers = await self.get_all_provider_metrics()
            
            error_providers = [
                p for p in providers
                if p.get('failed_requests', 0) > 0
            ]
            
            sorted_providers = sorted(
                error_providers,
                key=lambda x: x.get('failed_requests', 0) / max(x.get('total_requests', 1), 1),
                reverse=True
            )
            
            return sorted_providers[:limit]
            
        except Exception as e:
            logger.error(f"Error getting error-prone providers: {e}")
            return []
    
    async def record_cache_hit(self, cache_level: str):
        try:
            cache_key = f"cache_hits_{cache_level}"
            current = cache.get(cache_key) or 0
            cache.set(cache_key, current + 1, timeout=3600)
        except Exception as e:
            logger.error(f"Error recording cache hit: {e}")
    
    async def record_cache_miss(self, cache_level: str):
        try:
            cache_key = f"cache_misses_{cache_level}"
            current = cache.get(cache_key) or 0
            cache.set(cache_key, current + 1, timeout=3600)
        except Exception as e:
            logger.error(f"Error recording cache miss: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        try:
            stats = {}
            
            for level in ['L1', 'L2', 'L3']:
                hits_key = f"cache_hits_{level}"
                misses_key = f"cache_misses_{level}"
                
                hits = cache.get(hits_key) or 0
                misses = cache.get(misses_key) or 0
                total = hits + misses
                
                hit_rate = hits / total if total > 0 else 0
                
                stats[level] = {
                    'hits': hits,
                    'misses': misses,
                    'total': total,
                    'hit_rate': hit_rate
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    async def get_overall_statistics(self) -> Dict[str, Any]:
        try:
            provider_metrics = await self.get_all_provider_metrics()
            
            total_requests = sum(p.get('total_requests', 0) for p in provider_metrics)
            total_success = sum(p.get('successful_requests', 0) for p in provider_metrics)
            total_failures = sum(p.get('failed_requests', 0) for p in provider_metrics)
            
            avg_latency = 0
            if provider_metrics:
                latencies = [p.get('avg_latency_ms', 0) for p in provider_metrics]
                avg_latency = sum(latencies) / len(latencies)
            
            cache_stats = await self.get_cache_stats()
            
            overall_cache_hits = sum(s['hits'] for s in cache_stats.values())
            overall_cache_misses = sum(s['misses'] for s in cache_stats.values())
            overall_cache_total = overall_cache_hits + overall_cache_misses
            overall_cache_hit_rate = overall_cache_hits / overall_cache_total if overall_cache_total > 0 else 0
            
            return {
                'timestamp': timezone.now().isoformat(),
                'providers': {
                    'total': len(provider_metrics),
                    'healthy': sum(1 for p in provider_metrics if p.get('health_score', 0) >= 70),
                    'degraded': sum(1 for p in provider_metrics if 40 <= p.get('health_score', 0) < 70),
                    'unhealthy': sum(1 for p in provider_metrics if p.get('health_score', 0) < 40)
                },
                'requests': {
                    'total': total_requests,
                    'successful': total_success,
                    'failed': total_failures,
                    'success_rate': total_success / total_requests if total_requests > 0 else 0,
                    'error_rate': total_failures / total_requests if total_requests > 0 else 0
                },
                'latency': {
                    'average_ms': avg_latency,
                    'unit': 'ms'
                },
                'cache': {
                    'overall_hit_rate': overall_cache_hit_rate,
                    'by_level': cache_stats
                },
                'health_scores': await self.get_health_scores()
            }
            
        except Exception as e:
            logger.error(f"Error getting overall statistics: {e}")
            return {'error': str(e)}
    
    async def _background_health_check(self):
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for provider in list(self.providers.keys()):
                    metrics = self.providers[provider]
                    
                    if metrics.consecutive_failures >= 5:
                        logger.warning(
                            f"Provider {provider} has {metrics.consecutive_failures} "
                            f"consecutive failures. Health score: {metrics.health_score:.2f}"
                        )
                    
                    if metrics.health_score < 30:
                        logger.error(
                            f"Provider {provider} health score is critical: {metrics.health_score:.2f}"
                        )
                    
                    if metrics.avg_latency_ms > self.latency_threshold_ms:
                        logger.warning(
                            f"Provider {provider} latency is high: "
                            f"{metrics.avg_latency_ms:.2f}ms (threshold: {self.latency_threshold_ms}ms)"
                        )
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'running': self.running,
            'providers_tracked': len(self.providers),
            'latency_threshold_ms': self.latency_threshold_ms,
            'error_rate_threshold': self.error_rate_threshold,
            'health_check_interval': self.health_check_interval
        }


_performance_monitor_instance: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    global _performance_monitor_instance
    if _performance_monitor_instance is None:
        _performance_monitor_instance = PerformanceMonitor()
    return _performance_monitor_instance
