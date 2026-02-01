"""
CoinGecko Test Management Command
Test CoinGecko data fetching and integration
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError

from assets.models.asset import Asset
from investments.models.dex_data import DEXTradingPair
from investments.models.trending import TrendingAsset
from utils.services.cache_manager import get_cache_manager
from utils.services.coingecko_websocket import (
    CoinGeckoRESTClient,
    CoinGeckoWebSocketClient,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test CoinGecko API integration and data fetching"

    def add_arguments(self, parser):
        parser.add_argument(
            "--coins",
            type=str,
            default="bitcoin,ethereum,solana",
            help="Comma-separated list of CoinGecko coin IDs to test",
        )
        parser.add_argument(
            "--fetch-prices",
            action="store_true",
            help="Fetch and display current prices",
        )
        parser.add_argument(
            "--fetch-trending",
            action="store_true",
            help="Fetch and display trending cryptocurrencies",
        )
        parser.add_argument(
            "--fetch-market-chart",
            action="store_true",
            help="Fetch market chart data for coins",
        )
        parser.add_argument(
            "--test-cache",
            action="store_true",
            help="Test cache operations",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Run all tests",
        )

    def handle(self, *args, **options):
        coins = [c.strip() for c in options["coins"].split(",")]

        if options["all"]:
            options["fetch_prices"] = True
            options["fetch_trending"] = True
            options["fetch_market_chart"] = True
            options["test_cache"] = True

        self.stdout.write(
            self.style.SUCCESS(f"Testing CoinGecko integration for: {coins}")
        )

        if options["fetch_prices"]:
            self._test_price_fetch(coins)

        if options["fetch_trending"]:
            self._test_trending_fetch()

        if options["fetch_market_chart"]:
            self._test_market_chart(coins)

        if options["test_cache"]:
            self._test_cache_operations(coins)

    def _test_price_fetch(self, coins: List[str]):
        """Test fetching current prices"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing price fetch...")
        self.stdout.write("=" * 50)

        try:
            client = CoinGeckoRESTClient()
            prices = asyncio.run(
                client.get_price(
                    coin_ids=coins[:10],
                    currency="usd",
                    include_24hr_change=True,
                    include_market_cap=True,
                )
            )

            for coin_id, data in prices.items():
                price = data.get("usd", 0)
                change = data.get("usd_24h_change", 0)
                mcap = data.get("usd_market_cap", 0)

                self.stdout.write(f"\n{coin_id.upper()}:")
                self.stdout.write(f"  Price: ${price:,.2f}")
                self.stdout.write(f"  24h Change: {change:+.2f}%")
                self.stdout.write(f"  Market Cap: ${mcap:,.0f}")

            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully fetched prices for {len(prices)} coins"
                )
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            self.stdout.write(self.style.ERROR(f"Error fetching prices: {e}"))

    def _test_trending_fetch(self):
        """Test fetching trending cryptocurrencies"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing trending fetch...")
        self.stdout.write("=" * 50)

        try:
            from investments.tasks.coingecko_tasks import fetch_trending_cryptos

            result = fetch_trending_cryptos.delay()
            self.stdout.write(f"Task submitted: {result.id}")

            self.stdout.write(
                self.style.SUCCESS(
                    "Trending fetch task started (check Celery worker for results)"
                )
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            self.stdout.write(self.style.ERROR(f"Error starting trending fetch: {e}"))

    def _test_market_chart(self, coins: List[str]):
        """Test fetching market chart data"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing market chart fetch...")
        self.stdout.write("=" * 50)

        try:
            client = CoinGeckoRESTClient()

            for coin_id in coins[:3]:
                chart_data = asyncio.run(
                    client.get_coin_market_chart(
                        coin_id=coin_id,
                        currency="usd",
                        days=7,
                    )
                )

                prices = chart_data.get("prices", [])[:5]
                self.stdout.write(f"\n{coin_id.upper()} - Last 5 prices:")
                for price_data in prices:
                    timestamp, price = price_data
                    from datetime import datetime

                    dt = datetime.fromtimestamp(timestamp / 1000)
                    self.stdout.write(f"  {dt}: ${price:,.2f}")

            self.stdout.write(
                self.style.SUCCESS(f"\nSuccessfully fetched market charts")
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            self.stdout.write(self.style.ERROR(f"Error fetching market charts: {e}"))

    def _test_cache_operations(self, coins: List[str]):
        """Test cache operations"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing cache operations...")
        self.stdout.write("=" * 50)

        try:
            client = CoinGeckoRESTClient()
            prices = asyncio.run(
                client.get_price(
                    coin_ids=coins[:3],
                    currency="usd",
                )
            )

            for coin_id, data in prices.items():
                price = Decimal(str(data.get("usd", 0)))
                symbol = coin_id.upper()

                cache_manager = get_cache_manager()

                cache_manager.set_cached_price(
                    symbol=symbol,
                    price=price,
                    provider="coingecko",
                )

                cached = cache_manager.get_cached_price(symbol, provider="coingecko")

                if cached:
                    self.stdout.write(f"\n{symbol}:")
                    self.stdout.write(f"  Cached: ${cached:,.2f}")
                    self.stdout.write(self.style.SUCCESS("  Cache test PASSED"))
                else:
                    self.stdout.write(
                        self.style.ERROR(f"  Cache test FAILED - value not found")
                    )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            self.stdout.write(self.style.ERROR(f"Error testing cache: {e}"))
