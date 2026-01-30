"""
Polygon.io Stock Scraper using BaseAPIFetcher for key rotation
Performance optimized with orjson and async operations
"""

import aiohttp
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

import polars as pl

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class PolygonIOScraper(BaseAPIFetcher):
    """
    Polygon.io API implementation with key rotation

    Free tier: 5 requests/minute per key
    Strategy: Rotate between multiple free accounts (6 keys = 30 requests/minute)

    Data Available:
    - End-of-day stock prices
    - 2 years of historical data
    - Options chains (delayed)
    - Dividends and stock splits
    - Reference data (tickers, company info)
    """

    def __init__(self):
        super().__init__(provider_name="polygon_io")

    def get_base_url(self) -> str:
        return "https://api.polygon.io/v2"

    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from Polygon.io response"""
        if "error" in response:
            error = response["error"]
            if any(
                keyword in error.lower()
                for keyword in ["rate limit", "too many requests", "429"]
            ):
                return error
        return None

    async def _make_request(
        self, endpoint: str, params: Optional[Dict], method: str, api_key
    ) -> Dict:
        """Make request with async HTTP client"""
        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)

        async with self.session.request(
            method, url, params=params, headers=headers
        ) as response:
            response.raise_for_status()
            content = await response.read()

            # Use orjson for fast parsing
            try:
                import orjson

                return orjson.loads(content)
            except ImportError:
                import json

                return json.loads(content)

    def _get_headers(self, api_key) -> Dict:
        """Polygon.io uses API key in query string"""
        return {"Accept": "application/json", "User-Agent": "FinanceHub/1.0"}

    async def get_aggregate_bars(
        self,
        ticker: str,
        timespan: str = "day",
        multiplier: int = 1,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        adjusted: bool = True,
    ) -> Optional[Dict]:
        """
        Get aggregate bars (OHLCV) for a ticker

        Args:
            ticker: Stock ticker (e.g., 'AAPL')
            timespan: Size of the time window (minute, hour, day, week, month, quarter, year)
            multiplier: Size of the timespan multiplier (e.g., 1 for 1 day)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            adjusted: Whether to use adjusted prices (default: True)
        """
        params = {
            "ticker": ticker,
            "timespan": timespan,
            "multiplier": multiplier,
            "adjusted": "true" if adjusted else "false",
        }

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        return await self.request(
            "aggs/ticker/{ticker}/range/{multiplier}/{timespan}", params
        )

    async def get_daily_open_close(self, ticker: str, date: str) -> Optional[Dict]:
        """
        Get daily open/close for a ticker

        Args:
            ticker: Stock ticker
            date: Date in YYYY-MM-DD format
        """
        params = {"ticker": ticker, "date": date, "adjusted": "true"}

        return await self.request("aggs/ticker/{ticker}/open-close/{date}", params)

    async def get_ticker_details(self, ticker: str) -> Optional[Dict]:
        """
        Get ticker details

        Args:
            ticker: Stock ticker
        """
        return await self.request("reference/tickers/{ticker}")

    async def get_ticker_types(self, asset_class: str = "stocks") -> Optional[List]:
        """
        Get ticker types

        Args:
            asset_class: Asset class (stocks, crypto, fx, indices)
        """
        params = {"asset_class": asset_class}
        return await self.request("reference/tickers/types", params)

    async def get_tickers(
        self,
        tickers: Optional[str] = None,
        ticker_gt: Optional[str] = None,
        limit: int = 100,
        sort: str = "ticker",
        order: str = "asc",
        active: bool = True,
        market: str = "stocks",
        type: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get list of tickers

        Args:
            tickers: Comma separated list of tickers
            ticker_gt: Ticker greater than this value
            limit: Number of results (max 50)
            sort: Sort field
            order: Sort order (asc, desc)
            active: Whether to show active tickers
            market: Market type
            type: Ticker type
        """
        params = {
            "limit": limit,
            "sort": sort,
            "order": order,
            "active": "true" if active else "false",
            "market": market,
        }

        if tickers:
            params["tickers"] = tickers
        if ticker_gt:
            params["ticker_gt"] = ticker_gt
        if type:
            params["type"] = type

        return await self.request("reference/tickers", params)

    async def get_dividends(
        self,
        ticker: str,
        limit: int = 100,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get dividends for a ticker

        Args:
            ticker: Stock ticker
            limit: Number of results
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        """
        params = {"limit": limit}

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        return await self.request("reference/dividends/{ticker}", params)

    async def get_splits(
        self,
        ticker: str,
        limit: int = 100,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get stock splits for a ticker

        Args:
            ticker: Stock ticker
            limit: Number of results
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        """
        params = {"limit": limit}

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        return await self.request("reference/splits/{ticker}", params)

    async def get_last_trade(self, ticker: str) -> Optional[Dict]:
        """
        Get last trade for a ticker (stocks or options)

        Args:
            ticker: Stock ticker (e.g., 'AAPL') or option contract (e.g., 'O:AAPL230120C00150000')
        """
        return await self.request(f"last/trade/{ticker}")

    async def get_last_quote(self, ticker: str) -> Optional[Dict]:
        """
        Get last NBBO quote for a ticker (stocks or options)

        Args:
            ticker: Stock ticker (e.g., 'AAPL') or option contract (e.g., 'O:AAPL230120C00150000')
        """
        return await self.request(f"last/quote/{ticker}")

    async def get_trades(
        self, ticker: str, timestamp: Optional[str] = None, limit: int = 5000
    ) -> Optional[Dict]:
        """
        Get trades for a ticker (tick-level data)

        Args:
            ticker: Stock ticker
            timestamp: Timestamp to fetch trades from (Unix timestamp in milliseconds)
            limit: Number of trades to return (max 5000)
        """
        params = {"limit": limit}
        if timestamp:
            params["timestamp"] = timestamp

        return await self.request(f"trades/{ticker}", params)

    async def get_quotes(
        self, ticker: str, timestamp: Optional[str] = None, limit: int = 5000
    ) -> Optional[Dict]:
        """
        Get NBBO quotes for a ticker (tick-level data)

        Args:
            ticker: Stock ticker
            timestamp: Timestamp to fetch quotes from (Unix timestamp in milliseconds)
            limit: Number of quotes to return (max 5000)
        """
        params = {"limit": limit}
        if timestamp:
            params["timestamp"] = timestamp

        return await self.request(f"quotes/{ticker}", params)

    async def get_option_contracts(
        self,
        underlying_symbol: Optional[str] = None,
        contract_symbol: Optional[str] = None,
        limit: int = 100,
        ticker_gt: Optional[str] = None,
        sort: str = "ticker",
        order: str = "asc",
    ) -> Optional[Dict]:
        """
        Get list of options contracts

        Args:
            underlying_symbol: Underlying stock ticker (e.g., 'AAPL')
            contract_symbol: Full option contract ticker (e.g., 'O:AAPL230120C00150000')
            limit: Number of results (default 100, max 1000)
            ticker_gt: Filter contracts greater than this ticker
            sort: Sort field
            order: Sort order (asc, desc)
        """
        params = {
            "limit": limit,
            "sort": sort,
            "order": order,
        }

        if underlying_symbol:
            params["underlying_symbol"] = underlying_symbol
        if contract_symbol:
            params["ticker"] = contract_symbol
        if ticker_gt:
            params["ticker_gt"] = ticker_gt

        return await self.request("reference/options/contracts", params)

    async def get_options_chain(
        self,
        underlying_symbol: str,
        expiration: Optional[str] = None,
        strike_price: Optional[float] = None,
        contract_type: Optional[str] = None,
        limit: int = 100,
    ) -> Optional[Dict]:
        """
        Get options chain for an underlying symbol

        Args:
            underlying_symbol: Underlying stock ticker (e.g., 'AAPL')
            expiration: Expiration date (YYYY-MM-DD)
            strike_price: Strike price filter
            contract_type: 'call' or 'put'
            limit: Number of results
        """
        params = {
            "limit": limit,
            "sort": "strike_price",
        }

        if expiration:
            params["expiration_date"] = expiration
        if strike_price:
            params["strike_price"] = strike_price
        if contract_type:
            params["contract_type"] = contract_type.upper()

        return await self.request(
            f"reference/options/contracts/{underlying_symbol}", params
        )

    async def get_option_snapshot(
        self,
        underlying_symbol: Optional[str] = None,
        option_ticker: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get real-time snapshot for options

        Args:
            underlying_symbol: Get snapshot for all options of this underlying
            option_ticker: Get snapshot for specific option contract
        """
        params = {}

        if underlying_symbol:
            params["underlying_asset"] = underlying_symbol

        endpoint = "snapshot"

        if option_ticker:
            endpoint = f"snapshot/{option_ticker}"

        return await self.request(endpoint, params)

    async def get_sma(
        self,
        ticker: str,
        timespan: str = "day",
        window: int = 50,
        series: str = "close",
        adjusted: bool = True,
        limit: int = 252,
    ) -> Optional[Dict]:
        """
        Get Simple Moving Average (SMA) for a ticker

        Args:
            ticker: Stock ticker
            timespan: Size of the time window (minute, hour, day, week, month, quarter, year)
            window: Number of periods for SMA (default 50)
            series: Which price series to use (open, high, low, close, adjusted_close, volume)
            adjusted: Whether to use adjusted prices
            limit: Number of results to return
        """
        params = {
            "timespan": timespan,
            "window": window,
            "series": series,
            "adjusted": "true" if adjusted else "false",
            "limit": limit,
        }

        return await self.request(f"indicators/sma/{ticker}", params)

    async def get_ema(
        self,
        ticker: str,
        timespan: str = "day",
        window: int = 50,
        series: str = "close",
        adjusted: bool = True,
        limit: int = 252,
    ) -> Optional[Dict]:
        """
        Get Exponential Moving Average (EMA) for a ticker

        Args:
            ticker: Stock ticker
            timespan: Size of the time window
            window: Number of periods for EMA (default 50)
            series: Which price series to use
            adjusted: Whether to use adjusted prices
            limit: Number of results to return
        """
        params = {
            "timespan": timespan,
            "window": window,
            "series": series,
            "adjusted": "true" if adjusted else "false",
            "limit": limit,
        }

        return await self.request(f"indicators/ema/{ticker}", params)

    async def get_rsi(
        self,
        ticker: str,
        timespan: str = "day",
        window: int = 14,
        series: str = "close",
        adjusted: bool = True,
        limit: int = 252,
    ) -> Optional[Dict]:
        """
        Get Relative Strength Index (RSI) for a ticker

        Args:
            ticker: Stock ticker
            timespan: Size of the time window
            window: Number of periods for RSI (default 14)
            series: Which price series to use
            adjusted: Whether to use adjusted prices
            limit: Number of results to return
        """
        params = {
            "timespan": timespan,
            "window": window,
            "series": series,
            "adjusted": "true" if adjusted else "false",
            "limit": limit,
        }

        return await self.request(f"indicators/rsi/{ticker}", params)

    async def get_macd(
        self,
        ticker: str,
        timespan: str = "day",
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        series: str = "close",
        adjusted: bool = True,
        limit: int = 252,
    ) -> Optional[Dict]:
        """
        Get Moving Average Convergence Divergence (MACD) for a ticker

        Args:
            ticker: Stock ticker
            timespan: Size of the time window
            fast: Fast period (default 12)
            slow: Slow period (default 26)
            signal: Signal period (default 9)
            series: Which price series to use
            adjusted: Whether to use adjusted prices
            limit: Number of results to return
        """
        params = {
            "timespan": timespan,
            "fast": fast,
            "slow": slow,
            "signal": signal,
            "series": series,
            "adjusted": "true" if adjusted else "false",
            "limit": limit,
        }

        return await self.request(f"indicators/macd/{ticker}", params)

    async def get_bollinger_bands(
        self,
        ticker: str,
        timespan: str = "day",
        window: int = 20,
        std: int = 2,
        series: str = "close",
        adjusted: bool = True,
        limit: int = 252,
    ) -> Optional[Dict]:
        """
        Get Bollinger Bands for a ticker

        Args:
            ticker: Stock ticker
            timespan: Size of the time window
            window: Number of periods (default 20)
            std: Number of standard deviations (default 2)
            series: Which price series to use
            adjusted: Whether to use adjusted prices
            limit: Number of results to return
        """
        params = {
            "timespan": timespan,
            "window": window,
            "std": std,
            "series": series,
            "adjusted": "true" if adjusted else "false",
            "limit": limit,
        }

        return await self.request(f"indicators/bbands/{ticker}", params)

    async def get_gainers_losers(
        self, direction: str = "gainers", market: str = "stocks"
    ) -> Optional[Dict]:
        """
        Get top gainers or losers

        Args:
            direction: 'gainers', 'losers', or 'unchanged'
            market: Market type ('stocks', 'crypto', 'fx', 'indices')
        """
        return await self.request(f"snapshot/{market}/{direction}")

    async def get_snapshot(self, tickers: Optional[str] = None) -> Optional[Dict]:
        """
        Get snapshot data for multiple tickers

        Args:
            tickers: Comma-separated list of tickers
        """
        params = {}
        if tickers:
            params["tickers"] = tickers

        return await self.request("snapshot", params)

    async def get_daily_best(
        self, market: str = "stocks", direction: str = "gainers", limit: int = 10
    ) -> Optional[Dict]:
        """
        Get daily best gainers/losers with OHLCV data

        Args:
            market: Market type ('stocks', 'crypto', 'fx', 'indices')
            direction: 'gainers' or 'losers'
            limit: Number of results
        """
        params = {"limit": limit}
        return await self.request(f"snapshot/{market}/{direction}", params)

    async def get_company_details(self, ticker: str) -> Optional[Dict]:
        """
        Get company details

        Args:
            ticker: Stock ticker
        """
        return await self.request("reference/company/{ticker}")

    async def fetch_and_save_stock(
        self, ticker: str, historical_days: int = 252
    ) -> bool:
        """
        Fetch and save stock data to database

        Args:
            ticker: Stock ticker (e.g., 'AAPL')
            historical_days: Number of days of historical data to fetch (default: 252 = 1 year)

        Returns:
            True if successful, False otherwise
        """
        try:
            from assets.models.asset import Asset, AssetType
            from assets.models.historic.prices import AssetPricesHistoric
            from datetime import timedelta
            import asyncio

            # Get or create asset type for stock
            stock_type, _ = await asyncio.to_thread(
                AssetType.objects.get_or_create,
                name="Stock",
                defaults={"name": "Stock"},
            )

            # Get or create asset
            asset, created = await asyncio.to_thread(
                Asset.objects.update_or_create,
                symbol__iexact=ticker,
                defaults={
                    "symbol": ticker,
                    "name": ticker,
                    "asset_type": stock_type,
                },
            )

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=historical_days)

            # Fetch historical data
            from_str = start_date.strftime("%Y-%m-%d")
            to_str = end_date.strftime("%Y-%m-%d")

            historical_data = await self.get_aggregate_bars(
                ticker, timespan="day", multiplier=1, from_date=from_str, to_date=to_str
            )

            if not historical_data or "results" not in historical_data:
                logger.warning(f"No historical data found for {ticker}")
                return False

            # Get ticker details
            ticker_details = await self.get_ticker_details(ticker)

            if ticker_details and "results" in ticker_details:
                details = ticker_details["results"][0]
                asset.name = details.get("name", ticker)
                asset.description = details.get("description", "")
                asset.website = details.get("homepage_url", "")
                asset.country = details.get("country", "")
                asset.is_active = True

                # Save logo URL
                if "branding" in details:
                    asset.logo_url = details["branding"].get("icon_url", "")

                await asyncio.to_thread(asset.save)

            # Save historical prices efficiently
            count = 0
            for bar in historical_data["results"]:
                try:
                    await asyncio.to_thread(
                        AssetPricesHistoric.objects.create,
                        asset=asset,
                        timestamp=datetime.strptime(bar["t"][:10], "%Y-%m-%d"),
                        open=float(bar.get("o", 0)),
                        high=float(bar.get("h", 0)),
                        low=float(bar.get("l", 0)),
                        close=float(bar.get("c", 0)),
                        volume=float(bar.get("v", 0)),
                    )
                    count += 1
                except Exception as e:
                    logger.debug(f"Error saving price point for {ticker}: {str(e)}")
                    continue

            logger.info(f"Saved {count} historical prices for {ticker}")
            return True

        except Exception as e:
            logger.error(f"Error fetching/saving stock {ticker}: {str(e)}")
            return False

    async def fetch_multiple_stocks(
        self, tickers: List[str], historical_days: int = 252
    ) -> Dict[str, bool]:
        """
        Fetch multiple stocks with batch operations

        Args:
            tickers: List of stock tickers
            historical_days: Number of days of historical data

        Returns:
            Dict mapping tickers to success/failure
        """
        logger.info(f"Fetching {len(tickers)} stocks...")

        results = {}
        async with self:
            tasks = [
                self.fetch_and_save_stock(ticker, historical_days) for ticker in tickers
            ]
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for ticker, result in zip(tickers, task_results):
                if isinstance(result, Exception):
                    results[ticker] = False
                    logger.error(f"Error fetching {ticker}: {str(result)}")
                else:
                    results[ticker] = result

        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Fetched {success_count}/{len(tickers)} stocks successfully")

        return results

    async def get_popular_stocks(self, limit: int = 100) -> List[str]:
        """Get list of popular stocks to track"""
        tickers_data = await self.get_tickers(limit=limit)

        if tickers_data and "results" in tickers_data:
            return [t["ticker"] for t in tickers_data["results"]]
        return []

    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings

        scraper = cls()
        return scraper


async def get_popular_stocks(limit: int = 100) -> List[str]:
    """Get list of popular stocks to track"""
    scraper = PolygonIOScraper()
    popular_stocks = await scraper.get_popular_stocks(limit)

    logger.info(f"Retrieved {len(popular_stocks)} popular stocks from Polygon.io")
    return popular_stocks


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = PolygonIOScraper()

        # Test with AAPL
        print("Testing Polygon.io scraper with AAPL...")
        result = await scraper.fetch_and_save_stock("AAPL")
        print(f"AAPL Result: {result}")

        # Test with MSFT
        print("\nTesting Polygon.io scraper with MSFT...")
        result = await scraper.fetch_and_save_stock("MSFT")
        print(f"MSFT Result: {result}")

        # Test with multiple stocks
        print("\nTesting Polygon.io scraper with popular stocks...")
        popular = await get_popular_stocks(10)
        results = await scraper.fetch_multiple_stocks(popular)
        print(f"Results: {results}")

        # Get ticker details
        print("\nGetting ticker details for AAPL...")
        details = await scraper.get_ticker_details("AAPL")
        print(f"Details: {details}")

        # Get company details
        print("\nGetting company details for AAPL...")
        company = await scraper.get_company_details("AAPL")
        print(f"Company: {company}")

    asyncio.run(main())
