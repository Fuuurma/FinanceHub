"""
CoinMarketCap Test Management Command
Test CoinMarketCap API integration for cryptocurrency data
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand

from data.data_providers.coinmarketcap.scraper import CoinMarketCapScraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test CoinMarketCap API integration for cryptocurrency data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="BTC",
            help="Cryptocurrency symbol to test (default: BTC)",
        )
        parser.add_argument(
            "--info",
            action="store_true",
            help="Test cryptocurrency info endpoint",
        )
        parser.add_argument(
            "--quote",
            action="store_true",
            help="Test quote endpoint",
        )
        parser.add_argument(
            "--listings",
            action="store_true",
            help="Test listings endpoint",
        )
        parser.add_argument(
            "--map",
            action="store_true",
            help="Test cryptocurrency map endpoint",
        )
        parser.add_argument(
            "--global",
            action="store_true",
            help="Test global metrics endpoint",
        )
        parser.add_argument(
            "--trending",
            action="store_true",
            help="Test trending endpoint",
        )
        parser.add_argument(
            "--pairs",
            action="store_true",
            help="Test market pairs endpoint",
        )
        parser.add_argument(
            "--exchanges",
            action="store_true",
            help="Test exchange listings endpoint",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Test all endpoints",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]

        if options["all"]:
            options["info"] = True
            options["quote"] = True
            options["listings"] = True
            options["map"] = True
            options["global"] = True
            options["trending"] = True
            options["exchanges"] = True

        self.stdout.write(
            self.style.SUCCESS(f"Testing CoinMarketCap API for: {symbol}")
        )

        if options["info"]:
            self._test_crypto_info(symbol)

        if options["quote"]:
            self._test_quote(symbol)

        if options["listings"]:
            self._test_listings()

        if options["map"]:
            self._test_crypto_map()

        if options["global"]:
            self._test_global_metrics()

        if options["trending"]:
            self._test_trending()

        if options["exchanges"]:
            self._test_exchange_listings()

    def _test_crypto_info(self, symbol: str):
        """Test cryptocurrency info endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing cryptocurrency info endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_cryptocurrency_info(symbol)

        try:
            info = asyncio.run(fetch())

            if info and symbol in info:
                data = info[symbol]
                self.stdout.write(f"\n{symbol} Info:")
                self.stdout.write(f"  Name: {data.get('name', 'N/A')}")
                self.stdout.write(f"  Symbol: {data.get('symbol', 'N/A')}")
                self.stdout.write(f"  Category: {data.get('category', 'N/A')}")
                self.stdout.write(
                    f"  Description: {data.get('description', 'N/A')[:100]}..."
                )
                self.stdout.write(f"  Logo: {data.get('logo', 'N/A')[:50]}...")
                self.stdout.write(f"  CMC Rank: {data.get('cmc_rank', 'N/A')}")
                self.stdout.write(
                    f"  Circulating Supply: {data.get('circulating_supply', 'N/A')}"
                )
                self.stdout.write(f"  Total Supply: {data.get('total_supply', 'N/A')}")
                self.stdout.write(f"  Max Supply: {data.get('max_supply', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Crypto info test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No crypto info data returned"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Crypto info test FAILED: {e}"))

    def _test_quote(self, symbol: str):
        """Test quote endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing quote endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_quotes_latest(symbol=symbol)

        try:
            quotes = asyncio.run(fetch())

            if quotes and len(quotes) > 0:
                quote = quotes[0]
                quote_data = quote.get("quote", {}).get("USD", {})
                self.stdout.write(f"\n{symbol} Quote:")
                self.stdout.write(f"  Price: ${quote_data.get('price', 'N/A'):,.6f}")
                self.stdout.write(
                    f"  Market Cap: ${quote_data.get('market_cap', 'N/A'):,.0f}"
                )
                self.stdout.write(
                    f"  Volume 24h: ${quote_data.get('volume_24h', 'N/A'):,.0f}"
                )
                self.stdout.write(
                    f"  Change 24h: {quote_data.get('percent_change_24h', 'N/A'):.2f}%"
                )
                self.stdout.write(
                    f"  Circulating Supply: {quote_data.get('circulating_supply', 'N/A'):,.0f}"
                )
                self.stdout.write(f"  CMC Rank: {quote.get('cmc_rank', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Quote test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No quote data returned"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Quote test FAILED: {e}"))

    def _test_listings(self):
        """Test listings endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing listings endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_listings(limit=20)

        try:
            listings = asyncio.run(fetch())

            if listings:
                self.stdout.write(f"\nTop {len(listings)} Cryptocurrencies:")
                for item in listings[:10]:
                    symbol = item.get("symbol", "N/A")
                    name = item.get("name", "N/A")
                    price = item.get("quote", {}).get("USD", {}).get("price", 0)
                    mc = item.get("quote", {}).get("USD", {}).get("market_cap", 0)
                    change = (
                        item.get("quote", {})
                        .get("USD", {})
                        .get("percent_change_24h", 0)
                    )
                    self.stdout.write(
                        f"  {symbol} ({name}): ${price:,.2f} | MC: ${mc:,.0f} | 24h: {change:.2f}%"
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Listings test PASSED ({len(listings)} cryptos)"
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("  No listings data returned"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Listings test FAILED: {e}"))

    def _test_crypto_map(self):
        """Test cryptocurrency map endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing cryptocurrency map endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_cryptocurrency_map()

        try:
            crypto_map = asyncio.run(fetch())

            if crypto_map:
                self.stdout.write(f"\nCryptocurrency Map:")
                self.stdout.write(f"  Total cryptocurrencies: {len(crypto_map)}")

                # Show first 5
                count = 0
                for item in crypto_map:
                    if isinstance(item, dict) and count < 5:
                        self.stdout.write(
                            f"  - {item.get('name', 'N/A')} ({item.get('symbol', 'N/A')}): {item.get('id', 'N/A')}"
                        )
                        count += 1

                self.stdout.write(self.style.SUCCESS(f"  Crypto map test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No crypto map data returned"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Crypto map test FAILED: {e}"))

    def _test_global_metrics(self):
        """Test global metrics endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing global metrics endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_global_metrics()

        try:
            metrics = asyncio.run(fetch())

            if metrics:
                quote = metrics.get("quote", {}).get("USD", {})
                self.stdout.write(f"\nGlobal Crypto Metrics:")
                self.stdout.write(
                    f"  Total Market Cap: ${quote.get('total_market_cap', 'N/A'):,.0f}"
                )
                self.stdout.write(
                    f"  Total Volume 24h: ${quote.get('total_volume_24h', 'N/A'):,.0f}"
                )
                self.stdout.write(
                    f"  Bitcoin Dominance: {quote.get('btc_dominance', 'N/A'):.2f}%"
                )
                self.stdout.write(
                    f"  Ethereum Dominance: {quote.get('eth_dominance', 'N/A'):.2f}%"
                )
                self.stdout.write(
                    f"  Active Cryptocurrencies: {metrics.get('active_cryptocurrencies', 'N/A')}"
                )
                self.stdout.write(
                    f"  Active Exchanges: {metrics.get('active_exchanges', 'N/A')}"
                )
                self.stdout.write(self.style.SUCCESS("  Global metrics test PASSED"))
            else:
                self.stdout.write(
                    self.style.WARNING("  No global metrics data returned")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Global metrics test FAILED: {e}"))

    def _test_trending(self):
        """Test trending endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing trending endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_trending_gainers_losers(
                    sort="percent_change_24h", sort_dir="desc", limit=20
                )

        try:
            trending = asyncio.run(fetch())

            if trending:
                self.stdout.write(f"\nTop Gainers (24h):")
                count = 0
                for item in trending:
                    if isinstance(item, dict) and count < 10:
                        symbol = item.get("symbol", "N/A")
                        name = item.get("name", "N/A")
                        change = item.get("percent_change_24h", 0)
                        price = item.get("price", 0)
                        self.stdout.write(
                            f"  {symbol} ({name}): ${price:,.6f} | +{change:.2f}%"
                        )
                        count += 1

                self.stdout.write(self.style.SUCCESS(f"  Trending test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No trending data returned"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Trending test FAILED: {e}"))

    def _test_exchange_listings(self):
        """Test exchange listings endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing exchange listings endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with CoinMarketCapScraper() as scraper:
                return await scraper.get_exchange_listings(limit=10)

        try:
            exchanges = asyncio.run(fetch())

            if exchanges:
                self.stdout.write(f"\nTop Exchanges:")
                for ex in exchanges[:10]:
                    name = ex.get("name", "N/A")
                    vol = ex.get("volume_24h", 0)
                    pairs = ex.get("num_market_pairs", 0)
                    rank = ex.get("cmc_rank", "N/A")
                    self.stdout.write(
                        f"  {name}: Rank #{rank} | Vol: ${vol:,.0f} | Pairs: {pairs}"
                    )

                self.stdout.write(
                    self.style.SUCCESS(f"  Exchange listings test PASSED")
                )
            else:
                self.stdout.write(self.style.WARNING("  No exchange data returned"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Exchange listings test FAILED: {e}"))
