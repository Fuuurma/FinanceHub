from typing import Optional, List
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache

from investments.models.api_key import APIKey, APIKeyStatus
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class APIKeyManager:
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.cache_timeout = 60
    
    def get_best_key(self, exclude_ids: List[int] = None) -> Optional[APIKey]:
        cache_key = f"api_keys:best:{self.provider_name}"
        
        cached_key_id = cache.get(cache_key)
        if cached_key_id:
            try:
                key = APIKey.objects.get(id=cached_key_id)
                if key.is_available():
                    return key
            except APIKey.DoesNotExist:
                cache.delete(cache_key)
        
        available_keys = self._get_available_keys(exclude_ids)
        
        if not available_keys:
            logger.warning(f"No available keys for provider {self.provider_name}")
            return None
        
        selected_key = self._select_weighted_key(available_keys)
        
        cache.set(cache_key, selected_key.id, self.cache_timeout)
        
        return selected_key
    
    def _get_available_keys(self, exclude_ids: List[int] = None) -> List[APIKey]:
        queryset = APIKey.objects.filter(
            provider__name=self.provider_name,
            status=APIKeyStatus.ACTIVE
        ).select_related("provider")
        
        if exclude_ids:
            queryset = queryset.exclude(id__in=exclude_ids)
        
        return list(queryset)
    
    def _select_weighted_key(self, keys: List[APIKey]) -> APIKey:
        now = timezone.now()
        best_key = None
        best_score = float("-inf")
        
        for key in keys:
            priority_score = (100 - key.priority) * 10
            usage_penalty = key.usage_this_hour * 2
            
            recent_use_penalty = 0
            if key.last_used_at:
                minutes_since_use = (now - key.last_used_at).total_seconds() / 60
                recent_use_penalty = max(0, 10 - minutes_since_use) * 5
            
            total_score = priority_score - usage_penalty - recent_use_penalty
            
            if total_score > best_score:
                best_score = total_score
                best_key = key
        
        return best_key
    
    def rotate_on_rate_limit(self, failed_key: APIKey) -> Optional[APIKey]:
        logger.warning(f"Rate limit hit for key {failed_key.name}")
        
        failed_key.mark_rate_limited()
        
        next_key = self.get_best_key(exclude_ids=[failed_key.id])
        
        if next_key:
            logger.info(f"Rotated to key {next_key.name}")
        else:
            logger.error(f"No available keys for {self.provider_name}")
        
        return next_key
    
    def recover_rate_limited_keys(self) -> int:
        now = timezone.now()
        keys_to_recover = []
        
        rate_limited_keys = APIKey.objects.filter(
            provider__name=self.provider_name,
            status=APIKeyStatus.RATE_LIMITED
        )
        
        for key in rate_limited_keys:
            if key.last_failure_at:
                minutes_since_failure = (now - key.last_failure_at).total_seconds() / 60
                
                if minutes_since_failure >= key.auto_recover_after_minutes:
                    keys_to_recover.append(key)
        
        for key in keys_to_recover:
            key.status = APIKeyStatus.ACTIVE
            key.consecutive_failures = 0
            key.save(update_fields=["status", "consecutive_failures"])
            logger.info(f"Recovered rate-limited key {key.name}")
        
        cache.delete(f"api_keys:best:{self.provider_name}")
        
        return len(keys_to_recover)
    
    def get_key_health_report(self) -> dict:
        keys = APIKey.objects.filter(provider__name=self.provider_name)
        
        report = {
            "provider": self.provider_name,
            "total_keys": keys.count(),
            "active_keys": keys.filter(status=APIKeyStatus.ACTIVE).count(),
            "rate_limited_keys": keys.filter(status=APIKeyStatus.RATE_LIMITED).count(),
            "disabled_keys": keys.filter(status=APIKeyStatus.DISABLED).count(),
            "keys": []
        }
        
        for key in keys:
            report["keys"].append({
                "name": key.name,
                "status": key.status,
                "priority": key.priority,
                "usage_today": key.usage_today,
                "usage_this_hour": key.usage_this_hour,
                "consecutive_failures": key.consecutive_failures,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            })
        
        return report
