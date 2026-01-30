from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

from django.utils import timezone

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthScore:
    overall_score: float
    latency_score: float
    reliability_score: float
    freshness_score: float
    status: HealthStatus
    factors: Dict[str, float]
    last_checked: str


class HealthScorer:
    def __init__(self):
        self.logger = logger
        
        self.weights = {
            'latency': 0.25,
            'reliability': 0.35,
            'freshness': 0.20,
            'error_rate': 0.20
        }
        
        self.latency_thresholds = {
            'excellent_ms': 100,
            'good_ms': 500,
            'acceptable_ms': 2000,
            'poor_ms': 5000
        }
        
        self.reliability_thresholds = {
            'excellent': 0.99,
            'good': 0.95,
            'acceptable': 0.90,
            'poor': 0.80
        }
        
        self.freshness_thresholds = {
            'excellent_seconds': 60,
            'good_seconds': 300,
            'acceptable_seconds': 900,
            'poor_seconds': 3600
        }
    
    def calculate_health_score(
        self,
        provider: str,
        metrics: Dict[str, any]
    ) -> HealthScore:
        try:
            total_requests = metrics.get('total_requests', 0)
            
            if total_requests == 0:
                return HealthScore(
                    overall_score=50.0,
                    latency_score=50.0,
                    reliability_score=50.0,
                    freshness_score=50.0,
                    status=HealthStatus.UNKNOWN,
                    factors={'no_data': 1.0},
                    last_checked=timezone.now().isoformat()
                )
            
            latency_score = self._calculate_latency_score(
                metrics.get('avg_latency_ms', 0),
                metrics.get('max_latency_ms', 0)
            )
            
            reliability_score = self._calculate_reliability_score(
                metrics.get('successful_requests', 0),
                metrics.get('failed_requests', 0),
                metrics.get('rate_limited_requests', 0),
                total_requests
            )
            
            freshness_score = self._calculate_freshness_score(
                metrics.get('last_success'),
                metrics.get('last_failure')
            )
            
            error_rate_score = self._calculate_error_rate_score(
                metrics.get('failed_requests', 0),
                metrics.get('rate_limited_requests', 0),
                total_requests
            )
            
            overall_score = (
                latency_score * self.weights['latency'] +
                reliability_score * self.weights['reliability'] +
                freshness_score * self.weights['freshness'] +
                error_rate_score * self.weights['error_rate']
            )
            
            if overall_score >= 70:
                status = HealthStatus.HEALTHY
            elif overall_score >= 40:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            factors = {
                'latency': latency_score,
                'reliability': reliability_score,
                'freshness': freshness_score,
                'error_rate': error_rate_score
            }
            
            return HealthScore(
                overall_score=overall_score,
                latency_score=latency_score,
                reliability_score=reliability_score,
                freshness_score=freshness_score,
                status=status,
                factors=factors,
                last_checked=timezone.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error calculating health score for {provider}: {e}")
            return HealthScore(
                overall_score=0.0,
                latency_score=0.0,
                reliability_score=0.0,
                freshness_score=0.0,
                status=HealthStatus.UNHEALTHY,
                factors={'error': 1.0},
                last_checked=timezone.now().isoformat()
            )
    
    def _calculate_latency_score(self, avg_latency: float, max_latency: float) -> float:
        if avg_latency <= self.latency_thresholds['excellent_ms']:
            return 100.0
        elif avg_latency <= self.latency_thresholds['good_ms']:
            return 90.0 + (100 - 90) * (1 - (avg_latency - self.latency_thresholds['excellent_ms']) / 
                                     (self.latency_thresholds['good_ms'] - self.latency_thresholds['excellent_ms']))
        elif avg_latency <= self.latency_thresholds['acceptable_ms']:
            return 70.0 + (90 - 70) * (1 - (avg_latency - self.latency_thresholds['good_ms']) / 
                                     (self.latency_thresholds['acceptable_ms'] - self.latency_thresholds['good_ms']))
        elif avg_latency <= self.latency_thresholds['poor_ms']:
            return 40.0 + (70 - 40) * (1 - (avg_latency - self.latency_thresholds['acceptable_ms']) / 
                                     (self.latency_thresholds['poor_ms'] - self.latency_thresholds['acceptable_ms']))
        else:
            return max(0, 40 - (avg_latency - self.latency_thresholds['poor_ms']) / 100)
    
    def _calculate_reliability_score(
        self,
        successful: int,
        failed: int,
        rate_limited: int,
        total: int
    ) -> float:
        if total == 0:
            return 50.0
        
        success_rate = successful / total
        
        if success_rate >= self.reliability_thresholds['excellent']:
            return 100.0
        elif success_rate >= self.reliability_thresholds['good']:
            return 90.0 + (100 - 90) * (success_rate - self.reliability_thresholds['good']) / \
                                (self.reliability_thresholds['excellent'] - self.reliability_thresholds['good'])
        elif success_rate >= self.reliability_thresholds['acceptable']:
            return 70.0 + (90 - 70) * (success_rate - self.reliability_thresholds['acceptable']) / \
                                (self.reliability_thresholds['good'] - self.reliability_thresholds['acceptable'])
        elif success_rate >= self.reliability_thresholds['poor']:
            return 40.0 + (70 - 40) * (success_rate - self.reliability_thresholds['poor']) / \
                                (self.reliability_thresholds['acceptable'] - self.reliability_thresholds['poor'])
        else:
            return max(0, 40 - (self.reliability_thresholds['poor'] - success_rate) * 100)
    
    def _calculate_freshness_score(
        self,
        last_success: Optional[str],
        last_failure: Optional[str]
    ) -> float:
        if not last_success and not last_failure:
            return 50.0
        
        last_activity = None
        if last_success and last_failure:
            success_time = timezone.make_aware(__import__('datetime').datetime.fromisoformat(last_success))
            failure_time = timezone.make_aware(__import__('datetime').datetime.fromisoformat(last_failure))
            last_activity = max(success_time, failure_time)
        elif last_success:
            last_activity = timezone.make_aware(__import__('datetime').datetime.fromisoformat(last_success))
        else:
            last_activity = timezone.make_aware(__import__('datetime').datetime.fromisoformat(last_failure))
        
        if not last_activity:
            return 50.0
        
        seconds_ago = (timezone.now() - last_activity).total_seconds()
        
        if seconds_ago <= self.freshness_thresholds['excellent_seconds']:
            return 100.0
        elif seconds_ago <= self.freshness_thresholds['good_seconds']:
            return 90.0 + (100 - 90) * (1 - (seconds_ago - self.freshness_thresholds['excellent_seconds']) / \
                                        (self.freshness_thresholds['good_seconds'] - self.freshness_thresholds['excellent_seconds']))
        elif seconds_ago <= self.freshness_thresholds['acceptable_seconds']:
            return 70.0 + (90 - 70) * (1 - (seconds_ago - self.freshness_thresholds['good_seconds']) / \
                                        (self.freshness_thresholds['acceptable_seconds'] - self.freshness_thresholds['good_seconds']))
        elif seconds_ago <= self.freshness_thresholds['poor_seconds']:
            return 40.0 + (70 - 40) * (1 - (seconds_ago - self.freshness_thresholds['acceptable_seconds']) / \
                                        (self.freshness_thresholds['poor_seconds'] - self.freshness_thresholds['acceptable_seconds']))
        else:
            return max(0, 40 - (seconds_ago - self.freshness_thresholds['poor_seconds']) / 3600)
    
    def _calculate_error_rate_score(
        self,
        failed: int,
        rate_limited: int,
        total: int
    ) -> float:
        if total == 0:
            return 50.0
        
        error_count = failed + rate_limited
        error_rate = error_count / total
        
        if error_rate == 0:
            return 100.0
        elif error_rate <= 0.01:
            return 95.0
        elif error_rate <= 0.05:
            return 85.0
        elif error_rate <= 0.10:
            return 70.0
        elif error_rate <= 0.20:
            return 50.0
        else:
            return max(0, 50 - (error_rate - 0.20) * 200)
    
    def get_recommended_provider(
        self,
        providers: Dict[str, Dict[str, any]]
    ) -> Optional[str]:
        best_provider = None
        best_score = -1
        
        for provider_name, metrics in providers.items():
            health = self.calculate_health_score(provider_name, metrics)
            
            if health.overall_score > best_score:
                best_score = health.overall_score
                best_provider = provider_name
        
        return best_provider
    
    def get_health_summary(self, providers: Dict[str, Dict[str, any]]) -> Dict[str, any]:
        if not providers:
            return {
                'total': 0,
                'healthy': 0,
                'degraded': 0,
                'unhealthy': 0,
                'average_score': 0,
                'best_provider': None
            }
        
        scores = []
        healthy = 0
        degraded = 0
        unhealthy = 0
        
        for provider_name, metrics in providers.items():
            health = self.calculate_health_score(provider_name, metrics)
            scores.append(health.overall_score)
            
            if health.status == HealthStatus.HEALTHY:
                healthy += 1
            elif health.status == HealthStatus.DEGRADED:
                degraded += 1
            else:
                unhealthy += 1
        
        best_provider = self.get_recommended_provider(providers)
        
        return {
            'total': len(providers),
            'healthy': healthy,
            'degraded': degraded,
            'unhealthy': unhealthy,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'best_provider': best_provider
        }
    
    def should_blacklist(self, health: HealthScore) -> bool:
        return (
            health.status == HealthStatus.UNHEALTHY and
            health.overall_score < 20 and
            health.factors.get('reliability', 100) < 30
        )
    
    def should_retry(self, health: HealthScore) -> bool:
        return health.overall_score >= 20 and health.overall_score < 70


_health_scorer_instance: Optional[HealthScorer] = None


def get_health_scorer() -> HealthScorer:
    global _health_scorer_instance
    if _health_scorer_instance is None:
        _health_scorer_instance = HealthScorer()
    return _health_scorer_instance
