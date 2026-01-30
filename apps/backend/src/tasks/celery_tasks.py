"""
Celery-based Task Scheduler and Queue
Production-ready background task processing with Celery and Redis
"""
from celery import Celery, shared_task
from celery.schedules import crontab
from celery.exceptions import Retry
from django.conf import settings
from datetime import datetime, timedelta
import logging
import time

from data.data_providers.yahooFinance.scraper import YahooFinanceScraper
from data.data_providers.alphaVantage.scraper import AlphaVantageScraper
from data.data_providers.binance.scraper import BinanceScraper
from data.data_providers.coinGecko.scraper import CoinGeckoScraper
from data.data_providers.coinMarketCap.scraper import CoinMarketCapScraper
from data.processing.pipeline import DataPipeline, create_pipeline
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Celery app configuration
app = Celery('financehub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['tasks'])

# Enable Django settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Initialize scrapers
yahoo_scraper = YahooFinanceScraper()
alpha_scraper = AlphaVantageScraper(api_key=getattr(settings, 'ALPHA_VANTAGE_API_KEY', None))
binance_scraper = BinanceScraper()
coingecko_scraper = CoinGeckoScraper()
coinmarketcap_scraper = CoinMarketCapScraper()

# Initialize data pipeline
data_pipeline = create_pipeline()

# Asset symbols for regular fetching
TOP_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
    'V', 'JNJ', 'WMT', 'PG', 'XOM', 'BAC', 'KO', 'PEP', 'COST',
    'DIS', 'NFLX', 'ADBE', 'INTC', 'AMD', 'CRM', 'QCOM', 'AVGO',
    'CSCO', 'IBM', 'ORCL', 'ACN', 'TXN', 'NOW', 'INTU', 'LMT',
    'BA', 'NOC', 'RTX', 'GD', 'HON', 'MMM', 'CAT', 'DE', 'GE',
    'MRK', 'UNH', 'PFE', 'CVX', 'COP', 'HES', 'SLB'
]

TOP_CRYPTOS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT',
    'MATIC', 'LTC', 'AVAX', 'LINK', 'UNI', 'ATOM', 'XLM',
    'ETC', 'XMR', 'ALGO', 'VET', 'FIL', 'NEAR', 'AAVE', 'XTZ',
    'SHIB', 'TRX', 'AVAX', 'MANA', 'SAND'
]

# Task priorities
HIGH_PRIORITY = 9
MEDIUM_PRIORITY = 5
LOW_PRIORITY = 1


@shared_task(bind=True, max_retries=3, priority=HIGH_PRIORITY)
def fetch_yahoo_stocks_task(self, symbols: list = None, limit: int = 20):
    """
    Fetch stock data from Yahoo Finance
    Runs every 5 minutes
    
    Args:
        symbols: List of stock symbols to fetch
        limit: Maximum number of symbols to fetch if symbols not provided
    
    Returns:
        Dict with fetch statistics
    """
    start_time = time.time()
    
    try:
        if symbols is None:
            symbols = TOP_STOCKS[:limit]
        
        logger.info(f"[Celery] Fetching {len(symbols)} stocks from Yahoo Finance")
        
        results = yahoo_scraper.fetch_multiple_stocks(symbols)
        success_count = sum(1 for v in results.values() if v)
        failed_count = len(symbols) - success_count
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"[Celery] Yahoo Finance fetch completed in {elapsed:.2f}s: "
            f"{success_count}/{len(symbols)} succeeded, {failed_count} failed"
        )
        
        return {
            'source': 'yahoo',
            'total': len(symbols),
            'success': success_count,
            'failed': failed_count,
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] Yahoo Finance fetch failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3, priority=MEDIUM_PRIORITY)
def fetch_alpha_stocks_task(self, symbols: list = None, limit: int = 10):
    """
    Fetch stock data from Alpha Vantage
    Runs every 10 minutes (rate limited)
    
    Args:
        symbols: List of stock symbols to fetch
        limit: Maximum number of symbols to fetch if symbols not provided
    
    Returns:
        Dict with fetch statistics
    """
    start_time = time.time()
    
    try:
        if symbols is None:
            symbols = TOP_STOCKS[:limit]
        
        logger.info(f"[Celery] Fetching {len(symbols)} stocks from Alpha Vantage")
        
        results = alpha_scraper.fetch_multiple_stocks(symbols)
        success_count = sum(1 for v in results.values() if v)
        failed_count = len(symbols) - success_count
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"[Celery] Alpha Vantage fetch completed in {elapsed:.2f}s: "
            f"{success_count}/{len(symbols)} succeeded, {failed_count} failed"
        )
        
        return {
            'source': 'alpha_vantage',
            'total': len(symbols),
            'success': success_count,
            'failed': failed_count,
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] Alpha Vantage fetch failed: {str(e)}")
        raise self.retry(exc=e, countdown=120)


@shared_task(bind=True, max_retries=3, priority=HIGH_PRIORITY)
def fetch_binance_cryptos_task(self, symbols: list = None, limit: int = 20):
    """
    Fetch crypto data from Binance
    Runs every 2 minutes
    
    Args:
        symbols: List of crypto symbols to fetch
        limit: Maximum number of symbols to fetch if symbols not provided
    
    Returns:
        Dict with fetch statistics
    """
    start_time = time.time()
    
    try:
        if symbols is None:
            symbols = TOP_CRYPTOS[:limit]
        
        logger.info(f"[Celery] Fetching {len(symbols)} cryptos from Binance")
        
        results = binance_scraper.fetch_multiple_cryptos(symbols)
        success_count = sum(1 for v in results.values() if v)
        failed_count = len(symbols) - success_count
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"[Celery] Binance fetch completed in {elapsed:.2f}s: "
            f"{success_count}/{len(symbols)} succeeded, {failed_count} failed"
        )
        
        return {
            'source': 'binance',
            'total': len(symbols),
            'success': success_count,
            'failed': failed_count,
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] Binance fetch failed: {str(e)}")
        raise self.retry(exc=e, countdown=30)


@shared_task(bind=True, max_retries=3, priority=MEDIUM_PRIORITY)
def fetch_coingecko_cryptos_task(self, symbols: list = None, limit: int = 20):
    """
    Fetch crypto data from CoinGecko
    Runs every 10 minutes (rate limited)
    
    Args:
        symbols: List of crypto symbols to fetch
        limit: Maximum number of symbols to fetch if symbols not provided
    
    Returns:
        Dict with fetch statistics
    """
    start_time = time.time()
    
    try:
        if symbols is None:
            symbols = TOP_CRYPTOS[:limit]
        
        logger.info(f"[Celery] Fetching {len(symbols)} cryptos from CoinGecko")
        
        results = coingecko_scraper.fetch_multiple_cryptos(symbols)
        success_count = sum(1 for v in results.values() if v)
        failed_count = len(symbols) - success_count
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"[Celery] CoinGecko fetch completed in {elapsed:.2f}s: "
            f"{success_count}/{len(symbols)} succeeded, {failed_count} failed"
        )
        
        return {
            'source': 'coingecko',
            'total': len(symbols),
            'success': success_count,
            'failed': failed_count,
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] CoinGecko fetch failed: {str(e)}")
        raise self.retry(exc=e, countdown=120)


@shared_task(bind=True, max_retries=3, priority=MEDIUM_PRIORITY)
def fetch_coinmarketcap_cryptos_task(self, symbols: list = None, limit: int = 20):
    """
    Fetch crypto data from CoinMarketCap
    Runs every 15 minutes (rate limited)
    
    Args:
        symbols: List of crypto symbols to fetch
        limit: Maximum number of symbols to fetch if symbols not provided
    
    Returns:
        Dict with fetch statistics
    """
    start_time = time.time()
    
    try:
        if symbols is None:
            symbols = TOP_CRYPTOS[:limit]
        
        logger.info(f"[Celery] Fetching {len(symbols)} cryptos from CoinMarketCap")
        
        results = coinmarketcap_scraper.fetch_multiple_cryptos(symbols)
        success_count = sum(1 for v in results.values() if v)
        failed_count = len(symbols) - success_count
        
        elapsed = time.time() - start_time
        
        logger.info(
            f"[Celery] CoinMarketCap fetch completed in {elapsed:.2f}s: "
            f"{success_count}/{len(symbols)} succeeded, {failed_count} failed"
        )
        
        return {
            'source': 'coinmarketcap',
            'total': len(symbols),
            'success': success_count,
            'failed': failed_count,
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] CoinMarketCap fetch failed: {str(e)}")
        raise self.retry(exc=e, countdown=180)


@shared_task(bind=True, max_retries=2, priority=HIGH_PRIORITY)
def fetch_all_markets_task(self):
    """
    Fetch data from all sources simultaneously
    Runs every 15 minutes
    
    This task chains multiple fetch tasks together
    """
    from celery import chain, group
    
    logger.info(f"[Celery] Starting full market data fetch: {self.request.id}")
    
    start_time = time.time()
    
    try:
        # Create group of fetch tasks
        fetch_group = group(
            fetch_yahoo_stocks_task.s(limit=25),
            fetch_alpha_stocks_task.s(limit=10),
            fetch_binance_cryptos_task.s(limit=30),
            fetch_coingecko_cryptos_task.s(limit=20),
            fetch_coinmarketcap_cryptos_task.s(limit=20)
        )
        
        # Execute group
        result = fetch_group.apply_async()
        
        elapsed = time.time() - start_time
        logger.info(f"[Celery] All market fetches initiated in {elapsed:.2f}s")
        
        return {
            'task_id': self.request.id,
            'group_id': result.id,
            'status': 'initiated',
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[Celery] Full market fetch failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3, priority=HIGH_PRIORITY)
def update_single_asset_task(self, symbol: str, source: str = 'auto'):
    """
    Update data for a single asset
    Used for real-time updates or manual triggers
    
    Args:
        symbol: Asset symbol to update
        source: Data source to use (or 'auto' to select best)
    
    Returns:
        Dict with update results
    """
    start_time = time.time()
    
    try:
        logger.info(f"[Celery] Updating asset: {symbol} from {source}")
        
        # Determine best source
        scraper_map = {
            'yahoo': yahoo_scraper,
            'alpha': alpha_scraper,
            'binance': binance_scraper,
            'coingecko': coingecko_scraper,
            'coinmarketcap': coinmarketcap_scraper
        }
        
        scraper = scraper_map.get(source)
        if not scraper and source == 'auto':
            # Auto-detect if crypto or stock
            if symbol in TOP_CRYPTOS:
                scraper = binance_scraper
            else:
                scraper = yahoo_scraper
        
        if not scraper:
            return {
                'symbol': symbol,
                'error': f'Unknown source: {source}',
                'success': False
            }
        
        # Fetch and save
        if source in ['binance', 'coingecko', 'coinmarketcap']:
            success = scraper.fetch_and_save_crypto(symbol)
        else:
            success = scraper.fetch_and_save_stock(symbol)
        
        elapsed = time.time() - start_time
        
        logger.info(f"[Celery] Asset update for {symbol} completed in {elapsed:.2f}s")
        
        return {
            'symbol': symbol,
            'source': source,
            'success': success,
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] Single asset update failed for {symbol}: {str(e)}")
        raise self.retry(exc=e, countdown=30)


@shared_task(bind=True, max_retries=1, priority=LOW_PRIORITY)
def calculate_indicators_task(self, symbol: str, period: int = 200):
    """
    Calculate technical indicators for an asset
    Runs hourly for recently updated assets
    
    Args:
        symbol: Asset symbol
        period: Number of data points to use (default: 200)
    
    Returns:
        Dict with calculated indicators
    """
    from assets.models.historic.prices import AssetPricesHistoric
    from datetime import timedelta
    
    try:
        logger.info(f"[Celery] Calculating indicators for {symbol}")
        
        # Get historical prices
        asset = Asset.objects.filter(symbol__iexact=symbol).first()
        if not asset:
            return {'error': f'Asset {symbol} not found', 'success': False}
        
        cutoff_date = datetime.now() - timedelta(days=365)
        prices = AssetPricesHistoric.objects.filter(
            asset=asset,
            timestamp__gte=cutoff_date
        ).order_by('timestamp')[:period]
        
        if len(prices) < 20:
            return {'error': 'Not enough data points', 'success': False}
        
        # Convert to list for processing
        price_data = [
            {
                'open': float(p.open),
                'high': float(p.high),
                'low': float(p.low),
                'close': float(p.close),
                'volume': float(p.volume),
                'timestamp': p.timestamp
            }
            for p in prices
        ]
        
        # Process with indicators
        result = data_pipeline.process_with_indicators(price_data, 'combined')
        
        logger.info(f"[Celery] Indicators calculated for {symbol}")
        
        return {
            'symbol': symbol,
            'success': True,
            'indicators': result.get('indicators', {}),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] Indicator calculation failed for {symbol}: {str(e)}")
        return {
            'symbol': symbol,
            'error': str(e),
            'success': False
        }


@shared_task(bind=True, max_retries=1, priority=LOW_PRIORITY)
def cleanup_old_data_task(self, days: int = 365):
    """
    Clean up old historical data
    Runs daily at midnight
    
    Args:
        days: Keep data newer than this many days
    
    Returns:
        Dict with cleanup statistics
    """
    from assets.models.historic.prices import AssetPricesHistoric
    from django.utils import timezone
    
    try:
        logger.info(f"[Celery] Starting cleanup of data older than {days} days")
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        deleted_count, _ = AssetPricesHistoric.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"[Celery] Cleanup completed: {deleted_count} records deleted")
        
        return {
            'deleted_count': deleted_count,
            'cutoff_days': days,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
    
    except Exception as e:
        logger.error(f"[Celery] Cleanup task failed: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }


@shared_task(bind=True, max_retries=1, priority=LOW_PRIORITY)
def health_check_task(self):
    """
    Health check task
    Runs every minute
    
    Checks system health and logs status
    """
    from django.core.cache import cache
    
    try:
        # Check cache connectivity
        cache.set('health_check', 'ok', timeout=60)
        cache_ok = cache.get('health_check') == 'ok'
        
        # Check task queue
        from celery import current_app
        inspect = current_app.control.inspect()
        active_tasks = inspect.active()
        
        stats = {
            'cache_healthy': cache_ok,
            'active_tasks': len(active_tasks) if active_tasks else 0,
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id,
            'status': 'healthy' if cache_ok else 'unhealthy'
        }
        
        logger.info(f"[Celery] Health check: {stats}")
        
        return stats
    
    except Exception as e:
        logger.error(f"[Celery] Health check failed: {str(e)}")
        return {
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }


# Schedule configuration
app.conf.beat_schedule = {
    # Market data fetches
    'fetch-yahoo-stocks-every-5-minutes': {
        'task': 'tasks.celery_tasks.fetch_yahoo_stocks_task',
        'schedule': crontab(minute='*/5'),
    },
    'fetch-alpha-stocks-every-10-minutes': {
        'task': 'tasks.celery_tasks.fetch_alpha_stocks_task',
        'schedule': crontab(minute='*/10'),
    },
    'fetch-binance-cryptos-every-2-minutes': {
        'task': 'tasks.celery_tasks.fetch_binance_cryptos_task',
        'schedule': crontab(minute='*/2'),
    },
    'fetch-coingecko-cryptos-every-10-minutes': {
        'task': 'tasks.celery_tasks.fetch_coingecko_cryptos_task',
        'schedule': crontab(minute='*/10'),
    },
    'fetch-coinmarketcap-cryptos-every-15-minutes': {
        'task': 'tasks.celery_tasks.fetch_coinmarketcap_cryptos_task',
        'schedule': crontab(minute='*/15'),
    },
    'fetch-all-markets-every-15-minutes': {
        'task': 'tasks.celery_tasks.fetch_all_markets_task',
        'schedule': crontab(minute='*/15'),
    },
    # Indicator calculations
    'calculate-indicators-every-hour': {
        'task': 'tasks.celery_tasks.calculate_indicators_task',
        'schedule': crontab(minute=0, hour='*'),  # Every hour
        'kwargs': {
            'symbol': 'AAPL',  # This would be dynamic in production
            'period': 200
        }
    },
    # Maintenance
    'cleanup-old-data-daily': {
        'task': 'tasks.celery_tasks.cleanup_old_data_task',
        'schedule': crontab(minute=0, hour=2),  # 2 AM daily
    },
    'health-check-every-minute': {
        'task': 'tasks.celery_tasks.health_check_task',
        'schedule': crontab(minute='*'),
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f"[Celery] Debug task executed: {self.request.id}")
    return {
        'message': 'Celery is working!',
        'task_id': self.request.id,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    # Test individual tasks
    app.worker_main(['worker', '--loglevel=info'])
