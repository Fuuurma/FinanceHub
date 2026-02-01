"""
CoinGecko WebSocket Client
Real-time cryptocurrency price streaming via CoinGecko's WebSocket API
"""

import asyncio
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Set

import websockets
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CoinGeckoWebSocketConfig(BaseModel):
    """Configuration for CoinGecko WebSocket client"""

    WS_URL: str = "wss://ws.coingecko.com/price/v1"
    RECONNECT_DELAY: float = 5.0
    MAX_RECONNECT_ATTEMPTS: int = 10
    PING_INTERVAL: float = 30.0
    SUBSCRIPTION_TIMEOUT: float = 10.0


class CoinGeckoPriceUpdate(BaseModel):
    """Price update message from CoinGecko WebSocket"""

    type: str
    coin_id: str
    currency: str = "usd"
    price: float
    timestamp: int
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True


class CoinGeckoWebSocketClient:
    """
    WebSocket client for real-time cryptocurrency prices from CoinGecko.

    Features:
    - Auto-reconnection with exponential backoff
    - Heartbeat/ping-pong mechanism
    - Subscription management (subscribe/unsubscribe)
    - Price update callbacks
    - Connection state tracking
    """

    def __init__(self, config: Optional[CoinGeckoWebSocketConfig] = None):
        self.config = config or CoinGeckoWebSocketConfig()
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected: bool = False
        self._reconnect_attempts: int = 0
        self._subscriptions: Set[str] = set()
        self._callbacks: List[Callable[[CoinGeckoPriceUpdate], None]] = []
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._listener_task: Optional[asyncio.Task] = None
        self._price_buffer: Dict[str, CoinGeckoPriceUpdate] = {}
        self._buffer_flush_task: Optional[asyncio.Task] = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def subscribed_coins(self) -> Set[str]:
        return self._subscriptions.copy()

    def add_price_callback(
        self, callback: Callable[[CoinGeckoPriceUpdate], None]
    ) -> None:
        """Register a callback for price updates"""
        self._callbacks.append(callback)

    def remove_price_callback(
        self, callback: Callable[[CoinGeckoPriceUpdate], None]
    ) -> None:
        """Remove a callback from price updates"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def connect(self) -> bool:
        """Establish WebSocket connection to CoinGecko"""
        try:
            if self._connected:
                logger.warning("Already connected to CoinGecko WebSocket")
                return True

            logger.info(f"Connecting to CoinGecko WebSocket at {self.config.WS_URL}")
            self._websocket = await websockets.connect(
                self.config.WS_URL,
                ping_interval=None,
                close_timeout=10.0,
            )

            self._connected = True
            self._reconnect_attempts = 0
            logger.info("Successfully connected to CoinGecko WebSocket")

            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._listener_task = asyncio.create_task(self._listen())

            return True

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Failed to connect to CoinGecko WebSocket: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Close WebSocket connection"""
        self._connected = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self._websocket:
            try:
                await self._websocket.close()
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.warning(f"Error closing WebSocket: {e}")

        self._websocket = None
        logger.info("Disconnected from CoinGecko WebSocket")

    async def subscribe(self, coin_ids: List[str], currency: str = "usd") -> bool:
        """
        Subscribe to price updates for given coin IDs.

        Args:
            coin_ids: List of CoinGecko coin IDs (e.g., ['bitcoin', 'ethereum'])
            currency: Quote currency (default: 'usd')

        Returns:
            True if subscription successful
        """
        if not self._connected or not self._websocket:
            logger.error("Cannot subscribe: not connected")
            return False

        try:
            for coin_id in coin_ids:
                self._subscriptions.add(coin_id)

            message = {
                "action": "subscribe",
                "coins": [
                    {"id": coin_id, "currency": currency} for coin_id in coin_ids
                ],
            }

            await self._websocket.send(json.dumps(message))
            logger.info(f"Subscribed to {len(coin_ids)} coins: {coin_ids}")
            return True

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Failed to subscribe: {e}")
            return False

    async def unsubscribe(self, coin_ids: List[str], currency: str = "usd") -> bool:
        """
        Unsubscribe from price updates for given coin IDs.

        Args:
            coin_ids: List of CoinGecko coin IDs
            currency: Quote currency

        Returns:
            True if unsubscription successful
        """
        if not self._connected or not self._websocket:
            logger.error("Cannot unsubscribe: not connected")
            return False

        try:
            for coin_id in coin_ids:
                self._subscriptions.discard(coin_id)

            message = {
                "action": "unsubscribe",
                "coins": [
                    {"id": coin_id, "currency": currency} for coin_id in coin_ids
                ],
            }

            await self._websocket.send(json.dumps(message))
            logger.info(f"Unsubscribed from {len(coin_ids)} coins: {coin_ids}")
            return True

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Failed to unsubscribe: {e}")
            return False

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to keep connection alive"""
        while self._connected:
            try:
                await asyncio.sleep(self.config.PING_INTERVAL)
                if self._connected and self._websocket:
                    try:
                        await self._websocket.ping()
                    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                        logger.warning(f"Heartbeat failed: {e}")
                        break
            except asyncio.CancelledError:
                break
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Heartbeat loop error: {e}")
                break

        if self._connected:
            logger.warning("Heartbeat failed, attempting reconnection...")
            await self._reconnect()

    async def _listen(self) -> None:
        """Listen for incoming price updates"""
        while self._connected:
            try:
                if self._websocket:
                    message = await self._websocket.recv()
                    await self._handle_message(message)
            except asyncio.CancelledError:
                break
            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                break
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Error listening for messages: {e}")
                break

        if self._connected:
            await self._reconnect()

    async def _handle_message(self, message: str) -> None:
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)

            if data.get("type") == "price":
                update = CoinGeckoPriceUpdate(
                    type=data.get("type", "price"),
                    coin_id=data.get("coin_id", data.get("id", "")),
                    currency=data.get("currency", "usd"),
                    price=data.get("price", 0),
                    timestamp=data.get("timestamp", 0),
                    market_cap=data.get("market_cap"),
                    volume_24h=data.get("volume_24h"),
                    price_change_24h=data.get("price_change_24h"),
                    price_change_percentage_24h=data.get("price_change_percentage_24h"),
                )

                await self._notify_callbacks(update)

            elif data.get("type") == "heartbeat":
                logger.debug("Received heartbeat from CoinGecko")

            else:
                logger.debug(f"Unknown message type: {data.get('type')}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error handling message: {e}")

    async def _notify_callbacks(self, update: CoinGeckoPriceUpdate) -> None:
        """Notify all registered callbacks of price update"""
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(update)
                else:
                    callback(update)
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Error in price callback: {e}")

    async def _reconnect(self) -> None:
        """Attempt to reconnect with exponential backoff"""
        if self._reconnect_attempts >= self.config.MAX_RECONNECT_ATTEMPTS:
            logger.error("Max reconnection attempts reached")
            return

        self._connected = False
        delay = min(self.config.RECONNECT_DELAY * (2**self._reconnect_attempts), 60.0)

        logger.info(
            f"Reconnecting in {delay:.1f}s (attempt {self._reconnect_attempts + 1})"
        )
        await asyncio.sleep(delay)

        self._reconnect_attempts += 1

        if await self.connect():
            if self._subscriptions:
                await self.subscribe(list(self._subscriptions), currency="usd")
            self._reconnect_attempts = 0


class CoinGeckoRESTClient:
    """
    REST API client for CoinGecko (used when WebSocket is unavailable)
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._session = None

    async def get_price(
        self,
        coin_ids: List[str],
        currency: str = "usd",
        include_24hr_change: bool = True,
        include_24hr_vol: bool = True,
        include_market_cap: bool = True,
    ) -> Dict[str, Any]:
        """Get current prices for coins"""
        from .call_planner import get_call_planner

        planner = get_call_planner("coingecko")

        async with planner:
            url = f"{self.BASE_URL}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": currency,
                "include_24hr_change": str(include_24hr_change).lower(),
                "include_24hr_vol": str(include_24hr_vol).lower(),
                "include_market_cap": str(include_market_cap).lower(),
            }

            headers = {}
            if self.api_key:
                headers["x-cg-pro-api-key"] = self.api_key

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()

    async def get_trending(self) -> Dict[str, Any]:
        """Get trending coins from CoinGecko"""
        from .call_planner import get_call_planner

        planner = get_call_planner("coingecko")

        async with planner:
            url = f"{self.BASE_URL}/search/trending"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()

    async def get_coin_market_chart(
        self,
        coin_id: str,
        currency: str = "usd",
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get historical market chart data for a coin"""
        from .call_planner import get_call_planner

        planner = get_call_planner("coingecko")

        async with planner:
            url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
            params = {
                "vs_currency": currency,
                "days": days,
            }

            headers = {}
            if self.api_key:
                headers["x-cg-pro-api-key"] = self.api_key

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()


async def get_coingecko_websocket_client() -> CoinGeckoWebSocketClient:
    """Factory function to create and connect CoinGecko WebSocket client"""
    client = CoinGeckoWebSocketClient()
    await client.connect()
    return client
