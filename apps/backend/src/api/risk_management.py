"""
Risk Management API
Provides endpoints for position sizing, stop loss, and risk/reward analysis.
"""

from typing import Dict, List
from ninja import Router
from pydantic import BaseModel

from investments.services.risk_service import RiskManagementService

router = Router(tags=["Risk Management"])
risk_service = RiskManagementService()


class PositionSizeRequest(BaseModel):
    portfolio_value: float
    account_balance: float
    risk_per_trade: float
    entry_price: float
    stop_loss_price: float


class StopLossRequest(BaseModel):
    entry_price: float
    stop_loss_pct: float
    position_type: str = 'LONG'


class RiskRewardRequest(BaseModel):
    entry_price: float
    stop_loss: float
    target_price: float
    position_type: str = 'LONG'


@router.post("/risk/position-size")
def calculate_position_size(request, data: PositionSizeRequest):
    """Calculate optimal position size based on risk parameters."""
    return risk_service.calculate_position_size(
        data.portfolio_value,
        data.account_balance,
        data.risk_per_trade,
        data.entry_price,
        data.stop_loss_price
    )


@router.post("/risk/stop-loss")
def calculate_stop_loss(request, data: StopLossRequest):
    """Calculate stop loss price."""
    return risk_service.calculate_stop_loss(
        data.entry_price,
        data.stop_loss_pct,
        data.position_type
    )


@router.post("/risk/risk-reward")
def calculate_risk_reward(request, data: RiskRewardRequest):
    """Calculate risk/reward ratio."""
    return risk_service.calculate_risk_reward_ratio(
        data.entry_price,
        data.stop_loss,
        data.target_price,
        data.position_type
    )


@router.post("/risk/portfolio-score")
def calculate_portfolio_risk(request, positions: List[Dict]):
    """Calculate portfolio risk score."""
    return risk_service.calculate_portfolio_risk_score(positions)
