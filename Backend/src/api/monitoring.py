from typing import Dict, List, Optional
from ninja import Router, Schema
from django_ratelimit.decorators import ratelimit

from utils.helpers.logger.logger import get_logger
from utils.services.monitor import get_performance_monitor
from utils.services.health_scorer import get_health_scorer, HealthStatus
from utils.constants.api import RATE_LIMIT_READ

logger = get_logger(__name__)

router = Router(tags=["Monitoring"])


class ProviderMetricsOut(Schema):
    provider_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    consecutive_failures: int
    health_score: float
    error_rate: float


class HealthSummaryOut(Schema):
    total: int
    healthy: int
    degraded: int
    unhealthy: int
    average_score: float
    best_provider: Optional[str]


class OverallStatsOut(Schema):
    timestamp: str
    providers: Dict
    requests: Dict
    latency: Dict
    cache: Dict
    health_scores: Dict


class CacheStatsOut(Schema):
    L1: Dict
    L2: Dict
    L3: Dict


@router.get("/providers", response=List[ProviderMetricsOut])
async def get_all_provider_metrics():
    """Get metrics for all data providers"""
    try:
        monitor = get_performance_monitor()
        
        providers = await monitor.get_all_provider_metrics()
        
        results = []
        for p in providers:
            results.append(ProviderMetricsOut(
                provider_name=p.get('provider_name', 'unknown'),
                total_requests=p.get('total_requests', 0),
                successful_requests=p.get('successful_requests', 0),
                failed_requests=p.get('failed_requests', 0),
                rate_limited_requests=p.get('rate_limited_requests', 0),
                avg_latency_ms=p.get('avg_latency_ms', 0),
                min_latency_ms=p.get('min_latency_ms', 0),
                max_latency_ms=p.get('max_latency_ms', 0),
                consecutive_failures=p.get('consecutive_failures', 0),
                health_score=p.get('health_score', 0),
                error_rate=p.get('error_rate', 0)
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting provider metrics: {e}")
        return []


@router.get("/providers/{provider_name}", response=ProviderMetricsOut)
async def get_provider_metrics(provider_name: str):
    """Get metrics for a specific provider"""
    try:
        monitor = get_performance_monitor()
        
        metrics = await monitor.get_provider_metrics(provider_name)
        
        if not metrics:
            return {"error": f"Provider {provider_name} not found"}
        
        return ProviderMetricsOut(
            provider_name=metrics.get('provider_name', provider_name),
            total_requests=metrics.get('total_requests', 0),
            successful_requests=metrics.get('successful_requests', 0),
            failed_requests=metrics.get('failed_requests', 0),
            rate_limited_requests=metrics.get('rate_limited_requests', 0),
            avg_latency_ms=metrics.get('avg_latency_ms', 0),
            min_latency_ms=metrics.get('min_latency_ms', 0),
            max_latency_ms=metrics.get('max_latency_ms', 0),
            consecutive_failures=metrics.get('consecutive_failures', 0),
            health_score=metrics.get('health_score', 0),
            error_rate=metrics.get('error_rate', 0)
        )
        
    except Exception as e:
        logger.error(f"Error getting provider metrics: {e}")
        return {"error": str(e)}


@router.get("/health", response=HealthSummaryOut)
async def get_health_summary():
    """Get overall health summary for all providers"""
    try:
        monitor = get_performance_monitor()
        scorer = get_health_scorer()
        
        providers = await monitor.get_all_provider_metrics()
        providers_dict = {p['provider_name']: p for p in providers}
        
        summary = scorer.get_health_summary(providers_dict)
        
        return HealthSummaryOut(**summary)
        
    except Exception as e:
        logger.error(f"Error getting health summary: {e}")
        return HealthSummaryOut(
            total=0,
            healthy=0,
            degraded=0,
            unhealthy=0,
            average_score=0,
            best_provider=None
        )


@router.get("/health/{provider_name}")
async def get_provider_health(provider_name: str):
    """Get detailed health information for a provider"""
    try:
        monitor = get_performance_monitor()
        scorer = get_health_scorer()
        
        metrics = await monitor.get_provider_metrics(provider_name)
        
        if not metrics:
            return {"error": f"Provider {provider_name} not found"}
        
        health = scorer.calculate_health_score(provider_name, metrics)
        
        return {
            "provider": provider_name,
            "overall_score": health.overall_score,
            "status": health.status.value,
            "scores": {
                "latency": health.latency_score,
                "reliability": health.reliability_score,
                "freshness": health.freshness_score
            },
            "factors": health.factors,
            "last_checked": health.last_checked,
            "recommendation": get_recommendation(health)
        }
        
    except Exception as e:
        logger.error(f"Error getting provider health: {e}")
        return {"error": str(e)}


@router.get("/slowest", response=List[ProviderMetricsOut])
async def get_slowest_providers(limit: int = 5):
    """Get the slowest providers by average latency"""
    try:
        monitor = get_performance_monitor()
        
        slowest = await monitor.get_slowest_providers(limit)
        
        results = []
        for p in slowest:
            results.append(ProviderMetricsOut(
                provider_name=p.get('provider_name', 'unknown'),
                total_requests=p.get('total_requests', 0),
                successful_requests=p.get('successful_requests', 0),
                failed_requests=p.get('failed_requests', 0),
                rate_limited_requests=p.get('rate_limited_requests', 0),
                avg_latency_ms=p.get('avg_latency_ms', 0),
                min_latency_ms=p.get('min_latency_ms', 0),
                max_latency_ms=p.get('max_latency_ms', 0),
                consecutive_failures=p.get('consecutive_failures', 0),
                health_score=p.get('health_score', 0),
                error_rate=p.get('error_rate', 0)
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting slowest providers: {e}")
        return []


@router.get("/error-prone", response=List[ProviderMetricsOut])
async def get_error_prone_providers(limit: int = 5):
    """Get providers with the highest error rates"""
    try:
        monitor = get_performance_monitor()
        
        error_prone = await monitor.get_error_prone_providers(limit)
        
        results = []
        for p in error_prone:
            results.append(ProviderMetricsOut(
                provider_name=p.get('provider_name', 'unknown'),
                total_requests=p.get('total_requests', 0),
                successful_requests=p.get('successful_requests', 0),
                failed_requests=p.get('failed_requests', 0),
                rate_limited_requests=p.get('rate_limited_requests', 0),
                avg_latency_ms=p.get('avg_latency_ms', 0),
                min_latency_ms=p.get('min_latency_ms', 0),
                max_latency_ms=p.get('max_latency_ms', 0),
                consecutive_failures=p.get('consecutive_failures', 0),
                health_score=p.get('health_score', 0),
                error_rate=p.get('error_rate', 0)
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting error-prone providers: {e}")
        return []


@router.get("/cache", response=CacheStatsOut)
async def get_cache_statistics():
    """Get cache statistics by level"""
    try:
        monitor = get_performance_monitor()
        
        stats = await monitor.get_cache_stats()
        
        return CacheStatsOut(
            L1=stats.get('L1', {'hits': 0, 'misses': 0, 'total': 0, 'hit_rate': 0}),
            L2=stats.get('L2', {'hits': 0, 'misses': 0, 'total': 0, 'hit_rate': 0}),
            L3=stats.get('L3', {'hits': 0, 'misses': 0, 'total': 0, 'hit_rate': 0})
        )
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return CacheStatsOut(
            L1={'hits': 0, 'misses': 0, 'total': 0, 'hit_rate': 0},
            L2={'hits': 0, 'misses': 0, 'total': 0, 'hit_rate': 0},
            L3={'hits': 0, 'misses': 0, 'total': 0, 'hit_rate': 0}
        )


@router.get("/stats", response=OverallStatsOut)
async def get_overall_statistics():
    """Get overall system statistics"""
    try:
        monitor = get_performance_monitor()
        
        stats = await monitor.get_overall_statistics()
        
        if 'error' in stats:
            return OverallStatsOut(
                timestamp=stats.get('timestamp', ''),
                providers={'total': 0, 'healthy': 0, 'degraded': 0, 'unhealthy': 0},
                requests={'total': 0, 'successful': 0, 'failed': 0, 'success_rate': 0, 'error_rate': 0},
                latency={'average_ms': 0, 'unit': 'ms'},
                cache={'overall_hit_rate': 0, 'by_level': {}},
                health_scores={}
            )
        
        return OverallStatsOut(
            timestamp=stats.get('timestamp', ''),
            providers=stats.get('providers', {}),
            requests=stats.get('requests', {}),
            latency=stats.get('latency', {}),
            cache=stats.get('cache', {}),
            health_scores=stats.get('health_scores', {})
        )
        
    except Exception as e:
        logger.error(f"Error getting overall statistics: {e}")
        return OverallStatsOut(
            timestamp='',
            providers={'total': 0, 'healthy': 0, 'degraded': 0, 'unhealthy': 0},
            requests={'total': 0, 'successful': 0, 'failed': 0, 'success_rate': 0, 'error_rate': 0},
            latency={'average_ms': 0, 'unit': 'ms'},
            cache={'overall_hit_rate': 0, 'by_level': {}},
            health_scores={}
        )


@router.get("/status")
async def get_monitor_status():
    """Get monitoring service status"""
    try:
        monitor = get_performance_monitor()
        status = monitor.get_status()
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting monitor status: {e}")
        return {"error": str(e)}


def get_recommendation(health) -> str:
    if health.status == HealthStatus.HEALTHY:
        return "Provider is healthy. Continue using as primary."
    elif health.status == HealthStatus.DEGRADED:
        if health.factors.get('latency', 100) < health.factors.get('reliability', 100):
            return "High latency detected. Consider using as fallback."
        else:
            return "Reliability issues detected. Monitor closely."
    else:
        if health.overall_score < 20:
            return "Critical issues. Consider blacklisting this provider."
        else:
            return "Unhealthy. Use only as last resort."
