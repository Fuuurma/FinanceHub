import asyncio
import base64
import json
import time
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


class CoinbaseBroker(BaseBroker):
    broker_name = "Coinbase"
    broker_id = "coinbase"

    BASE_URLS = {
        "api": "https://api.coinbase.com",
        "api_version": "2024-01-01",
    }

    def __init__(
        self,
        api_key: bytes,
        api_secret: bytes,
        passphrase: bytes = None,
        paper_trading: bool = False,
    ):
        super().__init__(api_key, api_secret, passphrase, paper_trading)
        self.base_url = self.BASE_URLS["api"]
        self.api_version = self.BASE_URLS["api_version"]
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

    def _get_passphrase(self) -> str:
        if self.passphrase is None:
            return ""
        return (
            self.passphrase.decode("utf-8")
            if isinstance(self.passphrase, bytes)
            else self.passphrase
        )

    def _create_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    def _create_signature(
        self, method: str, path: str, body: str = ""
    ) -> Dict[str, str]:
        timestamp = str(int(time.time()))
        message = timestamp + method + path + body
        secret = base64.b64decode(self._get_api_secret())
        signature = base64.b64encode(
            hmac.new(secret, message.encode(), "sha256").digest()
        ).decode()

        return {
            "CB-ACCESS-KEY": self._get_api_key(),
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self._get_passphrase(),
        }

    async def _request(
        self,
        method: str,
        path: str,
        body: str = "",
    ) -> Dict[str, Any]:
        self._create_session()
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "CB-VERSION": self.api_version,
        }
        headers.update(self._create_signature(method, path, body))

        for attempt in range(3):
            try:
                async with self._session.request(
                    method, url, data=body if body else None, headers=headers
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

                    return await response.json()

            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                raise BrokerAPIError("Request timeout", code="TIMEOUT")

        raise BrokerAPIError("Max retries exceeded", code="MAX_RETRIES")

    async def test_connection(self) -> bool:
        try:
            await self._request("GET", "/v2/user")
            return True
        except Exception as e:
            logger.error(f"Coinbase connection test failed: {e}")
            return False

    async def get_account(self) -> BrokerAccount:
        accounts = await self._request("GET", "/v2/accounts")
        total_usd = Decimal("0")

        for acc in accounts.get("data", []):
            balance = Decimal(acc.get("balance", {}).get("amount", "0"))
            currency = acc.get("balance", {}).get("currency", "")
            if currency in ["USD", "USDC", "USDT"]:
                total_usd += balance

        return BrokerAccount(
            account_id="coinbase_api",
            account_name=f"Coinbase {'Sandbox' if self.paper_trading else 'Live'}",
            account_type="paper" if self.paper_trading else "live",
            currency="USD",
            cash_balance=total_usd,
            portfolio_value=total_usd,
            buying_power=total_usd,
            last_updated=datetime.now(),
        )

    async def get_positions(self) -> List[BrokerPosition]:
        accounts = await self._request("GET", "/v2/accounts")
        positions = []

        for acc in accounts.get("data", []):
            balance = Decimal(acc.get("balance", {}).get("amount", "0"))
            currency = acc.get("balance", {}).get("currency", "")
            if currency in ["USD", "USDC", "USDT"]:
                continue
            if balance > 0:
                symbol = currency
                price_data = await self._request("GET", f"/v2/prices/{symbol}-USD/spot")
                if price_data.get("data"):
                    current_price = Decimal(price_data["data"].get("amount", "0"))
                    market_value = balance * current_price

                    positions.append(
                        BrokerPosition(
                            symbol=symbol,
                            asset_id=symbol,
                            quantity=balance,
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
        params = {"limit": 100}
        orders = await self._request("GET", "/v2/orders", params=params)

        result = []
        for order in orders.get("data", []):
            status_map = {
                "OPEN": "pending_new",
                "PENDING": "pending_new",
                "ACTIVE": "accepted",
                "FILLED": "filled",
                "DONE": "filled",
                "CANCELLED": "canceled",
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
                    order_id=order.get("id", ""),
                    symbol=order.get("product_id", "").split("-")[0],
                    order_type=order.get("order_type", "").lower(),
                    side=order.get("side", "").lower(),
                    quantity=Decimal(order.get("size", "0")),
                    filled_quantity=Decimal(order.get("filled_size", "0")),
                    limit_price=Decimal(order.get("limit_price", "0"))
                    if order.get("limit_price")
                    else None,
                    time_in_force=order.get("time_in_force", "GTC"),
                    status=status_map.get(order.get("status", "OPEN"), "pending"),
                    submitted_at=parse_dt(order.get("created_at")),
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
        accounts = await self._request("GET", "/v2/accounts")
        transactions = []

        for acc in accounts.get("data", []):
            currency = acc.get("balance", {}).get("currency", "")
            ledger = await self._request("GET", f"/v2/accounts/{acc['id']}/ledger")

            for entry in ledger.get("data", []):
                type_map = {
                    "BUY": "buy",
                    "SELL": "sell",
                    "DEPOSIT": "deposit",
                    "WITHDRAWAL": "withdrawal",
                    "FEE": "fee",
                }

                transactions.append(
                    BrokerTransaction(
                        transaction_id=entry.get("id", ""),
                        transaction_type=type_map.get(entry.get("type", ""), "other"),
                        symbol=currency,
                        quantity=Decimal(entry.get("amount", "0")),
                        price=Decimal(entry.get("native_amount", {}).get("amount", "0"))
                        if entry.get("native_amount")
                        else None,
                        total=Decimal(entry.get("native_amount", {}).get("amount", "0"))
                        if entry.get("native_amount")
                        else None,
                        fee=Decimal("0"),
                        currency=entry.get("native_amount", {}).get("currency", "USD"),
                        status="completed",
                        executed_at=datetime.fromisoformat(
                            entry.get("created_at", "").replace("Z", "+00:00")
                        )
                        if entry.get("created_at")
                        else None,
                    )
                )

        return transactions

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
        order_data = {
            "product_id": f"{symbol}-USD",
            "side": side,
            "type": "market" if order_type == "market" else "limit",
            "size": str(quantity),
        }

        if order_type == "limit":
            order_data["price"] = str(limit_price)
            order_data["time_in_force"] = time_in_force

        if stop_price:
            order_data["stop"] = "price"
            order_data["stop_price"] = str(stop_price)

        body = json.dumps(order_data)
        result = await self._request("POST", "/v2/orders", body)

        return BrokerOrder(
            order_id=result.get("data", {}).get("id", ""),
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            filled_quantity=Decimal("0"),
            limit_price=limit_price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            status="pending_new",
            submitted_at=datetime.now(),
        )

    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        try:
            await self._request("DELETE", f"/v2/orders/{order_id}")
            return True
        except OrderNotFoundError:
            return False

    async def get_order(self, order_id: str, symbol: str = None) -> BrokerOrder:
        result = await self._request("GET", f"/v2/orders/{order_id}")
        order = result.get("data", {})

        status_map = {
            "OPEN": "pending_new",
            "FILLED": "filled",
            "DONE": "filled",
            "CANCELLED": "canceled",
        }

        return BrokerOrder(
            order_id=order.get("id", ""),
            symbol=order.get("product_id", "").split("-")[0],
            order_type=order.get("order_type", "market").lower(),
            side=order.get("side", "").lower(),
            quantity=Decimal(order.get("size", "0")),
            filled_quantity=Decimal(order.get("filled_size", "0")),
            limit_price=Decimal(order.get("price", "0"))
            if order.get("price")
            else None,
            status=status_map.get(order.get("status", "OPEN"), "pending"),
            submitted_at=datetime.fromisoformat(
                order.get("created_at", "").replace("Z", "+00:00")
            )
            if order.get("created_at")
            else None,
        )

    async def get_quote(self, symbol: str) -> Quote:
        data = await self._request("GET", f"/v2/products/{symbol}-USD/ticker")
        ticker = data.get("data", {})

        return Quote(
            symbol=symbol,
            bid=Decimal(ticker.get("bid", "0")),
            ask=Decimal(ticker.get("ask", "0")),
            last_price=Decimal(ticker.get("price", "0")),
            volume=Decimal(ticker.get("volume", "0")),
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
        limit: int = 100,
    ) -> Dict[str, List[Dict]]:
        timeframe_map = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }
        granularity = timeframe_map.get(timeframe, 86400)

        result = {}
        for symbol in symbols:
            params = {"granularity": str(granularity), "limit": str(limit)}
            if start:
                params["start"] = start.isoformat()
            if end:
                params["end"] = end.isoformat()

            data = await self._request(
                "GET", f"/v2/products/{symbol}-USD/candles", params=params
            )

            bars = []
            for candle in data:
                bars.append(
                    {
                        "timestamp": candle[0],
                        "low": candle[1],
                        "high": candle[2],
                        "open": candle[3],
                        "close": candle[4],
                        "volume": candle[5],
                    }
                )
            result[symbol] = bars

        return result
