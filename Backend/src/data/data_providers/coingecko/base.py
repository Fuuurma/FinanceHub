# apps/assets/services/fetchers/coingecko_fetcher.py
"""CoinGecko API Fetcher - Comprehensive cryptocurrency data"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.core.cache import cache

from utils.helpers.logger.logger import get_logger


logger = get_logger(__name__)


class CoinGeckoFetcher:
    """
    CoinGecko API Fetcher
    Free tier: 10-50 calls/minute
    Pro tier: 500 calls/minute
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {}
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with rate limiting"""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    # Rate limited, wait and retry
                    logger.warning("CoinGecko rate limit hit, waiting 60s...")
                    await asyncio.sleep(60)
                    return await self._request(endpoint, params)

                response.raise_for_status()
                data = await response.json()

                # Rate limiting: Free tier = 10-50 calls/min
                await asyncio.sleep(1.2 if not self.api_key else 0.12)

                return data

        except Exception as e:
            logger.error(f"CoinGecko API error: {str(e)}")
            raise

    async def ping(self) -> bool:
        """Check API connectivity"""
        try:
            data = await self._request("ping")
            return data.get("gecko_says") == "(V3) To the Moon!"
        except:
            return False

    async def get_coins_list(self, include_platform: bool = True) -> List[Dict]:
        """
        Get list of all coins with id, symbol, name
        Returns: [{'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin', ...}]
        """
        endpoint = "coins/list"
        params = {"include_platform": str(include_platform).lower()}
        return await self._request(endpoint, params)

    async def get_coin_markets(
        self,
        vs_currency: str = "usd",
        category: Optional[str] = None,
        order: str = "market_cap_desc",
        per_page: int = 250,
        page: int = 1,
    ) -> List[Dict]:
        """
        Get coins market data (price, market cap, volume)

        Args:
            vs_currency: Target currency (usd, eur, jpy, etc.)
            category: Filter by category (e.g., 'decentralized_finance_defi')
            order: Sort order (market_cap_desc, volume_desc, etc.)
            per_page: Results per page (1-250)
            page: Page number

        Returns:
            List of coin market data with current prices, 24h changes, etc.
        """
        endpoint = "coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": False,
            "price_change_percentage": "24h,7d,30d",
        }

        if category:
            params["category"] = category

        return await self._request(endpoint, params)

    async def get_coin_by_id(
        self,
        coin_id: str,
        localization: bool = False,
        tickers: bool = True,
        market_data: bool = True,
        community_data: bool = True,
        developer_data: bool = True,
    ) -> Dict:
        """
        Get comprehensive coin data by ID

        Returns:
            Full coin data including price, market cap, description, links, etc.
        """
        endpoint = f"coins/{coin_id}"
        params = {
            "localization": str(localization).lower(),
            "tickers": str(tickers).lower(),
            "market_data": str(market_data).lower(),
            "community_data": str(community_data).lower(),
            "developer_data": str(developer_data).lower(),
        }
        return await self._request(endpoint, params)

    async def get_coin_ohlc(
        self, coin_id: str, vs_currency: str = "usd", days: int = 30
    ) -> List[List]:
        """
        Get OHLC (candlestick) data

        Args:
            coin_id: Coin ID (e.g., 'bitcoin')
            vs_currency: Target currency
            days: Data up to number of days ago (1/7/14/30/90/180/365/max)

        Returns:
            [[timestamp, open, high, low, close], ...]
        """
        endpoint = f"coins/{coin_id}/ohlc"
        params = {"vs_currency": vs_currency, "days": days}
        return await self._request(endpoint, params)

    async def get_coin_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30,
        interval: Optional[str] = None,
    ) -> Dict:
        """
        Get historical market data (price, market cap, volume)

        Args:
            coin_id: Coin ID
            vs_currency: Target currency
            days: Number of days (1-max)
            interval: Data interval (daily, hourly) - auto if None

        Returns:
            {
                'prices': [[timestamp, price], ...],
                'market_caps': [[timestamp, cap], ...],
                'total_volumes': [[timestamp, volume], ...]
            }
        """
        endpoint = f"coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days}

        if interval:
            params["interval"] = interval

        return await self._request(endpoint, params)

    async def get_coin_market_chart_range(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        from_timestamp: int = None,
        to_timestamp: int = None,
    ) -> Dict:
        """
        Get historical market data within date range

        Args:
            coin_id: Coin ID
            vs_currency: Target currency
            from_timestamp: From UNIX timestamp
            to_timestamp: To UNIX timestamp
        """
        endpoint = f"coins/{coin_id}/market_chart/range"
        params = {
            "vs_currency": vs_currency,
            "from": from_timestamp,
            "to": to_timestamp,
        }
        return await self._request(endpoint, params)

    async def get_trending_coins(self) -> Dict:
        """Get trending search coins (Top 7)"""
        return await self._request("search/trending")

    async def get_global_data(self) -> Dict:
        """Get cryptocurrency global data (market cap, volume, etc.)"""
        return await self._request("global")

    async def get_exchanges_list(
        self, per_page: int = 100, page: int = 1
    ) -> List[Dict]:
        """Get list of exchanges"""
        params = {"per_page": per_page, "page": page}
        return await self._request("exchanges", params)

    async def get_exchange_by_id(self, exchange_id: str) -> Dict:
        """Get exchange data by ID"""
        return await self._request(f"exchanges/{exchange_id}")

    async def get_categories_list(self) -> List[Dict]:
        """Get list of coin categories"""
        return await self._request("coins/categories/list")
