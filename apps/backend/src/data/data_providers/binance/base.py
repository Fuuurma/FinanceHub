"""Binance API Fetcher"""

import asyncio
import aiohttp
import hmac
import hashlib
import time
from typing import List, Dict, Optional
from decimal import Decimal

from utils.helpers.logger.logger import get_logger


logger = get_logger(__name__)


class BinanceFetcher:
    """
    Binance API Fetcher
    Public endpoints: No limits
    Authenticated: Weight-based rate limits
    """

    BASE_URL = "https://api.binance.com/api/v3"
    BASE_URL_FAPI = "https://fapi.binance.com/fapi/v1"  # Futures

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {}
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def _request(
        self, endpoint: str, params: Optional[Dict] = None, signed: bool = False
    ) -> Dict:
        """Make API request"""
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._generate_signature(params)

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Binance API error: {str(e)}")
            raise

    async def ping(self) -> Dict:
        """Test connectivity"""
        return await self._request("ping")

    async def get_server_time(self) -> Dict:
        """Get server time"""
        return await self._request("time")

    async def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        """
        Get exchange trading rules and symbol information

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
        """
        params = {}
        if symbol:
            params["symbol"] = symbol

        return await self._request("exchangeInfo", params)

    async def get_ticker_price(self, symbol: Optional[str] = None) -> Dict:
        """
        Get latest price for symbol(s)

        Args:
            symbol: Trading pair, if None returns all symbols
        """
        params = {}
        if symbol:
            params["symbol"] = symbol

        return await self._request("ticker/price", params)

    async def get_ticker_24hr(self, symbol: Optional[str] = None) -> Dict:
        """
        Get 24hr price change statistics

        Returns price, volume, high, low, etc.
        """
        params = {}
        if symbol:
            params["symbol"] = symbol

        return await self._request("ticker/24hr", params)

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[List]:
        """
        Get candlestick/kline data (OHLCV)

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Kline interval
                      1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
            start_time: Start time in ms
            end_time: End time in ms
            limit: Number of results (max 1000)

        Returns:
            [
                [
                    open_time,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    close_time,
                    quote_asset_volume,
                    number_of_trades,
                    taker_buy_base_asset_volume,
                    taker_buy_quote_asset_volume,
                    ignore
                ],
                ...
            ]
        """
        params = {"symbol": symbol, "interval": interval, "limit": limit}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        return await self._request("klines", params)

    async def get_avg_price(self, symbol: str) -> Dict:
        """Get current average price"""
        params = {"symbol": symbol}
        return await self._request("avgPrice", params)

    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get order book depth

        Args:
            symbol: Trading pair
            limit: Number of levels (5, 10, 20, 50, 100, 500, 1000, 5000)
        """
        params = {"symbol": symbol, "limit": limit}
        return await self._request("depth", params)

    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """
        Get recent trades

        Args:
            symbol: Trading pair
            limit: Number of trades (max 1000)
        """
        params = {"symbol": symbol, "limit": limit}
        return await self._request("trades", params)

    async def get_historical_trades(
        self, symbol: str, limit: int = 500, from_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get historical trades (requires API key)

        Args:
            symbol: Trading pair
            limit: Number of trades (max 1000)
            from_id: Trade ID to fetch from
        """
        params = {"symbol": symbol, "limit": limit}
        if from_id:
            params["fromId"] = from_id

        return await self._request("historicalTrades", params)

    async def get_agg_trades(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[Dict]:
        """
        Get compressed/aggregate trades

        Args:
            symbol: Trading pair
            start_time: Start time in ms
            end_time: End time in ms
            limit: Number of results (max 1000)
        """
        params = {"symbol": symbol, "limit": limit}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        return await self._request("aggTrades", params)

    # Authenticated endpoints (require API key + secret)

    async def get_account_info(self) -> Dict:
        """Get current account information (requires authentication)"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret required")

        return await self._request("account", signed=True)

    async def get_account_trades(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[Dict]:
        """Get account trade history (requires authentication)"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret required")

        params = {"symbol": symbol, "limit": limit}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        return await self._request("myTrades", params, signed=True)
