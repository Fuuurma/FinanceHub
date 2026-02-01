"""
IEX Cloud Fundamentals Scraper using BaseAPIFetcher for key rotation
Best for company fundamentals, financial statements, and earnings data
"""

import aiohttp
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

import polars as pl

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class IEXCloudScraper(BaseAPIFetcher):
    """
    IEX Cloud API implementation with key rotation

    Free tier (Launch): 500,000 calls/month (sandbox environment)
    Strategy: Use for fundamentals, not real-time prices

    Data Available:
    - Company fundamentals
    - Financial statements (10-K, 10-Q)
    - Earnings data
    - Dividends and splits
    - News
    - 20+ years of historical data (sandbox)
    """

    def __init__(self):
        super().__init__(provider_name="iex_cloud")
        self.is_sandbox = True  # Free tier uses sandbox

    def get_base_url(self) -> str:
        if self.is_sandbox:
            return "https://sandbox.iexapis.com/stable"
        return "https://cloud.iexapis.com/stable"

    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from IEX Cloud response"""
        if response and isinstance(response, dict):
            if "error" in response:
                error = response["error"]
                if any(
                    keyword in str(error).lower()
                    for keyword in ["rate limit", "too many", "limit"]
                ):
                    return str(error)
            # IEX Cloud returns HTTP 429 for rate limits
            if response.get("statusCode") == 429:
                return "Rate limit exceeded"
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
            import orjson

            return orjson.loads(content)

    def _get_headers(self, api_key) -> Dict:
        """IEX Cloud uses API key in query string"""
        return {"Accept": "application/json", "User-Agent": "FinanceHub/1.0"}

    def _add_api_key_param(self, params: Dict, api_key) -> Dict:
        """Add API key to query params (IEX uses query string, not header)"""
        if params is None:
            params = {}
        params["token"] = api_key.key_value
        return params

    async def get_company(self, symbol: str) -> Optional[Dict]:
        """
        Get company information

        Args:
            symbol: Stock ticker (e.g., 'AAPL')
        """
        params = {"symbol": symbol}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/company", params=params_with_key)

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get quote for a symbol (sandbox data)

        Args:
            symbol: Stock ticker
        """
        params = {"symbol": symbol}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/quote", params=params_with_key)

    async def get_quotes(self, symbols: List[str]) -> Optional[Dict]:
        """
        Get quotes for multiple symbols

        Args:
            symbols: List of stock tickers
        """
        params = {"symbols": ",".join(symbols)}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/market/batch", params=params_with_key)

    async def get_chart(
        self, symbol: str, period: str = "1y", range: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get historical chart data

        Args:
            symbol: Stock ticker
            period: Time period (dynamic, 1d, 1m, 3m, 6m, 1y, 2y, 5y, ytd, max)
            range: Date range (YYYYMMDD-YYYYMMDD)
        """
        params = {"symbol": symbol}
        if range:
            params["range"] = range

        params_with_key = await self._get_api_key_params(params)

        endpoint = f"stock/{symbol}/chart/{period}"
        if range:
            endpoint = f"stock/{symbol}/chart/{period}/{range}"

        return await self.request(endpoint, params=params_with_key)

    async def get_income_statement(
        self, symbol: str, period: str = "annual", last: int = 4
    ) -> Optional[Dict]:
        """
        Get income statement

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarterly'
            last: Number of periods to return
        """
        params = {"period": period, "last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/income", params=params_with_key)

    async def get_balance_sheet(
        self, symbol: str, period: str = "annual", last: int = 4
    ) -> Optional[Dict]:
        """
        Get balance sheet

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarterly'
            last: Number of periods to return
        """
        params = {"period": period, "last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            "stock/{symbol}/balance-sheet", params=params_with_key
        )

    async def get_cash_flow(
        self, symbol: str, period: str = "annual", last: int = 4
    ) -> Optional[Dict]:
        """
        Get cash flow statement

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarterly'
            last: Number of periods to return
        """
        params = {"period": period, "last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/cash-flow", params=params_with_key)

    async def get_financials(
        self, symbol: str, period: str = "annual", last: int = 4
    ) -> Optional[Dict]:
        """
        Get all financial statements (income, balance sheet, cash flow)

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarterly'
            last: Number of periods to return
        """
        params = {"period": period, "last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/financials", params=params_with_key)

    async def get_earnings(
        self, symbol: str, period: str = "annual", last: int = 4
    ) -> Optional[Dict]:
        """
        Get earnings data

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarterly'
            last: Number of periods to return
        """
        params = {"period": period, "last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/earnings", params=params_with_key)

    async def get_dividends(
        self, symbol: str, range: Optional[str] = None, by: str = "ex"
    ) -> Optional[Dict]:
        """
        Get dividends data

        Args:
            symbol: Stock ticker
            range: Date range (YYYYMMDD-YYYYMMDD)
            by: 'ex' (ex-dividend date) or 'pay' (payment date)
        """
        params = {"by": by}
        if range:
            params["range"] = range

        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/dividends", params=params_with_key)

    async def get_splits(
        self, symbol: str, range: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get stock splits data

        Args:
            symbol: Stock ticker
            range: Date range (YYYYMMDD-YYYYMMDD)
        """
        params = {}
        if range:
            params["range"] = range

        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/{symbol}/splits", params=params_with_key)

    async def get_news(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """
        Get news for a symbol

        Args:
            symbol: Stock ticker
            limit: Number of articles
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/news/last/{limit}", params=params_with_key
        )

    async def get_key_stats(self, symbol: str) -> Optional[Dict]:
        """
        Get key statistics for a symbol

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(f"stock/{symbol}/stats", params=params_with_key)

    async def get_estimates(
        self, symbol: str, period: str = "annual", last: int = 4
    ) -> Optional[Dict]:
        """
        Get analyst estimates

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarterly'
            last: Number of periods
        """
        params = {"period": period, "last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(f"stock/{symbol}/estimates", params=params_with_key)

    async def get_peers(self, symbol: str) -> Optional[List]:
        """
        Get peer companies

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(f"stock/{symbol}/peers", params=params_with_key)

    async def get_stats_valuation(self, symbol: str) -> Optional[Dict]:
        """
        Get valuation metrics

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/stats/valuation", params=params_with_key
        )

    async def get_advanced_stats(self, symbol: str) -> Optional[Dict]:
        """
        Get advanced statistics

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/advanced-stats", params=params_with_key
        )

    async def get_daily_basic(self, symbol: str, last: int = 1) -> Optional[Dict]:
        """
        Get daily basic data (market cap, etc.)

        Args:
            symbol: Stock ticker
            last: Number of days
        """
        params = {"last": last}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/daily-basic/last/{last}", params=params_with_key
        )

    async def get_ipos(self, date: Optional[str] = None) -> Optional[Dict]:
        """
        Get upcoming or recent IPOs

        Args:
            date: Specific date (YYYYMMDD) or None for calendar
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        if date:
            return await self.request(f"stock/market/ipo/next", params=params_with_key)
        return await self.request("stock/market/ipo", params=params_with_key)

    async def get_market_volume(self) -> Optional[Dict]:
        """Get market volume data"""
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request("stock/market/volume", params=params_with_key)

    async def get_market_list(self, list_type: str = "mostactive") -> Optional[Dict]:
        """
        Get market movers

        Args:
            list_type: 'mostactive', 'gainers', 'losers', 'mlist', 'ulist'
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/market/list/{list_type}", params=params_with_key
        )

    async def get_sector_performance(self) -> Optional[List]:
        """Get sector performance data"""
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            "stock/market/sector-performance", params=params_with_key
        )

    async def get_insider_transactions(self, symbol: str) -> Optional[Dict]:
        """
        Get insider transactions

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/insider-transactions", params=params_with_key
        )

    async def get_institutional_ownership(self, symbol: str) -> Optional[Dict]:
        """
        Get institutional ownership

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/institutional-ownership", params=params_with_key
        )

    async def get_fund_ownership(self, symbol: str) -> Optional[Dict]:
        """
        Get fund ownership

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/fund-ownership", params=params_with_key
        )

    async def get_board_members(self, symbol: str) -> Optional[Dict]:
        """
        Get board members

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(
            f"stock/{symbol}/board-members", params=params_with_key
        )

    async def get_SEC_filings(self, symbol: str) -> Optional[Dict]:
        """
        Get SEC filings

        Args:
            symbol: Stock ticker
        """
        params = {}
        params_with_key = await self._get_api_key_params(params)

        return await self.request(f"stock/{symbol}/sec-filings", params=params_with_key)

    async def fetch_and_save_stock(
        self, symbol: str, historical_years: int = 2
    ) -> bool:
        """
        Fetch and save stock fundamentals and historical data

        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            historical_years: Number of years of historical data (default: 2)

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
                symbol__iexact=symbol,
                defaults={
                    "symbol": symbol,
                    "name": symbol,
                    "asset_type": stock_type,
                },
            )

            # Get company data
            company_data = await self.get_company(symbol)

            if company_data:
                asset.name = company_data.get("companyName", symbol)
                asset.description = company_data.get("description", "")
                asset.website = company_data.get("website", "")
                asset.country = company_data.get("country", "")
                asset.industry = company_data.get("industry", "")
                asset.sector = company_data.get("sector", "")
                asset.employees = company_data.get("employees", None)

                # Save logo
                if "logo" in company_data:
                    asset.logo_url = company_data["logo"]

                asset.is_active = True

                # Save synchronously
                await asyncio.to_thread(asset.save)

                logger.info(f"Saved company data for {symbol}")

            # Get financial statements
            try:
                financials = await self.get_financials(symbol, period="annual", last=1)

                if financials:
                    logger.info(f"Fetched financials for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching financials for {symbol}: {str(e)}")

            # Get earnings data
            try:
                earnings = await self.get_earnings(symbol, period="annual", last=4)

                if earnings:
                    logger.info(f"Fetched earnings for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching earnings for {symbol}: {str(e)}")

            # Get dividends
            try:
                dividends = await self.get_dividends(symbol)

                if dividends:
                    logger.info(f"Fetched dividends for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching dividends for {symbol}: {str(e)}")

            # Get historical data
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=historical_years * 365)

                historical_data = await self.get_chart(
                    symbol,
                    period="daily",
                    range=f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}",
                )

                if historical_data and isinstance(historical_data, list):
                    # Save historical prices efficiently
                    count = 0
                    for bar in historical_data:
                        try:
                            await asyncio.to_thread(
                                AssetPricesHistoric.objects.create,
                                asset=asset,
                                timestamp=datetime.strptime(
                                    bar["date"][:10], "%Y-%m-%d"
                                ),
                                open=float(bar.get("open", 0)),
                                high=float(bar.get("high", 0)),
                                low=float(bar.get("low", 0)),
                                close=float(bar.get("close", 0)),
                                volume=float(bar.get("volume", 0)),
                            )
                            count += 1
                        except Exception as e:
                            logger.debug(
                                f"Error saving price point for {symbol}: {str(e)}"
                            )
                            continue

                    logger.info(f"Saved {count} historical prices for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {str(e)}")

            logger.info(
                f"Successfully fetched and saved data for stock {symbol} (created: {created})"
            )
            return True

        except Exception as e:
            logger.error(f"Error fetching/saving stock {symbol}: {str(e)}")
            return False

    async def fetch_multiple_stocks(
        self, symbols: List[str], historical_years: int = 2
    ) -> Dict[str, bool]:
        """
        Fetch multiple stocks with batch operations

        Args:
            symbols: List of stock tickers
            historical_years: Number of years of historical data

        Returns:
            Dict mapping symbols to success/failure
        """
        logger.info(f"Fetching {len(symbols)} stocks from IEX Cloud...")

        results = {}
        async with self:
            tasks = [
                self.fetch_and_save_stock(symbol, historical_years)
                for symbol in symbols
            ]
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            for symbol, result in zip(symbols, task_results):
                if isinstance(result, Exception):
                    results[symbol] = False
                    logger.error(f"Error fetching {symbol}: {str(result)}")
                else:
                    results[symbol] = result

        success_count = sum(1 for v in results.values() if v)
        logger.info(
            f"IEX Cloud: {success_count}/{len(symbols)} stocks fetched successfully"
        )

        return results

    async def get_popular_stocks(self, limit: int = 100) -> List[str]:
        """Get list of popular stocks to track"""
        # For IEX, we'll return predefined popular stocks
        # since there's no "popular" endpoint
        from tasks.data_fetcher import POPULAR_STOCKS

        return POPULAR_STOCKS[:limit]

    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings

        scraper = cls()
        return scraper


async def get_popular_stocks(limit: int = 100) -> List[str]:
    """Get list of popular stocks to track"""
    scraper = IEXCloudScraper()
    popular_stocks = await scraper.get_popular_stocks(limit)

    logger.info(f"Retrieved {len(popular_stocks)} popular stocks from IEX Cloud")
    return popular_stocks


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = IEXCloudScraper()

        # Test with AAPL
        logger.info("Testing IEX Cloud scraper with AAPL...")
        result = await scraper.fetch_and_save_stock("AAPL")
        logger.info("AAPL Result: %s", result)

        # Test with MSFT
        logger.info("Testing IEX Cloud scraper with MSFT...")
        result = await scraper.fetch_and_save_stock("MSFT")
        logger.info("MSFT Result: %s", result)

        # Test with multiple stocks
        logger.info("Testing IEX Cloud scraper with popular stocks...")
        popular = await get_popular_stocks(5)
        results = await scraper.fetch_multiple_stocks(popular)
        logger.info("Results: %s", results)

        # Get financials
        logger.info("Getting financials for AAPL...")
        financials = await scraper.get_financials("AAPL")
        logger.info("Financials: %s", financials)

    asyncio.run(main())
