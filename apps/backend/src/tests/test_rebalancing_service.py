"""
Unit tests for the RebalancingService.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from investments.services.rebalancing_service import RebalancingService
from investments.models.rebalancing import (
    TargetAllocation,
    PortfolioDrift,
    RebalancingSuggestion,
    RebalancingSession,
    TaxLot,
)


class MockAsset:
    """Mock Asset for testing."""

    def __init__(self, asset_type="stock", symbol="AAPL"):
        self.asset_type = asset_type
        self.symbol = symbol


class MockHolding:
    """Mock Holding for testing."""

    def __init__(
        self,
        asset,
        quantity=Decimal("10"),
        current_value=Decimal("2000"),
        current_price=Decimal("200"),
        purchase_date=None,
        purchase_price=None,
        unrealized_pnl=None,
    ):
        self.asset = asset
        self.quantity = quantity
        self.current_value = current_value
        self.current_price = current_price
        self.purchase_date = purchase_date
        self.purchase_price = purchase_price
        self.unrealized_pnl = unrealized_pnl


class MockPortfolio:
    """Mock Portfolio for testing."""

    def __init__(self, holdings=None):
        self.holdings = MagicMock()
        self.holdings.select_related = MagicMock(return_value=self)
        self.holdings.all = MagicMock(return_value=holdings or [])
        self.id = "test-portfolio-id"
        self.name = "Test Portfolio"


class TestRebalancingServiceUnit:
    """Unit tests for RebalancingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_portfolio = MockPortfolio()
        self.service = RebalancingService(self.mock_portfolio)

    def test_get_asset_class_stock(self):
        """Test asset class classification for stocks."""
        stock = MockAsset(asset_type="stock", symbol="AAPL")
        result = self.service._get_asset_class(stock)
        assert result == "stock"

    def test_get_asset_class_bond(self):
        """Test asset class classification for bonds."""
        bond = MockAsset(asset_type="bond", symbol="BND")
        result = self.service._get_asset_class(bond)
        assert result == "bond"

    def test_get_asset_class_crypto(self):
        """Test asset class classification for crypto."""
        crypto = MockAsset(asset_type="crypto", symbol="BTC")
        result = self.service._get_asset_class(crypto)
        assert result == "crypto"

    def test_get_asset_class_etf(self):
        """Test asset class classification for ETFs."""
        etf = MockAsset(asset_type="etf", symbol="SPY")
        result = self.service._get_asset_class(etf)
        assert result == "etf"

    def test_get_asset_class_real_estate(self):
        """Test asset class classification for real estate."""
        re = MockAsset(asset_type="real_estate", symbol="VNQ")
        result = self.service._get_asset_class(re)
        assert result == "real_estate"

    def test_get_asset_class_cash(self):
        """Test asset class classification for cash."""
        cash = MockAsset(asset_type="cash", symbol="CASH")
        result = self.service._get_asset_class(cash)
        assert result == "cash"

    def test_get_asset_class_commodity(self):
        """Test asset class classification for commodities."""
        gold = MockAsset(asset_type="commodity", symbol="GLD")
        result = self.service._get_asset_class(gold)
        assert result == "commodity"

    def test_get_asset_class_unknown(self):
        """Test asset class classification for unknown types."""
        unknown = MockAsset(asset_type="unknown", symbol="XYZ")
        result = self.service._get_asset_class(unknown)
        assert result == "other"

    def test_get_asset_class_none(self):
        """Test asset class classification for None asset."""
        result = self.service._get_asset_class(None)
        assert result == "other"

    def test_calculate_priority_high(self):
        """Test priority calculation for high drift."""
        result = self.service._calculate_priority(Decimal("20"))
        assert result == "HIGH"

    def test_calculate_priority_medium(self):
        """Test priority calculation for medium drift."""
        result = self.service._calculate_priority(Decimal("10"))
        assert result == "MEDIUM"

    def test_calculate_priority_low(self):
        """Test priority calculation for low drift."""
        result = self.service._calculate_priority(Decimal("5"))
        assert result == "LOW"

    def test_estimate_tax_implication_loss(self):
        """Test tax implication estimation for loss."""
        holding = MockHolding(unrealized_pnl=Decimal("-500"))
        result = self.service._estimate_tax_implication(holding)
        assert result == "LOSS"

    def test_estimate_tax_implication_gain(self):
        """Test tax implication estimation for gain."""
        holding = MockHolding(unrealized_pnl=Decimal("500"))
        result = self.service._estimate_tax_implication(holding)
        assert result == "GAIN"

    def test_estimate_tax_implication_neutral(self):
        """Test tax implication estimation for neutral position."""
        holding = MockHolding(unrealized_pnl=Decimal("0"))
        result = self.service._estimate_tax_implication(holding)
        assert result == "NEUTRAL"

    def test_estimate_tax_implication_none(self):
        """Test tax implication estimation for None holding."""
        result = self.service._estimate_tax_implication(None)
        assert result == "NEUTRAL"

    def test_get_tolerance_with_target(self):
        """Test tolerance retrieval with existing target."""
        with patch(
            "investments.services.rebalancing_service.TargetAllocation"
        ) as mock_target:
            mock_target.objects.get.return_value.tolerance_percentage = Decimal("3.00")
            result = self.service._get_tolerance("stock")
            assert result == Decimal("3.00")

    def test_get_tolerance_without_target(self):
        """Test tolerance retrieval without existing target."""
        with patch(
            "investments.services.rebalancing_service.TargetAllocation"
        ) as mock_target:
            mock_target.objects.get.side_effect = TargetAllocation.DoesNotExist
            result = self.service._get_tolerance("stock")
            assert result == Decimal("5.00")

    def test_get_holding_for_class_found(self):
        """Test finding holding for asset class."""
        stock = MockAsset(asset_type="stock", symbol="AAPL")
        holding = MockHolding(asset=stock)
        holdings = [holding]

        result = self.service._get_holding_for_class(holdings, "stock")
        assert result == holding

    def test_get_holding_for_class_not_found(self):
        """Test finding holding when not found."""
        stock = MockAsset(asset_type="stock", symbol="AAPL")
        holding = MockHolding(asset=stock)
        holdings = [holding]

        result = self.service._get_holding_for_class(holdings, "crypto")
        assert result is None

    def test_get_current_allocation_empty(self):
        """Test current allocation calculation with no holdings."""
        self.mock_portfolio.holdings.all.return_value = []

        with patch.object(self.service, "_get_asset_class", return_value="stock"):
            result = self.service.get_current_allocation()
            assert result == {}


class TestRebalancingServiceIntegration:
    """Integration tests for RebalancingService."""

    def test_get_drift_status_structure(self):
        """Test drift status response structure."""
        mock_portfolio = MockPortfolio()
        service = RebalancingService(mock_portfolio)

        with patch.object(
            service,
            "get_current_allocation",
            return_value={
                "stock": {"value": Decimal("6000"), "percentage": Decimal("60")},
                "bond": {"value": Decimal("4000"), "percentage": Decimal("40")},
            },
        ):
            with patch.object(
                service,
                "get_target_allocation",
                return_value={
                    "stock": Decimal("50"),
                    "bond": Decimal("50"),
                },
            ):
                with patch.object(service, "_get_tolerance", return_value=Decimal("5")):
                    result = service.get_drift_status()

        assert "needs_rebalancing" in result
        assert "drifts" in result
        assert "checked_at" in result
        assert isinstance(result["drifts"], list)

    def test_what_if_analysis_valid(self):
        """Test what-if analysis with valid allocation."""
        mock_portfolio = MockPortfolio()
        service = RebalancingService(mock_portfolio)

        stock = MockAsset(asset_type="stock", symbol="AAPL")
        holding = MockHolding(asset=stock, quantity=Decimal("10"))

        with patch.object(
            service,
            "get_current_allocation",
            return_value={
                "stock": {"value": Decimal("8000"), "percentage": Decimal("80")},
            },
        ):
            result = service.what_if_analysis(
                {
                    "stock": Decimal("60"),
                    "bond": Decimal("40"),
                }
            )

        assert result["valid"] is True
        assert "trades" in result
        assert "total_trades_needed" in result

    def test_what_if_analysis_invalid_total(self):
        """Test what-if analysis with invalid total allocation."""
        mock_portfolio = MockPortfolio()
        service = RebalancingService(mock_portfolio)

        with patch.object(service, "get_current_allocation", return_value={}):
            result = service.what_if_analysis(
                {
                    "stock": Decimal("60"),
                    "bond": Decimal("50"),
                }
            )

        assert result["valid"] is False
        assert "error" in result
        assert "100%" in result["error"]


class TestTaxImplicationEstimation:
    """Tests for tax implication estimation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_portfolio = MockPortfolio()
        self.service = RebalancingService(self.mock_portfolio)

    def test_significant_loss_priority(self):
        """Test that significant drift gets high priority."""
        result = self.service._calculate_priority(Decimal("16"))
        assert result == "HIGH"

    def test_moderate_drift_priority(self):
        """Test that moderate drift gets medium priority."""
        result = self.service._calculate_priority(Decimal("9"))
        assert result == "MEDIUM"

    def test_small_drift_priority(self):
        """Test that small drift gets low priority."""
        result = self.service._calculate_priority(Decimal("4"))
        assert result == "LOW"

    def test_boundary_drift_priority(self):
        """Test boundary conditions for priority calculation."""
        assert self.service._calculate_priority(Decimal("15")) == "HIGH"
        assert self.service._calculate_priority(Decimal("8")) == "MEDIUM"
        assert self.service._calculate_priority(Decimal("5")) == "LOW"


class TestAssetClassMapping:
    """Tests for asset class mapping functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_portfolio = MockPortfolio()
        self.service = RebalancingService(self.mock_portfolio)

    @pytest.mark.parametrize(
        "asset_type,expected_class",
        [
            ("stock", "stock"),
            ("equity", "stock"),
            ("bond", "bond"),
            ("fixed_income", "bond"),
            ("crypto", "crypto"),
            ("cryptocurrency", "crypto"),
            ("etf", "etf"),
            ("fund", "etf"),
            ("real_estate", "real_estate"),
            ("reit", "real_estate"),
            ("cash", "cash"),
            ("money_market", "cash"),
            ("commodity", "commodity"),
            ("gold", "commodity"),
            ("silver", "commodity"),
            ("unknown", "other"),
        ],
    )
    def test_asset_class_mapping(self, asset_type, expected_class):
        """Test that various asset types map to correct classes."""
        asset = MockAsset(asset_type=asset_type)
        result = self.service._get_asset_class(asset)
        assert result == expected_class
