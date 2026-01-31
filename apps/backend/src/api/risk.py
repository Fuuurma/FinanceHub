from typing import Optional
from ninja import Router, Schema
from pydantic import Field
from decimal import Decimal

router = Router(tags=["Risk Management"])

var_service = None

try:
    from investments.services.var_service import ValueAtRiskService

    var_service = ValueAtRiskService()
except ImportError:
    pass


class VaRCalculateSchema(Schema):
    method: str = Field(
        default="parametric",
        description="VaR calculation method: parametric, historical, monte_carlo",
    )
    confidence_level: int = Field(
        default=95, ge=90, le=99, description="Confidence level percentage"
    )
    time_horizon: int = Field(
        default=1, ge=1, le=365, description="Time horizon in days"
    )
    lookback_days: int = Field(
        default=252, ge=30, le=1000, description="Historical lookback period"
    )


class StressTestSchema(Schema):
    market_shock_pct: float = Field(
        default=-0.20, ge=-1.0, le=1.0, description="Overall market shock percentage"
    )
    sector_shocks: Optional[dict] = Field(
        default=None, description="Sector-specific shocks"
    )
    fx_shocks: Optional[dict] = Field(
        default=None, description="Currency-specific shocks"
    )


@router.get("/risk/scenarios")
def list_stress_scenarios(request):
    """Get available historical stress test scenarios"""
    if not var_service:
        return {"error": "Risk service not available"}
    return {"scenarios": var_service.get_available_scenarios()}


@router.post("/risk/var/{portfolio_id}")
def calculate_var(request, portfolio_id: int, data: VaRCalculateSchema):
    """Calculate Value-at-Risk for a portfolio"""
    if not var_service:
        return {"error": "Risk service not available"}, 503

    try:
        positions_data = _get_portfolio_positions(request, portfolio_id)
        if "error" in positions_data:
            return positions_data, 404

        portfolio_name = positions_data.get("name", f"Portfolio {portfolio_id}")
        positions = positions_data.get("positions", [])

        result = var_service.calculate_var(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name,
            user_id=request.auth.id
            if hasattr(request, "auth") and hasattr(request.auth, "id")
            else 0,
            positions=positions,
            method=data.method,
            confidence_level=data.confidence_level,
            time_horizon=data.time_horizon,
            lookback_days=data.lookback_days,
        )

        return result
    except Exception as e:
        return {"error": str(e)}, 500


@router.post("/risk/stress-test/{portfolio_id}/historical")
def historical_stress_test(
    request, portfolio_id: int, scenario: str = "2008_financial_crisis"
):
    """Run historical stress test scenario"""
    if not var_service:
        return {"error": "Risk service not available"}, 503

    try:
        positions_data = _get_portfolio_positions(request, portfolio_id)
        if "error" in positions_data:
            return positions_data, 404

        portfolio_name = positions_data.get("name", f"Portfolio {portfolio_id}")
        positions = positions_data.get("positions", [])

        result = var_service.run_historical_stress_test(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name,
            user_id=request.auth.id
            if hasattr(request, "auth") and hasattr(request.auth, "id")
            else 0,
            positions=positions,
            scenario_key=scenario,
        )

        return result
    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500


@router.post("/risk/stress-test/{portfolio_id}/custom")
def custom_stress_test(request, portfolio_id: int, data: StressTestSchema):
    """Run custom stress test scenario"""
    if not var_service:
        return {"error": "Risk service not available"}, 503

    try:
        positions_data = _get_portfolio_positions(request, portfolio_id)
        if "error" in positions_data:
            return positions_data, 404

        portfolio_name = positions_data.get("name", f"Portfolio {portfolio_id}")
        positions = positions_data.get("positions", [])

        result = var_service.run_custom_stress_test(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name,
            user_id=request.auth.id
            if hasattr(request, "auth") and hasattr(request.auth, "id")
            else 0,
            positions=positions,
            market_shock_pct=data.market_shock_pct,
            sector_shocks=data.sector_shocks,
            fx_shocks=data.fx_shocks,
        )

        return result
    except Exception as e:
        return {"error": str(e)}, 500


def _get_portfolio_positions(request, portfolio_id: int) -> dict:
    """Helper function to get portfolio positions - simplified for demo"""
    try:
        from investments.models import Portfolio, PortfolioPosition

        portfolio = Portfolio.objects.filter(id=portfolio_id).first()
        if not portfolio:
            return {"error": "Portfolio not found"}

        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id, is_open=True
        ).select_related("asset")

        positions_data = []
        for pos in positions:
            asset = pos.asset
            position_dict = {
                "asset_id": asset.id if asset else 0,
                "symbol": asset.symbol if asset else "UNKNOWN",
                "name": asset.name if asset else "",
                "quantity": float(pos.quantity) if pos.quantity else 0,
                "current_price": float(pos.current_price) if pos.current_price else 0,
                "sector": getattr(asset, "sector", None) if asset else None,
                "price_history": [],
            }
            positions_data.append(position_dict)

        return {"id": portfolio.id, "name": portfolio.name, "positions": positions_data}
    except Exception as e:
        return {"error": str(e)}


@router.get("/risk/var/methods")
def get_var_methods(request):
    """Get available VaR calculation methods"""
    return {
        "methods": [
            {
                "id": "parametric",
                "name": "Parametric (Variance-Covariance)",
                "description": "Assumes normal distribution of returns. Fast but may underestimate tail risk.",
                "pros": ["Fast calculation", "Well understood"],
                "cons": ["Assumes normality", "May underestimate extreme losses"],
            },
            {
                "id": "historical",
                "name": "Historical Simulation",
                "description": "Uses actual historical returns. Non-parametric approach.",
                "pros": ["No distribution assumptions", "Captures fat tails"],
                "cons": ["Requires sufficient history", "Past may not predict future"],
            },
            {
                "id": "monte_carlo",
                "name": "Monte Carlo Simulation",
                "description": "Simulates thousands of random scenarios based on historical parameters.",
                "pros": ["Flexible", "Handles complex portfolios"],
                "cons": ["Computationally intensive", "Model risk"],
            },
        ],
        "confidence_levels": [
            {"value": 90, "description": "Moderate confidence - for daily monitoring"},
            {"value": 95, "description": "Standard confidence - most common choice"},
            {
                "value": 99,
                "description": "High confidence - for risk-averse strategies",
            },
            {
                "value": 99.9,
                "description": "Very high confidence - for extreme scenarios",
            },
        ],
    }
