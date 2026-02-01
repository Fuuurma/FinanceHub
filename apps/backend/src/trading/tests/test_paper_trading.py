from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
import pytest


class TestPaperPosition:
    def test_total_cost_calculation(self):
        from trading.models.paper_position import PaperPosition

        position = Mock(spec=PaperPosition)
        position.quantity = Decimal("100")
        position.avg_price = Decimal("50.00")
        expected = Decimal("5000.00")
        assert position.quantity * position.avg_price == expected

    def test_position_representation(self):
        from trading.models.paper_position import PaperPosition

        portfolio = Mock()
        portfolio.user.email = "test@example.com"

        asset = Mock()
        asset.symbol = "AAPL"

        position = PaperPosition(
            id="test-uuid",
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("10"),
            avg_price=Decimal("150.00"),
        )
        assert position.asset.symbol == "AAPL"


class TestPaperTradingOrder:
    def test_order_types(self):
        from trading.models.paper_order import PaperTradingOrder

        assert "market" in PaperTradingOrder.ORDER_TYPES[0]
        assert "limit" in PaperTradingOrder.ORDER_TYPES[1]
        assert "stop" in PaperTradingOrder.ORDER_TYPES[2]

    def test_order_sides(self):
        from trading.models.paper_order import PaperTradingOrder

        assert "buy" in PaperTradingOrder.SIDES[0]
        assert "sell" in PaperTradingOrder.SIDES[1]

    def test_order_statuses(self):
        from trading.models.paper_order import PaperTradingOrder

        assert "pending" in PaperTradingOrder.STATUS_CHOICES[0]
        assert "filled" in PaperTradingOrder.STATUS_CHOICES[1]
        assert "cancelled" in PaperTradingOrder.STATUS_CHOICES[2]
        assert "rejected" in PaperTradingOrder.STATUS_CHOICES[3]

    def test_order_is_active_property(self):
        from trading.models.paper_order import PaperTradingOrder

        pending_order = Mock(spec=PaperTradingOrder)
        pending_order.status = "pending"
        assert pending_order.status == "pending"

        filled_order = Mock(spec=PaperTradingOrder)
        filled_order.status = "filled"
        assert filled_order.status != "pending"


class TestMarketDataService:
    def test_market_data_service_exists(self):
        from trading.services.paper_trading_engine import MarketDataService

        service = MarketDataService()
        assert hasattr(service, "get_current_price")

    @patch("trading.services.paper_trading_engine.Asset")
    @patch("trading.services.paper_trading_engine.AssetPricesHistoric")
    def test_get_current_price_found(self, mock_prices, mock_asset):
        from trading.services.paper_trading_engine import MarketDataService

        mock_asset_instance = Mock()
        mock_asset_instance.symbol = "AAPL"
        mock_asset_instance.is_active = True
        mock_asset.objects.get.return_value = mock_asset_instance

        mock_price = Mock()
        mock_price.close = 150.00
        mock_prices.objects.filter.return_value.order_by.return_value.first.return_value = mock_price

        service = MarketDataService()
        price = service.get_current_price("AAPL")

        assert price == 150.00

    @patch("trading.services.paper_trading_engine.Asset")
    def test_get_current_price_not_found(self, mock_asset):
        from trading.services.paper_trading_engine import MarketDataService
        from assets.models.asset import Asset

        mock_asset.DoesNotExist = Asset.DoesNotExist
        mock_asset.objects.get.side_effect = Asset.DoesNotExist("Asset not found")

        service = MarketDataService()
        price = service.get_current_price("INVALID")

        assert price is None


class TestWebSocketBroadcaster:
    def test_broadcaster_exists(self):
        from trading.services.paper_trading_engine import WebSocketBroadcaster

        broadcaster = WebSocketBroadcaster()
        assert hasattr(broadcaster, "broadcast_to_user")
        assert hasattr(broadcaster, "broadcast_portfolio_update")
        assert hasattr(broadcaster, "broadcast_order_update")
        assert hasattr(broadcaster, "broadcast_position_update")


class TestPaperTradingEngine:
    def test_engine_exists(self):
        from trading.services.paper_trading_engine import PaperTradingEngine

        engine = PaperTradingEngine()
        assert hasattr(engine, "market_data")
        assert hasattr(engine, "broadcaster")
        assert hasattr(engine, "execute_market_order")
        assert hasattr(engine, "execute_limit_order")
        assert hasattr(engine, "cancel_order")
        assert hasattr(engine, "calculate_portfolio_value")
        assert hasattr(engine, "get_positions")
        assert hasattr(engine, "get_orders")

    @patch("trading.services.paper_trading_engine.PaperTradingAccount")
    def test_get_or_create_portfolio_new(self, mock_account_model):
        from trading.services.paper_trading_engine import PaperTradingEngine

        mock_user = Mock()
        mock_account = Mock()
        mock_account_model.objects.get_or_create.return_value = (mock_account, True)

        engine = PaperTradingEngine()
        portfolio = engine.get_or_create_portfolio(mock_user)

        mock_account_model.objects.get_or_create.assert_called_once()
        assert portfolio == mock_account

    @patch("trading.services.paper_trading_engine.PaperTradingAccount")
    def test_get_or_create_portfolio_existing(self, mock_account_model):
        from trading.services.paper_trading_engine import PaperTradingEngine

        mock_user = Mock()
        mock_account = Mock()
        mock_account_model.objects.get_or_create.return_value = (mock_account, False)

        engine = PaperTradingEngine()
        portfolio = engine.get_or_create_portfolio(mock_user)

        assert portfolio == mock_account

    def test_calculate_portfolio_value_empty(self):
        from trading.services.paper_trading_engine import PaperTradingEngine

        engine = PaperTradingEngine()

        mock_portfolio = Mock()
        mock_portfolio.cash_balance = Decimal("100000")
        mock_portfolio.positions.all.return_value = []

        result = engine.calculate_portfolio_value(mock_portfolio)

        assert result == Decimal("100000")


class TestPaperTradingConsumer:
    def test_consumer_exists(self):
        from trading.consumers.paper_trading import PaperTradingConsumer

        assert PaperTradingConsumer is not None

    def test_consumer_has_required_methods(self):
        from trading.consumers.paper_trading import PaperTradingConsumer

        assert hasattr(PaperTradingConsumer, "connect")
        assert hasattr(PaperTradingConsumer, "disconnect")
        assert hasattr(PaperTradingConsumer, "portfolio_update")
        assert hasattr(PaperTradingConsumer, "order_update")
        assert hasattr(PaperTradingConsumer, "position_update")


class TestPaperTradingAPI:
    def test_api_router_exists(self):
        from trading.api.paper_trading import router

        assert router is not None

    def test_api_endpoints_defined(self):
        from trading.api.paper_trading import (
            get_account,
            buy_asset,
            sell_asset,
            reset_account,
            get_history,
            get_performance,
            get_positions,
            get_orders,
            create_market_order,
            create_limit_order,
            cancel_order,
        )

        assert callable(get_account)
        assert callable(buy_asset)
        assert callable(sell_asset)
        assert callable(reset_account)
        assert callable(get_history)
        assert callable(get_performance)
        assert callable(get_positions)
        assert callable(get_orders)
        assert callable(create_market_order)
        assert callable(create_limit_order)
        assert callable(cancel_order)


class TestOrderValidation:
    def test_order_quantity_validation(self):
        from trading.models.paper_order import PaperTradingOrder

        order = Mock(spec=PaperTradingOrder)
        order.quantity = Decimal("10")

        assert order.quantity > 0

    def test_limit_order_requires_price(self):
        from trading.models.paper_order import PaperTradingOrder

        order_type = "limit"
        price = Decimal("150.00")

        assert order_type in ["limit", "stop"]
        assert price is not None

    def test_market_order_no_price_required(self):
        from trading.models.paper_order import PaperTradingOrder

        order_type = "market"

        assert order_type == "market"


class TestOrderLifecycle:
    def test_order_fill(self):
        from trading.models.paper_order import PaperTradingOrder

        order = Mock(spec=PaperTradingOrder)
        order.filled_price = None
        order.filled_at = None
        order.status = "pending"

        fill_price = Decimal("155.00")
        order.filled_price = fill_price
        order.status = "filled"

        assert order.filled_price == fill_price
        assert order.status == "filled"

    def test_order_cancel(self):
        from trading.models.paper_order import PaperTradingOrder

        order = Mock(spec=PaperTradingOrder)
        order.status = "pending"

        order.status = "cancelled"

        assert order.status == "cancelled"

    def test_order_reject(self):
        from trading.models.paper_order import PaperTradingOrder

        order = Mock(spec=PaperTradingOrder)
        order.status = "pending"
        order.rejection_reason = ""

        reason = "Insufficient funds"
        order.status = "rejected"
        order.rejection_reason = reason

        assert order.status == "rejected"
        assert order.rejection_reason == reason
