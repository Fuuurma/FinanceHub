"""
Unified Task Queue System
Consolidated background task processing with Celery
Replaces duplicate Dramatiq + Celery systems
"""

from celery import Celery, shared_task
from celery.schedules import crontab
from django.conf import settings
from django.db import DatabaseError, OperationalError
from datetime import datetime, timedelta
import logging
import traceback
from redis import RedisError as CacheError
from httpx import NetworkError, TimeoutException

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

app = Celery("financehub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["tasks"])

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

HIGH_PRIORITY = 9
MEDIUM_PRIORITY = 5
LOW_PRIORITY = 1

_scraper_cache = {}


def get_yahoo_scraper():
    if "yahoo" not in _scraper_cache:
        from data.data_providers.yahooFinance.scraper import YahooFinanceScraper

        _scraper_cache["yahoo"] = YahooFinanceScraper()
    return _scraper_cache["yahoo"]


def get_alpha_scraper():
    if "alpha" not in _scraper_cache:
        from data.data_providers.alphaVantage.scraper import AlphaVantageScraper

        api_key = getattr(settings, "ALPHA_VANTAGE_API_KEY", None)
        _scraper_cache["alpha"] = AlphaVantageScraper(api_key=api_key)
    return _scraper_cache["alpha"]


def get_binance_scraper():
    if "binance" not in _scraper_cache:
        from data.data_providers.binance.scraper import BinanceScraper

        _scraper_cache["binance"] = BinanceScraper()
    return _scraper_cache["binance"]


def get_coingecko_scraper():
    if "coingecko" not in _scraper_cache:
        from data.data_providers.coinGecko.scraper import CoinGeckoScraper

        _scraper_cache["coingecko"] = CoinGeckoScraper()
    return _scraper_cache["coingecko"]


def get_unified_crypto_provider():
    if "unified_crypto" not in _scraper_cache:
        from data.data_providers.unified_crypto_provider import UnifiedCryptoProvider

        _scraper_cache["unified_crypto"] = UnifiedCryptoProvider()
    return _scraper_cache["unified_crypto"]


def get_data_pipeline():
    if "pipeline" not in _scraper_cache:
        from data.processing.pipeline import create_pipeline

        _scraper_cache["pipeline"] = create_pipeline()
    return _scraper_cache["pipeline"]


def get_active_symbols(asset_type="stock", limit=100):
    from assets.models.asset import Asset, AssetType

    try:
        at = AssetType.objects.filter(name__iexact=asset_type).first()
        if at:
            return list(
                Asset.objects.filter(asset_type=at, is_active=True).values_list(
                    "symbol", flat=True
                )[:limit]
            )
    except (DatabaseError, CacheError) as e:
        logger.error(f"Failed to get active symbols: {e}")
    return []


TOP_STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "META",
    "NVDA",
    "JPM",
    "V",
    "JNJ",
    "WMT",
    "PG",
    "XOM",
    "BAC",
]
TOP_CRYPTOS = [
    "BTC",
    "ETH",
    "BNB",
    "XRP",
    "ADA",
    "DOGE",
    "SOL",
    "DOT",
    "MATIC",
    "LTC",
    "AVAX",
    "LINK",
    "UNI",
    "ATOM",
]


def send_to_dead_letter(task_name, args, kwargs, exception):
    try:
        from tasks.models import TaskFailure

        TaskFailure.objects.create(
            task_name=task_name,
            args=str(args),
            kwargs=str(kwargs),
            exception=str(exception),
            traceback=traceback.format_exc(),
        )
        logger.warning(f"Task {task_name} sent to dead letter queue")
    except (DatabaseError, ImportError) as e:
        logger.error(f"Failed to send to DLQ: {e}")


@shared_task(
    bind=True, max_retries=5, priority=HIGH_PRIORITY, name="tasks.fetch_yahoo_stocks"
)
def fetch_yahoo_stocks_task(self, symbols=None, limit=20):
    if symbols is None:
        symbols = TOP_STOCKS[:limit]
    try:
        scraper = get_yahoo_scraper()
        pipeline = get_data_pipeline()
        for symbol in symbols:
            try:
                data = scraper.get_stock_info(symbol)
                if data:
                    processed = pipeline.process_raw_data(data, "yahoo", "stock")
                    if processed.is_valid:
                        pipeline.save_to_database(processed)
                        logger.info(f"Updated Yahoo data for {symbol}")
            except (ValueError, KeyError, TypeError) as e:
                raise self.retry(exc=e, countdown=60 * (2**self.request.retries))
        return {"symbols_processed": len(symbols)}
    except (DatabaseError, ValueError) as e:
        logger.error(f"Yahoo task failed: {e}")
        send_to_dead_letter("fetch_yahoo_stocks", (symbols,), {}, e)
        raise


@shared_task(
    bind=True, max_retries=5, priority=HIGH_PRIORITY, name="tasks.fetch_binance_cryptos"
)
def fetch_binance_cryptos_task(self, symbols=None, limit=20):
    if symbols is None:
        symbols = TOP_CRYPTOS[:limit]
    try:
        scraper = get_binance_scraper()
        pipeline = get_data_pipeline()
        for symbol in symbols:
            try:
                data = scraper.get_crypto_info(symbol)
                if data:
                    processed = pipeline.process_raw_data(data, "binance", "crypto")
                    if processed.is_valid:
                        pipeline.save_to_database(processed)
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Binance fetch failed for {symbol}: {e}")
        return {"symbols_processed": len(symbols)}
    except (NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Binance task failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task(
    bind=True,
    max_retries=5,
    priority=HIGH_PRIORITY,
    name="tasks.fetch_coingecko_cryptos",
)
def fetch_coingecko_cryptos_task(self, symbols=None, limit=20):
    if symbols is None:
        symbols = TOP_CRYPTOS[:limit]
    try:
        scraper = get_coingecko_scraper()
        pipeline = get_data_pipeline()
        for symbol in symbols:
            try:
                data = scraper.get_crypto_data(symbol)
                if data:
                    processed = pipeline.process_raw_data(data, "coingecko", "crypto")
                    if processed.is_valid:
                        pipeline.save_to_database(processed)
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"CoinGecko fetch failed for {symbol}: {e}")
        return {"symbols_processed": len(symbols)}
    except (NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"CoinGecko task failed: {e}")
        raise self.retry(exc=e, countdown=120 * (2**self.request.retries))


@shared_task(
    bind=True, max_retries=3, priority=HIGH_PRIORITY, name="tasks.fetch_unified_crypto"
)
def fetch_unified_crypto_task(self, symbols=None):
    if symbols is None:
        symbols = ["BTC", "ETH", "SOL", "ADA", "DOGE", "XRP"]
    try:
        provider = get_unified_crypto_provider()
        pipeline = get_data_pipeline()
        for symbol in symbols:
            try:
                data = provider.get_crypto_price(symbol)
                if data:
                    processed = pipeline.process_raw_data(
                        data, "unified_crypto", "crypto"
                    )
                    if processed.is_valid:
                        pipeline.save_to_database(processed)
                        logger.info(f"Updated unified crypto for {symbol}")
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Unified crypto failed for {symbol}: {e}")
        return {"symbols_processed": len(symbols)}
    except (NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Unified crypto task failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task(
    bind=True,
    max_retries=3,
    priority=MEDIUM_PRIORITY,
    name="tasks.calculate_indicators",
)
def calculate_indicators_task(self, symbols=None, period=200):
    if symbols is None:
        symbols = get_active_symbols("stock", 50)
    try:
        pipeline = get_data_pipeline()
        for symbol in symbols:
            try:
                data = {
                    "symbol": symbol,
                    "source": "internal",
                    "close": [],
                    "high": [],
                    "low": [],
                    "open": [],
                    "volume": [],
                }
                processed = pipeline.process_raw_data(data, "internal", "stock")
                if processed.is_valid:
                    logger.debug(f"Calculated indicators for {symbol}")
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Indicator calc failed for {symbol}: {e}")
        return {"symbols_processed": len(symbols), "period": period}
    except (ValueError, DatabaseError) as e:
        logger.error(f"Calculate indicators task failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task(
    bind=True, max_retries=1, priority=LOW_PRIORITY, name="tasks.cleanup_old_data"
)
def cleanup_old_data_task(self, days=365):
    try:
        from assets.models.historic.prices import AssetPricesHistoric
        from datetime import datetime as dt

        cutoff = dt.now() - timedelta(days=days)
        deleted, _ = AssetPricesHistoric.objects.filter(timestamp__lt=cutoff).delete()
        logger.info(f"Cleaned up {deleted} old price records")
        return {"records_deleted": deleted}
    except (DatabaseError, OperationalError) as e:
        logger.error(f"Cleanup task failed: {e}")
        raise


@shared_task(bind=True, name="tasks.health_check")
def health_check_task(self):
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except (DatabaseError, OperationalError) as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@shared_task(
    bind=True, max_retries=3, priority=MEDIUM_PRIORITY, name="tasks.fetch_stock_prices"
)
def fetch_stock_prices_task(self, symbols=None, count=50):
    if symbols is None:
        symbols = get_active_symbols("stock", count)
    try:
        from data.data_providers.finnHub.scraper import FinnhubScraper

        scraper = FinnhubScraper()
        pipeline = get_data_pipeline()
        for symbol in symbols:
            try:
                data = scraper.get_real_time_price(symbol)
                if data:
                    processed = pipeline.process_raw_data(data, "finnhub", "stock")
                    if processed.is_valid:
                        pipeline.save_to_database(processed)
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Finnhub fetch failed for {symbol}: {e}")
        return {"symbols_processed": len(symbols)}
    except (NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Stock prices task failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task(
    bind=True, max_retries=3, priority=MEDIUM_PRIORITY, name="tasks.fetch_news"
)
def fetch_news_task(self, query=None, category=None, count=50):
    try:
        from data.data_providers.newsapi.scraper import NewsAPIScraper

        scraper = NewsAPIScraper()
        news_data = scraper.get_latest_news(query=query, category=category, limit=count)
        logger.info(f"Fetched {len(news_data) if news_data else 0} news articles")
        return {"articles_fetched": len(news_data) if news_data else 0}
    except (NetworkError, TimeoutException, ValueError) as e:
        logger.error(f"News task failed: {e}")
        raise self.retry(exc=e, countdown=120 * (2**self.request.retries))


@shared_task(
    bind=True, max_retries=3, priority=MEDIUM_PRIORITY, name="tasks.cache_warming"
)
def cache_warming_task(self, symbols=None):
    if symbols is None:
        symbols = TOP_STOCKS[:20] + TOP_CRYPTOS[:10]
    try:
        from utils.services.cache_manager import get_cache_manager

        cache = get_cache_manager()
        for symbol in symbols:
            try:
                cache.set("price", symbol, {"status": "warmed"}, ttl=3600)
            except (CacheError, ValueError) as e:
                logger.warning(f"Cache warming failed for {symbol}: {e}")
        return {"symbols_warmed": len(symbols)}
    except (ImportError, CacheError) as e:
        logger.error(f"Cache warming task failed: {e}")
        raise


@app.task(name="tasks.batch_update_popular")
def batch_update_popular_assets():
    fetch_yahoo_stocks_task.delay(symbols=TOP_STOCKS[:20])
    fetch_binance_cryptos_task.delay(symbols=TOP_CRYPTOS[:15])
    fetch_unified_crypto_task.delay(symbols=TOP_CRYPTOS[:10])
    return {"tasks_dispatched": 3, "timestamp": datetime.now().isoformat()}
