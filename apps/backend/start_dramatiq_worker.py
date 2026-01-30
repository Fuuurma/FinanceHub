#!/usr/bin/env python3
"""
Dramatiq Worker for FinanceHub
Processes background tasks for data collection
"""

import os
import sys

# Setup Django
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries, Prometheus
from dramatiq import Worker

# Configure broker
broker = RedisBroker(url="redis://localhost:6379")
dramatiq.set_broker(broker)

# Add middleware
broker.add_middleware(AgeLimit(max_age=1000 * 60 * 60))  # 1 hour max age
broker.add_middleware(TimeLimit(time_limit=1000 * 60 * 30))  # 30 min max runtime
broker.add_middleware(Retries(max_retries=3))

# Import all task modules to register actors
from tasks.crypto_data_tasks import (
    fetch_crypto_batch,
    fetch_trending_cryptos,
    fetch_top_cryptos,
    periodic_crypto_update,
    periodic_health_check,
)

from tasks.data_fetcher import (
    fetch_stocks_alpha,
    fetch_cryptos_coingecko,
    fetch_cryptos_coinmarketcap,
    fetch_all_markets,
)

if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "DRAMATIQ WORKER STARTED")
    print("=" * 70)
    print()
    print("✅ Worker ready to process tasks")
    print("📬 Connected to Redis: localhost:6379")
    print()
    print("📋 Registered Actors:")
    for actor in broker.get_declared_actors():
        print(f"  • {actor}")
    print()
    print("=" * 70)

    # Run the worker
    dramatiq.run_worker()
