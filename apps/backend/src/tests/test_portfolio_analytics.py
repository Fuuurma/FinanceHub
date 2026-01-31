"""
Tests for Portfolio Analytics Service
Tests sector allocation, geographic allocation, concentration risk, and other analytics
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import django

django.setup()

from investments.services.analytics_service import (
    PortfolioAnalyticsService,
    get_analytics_service,
)
from investments.models.portfolio_analytics import (
    PortfolioSectorAllocation,
    PortfolioGeographicAllocation,
    PortfolioAssetClassAllocation,
)


class TestPortfolioAnalyticsService:
    """Test PortfolioAnalyticsService class."""

    @pytest.fixture
    def service(self):
        return PortfolioAnalyticsService()

    @pytest.fixture
    def mock_portfolio(self):
        portfolio = Mock()
        portfolio.id = 1
        portfolio.name = "Test Portfolio"
        return portfolio

    @pytest.fixture
    def mock_holdings(self):
        """Create mock holdings with assets."""
        holdings = []

        assets_data = [
            (
                "AAPL",
                "Technology",
                "United States",
                "stock",
                Decimal("150.00"),
                Decimal("100"),
            ),
            (
                "MSFT",
                "Technology",
                "United States",
                "stock",
                Decimal("350.00"),
                Decimal("50"),
            ),
            (
                "GOOGL",
                "Technology",
                "United States",
                "stock",
                Decimal("140.00"),
                Decimal("100"),
            ),
            (
                "JPM",
                "Financial Services",
                "United States",
                "stock",
                Decimal("170.00"),
                Decimal("100"),
            ),
            (
                "JNJ",
                "Healthcare",
                "United States",
                "stock",
                Decimal("160.00"),
                Decimal("100"),
            ),
        ]

        for symbol, sector, country, asset_class, price, quantity in assets_data:
            asset = Mock()
            asset.symbol = symbol
            asset.name = symbol
            asset.sector = sector
            asset.country = country
            asset.asset_type = asset_class
            asset.last_price = price

            holding = Mock()
            holding.asset = asset
            holding.quantity = quantity
            holding.current_value = price * quantity
            holdings.append(holding)

        return holdings

    def test_get_asset_sector_known_symbol(self, service):
        """Test getting sector for known symbol."""
        asset = Mock()
        asset.symbol = "AAPL"
        asset.asset_type = None

        assert service.get_asset_sector(asset) == "Technology"

    def test_get_asset_sector_unknown_symbol(self, service):
        """Test getting sector for unknown symbol."""
        asset = Mock()
        asset.symbol = "UNKNOWN"
        asset.asset_type = "bond"

        result = service.get_asset_sector(asset)
        assert result == "Bond"

    def test_get_asset_country_known_symbol(self, service):
        """Test getting country for known symbol."""
        asset = Mock()
        asset.symbol = "AAPL"
        asset.exchange = None

        assert service.get_asset_country(asset) == "United States"

    def test_get_asset_country_unknown_symbol(self, service):
        """Test getting country for unknown symbol."""
        asset = Mock()
        asset.symbol = "UNKNOWN"
        asset.exchange = "LSE"

        assert service.get_asset_country(asset) == "United States"

    def test_get_asset_class_known_symbol(self, service):
        """Test getting asset class for known symbol."""
        asset = Mock()
        asset.symbol = "BTC"
        asset.asset_type = None

        assert service.get_asset_class(asset) == "crypto"

    def test_get_asset_class_unknown_symbol(self, service):
        """Test getting asset class for unknown symbol."""
        asset = Mock()
        asset.symbol = "UNKNOWN"
        asset.asset_type = "bond"

        assert service.get_asset_class(asset) == "bond"

    def test_calculate_total_value(self, service, mock_holdings):
        """Test calculating total portfolio value."""
        total = service.calculate_total_value(mock_holdings)

        expected = sum(h.current_value for h in mock_holdings)
        assert total == expected

    def test_calculate_sector_allocation(self, service, mock_portfolio, mock_holdings):
        """Test calculating sector allocation."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.calculate_sector_allocation(
                mock_portfolio, save_to_db=False
            )

            assert len(result) == 3  # Technology, Financial Services, Healthcare
            assert result[0]["sector"] == "Technology"
            assert result[0]["percentage"] > 50  # Technology should be largest

    def test_calculate_geographic_allocation(
        self, service, mock_portfolio, mock_holdings
    ):
        """Test calculating geographic allocation."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.calculate_geographic_allocation(
                mock_portfolio, save_to_db=False
            )

            assert len(result) == 1  # All US
            assert result[0]["country"] == "United States"
            assert result[0]["percentage"] == 100.0

    def test_calculate_asset_class_allocation(
        self, service, mock_portfolio, mock_holdings
    ):
        """Test calculating asset class allocation."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.calculate_asset_class_allocation(
                mock_portfolio, save_to_db=False
            )

            assert len(result) == 1  # All stock
            assert result[0]["asset_class"] == "stock"
            assert result[0]["percentage"] == 100.0

    def test_calculate_concentration_risk(self, service, mock_portfolio, mock_holdings):
        """Test calculating concentration risk."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.calculate_concentration_risk(
                mock_portfolio, save_to_db=False
            )

            assert len(result) == 5  # All 5 holdings
            # Check sorting by percentage (descending)
            for i in range(len(result) - 1):
                assert result[i]["percentage"] >= result[i + 1]["percentage"]

    def test_get_asset_beta_known_symbols(self, service):
        """Test getting beta for known symbols."""
        assert service.get_asset_beta(Mock(symbol="SPY")) == Decimal("1.0")
        assert service.get_asset_beta(Mock(symbol="VOO")) == Decimal("1.0")
        assert service.get_asset_beta(Mock(symbol="BTC")) == Decimal("2.0")
        assert service.get_asset_beta(Mock(symbol="BND")) == Decimal("0.1")

    def test_get_asset_beta_unknown_symbol(self, service):
        """Test getting beta for unknown symbol (defaults to 1.0)."""
        asset = Mock()
        asset.symbol = "UNKNOWN"
        assert service.get_asset_beta(asset) == Decimal("1.0")

    def test_calculate_portfolio_beta(self, service, mock_portfolio, mock_holdings):
        """Test calculating portfolio beta."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.calculate_portfolio_beta(
                mock_portfolio, "SPY", save_to_db=False
            )

            assert "beta" in result
            assert result["benchmark"] == "SPY"
            assert "calculated_at" in result

    def test_calculate_diversification_score_single_sector(
        self, service, mock_portfolio
    ):
        """Test diversification score with single sector."""
        single_sector_holdings = []
        for i in range(5):
            asset = Mock()
            asset.symbol = f"STOCK{i}"
            asset.sector = "Technology"
            asset.country = "United States"
            asset.asset_type = "stock"
            asset.last_price = Decimal("100")

            holding = Mock()
            holding.asset = asset
            holding.quantity = Decimal("10")
            holding.current_value = Decimal("1000")
            single_sector_holdings.append(holding)

        with patch.object(
            service, "get_holdings_with_values", return_value=single_sector_holdings
        ):
            score = service.calculate_diversification_score(mock_portfolio)

            assert score < 50  # Low diversification with single sector

    def test_calculate_diversification_score_multi_sector(
        self, service, mock_portfolio, mock_holdings
    ):
        """Test diversification score with multiple sectors."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            score = service.calculate_diversification_score(mock_portfolio)

            assert score > 40  # Better diversification with multiple sectors

    def test_calculate_overall_risk_metrics(
        self, service, mock_portfolio, mock_holdings
    ):
        """Test calculating overall risk metrics."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.calculate_overall_risk_metrics(
                mock_portfolio, save_to_db=False
            )

            assert "overall_risk_score" in result
            assert "risk_level" in result
            assert "concentration_risk" in result
            assert "diversification_score" in result
            assert "recommendations" in result
            assert "analyzed_at" in result

    def test_get_full_analytics(self, service, mock_portfolio, mock_holdings):
        """Test getting full analytics."""
        with patch.object(
            service, "get_holdings_with_values", return_value=mock_holdings
        ):
            result = service.get_full_analytics(mock_portfolio)

            assert result["portfolio_id"] == mock_portfolio.id
            assert result["portfolio_name"] == mock_portfolio.name
            assert "total_value" in result
            assert "sector_allocation" in result
            assert "geographic_allocation" in result
            assert "asset_class_allocation" in result
            assert "concentration_risk" in result
            assert "beta" in result
            assert "risk_metrics" in result
            assert "calculated_at" in result


class TestSectorAllocationModel:
    """Test PortfolioSectorAllocation model."""

    def test_str_representation(self):
        """Test string representation of sector allocation."""
        portfolio = Mock()
        portfolio.name = "Test Portfolio"

        from investments.models.portfolio_analytics import PortfolioSectorAllocation

        allocation = PortfolioSectorAllocation(
            portfolio=portfolio,
            sector="Technology",
            percentage=Decimal("50.00"),
            value=Decimal("50000"),
        )

        assert str(allocation) == "Test Portfolio - Technology: 50.00%"


class TestGeographicAllocationModel:
    """Test PortfolioGeographicAllocation model."""

    def test_str_representation(self):
        """Test string representation of geographic allocation."""
        portfolio = Mock()
        portfolio.name = "Test Portfolio"

        from investments.models.portfolio_analytics import PortfolioGeographicAllocation

        allocation = PortfolioGeographicAllocation(
            portfolio=portfolio,
            country="United States",
            percentage=Decimal("75.00"),
            value=Decimal("75000"),
        )

        assert str(allocation) == "Test Portfolio - United States: 75.00%"


class TestConcentrationRiskModel:
    """Test PortfolioConcentrationRisk model."""

    def test_str_representation(self):
        """Test string representation of concentration risk."""
        portfolio = Mock()
        portfolio.name = "Test Portfolio"

        asset = Mock()
        asset.symbol = "AAPL"

        from investments.models.portfolio_analytics import PortfolioConcentrationRisk

        risk = PortfolioConcentrationRisk(
            portfolio=portfolio,
            asset=asset,
            percentage=Decimal("25.00"),
            concentration_score=Decimal("75.00"),
            concentration_level="HIGH",
        )

        assert str(risk) == "Test Portfolio - AAPL: 25.00% (HIGH)"


class TestPortfolioBetaModel:
    """Test PortfolioBeta model."""

    def test_str_representation(self):
        """Test string representation of portfolio beta."""
        portfolio = Mock()
        portfolio.name = "Test Portfolio"

        benchmark = Mock()
        benchmark.symbol = "SPY"

        from investments.models.portfolio_analytics import PortfolioBeta

        beta = PortfolioBeta(
            portfolio=portfolio, benchmark=benchmark, beta=Decimal("1.15")
        )

        assert str(beta) == "Test Portfolio - Beta: 1.1500 vs SPY"


class TestAnalyticsServiceSingleton:
    """Test analytics service singleton pattern."""

    def test_get_analytics_service_returns_same_instance(self):
        """Test that get_analytics_service returns same instance."""
        service1 = get_analytics_service()
        service2 = get_analytics_service()

        assert service1 is service2

    def test_service_has_all_methods(self):
        """Test that service has all required methods."""
        service = PortfolioAnalyticsService()

        assert hasattr(service, "calculate_sector_allocation")
        assert hasattr(service, "calculate_geographic_allocation")
        assert hasattr(service, "calculate_asset_class_allocation")
        assert hasattr(service, "calculate_concentration_risk")
        assert hasattr(service, "calculate_portfolio_beta")
        assert hasattr(service, "calculate_diversification_score")
        assert hasattr(service, "calculate_overall_risk_metrics")
        assert hasattr(service, "get_full_analytics")
