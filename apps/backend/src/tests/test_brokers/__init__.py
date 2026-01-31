"""
Tests for Broker API Integration (C-030)
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import json

from brokers.models import (
    BrokerConnection,
    BrokerPosition,
    BrokerTransaction,
    BrokerOrder,
)
from brokers.services.broker_service import (
    BrokerService,
    EncryptionService,
    BROKER_CLASSES,
)
from brokers.integrations import AlpacaBroker, BinanceBroker, CoinbaseBroker, BaseBroker


class TestEncryptionService:
    """Test credential encryption/decryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypted data can be decrypted back to original."""
        original_data = b"test_api_key_12345"
        encrypted = EncryptionService.encrypt(original_data)
        decrypted = EncryptionService.decrypt(encrypted)
        assert decrypted == original_data

    def test_encrypt_produces_different_output(self):
        """Test that encryption produces different output each time."""
        original_data = b"same_key"
        encrypted1 = EncryptionService.encrypt(original_data)
        encrypted2 = EncryptionService.encrypt(original_data)
        assert encrypted1 != encrypted2


class TestBrokerClasses:
    """Test broker class registration."""

    def test_alpaca_registered(self):
        """Alpaca broker should be registered."""
        assert "alpaca" in BROKER_CLASSES
        assert BROKER_CLASSES["alpaca"] == AlpacaBroker

    def test_binance_registered(self):
        """Binance broker should be registered."""
        assert "binance" in BROKER_CLASSES
        assert BROKER_CLASSES["binance"] == BinanceBroker

    def test_coinbase_registered(self):
        """Coinbase broker should be registered."""
        assert "coinbase" in BROKER_CLASSES
        assert BROKER_CLASSES["coinbase"] == CoinbaseBroker

    def test_get_broker_class_returns_correct_class(self):
        """Test that get_broker_class returns correct class."""
        assert BrokerService.get_broker_class("alpaca") == AlpacaBroker
        assert BrokerService.get_broker_class("binance") == BinanceBroker
        assert BrokerService.get_broker_class("coinbase") == CoinbaseBroker

    def test_get_broker_class_returns_none_for_unknown(self):
        """Test that unknown broker returns None."""
        assert BrokerService.get_broker_class("unknown") is None


class TestBaseBrokerDataclasses:
    """Test base broker dataclasses."""

    def test_broker_account_creation(self):
        """Test BrokerAccount dataclass creation."""
        account = BrokerAccount(
            account_id="test123",
            account_name="Test Account",
            account_type="paper",
            currency="USD",
            cash_balance=Decimal("10000"),
            portfolio_value=Decimal("15000"),
            buying_power=Decimal("20000"),
        )
        assert account.account_id == "test123"
        assert account.cash_balance == Decimal("10000")
        assert account.portfolio_value == Decimal("15000")

    def test_broker_position_creation(self):
        """Test BrokerPosition dataclass creation."""
        position = BrokerPosition(
            symbol="AAPL",
            asset_id="aapl",
            quantity=Decimal("10"),
            avg_entry_price=Decimal("150.00"),
            current_price=Decimal("155.00"),
            market_value=Decimal("1550"),
            unrealized_pl=Decimal("50"),
            unrealized_pl_percent=Decimal("3.33"),
        )
        assert position.symbol == "AAPL"
        assert position.quantity == Decimal("10")
        assert position.side == "long"

    def test_broker_order_creation(self):
        """Test BrokerOrder dataclass creation."""
        order = BrokerOrder(
            order_id="order123",
            symbol="AAPL",
            order_type="limit",
            side="buy",
            quantity=Decimal("10"),
            limit_price=Decimal("150.00"),
            status="pending_new",
        )
        assert order.order_id == "order123"
        assert order.order_type == "limit"
        assert order.status == "pending_new"

    def test_broker_transaction_creation(self):
        """Test BrokerTransaction dataclass creation."""
        transaction = BrokerTransaction(
            transaction_id="tx123",
            transaction_type="buy",
            symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("150.00"),
            total=Decimal("1500"),
            fee=Decimal("1.50"),
            currency="USD",
            status="completed",
            executed_at=datetime.now(),
        )
        assert transaction.transaction_type == "buy"
        assert transaction.total == Decimal("1500")

    def test_quote_creation(self):
        """Test Quote dataclass creation."""
        quote = Quote(
            symbol="AAPL",
            bid=Decimal("154.50"),
            ask=Decimal("154.60"),
            last_price=Decimal("154.55"),
            volume=Decimal("1000000"),
        )
        assert quote.symbol == "AAPL"
        assert quote.bid == Decimal("154.50")
        assert quote.ask == Decimal("154.60")


class TestBrokerService:
    """Test BrokerService methods."""

    @pytest.mark.asyncio
    async def test_get_broker_class_valid(self):
        """Test getting valid broker class."""
        result = BrokerService.get_broker_class("alpaca")
        assert result == AlpacaBroker

    @pytest.mark.asyncio
    async def test_get_broker_class_invalid(self):
        """Test getting invalid broker class returns None."""
        result = BrokerService.get_broker_class("invalid_broker")
        assert result is None


class TestAlpacaBroker:
    """Test AlpacaBroker integration."""

    def test_alpaca_broker_initialization(self):
        """Test Alpaca broker can be initialized."""
        broker = AlpacaBroker(
            api_key=b"test_key",
            api_secret=b"test_secret",
            passphrase=b"test_passphrase",
            paper_trading=True,
        )
        assert broker.broker_name == "Alpaca"
        assert broker.broker_id == "alpaca"
        assert broker.paper_trading is True
        assert "paper-api" in broker.base_url

    def test_alpaca_live_mode(self):
        """Test Alpaca broker in live mode."""
        broker = AlpacaBroker(
            api_key=b"test_key",
            api_secret=b"test_secret",
            paper_trading=False,
        )
        assert broker.paper_trading is False
        assert "api.alpaca.markets" in broker.base_url


class TestBinanceBroker:
    """Test BinanceBroker integration."""

    def test_binance_broker_initialization(self):
        """Test Binance broker can be initialized."""
        broker = BinanceBroker(
            api_key=b"test_key",
            api_secret=b"test_secret",
            paper_trading=True,
        )
        assert broker.broker_name == "Binance"
        assert broker.broker_id == "binance"
        assert broker.paper_trading is True
        assert "testnet" in broker.base_url

    def test_binance_live_mode(self):
        """Test Binance broker in live mode."""
        broker = BinanceBroker(
            api_key=b"test_key",
            api_secret=b"test_secret",
            paper_trading=False,
        )
        assert broker.paper_trading is False
        assert broker.base_url == "https://api.binance.com"


class TestCoinbaseBroker:
    """Test CoinbaseBroker integration."""

    def test_coinbase_broker_initialization(self):
        """Test Coinbase broker can be initialized."""
        broker = CoinbaseBroker(
            api_key=b"test_key",
            api_secret=b"test_secret",
            passphrase=b"test_passphrase",
            paper_trading=False,
        )
        assert broker.broker_name == "Coinbase"
        assert broker.broker_id == "coinbase"
        assert broker.api_version == "2024-01-01"


class TestBrokerConnectionModel:
    """Test BrokerConnection model fields."""

    def test_broker_connection_fields(self):
        """Test BrokerConnection has required fields."""
        assert hasattr(BrokerConnection, "broker")
        assert hasattr(BrokerConnection, "account_type")
        assert hasattr(BrokerConnection, "api_key_encrypted")
        assert hasattr(BrokerConnection, "api_secret_encrypted")
        assert hasattr(BrokerConnection, "status")
        assert hasattr(BrokerConnection, "sync_enabled")

    def test_broker_connection_choices(self):
        """Test BrokerConnection has correct choices."""
        broker_choices = [choice[0] for choice in BrokerConnection.BROKER_CHOICES]
        assert "alpaca" in broker_choices
        assert "binance" in broker_choices
        assert "coinbase" in broker_choices

        account_types = [choice[0] for choice in BrokerConnection.ACCOUNT_TYPE_CHOICES]
        assert "paper" in account_types
        assert "live" in account_types


class TestBrokerPositionModel:
    """Test BrokerPosition model fields."""

    def test_broker_position_fields(self):
        """Test BrokerPosition has required fields."""
        assert hasattr(BrokerPosition, "symbol")
        assert hasattr(BrokerPosition, "quantity")
        assert hasattr(BrokerPosition, "avg_entry_price")
        assert hasattr(BrokerPosition, "current_price")
        assert hasattr(BrokerPosition, "unrealized_pl")


class TestBrokerOrderModel:
    """Test BrokerOrder model fields."""

    def test_broker_order_fields(self):
        """Test BrokerOrder has required fields."""
        assert hasattr(BrokerOrder, "order_type")
        assert hasattr(BrokerOrder, "side")
        assert hasattr(BrokerOrder, "quantity")
        assert hasattr(BrokerOrder, "status")
        assert hasattr(BrokerOrder, "time_in_force")


class TestBrokerTransactionModel:
    """Test BrokerTransaction model fields."""

    def test_broker_transaction_fields(self):
        """Test BrokerTransaction has required fields."""
        assert hasattr(BrokerTransaction, "transaction_type")
        assert hasattr(BrokerTransaction, "symbol")
        assert hasattr(BrokerTransaction, "quantity")
        assert hasattr(BrokerTransaction, "price")
        assert hasattr(BrokerTransaction, "total")


class TestIntegrationCompleteness:
    """Test that all required integrations are complete."""

    def test_all_required_brokers_implemented(self):
        """Verify all required brokers are implemented."""
        required_brokers = ["alpaca", "binance", "coinbase"]
        for broker in required_brokers:
            assert broker in BROKER_CLASSES, f"{broker} not implemented"
            broker_class = BROKER_CLASSES[broker]
            assert hasattr(broker_class, "test_connection")
            assert hasattr(broker_class, "get_account")
            assert hasattr(broker_class, "get_positions")
            assert hasattr(broker_class, "get_orders")
            assert hasattr(broker_class, "get_transactions")
            assert hasattr(broker_class, "place_order")
            assert hasattr(broker_class, "cancel_order")
            assert hasattr(broker_class, "get_quote")

    def test_broker_has_required_methods(self):
        """Test that BaseBroker has all required abstract methods."""
        required_methods = [
            "test_connection",
            "get_account",
            "get_positions",
            "get_orders",
            "get_transactions",
            "place_order",
            "cancel_order",
            "get_order",
            "modify_order",
            "get_quote",
            "get_quotes",
            "get_bars",
        ]
        for method in required_methods:
            assert hasattr(BaseBroker, method), f"{method} not found in BaseBroker"
            assert callable(getattr(BaseBroker, method)), f"{method} is not callable"


# Run tests with: pytest apps/backend/src/tests/test_brokers/ -v
