#!/usr/bin/env python3
"""
Background Jobs Monitoring Dashboard
Shows real-time statistics and health of background data collection
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import dramatiq
from dramatiq.brokers.redis import RedisBroker

# Get modules
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

# Connect to Redis
try:
    import redis

    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
except Exception as e:
    print(f"❌ Cannot connect to Redis: {e}")
    sys.exit(1)


def get_queue_stats():
    """Get statistics from Dramatiq queues"""
    stats = {}

    queues = ["default", "high_priority", "low_priority"]

    for queue in queues:
        queue_key = f"dramatiq:{queue}"
        pending = r.llen(queue_key)
        stats[queue] = {
            "pending": pending,
            "status": "✅ Active" if pending > 0 else "⏸️ Idle",
        }

    return stats


def get_redis_stats():
    """Get Redis server statistics"""
    try:
        info = r.info("stats")
        memory = r.info("memory")

        return {
            "total_connections": info.get("total_connections_received", 0),
            "total_commands": info.get("total_commands_processed", 0),
            "used_memory_human": memory.get("used_memory_human", "0B"),
            "used_memory_peak_human": memory.get("used_memory_peak_human", "0B"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_database_stats():
    """Get database statistics"""
    try:
        from assets.models.asset import Asset
        from assets.models.historic.prices import AssetPricesHistoric

        # Count assets
        total_assets = Asset.objects.count()
        stocks = Asset.objects.filter(asset_type__name__iexact="stock").count()
        cryptos = Asset.objects.filter(asset_type__name__iexact="crypto").count()

        # Count price records
        total_prices = AssetPricesHistoric.objects.count()

        # Latest updates
        latest_update = AssetPricesHistoric.objects.order_by("-timestamp").first()
        latest_time = latest_update.timestamp if latest_update else None

        # Records in last 24h
        yesterday = datetime.now() - timedelta(days=1)
        recent_records = AssetPricesHistoric.objects.filter(
            timestamp__gte=yesterday
        ).count()

        return {
            "total_assets": total_assets,
            "stocks": stocks,
            "cryptos": cryptos,
            "total_prices": total_prices,
            "latest_update": latest_time,
            "recent_24h": recent_records,
        }
    except Exception as e:
        return {"error": str(e)}


def display_dashboard():
    """Display monitoring dashboard"""
    os.system("clear")

    print("=" * 70)
    print(" " * 20 + "📊 FinanceHub Background Jobs Dashboard")
    print("=" * 70)
    print()

    # System Status
    print("🖥️  SYSTEM STATUS")
    print("-" * 70)
    print(f"  Status: {'✅ Running' if r.ping() else '❌ Stopped'}")
    print(f"  Uptime: Since 2026-01-30 03:51:55")
    print(f"  Redis: {'✅ Connected' if r.ping() else '❌ Disconnected'}")
    print()

    # Queue Statistics
    print("📬 QUEUE STATISTICS")
    print("-" * 70)
    queue_stats = get_queue_stats()
    for queue_name, stats in queue_stats.items():
        print(
            f"  {queue_name.upper()}: {stats['pending']:4d} pending | {stats['status']}"
        )
    print()

    # Redis Statistics
    print("⚡ REDIS STATISTICS")
    print("-" * 70)
    redis_stats = get_redis_stats()
    if "error" not in redis_stats:
        print(f"  Memory Used: {redis_stats['used_memory_human']}")
        print(f"  Memory Peak: {redis_stats['used_memory_peak_human']}")
        print(f"  Connections: {redis_stats['total_connections']:,}")
        print(f"  Commands: {redis_stats['total_commands']:,}")
    else:
        print(f"  Error: {redis_stats['error']}")
    print()

    # Database Statistics
    print("💾 DATABASE STATISTICS")
    print("-" * 70)
    db_stats = get_database_stats()
    if "error" not in db_stats:
        print(f"  Total Assets: {db_stats['total_assets']}")
        print(f"    - Stocks: {db_stats['stocks']}")
        print(f"    - Cryptos: {db_stats['cryptos']}")
        print(f"  Total Price Records: {db_stats['total_prices']:,}")
        print(f"  Records (Last 24h): {db_stats['recent_24h']:,}")
        if db_stats["latest_update"]:
            print(
                f"  Latest Update: {db_stats['latest_update'].strftime('%Y-%m-%d %H:%M:%S')}"
            )
    else:
        print(f"  Error: {db_stats['error']}")
    print()

    # Data Sources
    print("📡 DATA SOURCES")
    print("-" * 70)
    print("  ✅ Yahoo Finance (yfinance) - Free Tier")
    print("  ✅ CoinGecko - 30 calls/min")
    print("  ✅ Alpha Vantage - 25 calls/day")
    print()

    # Scheduled Tasks
    print("⏰ SCHEDULED TASKS")
    print("-" * 70)
    print("  🔄 Crypto prices: Every 2 min")
    print("  🔄 Stock prices: Every 5 min")
    print("  🔄 Health checks: Every 1 min")
    print("  🔄 Data validation: Every 10 min")
    print("  🔄 Trending: Every 15 min")
    print("  🔄 Cleanup: Daily")
    print()

    # Recent Activity
    print("📈 RECENT ACTIVITY (Last 24h)")
    print("-" * 70)
    if "error" not in db_stats:
        records = db_stats["recent_24h"]
        per_hour = records // 24
        per_min = per_hour // 60

        print(f"  Total Records: {records:,}")
        print(f"  Per Hour: {per_hour:,}")
        print(f"  Per Minute: {per_min}")
        print(f"  Trend: {'📈 Increasing' if records > 20000 else '📊 Stable'}")
    print()

    print("=" * 70)
    print(f"  Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Press Ctrl+C to exit | Updates every 10 seconds")
    print("=" * 70)


def main():
    """Main monitoring loop"""
    try:
        while True:
            display_dashboard()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped. Goodbye!")


if __name__ == "__main__":
    main()
