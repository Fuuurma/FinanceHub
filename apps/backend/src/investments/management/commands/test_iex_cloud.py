"""
IEX Cloud Test Management Command
Test IEX Cloud API integration for fundamentals, stats, and market data
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand

from data.data_providers.iex_cloud.scraper import IEXCloudScraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test IEX Cloud API integration for fundamentals and market data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="AAPL",
            help="Stock symbol to test (default: AAPL)",
        )
        parser.add_argument(
            "--company",
            action="store_true",
            help="Test company endpoint",
        )
        parser.add_argument(
            "--quote",
            action="store_true",
            help="Test quote endpoint",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Test key stats endpoint",
        )
        parser.add_argument(
            "--financials",
            action="store_true",
            help="Test financials endpoint",
        )
        parser.add_argument(
            "--earnings",
            action="store_true",
            help="Test earnings endpoint",
        )
        parser.add_argument(
            "--estimates",
            action="store_true",
            help="Test analyst estimates endpoint",
        )
        parser.add_argument(
            "--peers",
            action="store_true",
            help="Test peers endpoint",
        )
        parser.add_argument(
            "--advanced",
            action="store_true",
            help="Test advanced stats endpoint",
        )
        parser.add_argument(
            "--insider",
            action="store_true",
            help="Test insider transactions endpoint",
        )
        parser.add_argument(
            "--movers",
            action="store_true",
            help="Test market movers endpoint",
        )
        parser.add_argument(
            "--sector",
            action="store_true",
            help="Test sector performance endpoint",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Test all endpoints",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]

        if options["all"]:
            options["company"] = True
            options["quote"] = True
            options["stats"] = True
            options["financials"] = True
            options["earnings"] = True
            options["estimates"] = True
            options["peers"] = True
            options["advanced"] = True
            options["insider"] = True
            options["movers"] = True
            options["sector"] = True

        self.stdout.write(self.style.SUCCESS(f"Testing IEX Cloud API for: {symbol}"))

        if options["company"]:
            self._test_company(symbol)

        if options["quote"]:
            self._test_quote(symbol)

        if options["stats"]:
            self._test_key_stats(symbol)

        if options["financials"]:
            self._test_financials(symbol)

        if options["earnings"]:
            self._test_earnings(symbol)

        if options["estimates"]:
            self._test_estimates(symbol)

        if options["peers"]:
            self._test_peers(symbol)

        if options["advanced"]:
            self._test_advanced_stats(symbol)

        if options["insider"]:
            self._test_insider_transactions(symbol)

        if options["movers"]:
            self._test_market_movers()

        if options["sector"]:
            self._test_sector_performance()

    def _test_company(self, symbol: str):
        """Test company endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing company endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_company(symbol)

        try:
            company = asyncio.run(fetch())

            if company and "companyName" in company:
                self.stdout.write(f"\n{symbol} Company:")
                self.stdout.write(f"  Name: {company.get('companyName', 'N/A')}")
                self.stdout.write(f"  Industry: {company.get('industry', 'N/A')}")
                self.stdout.write(f"  Sector: {company.get('sector', 'N/A')}")
                self.stdout.write(f"  CEO: {company.get('CEO', 'N/A')}")
                self.stdout.write(f"  Employees: {company.get('employees', 'N/A')}")
                self.stdout.write(f"  Website: {company.get('website', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Company test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No company data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Company test FAILED: {e}"))

    def _test_quote(self, symbol: str):
        """Test quote endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing quote endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_quote(symbol)

        try:
            quote = asyncio.run(fetch())

            if quote and "symbol" in quote:
                self.stdout.write(f"\n{symbol} Quote:")
                self.stdout.write(f"  Price: {quote.get('latestPrice', 'N/A')}")
                self.stdout.write(f"  Change: {quote.get('change', 'N/A')}")
                self.stdout.write(f"  Change %: {quote.get('changePercent', 'N/A')}")
                self.stdout.write(f"  Volume: {quote.get('volume', 'N/A')}")
                self.stdout.write(f"  Market Cap: {quote.get('marketCap', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Quote test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No quote data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Quote test FAILED: {e}"))

    def _test_key_stats(self, symbol: str):
        """Test key stats endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing key stats endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_key_stats(symbol)

        try:
            stats = asyncio.run(fetch())

            if stats and "marketCap" in stats:
                self.stdout.write(f"\n{symbol} Key Stats:")
                self.stdout.write(f"  Market Cap: {stats.get('marketCap', 'N/A')}")
                self.stdout.write(f"  PE Ratio: {stats.get('peRatio', 'N/A')}")
                self.stdout.write(f"  EPS: {stats.get('eps', 'N/A')}")
                self.stdout.write(f"  Dividend Yield: {stats.get('divYield', 'N/A')}")
                self.stdout.write(f"  Beta: {stats.get('beta', 'N/A')}")
                self.stdout.write(f"  52W High: {stats.get('week52High', 'N/A')}")
                self.stdout.write(f"  52W Low: {stats.get('week52Low', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Key stats test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No key stats data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Key stats test FAILED: {e}"))

    def _test_financials(self, symbol: str):
        """Test financials endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing financials endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_financials(symbol, period="annual", last=1)

        try:
            financials = asyncio.run(fetch())

            if financials:
                self.stdout.write(f"\n{symbol} Financials:")
                if "incomeStatement" in financials:
                    income = financials["incomeStatement"]
                    reports = income.get("reports", [])
                    if reports:
                        latest = reports[0]
                        self.stdout.write(
                            f"  Period: {latest.get('fiscalDate', 'N/A')}"
                        )
                        self.stdout.write(
                            f"  Revenue: {latest.get('totalRevenue', 'N/A')}"
                        )
                        self.stdout.write(
                            f"  Net Income: {latest.get('netIncome', 'N/A')}"
                        )
                self.stdout.write(self.style.SUCCESS("  Financials test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No financials data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Financials test FAILED: {e}"))

    def _test_earnings(self, symbol: str):
        """Test earnings endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing earnings endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_earnings(symbol, period="annual", last=4)

        try:
            earnings = asyncio.run(fetch())

            if earnings and "earnings" in earnings:
                reports = earnings["earnings"]
                if reports:
                    latest = reports[0]
                    self.stdout.write(f"\n{symbol} Latest Earnings:")
                    self.stdout.write(f"  Period: {latest.get('fiscalDate', 'N/A')}")
                    self.stdout.write(f"  Actual EPS: {latest.get('actualEPS', 'N/A')}")
                    self.stdout.write(
                        f"  Estimate EPS: {latest.get('estimatedEPS', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Surprise: {latest.get('EPSSurprisePercent', 'N/A')}%"
                    )
                self.stdout.write(self.style.SUCCESS("  Earnings test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No earnings data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Earnings test FAILED: {e}"))

    def _test_estimates(self, symbol: str):
        """Test analyst estimates endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing estimates endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_estimates(symbol)

        try:
            estimates = asyncio.run(fetch())

            if estimates and "estimates" in estimates:
                est_list = estimates["estimates"]
                self.stdout.write(
                    f"\n{symbol} Analyst Estimates ({len(est_list)} periods):"
                )
                for est in est_list[:3]:
                    self.stdout.write(f"  Period: {est.get('fiscalDate', 'N/A')}")
                    self.stdout.write(f"  Est EPS: {est.get('estimatedEPS', 'N/A')}")
                    self.stdout.write(
                        f"  Est Revenue: {est.get('estimatedRevenue', 'N/A')}"
                    )
                self.stdout.write(self.style.SUCCESS("  Estimates test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No estimates data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Estimates test FAILED: {e}"))

    def _test_peers(self, symbol: str):
        """Test peers endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing peers endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_peers(symbol)

        try:
            peers = asyncio.run(fetch())

            if peers and isinstance(peers, list):
                self.stdout.write(f"\n{symbol} Peers ({len(peers)} companies):")
                for peer in peers[:10]:
                    self.stdout.write(f"  - {peer}")
                if len(peers) > 10:
                    self.stdout.write(f"  ... and {len(peers) - 10} more")
                self.stdout.write(self.style.SUCCESS("  Peers test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No peers data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Peers test FAILED: {e}"))

    def _test_advanced_stats(self, symbol: str):
        """Test advanced stats endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing advanced stats endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_advanced_stats(symbol)

        try:
            stats = asyncio.run(fetch())

            if stats and "marketCap" in stats:
                self.stdout.write(f"\n{symbol} Advanced Stats:")
                self.stdout.write(f"  Market Cap: {stats.get('marketCap', 'N/A')}")
                self.stdout.write(f"  EV: {stats.get('enterpriseValue', 'N/A')}")
                self.stdout.write(f"  PE Ratio: {stats.get('peRatio', 'N/A')}")
                self.stdout.write(f"  Forward PE: {stats.get('forwardPE', 'N/A')}")
                self.stdout.write(f"  PEG Ratio: {stats.get('pegRatio', 'N/A')}")
                self.stdout.write(f"  Price/Book: {stats.get('priceToBook', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Advanced stats test PASSED"))
            else:
                self.stdout.write(
                    self.style.WARNING("  No advanced stats data returned")
                )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Advanced stats test FAILED: {e}"))

    def _test_insider_transactions(self, symbol: str):
        """Test insider transactions endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing insider transactions endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_insider_transactions(symbol)

        try:
            transactions = asyncio.run(fetch())

            if transactions and "transactions" in transactions:
                tx_list = transactions["transactions"]
                self.stdout.write(f"\n{symbol} Insider Transactions ({len(tx_list)}):")
                for tx in tx_list[:5]:
                    self.stdout.write(
                        f"  {tx.get('action', 'N/A')}: {tx.get('shares', 'N/A')} shares by {tx.get('name', 'N/A')}"
                    )
                self.stdout.write(
                    self.style.SUCCESS("  Insider transactions test PASSED")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("  No insider transactions data returned")
                )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(
                self.style.ERROR(f"  Insider transactions test FAILED: {e}")
            )

    def _test_market_movers(self):
        """Test market movers endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing market movers endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_market_list("mostactive")

        try:
            movers = asyncio.run(fetch())

            if movers and isinstance(movers, list):
                self.stdout.write(f"\nMost Active ({len(movers)} tickers):")
                for item in movers[:10]:
                    symbol = item.get("symbol", "N/A")
                    price = item.get("latestPrice", "N/A")
                    change = item.get("changePercent", 0)
                    self.stdout.write(f"  {symbol}: ${price} ({change}%)")
                self.stdout.write(self.style.SUCCESS("  Market movers test PASSED"))
            else:
                self.stdout.write(
                    self.style.WARNING("  No market movers data returned")
                )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Market movers test FAILED: {e}"))

    def _test_sector_performance(self):
        """Test sector performance endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing sector performance endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with IEXCloudScraper() as scraper:
                return await scraper.get_sector_performance()

        try:
            sectors = asyncio.run(fetch())

            if sectors and isinstance(sectors, list):
                self.stdout.write(f"\nSector Performance ({len(sectors)} sectors):")
                for sector in sectors:
                    name = sector.get("name", "N/A")
                    perf = sector.get("performance", 0)
                    self.stdout.write(f"  {name}: {perf:.2f}%")
                self.stdout.write(
                    self.style.SUCCESS("  Sector performance test PASSED")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("  No sector performance data returned")
                )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(
                self.style.ERROR(f"  Sector performance test FAILED: {e}")
            )
