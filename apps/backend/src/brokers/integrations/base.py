from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BrokerAccount:
    account_id: str
    account_name: str
    account_type: str
    currency: str
    cash_balance: Decimal
    portfolio_value: Decimal
    buying_power: Decimal
    daytrade_count: int = 0
    pattern_day_trader: bool = False
    trading_blocked: bool = False
    transfers_blocked: bool = False
    account_blocked: bool = False
    multiplier: str = "1"
    last_updated: Optional[datetime] = None


@dataclass
class BrokerPosition:
    symbol: str
    asset_id: str
    quantity: Decimal
    avg_entry_price: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pl: Decimal
    unrealized_pl_percent: Decimal
    side: str = "long"
    cost_basis: Decimal = Decimal("0")
    commission: Decimal = Decimal("0")
    external_position_id: str = ""
    metadata: Dict[str, Any] = None


@dataclass
class BrokerOrder:
    order_id: str
    symbol: str
    order_type: str
    side: str
    quantity: Decimal
    filled_quantity: Decimal = Decimal("0")
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trailing_amount: Optional[Decimal] = None
    trailing_percent: Optional[Decimal] = None
    time_in_force: str = "day"
    status: str = "pending"
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    avg_fill_price: Optional[Decimal] = None
    commission: Decimal = Decimal("0")
    parent_order_id: str = ""
    legs: List[Dict] = None


@dataclass
class BrokerTransaction:
    transaction_id: str
    transaction_type: str
    symbol: str
    quantity: Optional[Decimal]
    price: Optional[Decimal]
    total: Optional[Decimal]
    fee: Decimal
    currency: str
    status: str
    executed_at: Optional[datetime]
    external_transaction_id: str = ""
    order_id: str = ""
    notes: str = ""


@dataclass
class Quote:
    symbol: str
    bid: Optional[Decimal]
    ask: Optional[Decimal]
    bid_size: Optional[Decimal]
    ask_size: Optional[Decimal]
    last_price: Optional[Decimal]
    last_size: Optional[Decimal]
    volume: Optional[Decimal]
    timestamp: Optional[datetime]


class BrokerAPIError(Exception):
    def __init__(self, message: str, code: str = None, details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class RateLimitError(BrokerAPIError):
    pass


class AuthenticationError(BrokerAPIError):
    pass


class InsufficientFundsError(BrokerAPIError):
    pass


class OrderNotFoundError(BrokerAPIError):
    pass


class BaseBroker(ABC):
    broker_name: str = None
    broker_id: str = None

    def __init__(
        self,
        api_key: bytes,
        api_secret: bytes,
        passphrase: bytes = None,
        paper_trading: bool = False,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.paper_trading = paper_trading
        self._rate_limit_remaining: int = 0
        self._rate_limit_reset: Optional[datetime] = None
        self._session = None

    def _get_rate_limit_info(self) -> Dict[str, Any]:
        return {
            "remaining": self._rate_limit_remaining,
            "reset_at": self._rate_limit_reset,
        }

    def _update_rate_limit_info(
        self, remaining: int, reset_at: Optional[datetime] = None
    ):
        self._rate_limit_remaining = remaining
        self._rate_limit_reset = reset_at

    def _check_rate_limit(self) -> bool:
        if self._rate_limit_remaining <= 0:
            if self._rate_limit_reset and datetime.now() < self._rate_limit_reset:
                wait_seconds = (self._rate_limit_reset - datetime.now()).total_seconds()
                logger.warning(f"Rate limit exceeded. Waiting {wait_seconds} seconds")
                return False
        return True

    @abstractmethod
    def _create_session(self):
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        pass

    @abstractmethod
    async def get_account(self) -> BrokerAccount:
        pass

    @abstractmethod
    async def get_positions(self) -> List[BrokerPosition]:
        pass

    @abstractmethod
    async def get_orders(
        self,
        status: str = None,
        symbol: str = None,
        since: datetime = None,
        until: datetime = None,
    ) -> List[BrokerOrder]:
        pass

    @abstractmethod
    async def get_transactions(
        self,
        transaction_type: str = None,
        symbol: str = None,
        since: datetime = None,
        until: datetime = None,
    ) -> List[BrokerTransaction]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        pass

    @abstractmethod
    async def get_order(self, order_id: str) -> BrokerOrder:
        pass

    @abstractmethod
    async def modify_order(
        self,
        order_id: str,
        limit_price: Decimal = None,
        stop_price: Decimal = None,
        quantity: Decimal = None,
        time_in_force: str = None,
    ) -> BrokerOrder:
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        pass

    @abstractmethod
    async def get_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        pass

    @abstractmethod
    async def get_bars(
        self,
        symbols: List[str],
        timeframe: str = "1D",
        start: datetime = None,
        end: datetime = None,
        limit: int = 1000,
    ) -> Dict[str, List[Dict]]:
        pass

    async def sync_portfolio(self) -> Dict[str, Any]:
        account = await self.get_account()
        positions = await self.get_positions()
        orders = await self.get_orders(status="open")
        transactions = await self.get_transactions(since=None)

        return {
            "account": account,
            "positions": positions,
            "orders": orders,
            "transactions": transactions,
            "synced_at": datetime.now(),
        }

    def get_credentials_hash(self) -> str:
        import hashlib

        key_hash = hashlib.sha256(self.api_key).hexdigest()[:16]
        secret_hash = hashlib.sha256(self.api_secret).hexdigest()[:16]
        return f"{self.broker_id}:{key_hash}:{secret_hash}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.broker_name}, paper={self.paper_trading})>"
