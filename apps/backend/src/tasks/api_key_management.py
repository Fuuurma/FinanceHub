import dramatiq
from django.utils import timezone
from investments.services.api_key_manager import APIKeyManager
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

@dramatiq.actor
def recover_rate_limited_keys():
    providers = ["polygon", "iex_cloud", "finnhub", "alpha_vantage", "coingecko", "news_api"]
    
    total_recovered = 0
    for provider in providers:
        try:
            manager = APIKeyManager(provider)
            recovered = manager.recover_rate_limited_keys()
            total_recovered += recovered
        except Exception as e:
            logger.error(f"Error recovering keys for {provider}: {str(e)}")
    
    logger.info(f"Recovered {total_recovered} rate-limited keys")


@dramatiq.actor
def reset_daily_usage_counters():
    from investments.models.api_key import APIKey
    
    updated = APIKey.objects.filter(usage_today__gt=0).update(
        usage_today=0,
        usage_today_reset=timezone.now()
    )
    
    logger.info(f"Reset daily usage for {updated} keys")


@dramatiq.actor
def generate_health_report():
    providers = ["polygon", "iex_cloud", "finnhub", "alpha_vantage", "coingecko", "news_api"]
    
    for provider in providers:
        try:
            manager = APIKeyManager(provider)
            report = manager.get_key_health_report()
            logger.info(f"Health report for {provider}: {report}")
            
            from django.core.cache import cache
            cache.set(f"api_health:{provider}", report, 3600)
            
        except Exception as e:
            logger.error(f"Error generating health report for {provider}: {str(e)}")
