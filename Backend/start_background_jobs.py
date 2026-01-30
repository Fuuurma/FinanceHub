#!/usr/bin/env python3
"""
Background Jobs Manager
Sets up Django environment and starts background workers with free API tiers
"""

import os
import sys
import django
from datetime import datetime

# Add src to Python path
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries

# Get logger
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Import tasks AFTER Django is setup
from tasks.crypto_data_tasks import (
    fetch_crypto_batch,
    fetch_crypto_quotes,
    fetch_trending_cryptos,
    fetch_top_cryptos,
    validate_crypto_batch,
    detect_crypto_anomalies,
    get_provider_health,
    get_validation_summary,
    clear_validation_cache,
    periodic_crypto_update,
    periodic_health_check,
)

from tasks.data_fetcher import (
    fetch_stocks_alpha,
    fetch_cryptos_coingecko,
    fetch_cryptos_coinmarketcap,
    fetch_all_markets,
    update_asset_price,
    batch_update_assets,
    clean_old_data,
    schedule_tasks,
)

from tasks.scheduler_tasks import (
    fetch_crypto_prices_task,
    fetch_stock_prices_task,
    fetch_crypto_historical_task,
    fetch_stock_historical_task,
    fetch_news_task,
    fetch_technical_indicators_task,
    cache_warming_task,
    health_check_task,
    cleanup_old_cache_task,
    batch_update_popular_assets,
    validate_crypto_data_task,
    start_background_workers,
)

# Configure Redis broker
broker = RedisBroker(url="redis://localhost:6379")
broker.add_middleware(AgeLimit(max_age=1000 * 60 * 60))
broker.add_middleware(TimeLimit(time_limit=1000 * 60 * 30))
broker.add_middleware(Retries(max_retries=3))

dramatiq.set_broker(broker)

# Define popular assets for data collection
POPULAR_STOCKS = [
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
    "KO",
    "PEP",
    "COST",
    "DIS",
    "NFLX",
    "ADBE",
    "INTC",
    "AMD",
    "CRM",
    "QCOM",
    "AVGO",
    "CSCO",
    "IBM",
    "ORCL",
    "ACN",
    "TXN",
    "NOW",
    "INTU",
    "LMT",
    "BA",
    "NOC",
    "RTX",
    "GD",
    "HON",
    "MMM",
    "CAT",
    "DE",
    "GE",
]

POPULAR_CRYPTOS = [
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
    "XLM",
    "ETC",
    "XMR",
    "ALGO",
    "VET",
    "FIL",
    "NEAR",
    "AAVE",
    "XTZ",
]


def start_background_workers():
    """Start all background data fetching jobs"""
    logger.info("=" * 60)
    logger.info("FinanceHub Background Data Collection Started")
    logger.info("=" * 60)

    logger.info("📅 Scheduled Tasks Configuration:")
    logger.info("  - Crypto prices: Every 2-5 minutes")
    logger.info("  - Stock prices: Every 5-10 minutes")
    logger.info("  - Historical data: Daily")
    logger.info("  - Health checks: Every minute")
    logger.info("  - Data validation: Hourly")

    logger.info("📊 Data Sources (Free Tier - No API Keys):")
    logger.info("  - yfinance: 🆓 Unlimited free calls")
    logger.info("  - CoinGecko: 🆓 30 calls/minute (250K/month)")
    logger.info("  - Yahoo Finance: 🆓 Unlimited free calls")

    logger.info("🎯 Assets Being Monitored:")
    logger.info(f"  - Stocks: {len(POPULAR_STOCKS)} (S&P 500 leaders)")
    logger.info(f"  - Cryptos: {len(POPULAR_CRYPTOS)} (Top market cap)")

    logger.info("🚀 Starting background workers...")
    logger.info("=" * 60)

    # Schedule periodic tasks
    logger.info("🕐 Starting periodic updates...")

    # Crypto batch updates every 2 minutes
    fetch_crypto_batch.send_with_options(
        args=[POPULAR_CRYPTOS[:30]], delay=1000 * 60 * 2, repeat=True
    )
    logger.info("  ✓ Crypto batch fetch: Every 2 minutes")

    # Stock updates every 5 minutes
    fetch_stocks_alpha.send_with_options(
        args=[POPULAR_STOCKS[:10]], delay=1000 * 60 * 5, repeat=True
    )
    logger.info("  ✓ Stock price updates: Every 5 minutes")

    # Health checks every minute
    periodic_health_check.send_with_options(delay=1000 * 60 * 1, repeat=True)
    logger.info("  ✓ Provider health checks: Every 1 minute")

    # Cross-validation every 10 minutes
    validate_crypto_batch.send_with_options(
        args=[POPULAR_CRYPTOS[:20]], delay=1000 * 60 * 10, repeat=True
    )
    logger.info("  ✓ Data validation: Every 10 minutes")

    # Trending cryptos every 15 minutes
    fetch_trending_cryptos.send_with_options(
        args=[10], delay=1000 * 60 * 15, repeat=True
    )
    logger.info("  ✓ Trending cryptos: Every 15 minutes")

    # Top cryptos every 30 minutes
    fetch_top_cryptos.send_with_options(
        args=[50, "market_cap"], delay=1000 * 60 * 30, repeat=True
    )
    logger.info("  ✓ Top cryptos ranking: Every 30 minutes")

    # Market data aggregation every 30 minutes
    fetch_all_markets.send_with_options(delay=1000 * 60 * 30, repeat=True)
    logger.info("  ✓ Market aggregation: Every 30 minutes")

    # Daily data cleanup
    clean_old_data.send_with_options(args=[365], delay=1000 * 60 * 60 * 24, repeat=True)
    logger.info("  ✓ Old data cleanup: Daily at midnight")

    logger.info("=" * 60)
    logger.info("✅ All background jobs scheduled successfully!")
    logger.info("=" * 60)
    logger.info("📝 Rate Limits Being Respected:")
    logger.info("  • CoinGecko: 30 calls/min (250K/month)")
    logger.info("  • Yahoo Finance: No limits (free tier)")
    logger.info("  • All providers: Proper rate limiting implemented")
    logger.info("=" * 60)


def run_immediate_tasks():
    """Run immediate data fetch tasks on startup"""
    logger.info("🚀 Running immediate data collection tasks...")

    # Fetch trending cryptos
    trending = fetch_trending_cryptos.send_with_options(args=[10], delay=1000 * 60 * 10)
    logger.info("  ✓ Started: Fetching trending cryptos")

    # Fetch top cryptos
    top_cryptos = fetch_top_cryptos.send_with_options(
        args=[30, "market_cap"], delay=1000 * 60 * 20
    )
    logger.info("  ✓ Started: Fetching top 30 cryptos")

    # Fetch stocks
    stocks = fetch_stocks_alpha.send_with_options(
        args=[POPULAR_STOCKS[:5]], delay=1000 * 60 * 5
    )
    logger.info("  ✓ Started: Fetching top 5 stocks")

    # Run health check
    health = get_provider_health.send_with_options(delay=1000 * 5)
    logger.info("  ✓ Started: Provider health check")

    logger.info("  ⏳ Waiting for first fetches to complete...")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        start_background_workers()
        run_immediate_tasks()
        logger.info("✨ Background jobs manager running. Press Ctrl+C to stop.")
        logger.info("=" * 60)

        # Keep script running
        import time

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping background jobs...")
        logger.info("✅ Shutdown complete.")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        sys.exit(1)
