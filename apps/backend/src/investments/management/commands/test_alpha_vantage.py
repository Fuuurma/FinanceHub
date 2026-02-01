"""
Alpha Vantage Test Management Command
Test Alpha Vantage API integration and fundamental data fetching
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List

from django.core.management.base import BaseCommand

from assets.models.asset import Asset
from data.data_providers.alphaVantage.scraper import AlphaVantageScraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test Alpha Vantage API integration and fundamental data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="IBM",
            help="Stock symbol to test (default: IBM)",
        )
        parser.add_argument(
            "--quote",
            action="store_true",
            help="Test quote endpoint",
        )
        parser.add_argument(
            "--overview",
            action="store_true",
            help="Test company overview endpoint",
        )
        parser.add_argument(
            "--income",
            action="store_true",
            help="Test income statement endpoint",
        )
        parser.add_argument(
            "--balance",
            action="store_true",
            help="Test balance sheet endpoint",
        )
        parser.add_argument(
            "--cashflow",
            action="store_true",
            help="Test cash flow endpoint",
        )
        parser.add_argument(
            "--earnings",
            action="store_true",
            help="Test earnings endpoint",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Test all endpoints",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]

        if options["all"]:
            options["quote"] = True
            options["overview"] = True
            options["income"] = True
            options["balance"] = True
            options["cashflow"] = True
            options["earnings"] = True

        self.stdout.write(
            self.style.SUCCESS(f"Testing Alpha Vantage API for: {symbol}")
        )

        if options["quote"]:
            self._test_quote(symbol)

        if options["overview"]:
            self._test_overview(symbol)

        if options["income"]:
            self._test_income_statement(symbol)

        if options["balance"]:
            self._test_balance_sheet(symbol)

        if options["cashflow"]:
            self._test_cash_flow(symbol)

        if options["earnings"]:
            self._test_earnings(symbol)

    def _test_quote(self, symbol: str):
        """Test GLOBAL_QUOTE endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing GLOBAL_QUOTE endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with AlphaVantageScraper() as scraper:
                return await scraper.get_quote(symbol)

        try:
            quote = asyncio.run(fetch())

            if quote and "Global Quote" in quote:
                data = quote["Global Quote"]
                self.stdout.write(f"\n{symbol} Quote:")
                self.stdout.write(f"  Price: {data.get('05. price', 'N/A')}")
                self.stdout.write(f"  Volume: {data.get('06. volume', 'N/A')}")
                self.stdout.write(
                    f"  Previous Close: {data.get('09. previous close', 'N/A')}"
                )
                self.stdout.write(self.style.SUCCESS("  Quote test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No quote data returned"))

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(self.style.ERROR(f"  Quote test FAILED: {e}"))

    def _test_overview(self, symbol: str):
        """Test OVERVIEW endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing OVERVIEW endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with AlphaVantageScraper() as scraper:
                return await scraper.get_company_overview(symbol)

        try:
            overview = asyncio.run(fetch())

            if overview and "Symbol" in overview:
                self.stdout.write(f"\n{symbol} Overview:")
                self.stdout.write(f"  Name: {overview.get('Name', 'N/A')}")
                self.stdout.write(f"  Sector: {overview.get('Sector', 'N/A')}")
                self.stdout.write(f"  Industry: {overview.get('Industry', 'N/A')}")
                self.stdout.write(
                    f"  Market Cap: {overview.get('MarketCapitalization', 'N/A')}"
                )
                self.stdout.write(f"  PE Ratio: {overview.get('PERatio', 'N/A')}")
                self.stdout.write(f"  EPS: {overview.get('EPS', 'N/A')}")
                self.stdout.write(
                    f"  Dividend Yield: {overview.get('DividendYield', 'N/A')}"
                )
                self.stdout.write(self.style.SUCCESS("  Overview test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No overview data returned"))

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(self.style.ERROR(f"  Overview test FAILED: {e}"))

    def _test_income_statement(self, symbol: str):
        """Test INCOME_STATEMENT endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing INCOME_STATEMENT endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with AlphaVantageScraper() as scraper:
                return await scraper.get_income_statement(symbol)

        try:
            data = asyncio.run(fetch())

            if data and "incomeStatement" in data:
                reports = data["incomeStatement"].get("quarterlyReports", [])
                if reports:
                    latest = reports[0]
                    self.stdout.write(f"\n{symbol} Latest Quarterly Income Statement:")
                    self.stdout.write(
                        f"  Period: {latest.get('fiscalDateEnding', 'N/A')}"
                    )
                    self.stdout.write(f"  Revenue: {latest.get('totalRevenue', 'N/A')}")
                    self.stdout.write(
                        f"  Gross Profit: {latest.get('grossProfit', 'N/A')}"
                    )
                    self.stdout.write(f"  Net Income: {latest.get('netIncome', 'N/A')}")
                    self.stdout.write(f"  EPS: {latest.get('basicEPS', 'N/A')}")
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Income statement test PASSED ({len(reports)} reports)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("  No quarterly reports returned")
                    )
            else:
                self.stdout.write(
                    self.style.WARNING("  No income statement data returned")
                )

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(self.style.ERROR(f"  Income statement test FAILED: {e}"))

    def _test_balance_sheet(self, symbol: str):
        """Test BALANCE_SHEET endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing BALANCE_SHEET endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with AlphaVantageScraper() as scraper:
                return await scraper.get_balance_sheet(symbol)

        try:
            data = asyncio.run(fetch())

            if data and "balanceSheet" in data:
                reports = data["balanceSheet"].get("quarterlyReports", [])
                if reports:
                    latest = reports[0]
                    self.stdout.write(f"\n{symbol} Latest Quarterly Balance Sheet:")
                    self.stdout.write(
                        f"  Period: {latest.get('fiscalDateEnding', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Total Assets: {latest.get('totalAssets', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Total Liabilities: {latest.get('totalLiabilities', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Total Equity: {latest.get('totalStockholderEquity', 'N/A')}"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Balance sheet test PASSED ({len(reports)} reports)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("  No quarterly reports returned")
                    )
            else:
                self.stdout.write(
                    self.style.WARNING("  No balance sheet data returned")
                )

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(self.style.ERROR(f"  Balance sheet test FAILED: {e}"))

    def _test_cash_flow(self, symbol: str):
        """Test CASH_FLOW endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing CASH_FLOW endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with AlphaVantageScraper() as scraper:
                return await scraper.get_cash_flow(symbol)

        try:
            data = asyncio.run(fetch())

            if data and "cashFlow" in data:
                reports = data["cashFlow"].get("quarterlyReports", [])
                if reports:
                    latest = reports[0]
                    self.stdout.write(f"\n{symbol} Latest Quarterly Cash Flow:")
                    self.stdout.write(
                        f"  Period: {latest.get('fiscalDateEnding', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Operating Cash Flow: {latest.get('operatingCashflow', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Investing Cash Flow: {latest.get('investingCashflow', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Financing Cash Flow: {latest.get('financingCashflow', 'N/A')}"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Cash flow test PASSED ({len(reports)} reports)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("  No quarterly reports returned")
                    )
            else:
                self.stdout.write(self.style.WARNING("  No cash flow data returned"))

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(self.style.ERROR(f"  Cash flow test FAILED: {e}"))

    def _test_earnings(self, symbol: str):
        """Test EARNINGS endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing EARNINGS endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with AlphaVantageScraper() as scraper:
                return await scraper.get_earnings(symbol)

        try:
            data = asyncio.run(fetch())

            if data and "quarterlyEarnings" in data:
                reports = data["quarterlyEarnings"]
                if reports:
                    latest = reports[0]
                    self.stdout.write(f"\n{symbol} Latest Quarterly Earnings:")
                    self.stdout.write(
                        f"  Period: {latest.get('fiscalDateEnding', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Reported EPS: {latest.get('reportedEPS', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Estimated EPS: {latest.get('estimatedEPS', 'N/A')}"
                    )
                    self.stdout.write(
                        f"  Surprise: {latest.get('surprisePercentage', 'N/A')}"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Earnings test PASSED ({len(reports)} reports)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("  No quarterly reports returned")
                    )
            else:
                self.stdout.write(self.style.WARNING("  No earnings data returned"))

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            self.stdout.write(self.style.ERROR(f"  Earnings test FAILED: {e}"))
