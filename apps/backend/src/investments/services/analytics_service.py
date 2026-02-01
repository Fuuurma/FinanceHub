from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count
from django.utils import timezone
import logging

from portfolios.models.portfolio import Portfolio
from portfolios.models.holdings import Holding
from assets.models.asset import Asset
from investments.models.portfolio_analytics import (
    PortfolioSectorAllocation,
    PortfolioGeographicAllocation,
    PortfolioAssetClassAllocation,
    PortfolioConcentrationRisk,
    PortfolioBeta,
    PerformanceAttribution,
    PortfolioRiskMetrics,
)
from utils.services.pipeline_monitor import get_metrics

logger = logging.getLogger(__name__)


class PortfolioAnalyticsService:
    """Service for calculating portfolio analytics and metrics."""

    SECTOR_MAP = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Technology",
        "GOOG": "Technology",
        "AMZN": "Consumer Cyclical",
        "META": "Technology",
        "TSLA": "Consumer Cyclical",
        "NVDA": "Technology",
        "JPM": "Financial Services",
        "V": "Financial Services",
        "JNJ": "Healthcare",
        "WMT": "Consumer Defensive",
        "PG": "Consumer Defensive",
        "MA": "Financial Services",
        "HD": "Consumer Cyclical",
        "CVX": "Energy",
        "MRK": "Healthcare",
        "ABBV": "Healthcare",
        "PFE": "Healthcare",
        "KO": "Consumer Defensive",
    }

    COUNTRY_MAP = {
        "AAPL": "United States",
        "MSFT": "United States",
        "GOOGL": "United States",
        "GOOG": "United States",
        "AMZN": "United States",
        "META": "United States",
        "TSLA": "United States",
        "NVDA": "United States",
        "JPM": "United States",
        "V": "United States",
        "JNJ": "United States",
        "WMT": "United States",
        "TM": "Japan",
        "TMO": "United States",
        "ASML": "Netherlands",
        "NVO": "Denmark",
        "BABA": "China",
        "JD": "China",
        "SE": "Singapore",
    }

    ASSET_CLASS_MAP = {
        "AAPL": "stock",
        "MSFT": "stock",
        "GOOGL": "stock",
        "GOOG": "stock",
        "AMZN": "stock",
        "META": "stock",
        "TSLA": "stock",
        "NVDA": "stock",
        "JPM": "stock",
        "V": "stock",
        "BTC": "crypto",
        "ETH": "crypto",
        "BNB": "crypto",
        "SOL": "crypto",
        "XRP": "crypto",
        "ADA": "crypto",
        "SPY": "etf",
        "QQQ": "etf",
        "VTI": "etf",
        "VOO": "etf",
        "BND": "bond",
        "TLT": "bond",
    }

    def get_holdings_with_values(self, portfolio: Portfolio) -> List[Holding]:
        """Get all holdings with calculated current values."""
        return (
            Holding.objects.filter(portfolio=portfolio, is_deleted=False)
            .select_related("asset")
            .prefetch_related("asset__prices")
        )

    def calculate_total_value(self, holdings: List[Holding]) -> Decimal:
        """Calculate total portfolio value."""
        return sum(h.current_value for h in holdings)

    def get_asset_sector(self, asset: Asset) -> str:
        """Get asset sector with fallback."""
        if asset.symbol in self.SECTOR_MAP:
            return self.SECTOR_MAP[asset.symbol]
        if asset.asset_type:
            return asset.asset_type.capitalize()
        return "Unknown"

    def get_asset_country(self, asset: Asset) -> str:
        """Get asset country with fallback."""
        if asset.symbol in self.COUNTRY_MAP:
            return self.COUNTRY_MAP[asset.symbol]
        if asset.exchange:
            if (
                "US" in asset.exchange
                or "NYSE" in asset.exchange
                or "NASDAQ" in asset.exchange
            ):
                return "United States"
        return "United States"

    def get_asset_class(self, asset: Asset) -> str:
        """Get asset class with fallback."""
        if asset.symbol in self.ASSET_CLASS_MAP:
            return self.ASSET_CLASS_MAP[asset.symbol]
        if asset.asset_type:
            if asset.asset_type == "crypto":
                return "crypto"
            elif asset.asset_type == "bond":
                return "bond"
            elif asset.asset_type == "etf":
                return "etf"
        return "stock"

    def calculate_sector_allocation(
        self, portfolio: Portfolio, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Calculate sector breakdown of portfolio."""
        holdings = self.get_holdings_with_values(portfolio)
        total_value = self.calculate_total_value(holdings)

        if total_value == 0:
            return []

        sector_values: Dict[str, Decimal] = {}
        for holding in holdings:
            sector = self.get_asset_sector(holding.asset)
            sector_values[sector] = (
                sector_values.get(sector, Decimal("0")) + holding.current_value
            )

        result = []
        for sector, value in sector_values.items():
            percentage = (value / total_value) * 100
            result.append(
                {
                    "sector": sector,
                    "value": float(value),
                    "percentage": float(percentage),
                }
            )

        result.sort(key=lambda x: x["percentage"], reverse=True)

        if save_to_db:
            PortfolioSectorAllocation.objects.filter(portfolio=portfolio).delete()
            for item in result:
                PortfolioSectorAllocation.objects.create(
                    portfolio=portfolio,
                    sector=item["sector"],
                    percentage=Decimal(str(item["percentage"])),
                    value=Decimal(str(item["value"])),
                )

        return result

    def calculate_geographic_allocation(
        self, portfolio: Portfolio, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Calculate geographic breakdown of portfolio."""
        holdings = self.get_holdings_with_values(portfolio)
        total_value = self.calculate_total_value(holdings)

        if total_value == 0:
            return []

        country_values: Dict[str, Decimal] = {}
        for holding in holdings:
            country = self.get_asset_country(holding.asset)
            country_values[country] = (
                country_values.get(country, Decimal("0")) + holding.current_value
            )

        result = []
        for country, value in country_values.items():
            percentage = (value / total_value) * 100
            result.append(
                {
                    "country": country,
                    "percentage": float(percentage),
                    "value": float(value),
                }
            )

        result.sort(key=lambda x: x["percentage"], reverse=True)

        if save_to_db:
            PortfolioGeographicAllocation.objects.filter(portfolio=portfolio).delete()
            for item in result:
                PortfolioGeographicAllocation.objects.create(
                    portfolio=portfolio,
                    country=item["country"],
                    percentage=Decimal(str(item["percentage"])),
                    value=Decimal(str(item["value"])),
                )

        return result

    def calculate_asset_class_allocation(
        self, portfolio: Portfolio, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Calculate asset class breakdown of portfolio."""
        holdings = self.get_holdings_with_values(portfolio)
        total_value = self.calculate_total_value(holdings)

        if total_value == 0:
            return []

        class_values: Dict[str, Decimal] = {}
        for holding in holdings:
            asset_class = self.get_asset_class(holding.asset)
            class_values[asset_class] = (
                class_values.get(asset_class, Decimal("0")) + holding.current_value
            )

        result = []
        for asset_class, value in class_values.items():
            percentage = (value / total_value) * 100
            result.append(
                {
                    "asset_class": asset_class,
                    "percentage": float(percentage),
                    "value": float(value),
                }
            )

        result.sort(key=lambda x: x["percentage"], reverse=True)

        if save_to_db:
            PortfolioAssetClassAllocation.objects.filter(portfolio=portfolio).delete()
            for item in result:
                PortfolioAssetClassAllocation.objects.create(
                    portfolio=portfolio,
                    asset_class=item["asset_class"],
                    percentage=Decimal(str(item["percentage"])),
                    value=Decimal(str(item["value"])),
                )

        return result

    def calculate_concentration_risk(
        self, portfolio: Portfolio, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Calculate concentration risk by position."""
        holdings = self.get_holdings_with_values(portfolio)
        total_value = self.calculate_total_value(holdings)

        if total_value == 0:
            return []

        result = []
        for holding in holdings:
            percentage = (
                (holding.current_value / total_value) * 100 if total_value > 0 else 0
            )

            if percentage > 25:
                level = "VERY_HIGH"
                score = Decimal("95")
            elif percentage > 15:
                level = "HIGH"
                score = Decimal("75")
            elif percentage > 10:
                level = "MEDIUM"
                score = Decimal("50")
            else:
                level = "LOW"
                score = Decimal("25")

            result.append(
                {
                    "asset_id": holding.asset.id,
                    "asset_symbol": holding.asset.symbol,
                    "asset_name": holding.asset.name,
                    "percentage": float(percentage),
                    "value": float(holding.current_value),
                    "concentration_score": float(score),
                    "concentration_level": level,
                }
            )

        result.sort(key=lambda x: x["percentage"], reverse=True)

        if save_to_db:
            PortfolioConcentrationRisk.objects.filter(portfolio=portfolio).delete()
            for item in result:
                PortfolioConcentrationRisk.objects.create(
                    portfolio=portfolio,
                    asset_id=item["asset_id"],
                    percentage=Decimal(str(item["percentage"])),
                    concentration_score=Decimal(str(item["concentration_score"])),
                    concentration_level=item["concentration_level"],
                )

        return result

    def get_asset_beta(self, asset: Asset) -> Decimal:
        """Get asset beta with fallback to 1.0."""
        if asset.symbol in ["SPY", "VOO", "IVV"]:
            return Decimal("1.0")
        elif asset.symbol in ["BND", "AGG", "TLT"]:
            return Decimal("0.1")
        elif asset.symbol in ["BTC", "ETH"]:
            return Decimal("2.0")
        return Decimal("1.0")

    def calculate_portfolio_beta(
        self,
        portfolio: Portfolio,
        benchmark_symbol: str = "SPY",
        save_to_db: bool = True,
    ) -> Dict[str, Any]:
        """Calculate portfolio beta vs benchmark."""
        holdings = self.get_holdings_with_values(portfolio)
        total_value = self.calculate_total_value(holdings)

        if total_value == 0:
            return {"beta": 1.0, "benchmark": benchmark_symbol}

        weighted_beta = Decimal("0")
        for holding in holdings:
            weight = holding.current_value / total_value if total_value > 0 else 0
            asset_beta = self.get_asset_beta(holding.asset)
            weighted_beta += weight * asset_beta

        result = {
            "beta": float(weighted_beta),
            "benchmark": benchmark_symbol,
            "calculated_at": timezone.now().isoformat(),
        }

        if save_to_db:
            try:
                benchmark_asset = Asset.objects.filter(symbol=benchmark_symbol).first()
                PortfolioBeta.objects.create(
                    portfolio=portfolio,
                    benchmark=benchmark_asset or Asset.objects.first(),
                    beta=weighted_beta,
                    calculation_period_days=252,
                )
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                logger.error(f"Error saving portfolio beta: {e}")

        return result

    def calculate_diversification_score(self, portfolio: Portfolio) -> float:
        """Calculate portfolio diversification score (0-100)."""
        sector_allocation = self.calculate_sector_allocation(
            portfolio, save_to_db=False
        )
        if not sector_allocation:
            return 0.0

        if len(sector_allocation) == 1:
            return 20.0

        herfindahl_index = sum(
            (item["percentage"] / 100) ** 2 for item in sector_allocation
        )
        diversification_score = (1 - herfindahl_index) * 100

        return round(min(diversification_score, 100), 2)

    def calculate_overall_risk_metrics(
        self, portfolio: Portfolio, save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics."""
        concentration = self.calculate_concentration_risk(portfolio, save_to_db=False)
        diversification = self.calculate_diversification_score(portfolio)

        if not concentration:
            return {}

        largest_holding_percent = concentration[0]["percentage"] if concentration else 0

        if largest_holding_percent > 30:
            risk_level = "VERY_HIGH"
            risk_score = 85
        elif largest_holding_percent > 20:
            risk_level = "HIGH"
            risk_score = 70
        elif largest_holding_percent > 10 or diversification < 40:
            risk_level = "MEDIUM"
            risk_score = 50
        else:
            risk_level = "LOW"
            risk_score = 25

        concentration_risk = sum(
            item["concentration_score"] for item in concentration
        ) / len(concentration)

        recommendations = []
        if largest_holding_percent > 15:
            recommendations.append(
                f"Consider reducing {concentration[0]['asset_symbol']} exposure below 15%"
            )
        if len(concentration) < 5:
            recommendations.append("Add more positions to improve diversification")
        if diversification < 50:
            recommendations.append(
                "Sector allocation is concentrated - consider diversifying across sectors"
            )

        result = {
            "overall_risk_score": risk_score,
            "risk_level": risk_level,
            "concentration_risk": round(concentration_risk, 2),
            "diversification_score": diversification,
            "largest_holding_percent": round(largest_holding_percent, 2),
            "recommendations": recommendations,
            "analyzed_at": timezone.now().isoformat(),
        }

        if save_to_db:
            try:
                PortfolioRiskMetrics.objects.create(
                    portfolio=portfolio,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    volatility_30d=None,
                    volatility_90d=None,
                    volatility_1y=None,
                    sharpe_ratio=None,
                    sortino_ratio=None,
                    max_drawdown=None,
                    var_95=None,
                    var_99=None,
                    calculation_period_days=252,
                )
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                logger.error(f"Error saving risk metrics: {e}")

        return result

    def get_full_analytics(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics."""
        monitor = get_metrics()
        monitor.start_operation(f"analytics:{portfolio.id}")

        try:
            sector_allocation = self.calculate_sector_allocation(portfolio)
            geographic_allocation = self.calculate_geographic_allocation(portfolio)
            asset_class_allocation = self.calculate_asset_class_allocation(portfolio)
            concentration_risk = self.calculate_concentration_risk(portfolio)
            beta_data = self.calculate_portfolio_beta(portfolio)
            risk_metrics = self.calculate_overall_risk_metrics(portfolio)

            total_value = self.calculate_total_value(
                self.get_holdings_with_values(portfolio)
            )

            analytics = {
                "portfolio_id": portfolio.id,
                "portfolio_name": portfolio.name,
                "total_value": float(total_value),
                "sector_allocation": sector_allocation,
                "geographic_allocation": geographic_allocation,
                "asset_class_allocation": asset_class_allocation,
                "concentration_risk": concentration_risk,
                "beta": beta_data,
                "risk_metrics": risk_metrics,
                "calculated_at": timezone.now().isoformat(),
            }

            monitor.end_operation(f"analytics:{portfolio.id}", success=True)
            return analytics

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            monitor.end_operation(f"analytics:{portfolio.id}", success=False)
            logger.error(
                f"Error calculating analytics for portfolio {portfolio.id}: {e}"
            )
            raise


_analytics_service_instance: Optional[PortfolioAnalyticsService] = None


def get_analytics_service() -> PortfolioAnalyticsService:
    """Get singleton analytics service instance."""
    global _analytics_service_instance
    if _analytics_service_instance is None:
        _analytics_service_instance = PortfolioAnalyticsService()
    return _analytics_service_instance
