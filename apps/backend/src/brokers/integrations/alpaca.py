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


class AlpacaBroker(BaseBroker):
    broker_name = "Alpaca"
    broker_id = "alpaca"

    BASE_URLS = {
        "paper": "https://paper-api.alpaca.markets",
        "live": "https://api.alpaca.markets",
    }

    DATA_URL = "https://data.alpaca.markets"

    def __init__(
        self,
        api_key: bytes,
        api_secret: bytes,
        passphrase: bytes = None,
        paper_trading: bool = True,
    ):
        super().__init__(api_key, api_secret, passphrase, paper_trading)
        self.base_url = self.BASE_URLS["paper" if paper_trading else "live"]
        self.data_url = self.DATA_URL
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
            self._session = aiohttp.ClientSession(
                headers={
                    "APCA-API-KEY-ID": self._get_api_key(),
                    "APCA-API-SECRET-KEY": self._get_api_secret(),
                    "APCA-API-PASSPHRASE": self._get_passphrase(),
                }
            )

    def _sign_request(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        message = timestamp + method + path + body
        signature = hmac.new(
            self._get_api_secret().encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return {
            "APCA-API-SIGN": signature,
            "APCA-API-TIMESTAMP": timestamp,
        }

    async def _request(
        self, method: str, path: str, body: str = "", base_url: str = None
    ) -> Dict[str, Any]:
        self._create_session()
        url = (base_url or self.base_url) + path
        headers = {"Content-Type": "application/json"}
        headers.update(self._sign_request(method, path, body))

        for attempt in range(3):
            try:
                async with self._session.request(
                    method, url, data=body if body else None, headers=headers
                ) as response:
                    if response.status == 429:
                        reset_after = response.headers.get("Retry-After", "60")
                        self._update_rate_limit_info(
                            0, datetime.now() + timedelta(seconds=int(reset_after))
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

                    remaining = response.headers.get("X-RateLimit-Remaining")
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
            await self._request("GET", "/v2/account")
            return True
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Alpaca connection test failed: {e}")
            return False

    async def get_account(self) -> BrokerAccount:
        data = await self._request("GET", "/v2/account")
        return BrokerAccount(
            account_id=data.get("account_number", ""),
            account_name=f"Alpaca {'Paper' if self.paper_trading else 'Live'}",
            account_type="paper" if self.paper_trading else "live",
            currency=data.get("currency", "USD"),
            cash_balance=Decimal(data.get("cash", "0")),
            portfolio_value=Decimal(data.get("portfolio_value", "0")),
            buying_power=Decimal(data.get("buying_power", "0")),
            daytrade_count=int(data.get("daytrade_count", 0)),
            pattern_day_trader=data.get("pattern_day_trader", False),
            trading_blocked=data.get("trading_blocked", False),
            transfers_blocked=data.get("transfers_blocked", False),
            account_blocked=data.get("account_blocked", False),
            multiplier=data.get("multiplier", "1"),
            last_updated=datetime.now(),
        )

    async def get_positions(self) -> List[BrokerPosition]:
        positions = await self._request("GET", "/v2/positions")
        result = []
        for pos in positions:
            qty = Decimal(pos.get("qty", "0"))
            avg_entry = Decimal(pos.get("avg_entry_price", "0"))
            current_price = Decimal(pos.get("current_price", "0"))
            market_value = Decimal(pos.get("market_value", "0"))
            unrealized_pl = Decimal(pos.get("unrealized_pl", "0"))
            cost_basis = Decimal(pos.get("cost_basis", "0"))

            unrealized_pl_percent = Decimal("0")
            if cost_basis > 0:
                unrealized_pl_percent = (unrealized_pl / cost_basis) * 100

            result.append(
                BrokerPosition(
                    symbol=pos.get("symbol", ""),
                    asset_id=pos.get("asset_id", ""),
                    quantity=qty,
                    avg_entry_price=avg_entry,
                    current_price=current_price,
                    market_value=market_value,
                    unrealized_pl=unrealized_pl,
                    unrealized_pl_percent=unrealized_pl_percent,
                    side=pos.get("side", "long"),
                    cost_basis=cost_basis,
                    commission=Decimal(pos.get("commission", "0")),
                    external_position_id=pos.get("id", ""),
                )
            )
        return result

    def _map_order_status(self, alpaca_status: str) -> str:
        status_map = {
            "pending_new": "pending_new",
            "accepted": "accepted",
            "pending_cancel": "pending_cancel",
            "partial_filled": "partial_filled",
            "filled": "filled",
            "done": "filled",
            "canceled": "canceled",
            "expired": "expired",
            "rejected": "rejected",
        }
        return status_map.get(alpaca_status, "pending")

    async def get_orders(
        self,
        status: str = "all",
        symbol: str = None,
        since: datetime = None,
        until: datetime = None,
    ) -> List[BrokerOrder]:
        params = []
        if status and status != "all":
            params.append(f"status={status}")
        if symbol:
            params.append(f"symbol={symbol}")
        query = "?" + "&".join(params) if params else ""
        orders = await self._request("GET", f"/v2/orders{query}")

        result = []
        for order in orders:

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
                    symbol=order.get("symbol", ""),
                    order_type=order.get("type", "market"),
                    side=order.get("side", "buy"),
                    quantity=Decimal(order.get("qty", "0")),
                    filled_quantity=Decimal(order.get("filled_qty", "0")),
                    limit_price=Decimal(order.get("limit_price", "0"))
                    if order.get("limit_price")
                    else None,
                    stop_price=Decimal(order.get("stop_price", "0"))
                    if order.get("stop_price")
                    else None,
                    time_in_force=order.get("time_in_force", "day"),
                    status=self._map_order_status(order.get("status", "")),
                    submitted_at=parse_dt(order.get("submitted_at")),
                    filled_at=parse_dt(order.get("filled_at")),
                    avg_fill_price=Decimal(order.get("filled_avg_price", "0"))
                    if order.get("filled_avg_price")
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
        params = []
        if transaction_type:
            params.append(f"type={transaction_type}")
        query = "?" + "&".join(params) if params else ""
        transactions = await self._request("GET", f"/v2/activities{query}")

        result = []
        for tx in transactions:

            def parse_dt(val):
                if not val:
                    return None
                try:
                    return datetime.fromisoformat(val.replace("Z", "+00:00"))
                except:
                    return None

            result.append(
                BrokerTransaction(
                    transaction_id=tx.get("id", ""),
                    transaction_type=tx.get("activity_type", "other"),
                    symbol=tx.get("symbol", ""),
                    quantity=Decimal(tx.get("qty", "0")) if tx.get("qty") else None,
                    price=Decimal(tx.get("price", "0")) if tx.get("price") else None,
                    total=Decimal(tx.get("net_amount", "0"))
                    if tx.get("net_amount")
                    else None,
                    fee=Decimal(tx.get("commission", "0")),
                    currency=tx.get("currency", "USD"),
                    status="completed",
                    executed_at=parse_dt(tx.get("transaction_time")),
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
        time_in_force: str = "day",
        trailing_amount: Decimal = None,
        trailing_percent: Decimal = None,
    ) -> BrokerOrder:
        order_data = {
            "symbol": symbol,
            "qty": str(quantity),
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }
        if limit_price is not None:
            order_data["limit_price"] = str(limit_price)
        if stop_price is not None:
            order_data["stop_price"] = str(stop_price)

        body = json.dumps(order_data)
        result = await self._request("POST", "/v2/orders", body)

        def parse_dt(val):
            if not val:
                return None
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except:
                return None

        return BrokerOrder(
            order_id=result.get("id", ""),
            symbol=result.get("symbol", ""),
            order_type=result.get("type", "market"),
            side=result.get("side", "buy"),
            quantity=Decimal(result.get("qty", "0")),
            filled_quantity=Decimal(result.get("filled_qty", "0")),
            limit_price=Decimal(result.get("limit_price", "0"))
            if result.get("limit_price")
            else None,
            stop_price=Decimal(result.get("stop_price", "0"))
            if result.get("stop_price")
            else None,
            time_in_force=result.get("time_in_force", "day"),
            status=self._map_order_status(result.get("status", "")),
            submitted_at=parse_dt(result.get("submitted_at")),
            avg_fill_price=Decimal(result.get("filled_avg_price", "0"))
            if result.get("filled_avg_price")
            else None,
        )

    async def cancel_order(self, order_id: str) -> bool:
        try:
            await self._request("DELETE", f"/v2/orders/{order_id}")
            return True
        except OrderNotFoundError:
            return False

    async def get_order(self, order_id: str) -> BrokerOrder:
        result = await self._request("GET", f"/v2/orders/{order_id}")

        def parse_dt(val):
            if not val:
                return None
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except:
                return None

        return BrokerOrder(
            order_id=result.get("id", ""),
            symbol=result.get("symbol", ""),
            order_type=result.get("type", "market"),
            side=result.get("side", "buy"),
            quantity=Decimal(result.get("qty", "0")),
            filled_quantity=Decimal(result.get("filled_qty", "0")),
            limit_price=Decimal(result.get("limit_price", "0"))
            if result.get("limit_price")
            else None,
            stop_price=Decimal(result.get("stop_price", "0"))
            if result.get("stop_price")
            else None,
            time_in_force=result.get("time_in_force", "day"),
            status=self._map_order_status(result.get("status", "")),
            submitted_at=parse_dt(result.get("submitted_at")),
            filled_at=parse_dt(result.get("filled_at")),
            avg_fill_price=Decimal(result.get("filled_avg_price", "0"))
            if result.get("filled_avg_price")
            else None,
        )

    async def get_quote(self, symbol: str) -> Optional[Quote]:
        url = f"{self.data_url}/v2/latest/quote?symbols={symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "APCA-API-KEY-ID": self._get_api_key(),
                    "APCA-API-SECRET-KEY": self._get_api_secret(),
                },
            ) as response:
                data = await response.json()
        quote_data = data.get("quote", {})
        return Quote(
            symbol=symbol,
            bid=Decimal(str(quote_data.get("bp", 0))) if quote_data.get("bp") else None,
            ask=Decimal(str(quote_data.get("ap", 0))) if quote_data.get("ap") else None,
            bid_size=Decimal(str(quote_data.get("bs", 0)))
            if quote_data.get("bs")
            else None,
            ask_size=Decimal(str(quote_data.get("as", 0)))
            if quote_data.get("as")
            else None,
            last_price=None,
            last_size=None,
            volume=None,
            timestamp=None,
        )

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        if not symbols:
            return {}
        url = f"{self.data_url}/v2/latest/quote?symbols={','.join(symbols)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "APCA-API-KEY-ID": self._get_api_key(),
                    "APCA-API-SECRET-KEY": self._get_api_secret(),
                },
            ) as response:
                data = await response.json()
        result = {}
        for symbol, quote_data in data.get("quotes", {}).items():
            result[symbol] = Quote(
                symbol=symbol,
                bid=Decimal(str(quote_data.get("bp", 0)))
                if quote_data.get("bp")
                else None,
                ask=Decimal(str(quote_data.get("ap", 0)))
                if quote_data.get("ap")
                else None,
                bid_size=Decimal(str(quote_data.get("bs", 0)))
                if quote_data.get("bs")
                else None,
                ask_size=Decimal(str(quote_data.get("as", 0)))
                if quote_data.get("as")
                else None,
                last_price=None,
                last_size=None,
                volume=None,
                timestamp=None,
            )
        return result

    async def get_bars(
        self,
        symbols: List[str],
        timeframe: str = "1D",
        start: datetime = None,
        end: datetime = None,
        limit: int = 1000,
    ) -> Dict[str, List[Dict]]:
        params = {"timeframe": timeframe, "limit": str(limit)}
        if start:
            params["start"] = start.isoformat()
        if end:
            params["end"] = end.isoformat()
        url = f"{self.data_url}/v2/bars/{'&'.join(symbols)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                headers={
                    "APCA-API-KEY-ID": self._get_api_key(),
                    "APCA-API-SECRET-KEY": self._get_api_secret(),
                },
            ) as response:
                data = await response.json()
        return data.get("bars", {})
