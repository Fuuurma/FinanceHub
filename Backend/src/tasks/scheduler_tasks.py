from datetime import datetime, timedelta
from typing import List, Dict, Any
import dramatiq
from django.utils import timezone
from django.conf import settings

from utils.helpers.logger.logger import get_logger
from utils.services.data_orchestrator import get_data_orchestrator
from utils.services.cache_manager import get_cache_manager
from utils.services.call_planner import get_call_planner
from data.data_providers.unified_crypto_provider import UnifiedCryptoProvider
from data.data_providers.finnhub.scraper import FinnhubScraper
from data.data_providers.newsapi.scraper import NewsAPIScraper
from assets.models.asset import Asset

logger = get_logger(__name__)

orchestrator = get_data_orchestrator()
cache_manager = get_cache_manager()
call_planner = get_call_planner()


@dramatiq.actor
async def fetch_crypto_prices_task(symbols: List[str] = None):
    if symbols is None:
        symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOGE', 'XRP', 'DOT', 'MATIC']
    
    logger.info(f"Fetching crypto prices for {len(symbols)} symbols")
    
    try:
        unified_crypto = UnifiedCryptoProvider()
        
        for symbol in symbols:
            try:
                price_data = await unified_crypto.get_crypto_price(symbol)
                
                await cache_manager.set(
                    'crypto_price',
                    symbol,
                    value=price_data,
                    ttl=300
                )
                
                logger.debug(f"Updated crypto price for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to fetch price for {symbol}: {e}")
        
        logger.info(f"Successfully updated {len(symbols)} crypto prices")
        
    except Exception as e:
        logger.error(f"Crypto price fetch task failed: {e}")


@dramatiq.actor
async def fetch_stock_prices_task(symbols: List[str] = None, count: int = 50):
    from assets.models.asset import Asset, AssetType
    
    if symbols is None:
        try:
            crypto_type = AssetType.objects.filter(name__iexact='crypto').first()
            stocks = await Asset.objects.filter(asset_type=crypto_type).values_list('symbol', flat=True)[:count]
            symbols = list(stocks)
        except Exception as e:
            logger.error(f"Failed to fetch stock symbols: {e}")
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    
    logger.info(f"Fetching stock prices for {len(symbols)} symbols")
    
    try:
        finnhub = FinnhubScraper()
        
        for symbol in symbols:
            try:
                price_data = await finnhub.get_real_time_price(symbol)
                
                await cache_manager.set(
                    'stock_price',
                    symbol,
                    value=price_data,
                    ttl=900
                )
                
                logger.debug(f"Updated stock price for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to fetch price for {symbol}: {e}")
        
        logger.info(f"Successfully updated {len(symbols)} stock prices")
        
    except Exception as e:
        logger.error(f"Stock price fetch task failed: {e}")


@dramatiq.actor
async def fetch_crypto_historical_task(symbol: str, days: int = 30):
    logger.info(f"Fetching historical crypto data for {symbol} ({days} days)")
    
    try:
        unified_crypto = UnifiedCryptoProvider()
        historical_data = await unified_crypto.get_historical_prices(symbol, days=days)
        
        await cache_manager.set(
            'crypto_historical',
            symbol,
            value=historical_data,
            ttl=3600
        )
        
        logger.info(f"Updated historical data for {symbol}")
        
    except Exception as e:
        logger.error(f"Historical crypto fetch failed for {symbol}: {e}")


@dramatiq.actor
async def fetch_stock_historical_task(symbol: str, timespan: str = 'day', days: int = 30):
    logger.info(f"Fetching historical stock data for {symbol} ({days} days)")
    
    try:
        response = await orchestrator.get_market_data(
            'stock_historical',
            symbol,
            params={'timespan': timespan, 'days': days},
            priority=dramatiq.Priority.BATCH
        )
        
        logger.info(f"Updated historical data for {symbol}")
        
    except Exception as e:
        logger.error(f"Historical stock fetch failed for {symbol}: {e}")


@dramatiq.actor
async def fetch_news_task(query: str = None, category: str = None, count: int = 50):
    from data.data_providers.newsapi.scraper import NewsAPIScraper
    
    if query is None:
        query = "stocks OR crypto OR bitcoin OR ethereum OR finance"
    
    logger.info(f"Fetching news for query: {query}")
    
    try:
        newsapi = NewsAPIScraper()
        news_data = await newsapi.search_news(
            query=query,
            category=category,
            page_size=count
        )
        
        await cache_manager.set(
            'news',
            'general',
            value=news_data,
            ttl=3600
        )
        
        logger.info(f"Fetched {len(news_data.get('articles', []))} news articles")
        
    except Exception as e:
        logger.error(f"News fetch task failed: {e}")


@dramatiq.actor
async def fetch_technical_indicators_task(symbol: str, indicators: List[str] = None):
    if indicators is None:
        indicators = ['sma', 'ema', 'rsi', 'macd']
    
    logger.info(f"Fetching technical indicators for {symbol}")
    
    try:
        finnhub = FinnhubScraper()
        
        results = {}
        for indicator in indicators:
            try:
                data = await finnhub.get_technical_indicators(
                    symbol,
                    indicator=indicator
                )
                results[indicator] = data
            except Exception as e:
                logger.error(f"Failed to fetch {indicator} for {symbol}: {e}")
        
        await cache_manager.set(
            'technical_indicators',
            symbol,
            value=results,
            ttl=300
        )
        
        logger.info(f"Updated technical indicators for {symbol}")
        
    except Exception as e:
        logger.error(f"Technical indicators fetch failed for {symbol}: {e}")


@dramatiq.actor
async def cache_warming_task(symbols: List[str] = None):
    if symbols is None:
        symbols = ['BTC', 'ETH', 'SOL', 'AAPL', 'GOOGL', 'MSFT']
    
    logger.info(f"Warming cache for {len(symbols)} symbols")
    
    try:
        data_types = ['crypto_price', 'stock_price', 'crypto_historical', 'stock_historical']
        
        warmed = await orchestrator.prefetch_data(symbols, data_types)
        
        logger.info(f"Cache warming completed: {warmed}/{len(symbols) * len(data_types)} entries")
        
    except Exception as e:
        logger.error(f"Cache warming task failed: {e}")


@dramatiq.actor
async def health_check_task():
    logger.info("Running health checks")
    
    try:
        provider_health = await orchestrator.get_provider_health()
        
        for provider, health in provider_health.items():
            if not health.get('healthy'):
                logger.warning(f"Provider {provider} is unhealthy: {health}")
        
        cache_stats = await cache_manager.get_statistics()
        planner_stats = call_planner.get_statistics()
        
        logger.info(f"Cache hit rate: {cache_stats['statistics']['hit_rate']:.2%}")
        logger.info(f"Queue size: {planner_stats['queue_status']['pending']}")
        
    except Exception as e:
        logger.error(f"Health check task failed: {e}")


@dramatiq.actor
async def cleanup_old_cache_task(max_age_hours: int = 24):
    logger.info(f"Cleaning up cache entries older than {max_age_hours} hours")
    
    try:
        cutoff = timezone.now() - timedelta(hours=max_age_hours)
        
        cache_stats = await cache_manager.get_statistics()
        
        logger.info(f"Current L1 cache size: {cache_stats['l1_memory']['size']}")
        logger.info(f"Cache cleanup completed")
        
    except Exception as e:
        logger.error(f"Cache cleanup task failed: {e}")


@dramatiq.actor
async def batch_update_popular_assets():
    popular_symbols = {
        'crypto': ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'MATIC', 'AVAX', 'LINK'],
        'stocks': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT']
    }
    
    logger.info("Batch updating popular assets")
    
    try:
        await fetch_crypto_prices_task.send(popular_symbols['crypto'])
        await fetch_stock_prices_task.send(popular_symbols['stocks'])
        await fetch_news_task.send(query="bitcoin OR ethereum OR stocks", count=30)
        
        logger.info("Batch update completed")
        
    except Exception as e:
        logger.error(f"Batch update task failed: {e}")


@dramatiq.actor
async def validate_crypto_data_task(symbols: List[str] = None):
    if symbols is None:
        symbols = ['BTC', 'ETH', 'SOL']
    
    logger.info(f"Validating crypto data for {len(symbols)} symbols")
    
    try:
        from data.data_providers.crypto_cross_validator import CryptoCrossValidator
        
        validator = CryptoCrossValidator()
        
        for symbol in symbols:
            try:
                validation_result = await validator.validate_price(symbol)
                
                if validation_result['confidence_score'] < 0.85:
                    logger.warning(
                        f"Low confidence for {symbol}: "
                        f"{validation_result['confidence_score']:.2f}"
                    )
                else:
                    logger.debug(f"{symbol} validated successfully")
                
            except Exception as e:
                logger.error(f"Validation failed for {symbol}: {e}")
        
        logger.info("Crypto data validation completed")
        
    except Exception as e:
        logger.error(f"Validation task failed: {e}")


@dramatiq.actor
async def start_background_workers():
    logger.info("Starting background workers")
    
    try:
        if not call_planner.running:
            await call_planner.start(num_workers=3)
            logger.info("Call planner workers started")
        
        logger.info("Background workers initialized")
        
    except Exception as e:
        logger.error(f"Failed to start background workers: {e}")


def schedule_tasks():
    from dramatiq.brokers.rabbitmq import RabbitmqBroker
    from dramatiq.middleware import Prometheuses, AgeLimit, TimeLimit
    from dramatiq.scheduler import cron
    
    broker = RabbitmqBroker()
    broker.add_middleware(Prometheuses())
    broker.add_middleware(AgeLimit(max_age=3600000))
    broker.add_middleware(TimeLimit(time_limit=180000))
    
    broker.declare_queue('default')
    broker.declare_queue('high_priority')
    broker.declare_queue('low_priority')
    
    fetch_crypto_prices_task.send_with_options(
        queue='high_priority',
        kwargs={'symbols': ['BTC', 'ETH', 'SOL', 'ADA', 'DOGE', 'XRP', 'DOT', 'MATIC']}
    )
    
    fetch_stock_prices_task.send_with_options(
        queue='high_priority',
        kwargs={'count': 20}
    )
    
    fetch_news_task.send_with_options(
        queue='low_priority',
        kwargs={'query': 'bitcoin OR ethereum OR stocks OR finance', 'count': 30}
    )
    
    fetch_crypto_prices_task.send_with_options(
        queue='low_priority',
        kwargs={'symbols': ['AVAX', 'LINK', 'ATOM', 'NEAR', 'FIL']}
    )
    
    health_check_task.send_with_options(queue='low_priority')
    
    logger.info("Tasks scheduled successfully")
