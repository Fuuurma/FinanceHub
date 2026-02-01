"""
Polygon.io Test Management Command
Test Polygon.io API integration for stocks, options, and technical indicators
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand

from data.data_providers.polygon_io.scraper import PolygonIOScraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test Polygon.io API integration for stocks, options, and technical indicators"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            default="AAPL",
            help="Stock symbol to test (default: AAPL)",
        )
        parser.add_argument(
            "--trades",
            action="store_true",
            help="Test trades and quotes endpoints",
        )
        parser.add_argument(
            "--snapshot",
            action="store_true",
            help="Test snapshot endpoint",
        )
        parser.add_argument(
            "--options",
            action="store_true",
            help="Test options endpoints",
        )
        parser.add_argument(
            "--underlying",
            type=str,
            help="Underlying symbol for options (e.g., AAPL)",
        )
        parser.add_argument(
            "--chain",
            action="store_true",
            help="Test options chain endpoint",
        )
        parser.add_argument(
            "--expiration",
            type=str,
            help="Expiration date filter for options (YYYY-MM-DD)",
        )
        parser.add_argument(
            "--sma",
            action="store_true",
            help="Test SMA indicator endpoint",
        )
        parser.add_argument(
            "--ema",
            action="store_true",
            help="Test EMA indicator endpoint",
        )
        parser.add_argument(
            "--rsi",
            action="store_true",
            help="Test RSI indicator endpoint",
        )
        parser.add_argument(
            "--macd",
            action="store_true",
            help="Test MACD indicator endpoint",
        )
        parser.add_argument(
            "--bbands",
            action="store_true",
            help="Test Bollinger Bands indicator endpoint",
        )
        parser.add_argument(
            "--gainers",
            action="store_true",
            help="Test gainers endpoint",
        )
        parser.add_argument(
            "--losers",
            action="store_true",
            help="Test losers endpoint",
        )
        parser.add_argument(
            "--window",
            type=int,
            default=50,
            help="Window size for indicators (default: 50)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Test all endpoints",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]

        if options["all"]:
            options["trades"] = True
            options["snapshot"] = True
            options["options"] = True
            options["chain"] = True
            options["sma"] = True
            options["ema"] = True
            options["rsi"] = True
            options["macd"] = True
            options["bbands"] = True
            options["gainers"] = True
            options["losers"] = True

        self.stdout.write(
            self.style.SUCCESS(f"Testing Polygon.io API for: {symbol}")
        )

        if options["trades"]:
            self._test_trades_and_quotes(symbol)

        if options["snapshot"]:
            self._test_snapshot(symbol)

        if options["options"] or options["chain"]:
            self._test_options_chain(options.get("underlying", symbol), options.get("expiration"))

        if options["sma"]:
            self._test_sma(symbol, options["window"])

        if options["ema"]:
            self._test_ema(symbol, options["window"])

        if options["rsi"]:
            self._test_rsi(symbol, options["window"])

        if options["macd"]:
            self._test_macd(symbol)

        if options["bbands"]:
            self._test_bbands(symbol, options["window"])

        if options["gainers"]:
            self._test_gainers_losers("gainers")

        if options["losers"]:
            self._test_gainers_losers("losers")

    def _test_trades_and_quotes(self, symbol: str):
        """Test trades and quotes endpoints"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing trades and quotes endpoints...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                last_trade = await scraper.get_last_trade(symbol)
                last_quote = await scraper.get_last_quote(symbol)
                return last_trade, last_quote

        try:
            last_trade, last_quote = asyncio.run(fetch())

            if last_trade and 'results' in last_trade:
                trade = last_trade['results'][0]
                self.stdout.write(f"\n{symbol} Last Trade:")
                self.stdout.write(f"  Price: {trade.get('p', 'N/A')}")
                self.stdout.write(f"  Size: {trade.get('s', 'N/A')}")
                self.stdout.write(f"  Timestamp: {trade.get('t', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Last trade test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No trade data returned"))

            if last_quote and 'results' in last_quote:
                quote = last_quote['results'][0]
                self.stdout.write(f"\n{symbol} Last Quote:")
                self.stdout.write(f"  Bid: {quote.get('bp', 'N/A')}")
                self.stdout.write(f"  Ask: {quote.get('ap', 'N/A')}")
                self.stdout.write(f"  Bid Size: {quote.get('bs', 'N/A')}")
                self.stdout.write(f"  Ask Size: {quote.get('as', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Last quote test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No quote data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Trades/quotes test FAILED: {e}"))

    def _test_snapshot(self, symbol: str):
        """Test snapshot endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing snapshot endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_snapshot(tickers=symbol)

        try:
            snapshot = asyncio.run(fetch())

            if snapshot and 'results' in snapshot and snapshot['results']:
                data = snapshot['results'][0]
                self.stdout.write(f"\n{symbol} Snapshot:")
                self.stdout.write(f"  Open: {data.get('o', 'N/A')}")
                self.stdout.write(f"  High: {data.get('h', 'N/A')}")
                self.stdout.write(f"  Low: {data.get('l', 'N/A')}")
                self.stdout.write(f"  Close: {data.get('c', 'N/A')}")
                self.stdout.write(f"  Volume: {data.get('v', 'N/A')}")
                self.stdout.write(self.style.SUCCESS("  Snapshot test PASSED"))
            else:
                self.stdout.write(self.style.WARNING("  No snapshot data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Snapshot test FAILED: {e}"))

    def _test_options_chain(self, underlying_symbol: str, expiration: Optional[str] = None):
        """Test options chain endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Testing options chain for {underlying_symbol}...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                if expiration:
                    return await scraper.get_options_chain(
                        underlying_symbol=underlying_symbol,
                        expiration=expiration,
                        limit=50
                    )
                else:
                    return await scraper.get_option_contracts(
                        underlying_symbol=underlying_symbol,
                        limit=50
                    )

        try:
            chain = asyncio.run(fetch())

            if chain and 'results' in chain and chain['results']:
                contracts = chain['results']
                self.stdout.write(f"\n{underlying_symbol} Options ({len(contracts)} contracts):")
                
                # Show first few contracts
                for contract in contracts[:5]:
                    self.stdout.write(f"  {contract.get('ticker', 'N/A')}")
                    self.stdout.write(f"    Strike: {contract.get('strike_price', 'N/A')}")
                    self.stdout.write(f"    Expiry: {contract.get('expiration_date', 'N/A')}")
                    self.stdout.write(f"    Type: {contract.get('type', 'N/A')}")
                
                if len(contracts) > 5:
                    self.stdout.write(f"  ... and {len(contracts) - 5} more")
                
                self.stdout.write(self.style.SUCCESS(f"  Options chain test PASSED ({len(contracts)} contracts)"))
            else:
                self.stdout.write(self.style.WARNING("  No options data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Options chain test FAILED: {e}"))

    def _test_sma(self, symbol: str, window: int):
        """Test SMA indicator endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Testing SMA ({window}) endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_sma(symbol, window=window, limit=20)

        try:
            sma = asyncio.run(fetch())

            if sma and 'results' in sma:
                values = sma['results'].get('values', [])
                self.stdout.write(f"\n{symbol} SMA ({window}):")
                
                for value in values[:5]:
                    timestamp = value.get('timestamp', '')
                    self.stdout.write(f"  {timestamp[:10] if timestamp else 'N/A'}: {value.get('value', 'N/A')}")
                
                if len(values) > 5:
                    self.stdout.write(f"  ... and {len(values) - 5} more")
                
                self.stdout.write(self.style.SUCCESS(f"  SMA test PASSED ({len(values)} values)"))
            else:
                self.stdout.write(self.style.WARNING("  No SMA data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  SMA test FAILED: {e}"))

    def _test_ema(self, symbol: str, window: int):
        """Test EMA indicator endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Testing EMA ({window}) endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_ema(symbol, window=window, limit=20)

        try:
            ema = asyncio.run(fetch())

            if ema and 'results' in ema:
                values = ema['results'].get('values', [])
                self.stdout.write(f"\n{symbol} EMA ({window}):")
                
                for value in values[:5]:
                    timestamp = value.get('timestamp', '')
                    self.stdout.write(f"  {timestamp[:10] if timestamp else 'N/A'}: {value.get('value', 'N/A')}")
                
                if len(values) > 5:
                    self.stdout.write(f"  ... and {len(values) - 5} more")
                
                self.stdout.write(self.style.SUCCESS(f"  EMA test PASSED ({len(values)} values)"))
            else:
                self.stdout.write(self.style.WARNING("  No EMA data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  EMA test FAILED: {e}"))

    def _test_rsi(self, symbol: str, window: int):
        """Test RSI indicator endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Testing RSI ({window}) endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_rsi(symbol, window=window, limit=20)

        try:
            rsi = asyncio.run(fetch())

            if rsi and 'results' in rsi:
                values = rsi['results'].get('values', [])
                self.stdout.write(f"\n{symbol} RSI ({window}):")
                
                for value in values[:5]:
                    timestamp = value.get('timestamp', '')
                    self.stdout.write(f"  {timestamp[:10] if timestamp else 'N/A'}: {value.get('value', 'N/A')}")
                
                if len(values) > 5:
                    self.stdout.write(f"  ... and {len(values) - 5} more")
                
                self.stdout.write(self.style.SUCCESS(f"  RSI test PASSED ({len(values)} values)"))
            else:
                self.stdout.write(self.style.WARNING("  No RSI data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  RSI test FAILED: {e}"))

    def _test_macd(self, symbol: str):
        """Test MACD indicator endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Testing MACD endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_macd(symbol, limit=20)

        try:
            macd = asyncio.run(fetch())

            if macd and 'results' in macd:
                values = macd['results'].get('values', [])
                self.stdout.write(f"\n{symbol} MACD:")
                
                for value in values[:5]:
                    timestamp = value.get('timestamp', '')
                    macd_val = value.get('value', {})
                    self.stdout.write(f"  {timestamp[:10] if timestamp else 'N/A']}: MACD={macd_val.get('macd', 'N/A')}, Signal={macd_val.get('signal', 'N/A')}, Hist={macd_val.get('histogram', 'N/A')}")
                
                if len(values) > 5:
                    self.stdout.write(f"  ... and {len(values) - 5} more")
                
                self.stdout.write(self.style.SUCCESS(f"  MACD test PASSED ({len(values)} values)"))
            else:
                self.stdout.write(self.style.WARNING("  No MACD data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  MACD test FAILED: {e}"))

    def _test_bbands(self, symbol: str, window: int):
        """Test Bollinger Bands indicator endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Testing Bollinger Bands ({window}) endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_bollinger_bands(symbol, window=window, limit=20)

        try:
            bbands = asyncio.run(fetch())

            if bbands and 'results' in bbands:
                values = bbands['results'].get('values', [])
                self.stdout.write(f"\n{symbol} Bollinger Bands ({window}):")
                
                for value in values[:5]:
                    timestamp = value.get('timestamp', '')
                    bb_val = value.get('value', {})
                    self.stdout.write(f"  {timestamp[:10] if timestamp else 'N/A'}: Upper={bb_val.get('upper', 'N/A')}, Middle={bb_val.get('middle', 'N/A')}, Lower={bb_val.get('lower', 'N/A')}")
                
                if len(values) > 5:
                    self.stdout.write(f"  ... and {len(values) - 5} more")
                
                self.stdout.write(self.style.SUCCESS(f"  Bollinger Bands test PASSED ({len(values)} values)"))
            else:
                self.stdout.write(self.style.WARNING("  No Bollinger Bands data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  Bollinger Bands test FAILED: {e}"))

    def _test_gainers_losers(self, direction: str):
        """Test gainers/losers endpoint"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Testing {direction} endpoint...")
        self.stdout.write("=" * 50)

        async def fetch():
            async with PolygonIOScraper() as scraper:
                return await scraper.get_gainers_losers(direction=direction)

        try:
            data = asyncio.run(fetch())

            if data and 'results' in data:
                tickers = data['results']
                self.stdout.write(f"\nTop {direction.capitalize()} ({len(tickers)} tickers):")
                
                for ticker in tickers[:10]:
                    self.stdout.write(f"  {ticker.get('ticker', 'N/A')}: {ticker.get('percent_change', 'N/A')}%")
                
                if len(tickers) > 10:
                    self.stdout.write(f"  ... and {len(tickers) - 10} more")
                
                self.stdout.write(self.style.SUCCESS(f"  {direction.capitalize()} test PASSED ({len(tickers)} tickers)"))
            else:
                self.stdout.write(self.style.WARNING(f"  No {direction} data returned"))

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"  {direction.capitalize()} test FAILED: {e}"))
