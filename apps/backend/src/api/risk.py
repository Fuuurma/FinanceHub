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

risk_service = None

try:
    from investments.services.risk_service import RiskManagementService

    risk_service = RiskManagementService()
except ImportError:
    pass


class PositionSizeInput(Schema):
    portfolio_value: float = Field(..., description="Total portfolio value")
    account_balance: float = Field(..., description="Available cash for trading")
    risk_per_trade: float = Field(
        ..., gt=0, le=1, description="Risk per trade as decimal (e.g., 0.01 for 1%)"
    )
    entry_price: float = Field(..., gt=0, description="Entry price per share")
    stop_loss_price: float = Field(..., gt=0, description="Stop loss price per share")
    position_type: str = Field(
        default="LONG", description="Position type: LONG or SHORT"
    )


class PositionSizeOutput(Schema):
    position_shares: float
    position_value: float
    position_percentage: float
    risk_amount: float
    risk_per_share: float
    max_loss: float
    stop_loss_distance: float


class StopLossInput(Schema):
    entry_price: float = Field(..., gt=0, description="Entry price per share")
    stop_loss_pct: float = Field(
        ..., gt=0, le=1, description="Stop loss percentage as decimal"
    )
    position_type: str = Field(
        default="LONG", description="Position type: LONG or SHORT"
    )


class StopLossOutput(Schema):
    stop_loss_price: float
    stop_loss_pct: float
    position_type: str


class RiskRewardInput(Schema):
    entry_price: float = Field(..., gt=0, description="Entry price per share")
    stop_loss: float = Field(..., gt=0, description="Stop loss price per share")
    target_price: float = Field(..., gt=0, description="Target price per share")


class RiskRewardOutput(Schema):
    risk_reward_ratio: float
    verdict: str
    color: str
    risk_per_share: float
    reward_per_share: float


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


@router.get("/scenarios")
def list_stress_scenarios(request):
    """Get available historical stress test scenarios"""
    if not var_service:
        return {"error": "Risk service not available"}
    return {"scenarios": var_service.get_available_scenarios()}


@router.post("/var/{portfolio_id}")
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
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {"error": str(e)}, 500


@router.post("/stress-test/{portfolio_id}/historical")
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
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {"error": str(e)}, 500


@router.post("/stress-test/{portfolio_id}/custom")
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
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
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
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {"error": str(e)}


@router.get("/var/methods")
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


@router.post("/position-size", response=PositionSizeOutput)
def calculate_position_size(request, data: PositionSizeInput):
    """Calculate optimal position size based on risk parameters"""
    if not risk_service:
        return {"error": "Risk management service not available"}, 503

    try:
        result = risk_service.calculate_position_size(
            portfolio_value=data.portfolio_value,
            account_balance=data.account_balance,
            risk_per_trade=data.risk_per_trade,
            entry_price=data.entry_price,
            stop_loss_price=data.stop_loss_price,
        )

        if "error" in result:
            return {"error": result["error"]}, 400

        return {
            "position_shares": result.get("position_shares", 0),
            "position_value": result.get("position_value", 0),
            "position_percentage": result.get("position_percentage", 0),
            "risk_amount": result.get("risk_amount", 0),
            "risk_per_share": result.get("risk_per_share", 0),
            "max_loss": result.get("max_loss", 0),
            "stop_loss_distance": result.get("stop_loss_distance", 0),
        }
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {"error": str(e)}, 500


@router.post("/stop-loss", response=StopLossOutput)
def calculate_stop_loss_price(request, data: StopLossInput):
    """Calculate stop loss price based on percentage"""
    if not risk_service:
        return {"error": "Risk management service not available"}, 503

    try:
        result = risk_service.calculate_stop_loss(
            entry_price=data.entry_price,
            stop_loss_pct=data.stop_loss_pct,
            position_type=data.position_type,
        )

        if "error" in result:
            return {"error": result["error"]}, 400

        return {
            "stop_loss_price": result.get("stop_loss_price", 0),
            "stop_loss_pct": result.get("stop_loss_pct", 0),
            "position_type": result.get("position_type", "LONG"),
        }
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {"error": str(e)}, 500


@router.post("/risk-reward", response=RiskRewardOutput)
def calculate_risk_reward(request, data: RiskRewardInput):
    """Calculate risk/reward ratio"""
    if not risk_service:
        return {"error": "Risk management service not available"}, 503

    try:
        result = risk_service.calculate_risk_reward_ratio(
            entry_price=data.entry_price,
            stop_loss=data.stop_loss,
            target_price=data.target_price,
        )

        if "error" in result:
            return {"error": result["error"]}, 400

        return {
            "risk_reward_ratio": result.get("risk_reward_ratio", 0),
            "verdict": result.get("verdict", "FAIR"),
            "color": result.get("color", "yellow"),
            "risk_per_share": result.get("risk_per_share", 0),
            "reward_per_share": result.get("reward_per_share", 0),
        }
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {"error": str(e)}, 500
