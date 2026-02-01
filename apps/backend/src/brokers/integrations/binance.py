import asyncio
import hmac
import hashlib
import time
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging

import aiohttp

from .base import (
    BaseBroker,
    BrokerAccount,
    BrokerPosition,
    BrokerOrder,
    BrokerTransaction,
    Quote,
    BrokerAPIError,
    RateLimitError,
    AuthenticationError,
    OrderNotFoundError,
)

logger = logging.getLogger(__name__)


class BinanceBroker(BaseBroker):
    broker_name = "Binance"
    broker_id = "binance"

    BASE_URLS = {
        "spot": "https://api.binance.com",
        "spot_test": "https://testnet.binance.vision",
        "futures": "https://fapi.binance.com",
        "futures_test": "https://testnet.binancefuture.com",
    }

    def __init__(
        self,
        api_key: bytes,
        api_secret: bytes,
        passphrase: bytes = None,
        paper_trading: bool = False,
    ):
        super().__init__(api_key, api_secret, passphrase, paper_trading)
        self.base_url = self.BASE_URLS["spot_test" if paper_trading else "spot"]
        self._session: Optional[aiohttp.ClientSession] = None

    def _get_api_key(self) -> str:
        return (
            self.api_key.decode("utf-8")
            if isinstance(self.api_key, bytes)
            else self.api_key
        )

    def _get_api_secret(self) -> str:
        return (
            self.api_secret.decode("utf-8")
            if isinstance(self.api_secret, bytes)
            else self.api_secret
        )

    def _create_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    def _sign_request(self, params: Dict = None) -> Dict[str, str]:
        if params is None:
            params = {}
        timestamp = str(int(time.time() * 1000))
        params["timestamp"] = timestamp
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self._get_api_secret().encode(),
            query_string.encode(),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
    ) -> Dict[str, Any]:
        self._create_session()
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self._get_api_key()}
        params = params or {}

        if endpoint.startswith("/api/v3") or endpoint.startswith("/fapi/v1"):
            params = self._sign_request(params)

        for attempt in range(3):
            try:
                async with self._session.request(
                    method, url, params=params, headers=headers
                ) as response:
                    if response.status == 429:
                        self._update_rate_limit_info(
                            0, datetime.now() + timedelta(seconds=60)
                        )
                        raise RateLimitError(
                            "Rate limit exceeded", code="RATE_LIMIT_EXCEEDED"
                        )

                    if response.status == 401:
                        raise AuthenticationError(
                            "Invalid API credentials", code="UNAUTHORIZED"
                        )

                    if response.status == 404:
                        raise OrderNotFoundError("Resource not found", code="NOT_FOUND")

                    if response.status >= 400:
                        error_text = await response.text()
                        raise BrokerAPIError(error_text, code=f"HTTP_{response.status}")

                    remaining = response.headers.get("X-MBX-USED-WEIGHT-1M")
                    if remaining:
                        self._update_rate_limit_info(int(remaining))

                    return await response.json()

            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                raise BrokerAPIError("Request timeout", code="TIMEOUT")

        raise BrokerAPIError("Max retries exceeded", code="MAX_RETRIES")

    async def test_connection(self) -> bool:
        try:
            await self._request("GET", "/api/v3/ping")
            return True
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Binance connection test failed: {e}")
            return False

    async def get_account(self) -> BrokerAccount:
        data = await self._request("GET", "/api/v3/account")
        balances = {
            b["asset"]: float(b["free"]) + float(b["locked"])
            for b in data.get("balances", [])
        }
        total_value = 0
        if "USDT" in balances:
            total_value = balances["USDT"]

        return BrokerAccount(
            account_id=data.get("makerCommission", 0) or "binance_spot",
            account_name=f"Binance {'Testnet' if self.paper_trading else 'Live'}",
            account_type="paper" if self.paper_trading else "live",
            currency="USDT",
            cash_balance=Decimal(str(balances.get("USDT", 0))),
            portfolio_value=Decimal(str(total_value)),
            buying_power=Decimal(str(balances.get("USDT", 0))),
            trading_blocked=False,
            last_updated=datetime.now(),
        )

    async def get_positions(self) -> List[BrokerPosition]:
        data = await self._request("GET", "/api/v3/account")
        positions = []

        for balance in data.get("balances", []):
            asset = balance["asset"]
            if asset in ["USDT", "BUSD"]:
                continue
            qty = Decimal(balance["free"]) + Decimal(balance["locked"])
            if qty > 0:
                price_data = await self._request(
                    "GET", "/api/v3/ticker/price", {"symbol": f"{asset}USDT"}
                )
                current_price = Decimal(price_data.get("price", "0"))
                market_value = qty * current_price

                positions.append(
                    BrokerPosition(
                        symbol=asset,
                        asset_id=asset,
                        quantity=qty,
                        avg_entry_price=Decimal("0"),
                        current_price=current_price,
                        market_value=market_value,
                        unrealized_pl=Decimal("0"),
                        unrealized_pl_percent=Decimal("0"),
                        side="long",
                    )
                )

        return positions

    async def get_orders(
        self,
        status: str = "all",
        symbol: str = None,
        since: datetime = None,
        until: datetime = None,
    ) -> List[BrokerOrder]:
        params = {}
        if symbol:
            params["symbol"] = symbol

        data = await self._request(
            "GET",
            "/api/v3/openOrders" if status == "open" else "/api/v3/allOrders",
            params,
        )

        result = []
        for order in data:
            status_map = {
                "NEW": "pending_new",
                "PARTIALLY_FILLED": "partial_filled",
                "FILLED": "filled",
                "CANCELED": "canceled",
                "REJECTED": "rejected",
                "EXPIRED": "expired",
            }

            def parse_dt(val):
                if not val:
                    return None
                try:
                    return datetime.fromisoformat(val.replace("Z", "+00:00"))
                except:
                    return None

            result.append(
                BrokerOrder(
                    order_id=str(order.get("orderId", "")),
                    symbol=order.get("symbol", "").replace("USDT", ""),
                    order_type=order.get("type", "market").lower(),
                    side=order.get("side", "").lower(),
                    quantity=Decimal(order.get("origQty", "0")),
                    filled_quantity=Decimal(order.get("executedQty", "0")),
                    limit_price=Decimal(order.get("price", "0"))
                    if order.get("price") and order.get("price") != "0"
                    else None,
                    stop_price=Decimal(order.get("stopPrice", "0"))
                    if order.get("stopPrice") and order.get("stopPrice") != "0"
                    else None,
                    time_in_force=order.get("timeInForce", "GTC"),
                    status=status_map.get(order.get("status", "NEW"), "pending"),
                    submitted_at=parse_dt(order.get("time")),
                    avg_fill_price=Decimal(order.get("avgPrice", "0"))
                    if order.get("avgPrice")
                    else None,
                )
            )

        return result

    async def get_transactions(
        self,
        transaction_type: str = None,
        symbol: str = None,
        since: datetime = None,
        until: datetime = None,
    ) -> List[BrokerTransaction]:
        params = {"limit": 100}
        if symbol:
            params["symbol"] = f"{symbol}USDT"
        if since:
            params["startTime"] = int(since.timestamp() * 1000)

        data = await self._request("GET", "/api/v3/myTrades", params)

        result = []
        for tx in data:
            type_map = {"buy": "buy", "sell": "sell"}

            result.append(
                BrokerTransaction(
                    transaction_id=str(tx.get("id", "")),
                    transaction_type=type_map.get(
                        tx.get("isBuyer", True) and "buy" or "sell", "other"
                    ),
                    symbol=tx.get("symbol", "").replace("USDT", ""),
                    quantity=Decimal(tx.get("qty", "0")),
                    price=Decimal(tx.get("price", "0")),
                    total=Decimal(
                        str(float(tx.get("qty", "0")) * float(tx.get("price", "0")))
                    ),
                    fee=Decimal(tx.get("commission", "0")),
                    currency=tx.get("commissionAsset", "USDT"),
                    status="completed",
                    executed_at=datetime.fromtimestamp(tx.get("time", 0) / 1000),
                    order_id=str(tx.get("orderId", "")),
                )
            )

        return result

    async def place_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: Decimal,
        limit_price: Decimal = None,
        stop_price: Decimal = None,
        time_in_force: str = "GTC",
        trailing_amount: Decimal = None,
        trailing_percent: Decimal = None,
    ) -> BrokerOrder:
        params = {
            "symbol": f"{symbol}USDT",
            "side": side.upper(),
            "quantity": str(quantity),
        }

        order_type_map = {
            "market": "MARKET",
            "limit": "LIMIT",
            "stop": "STOP_LOSS",
            "stop_limit": "STOP_LOSS_LIMIT",
        }
        params["type"] = order_type_map.get(order_type, "MARKET")

        if order_type in ["limit", "stop_limit"]:
            params["timeInForce"] = time_in_force
            params["price"] = str(limit_price)

        if order_type in ["stop", "stop_limit"] and stop_price:
            params["stopPrice"] = str(stop_price)

        data = await self._request("POST", "/api/v3/order", params)

        return BrokerOrder(
            order_id=str(data.get("orderId", "")),
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=Decimal(data.get("origQty", "0")),
            filled_quantity=Decimal(data.get("executedQty", "0")),
            status="pending_new",
            submitted_at=datetime.now(),
        )

    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        params = {"orderId": order_id}
        if symbol:
            params["symbol"] = f"{symbol}USDT"
        try:
            await self._request("DELETE", "/api/v3/order", params)
            return True
        except OrderNotFoundError:
            return False

    async def get_order(self, order_id: str, symbol: str = None) -> BrokerOrder:
        params = {"orderId": order_id}
        if symbol:
            params["symbol"] = f"{symbol}USDT"

        data = await self._request("GET", "/api/v3/order", params)

        status_map = {
            "NEW": "pending_new",
            "PARTIALLY_FILLED": "partial_filled",
            "FILLED": "filled",
            "CANCELED": "canceled",
        }

        return BrokerOrder(
            order_id=str(data.get("orderId", "")),
            symbol=data.get("symbol", "").replace("USDT", ""),
            order_type=data.get("type", "market").lower(),
            side=data.get("side", "").lower(),
            quantity=Decimal(data.get("origQty", "0")),
            filled_quantity=Decimal(data.get("executedQty", "0")),
            limit_price=Decimal(data.get("price", "0"))
            if data.get("price") and data.get("price") != "0"
            else None,
            time_in_force=data.get("timeInForce", "GTC"),
            status=status_map.get(data.get("status", "NEW"), "pending"),
            submitted_at=datetime.fromtimestamp(data.get("time", 0) / 1000)
            if data.get("time")
            else None,
        )

    async def get_quote(self, symbol: str) -> Quote:
        params = {"symbol": f"{symbol}USDT"}
        data = await self._request("GET", "/api/v3/ticker/24hr", params)

        return Quote(
            symbol=symbol,
            bid=Decimal(data.get("bidPrice", "0")),
            ask=Decimal(data.get("askPrice", "0")),
            last_price=Decimal(data.get("lastPrice", "0")),
            volume=Decimal(data.get("volume", "0")),
            timestamp=datetime.now(),
        )

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        result = {}
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                result[symbol] = quote
            except Exception:
                continue
        return result

    async def get_bars(
        self,
        symbols: List[str],
        timeframe: str = "1d",
        start: datetime = None,
        end: datetime = None,
        limit: int = 1000,
    ) -> Dict[str, List[Dict]]:
        timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }
        interval = timeframe_map.get(timeframe, "1d")

        result = {}
        for symbol in symbols:
            params = {
                "symbol": f"{symbol}USDT",
                "interval": interval,
                "limit": limit,
            }
            if start:
                params["startTime"] = int(start.timestamp() * 1000)
            if end:
                params["endTime"] = int(end.timestamp() * 1000)

            data = await self._request("GET", "/api/v3/klines", params)

            bars = []
            for kline in data:
                bars.append(
                    {
                        "timestamp": kline[0],
                        "open": kline[1],
                        "high": kline[2],
                        "low": kline[3],
                        "close": kline[4],
                        "volume": kline[5],
                    }
                )
            result[symbol] = bars

        return result
