"""
Portfolio Rebalancing API
Provides endpoints for portfolio rebalancing, drift detection, and trade suggestions.
"""

from typing import Dict, List, Optional
from decimal import Decimal
from ninja import Router, Schema
from pydantic import BaseModel, Field
from django.contrib.auth.models import User
from django.utils import timezone
from portfolios.models.portfolio import Portfolio
from investments.services.rebalancing_service import RebalancingService
from investments.models.rebalancing import (
    TargetAllocation,
    RebalancingSession,
    RebalancingSuggestion,
)
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)
router = Router(tags=["Portfolio Rebalancing"])


class TargetAllocationRequest(BaseModel):
    asset_class: str
    target_percentage: Decimal = Field(..., ge=0, le=100)
    tolerance_percentage: Decimal = Field(default=Decimal("5.00"), ge=0, le=50)


class SetTargetAllocationRequest(BaseModel):
    allocations: List[TargetAllocationRequest]
    replace_existing: bool = True


class RebalancingSuggestionResponse(BaseModel):
    id: str
    asset_class: str
    action: str
    current_allocation: float
    target_allocation: float
    estimated_trade_value: float
    priority: str
    tax_implication: str
    reason: str


class DriftResponse(BaseModel):
    asset_class: str
    current_percentage: float
    target_percentage: float
    drift_percentage: float
    tolerance: float
    status: str


class DriftStatusResponse(BaseModel):
    needs_rebalancing: bool
    drifts: List[DriftResponse]
    checked_at: str


class CurrentAllocationResponse(BaseModel):
    asset_class: str
    value: float
    percentage: float


class WhatIfRequest(BaseModel):
    allocations: Dict[str, float]


class WhatIfResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    trades: List[Dict]
    total_trades_needed: int
    estimated_turnover: float


class TaxLotResponse(BaseModel):
    asset: Optional[str]
    quantity: float
    cost_basis: float
    current_value: float
    unrealized_loss: float
    loss_percentage: float
    is_long_term: bool
    wash_sale_risk: bool


class RebalancingSessionResponse(BaseModel):
    id: str
    name: str
    status: str
    total_trades: int
    estimated_total_value: float
    created_at: str


@router.get(
    "/portfolios/{portfolio_id}/rebalancing/drift", response=DriftStatusResponse
)
async def get_drift_status(request, portfolio_id: str):
    """
    Get portfolio drift status from target allocation.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)
    status = service.get_drift_status()

    return DriftStatusResponse(
        needs_rebalancing=status["needs_rebalancing"],
        drifts=[
            DriftResponse(
                asset_class=d["asset_class"],
                current_percentage=d["current_percentage"],
                target_percentage=d["target_percentage"],
                drift_percentage=d["drift_percentage"],
                tolerance=d["tolerance"],
                status=d["status"],
            )
            for d in status["drifts"]
        ],
        checked_at=status["checked_at"],
    )


@router.get("/portfolios/{portfolio_id}/rebalancing/allocation")
async def get_allocation(request, portfolio_id: str):
    """
    Get current and target allocation for portfolio.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)
    current = service.get_current_allocation()
    target = service.get_target_allocation()

    return {
        "current": [
            CurrentAllocationResponse(
                asset_class=asset_class,
                value=float(data["value"]),
                percentage=float(data["percentage"]),
            )
            for asset_class, data in current.items()
        ],
        "target": target,
    }


@router.post(
    "/portfolios/{portfolio_id}/rebalancing/target",
    response=List[TargetAllocationRequest],
)
async def set_target_allocation(
    request, portfolio_id: str, data: SetTargetAllocationRequest
):
    """
    Set target allocation for portfolio.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)

    allocations = {
        a.asset_class: {
            "target": a.target_percentage,
            "tolerance": a.tolerance_percentage,
        }
        for a in data.allocations
    }

    targets = service.set_target_allocation(
        allocations, replace_existing=data.replace_existing
    )

    return [
        TargetAllocationRequest(
            asset_class=t.asset_class,
            target_percentage=t.target_percentage,
            tolerance_percentage=t.tolerance_percentage,
        )
        for t in targets
    ]


@router.get(
    "/portfolios/{portfolio_id}/rebalancing/suggestions",
    response=List[RebalancingSuggestionResponse],
)
async def get_rebalancing_suggestions(
    request, portfolio_id: str, max_trades: int = 10, tax_efficient: bool = True
):
    """
    Get rebalancing trade suggestions.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)
    suggestions = service.generate_rebalancing_suggestions(
        max_trades=max_trades, prefer_tax_efficient=tax_efficient
    )

    return [
        RebalancingSuggestionResponse(
            id=str(s.id),
            asset_class=s.asset_class,
            action=s.action,
            current_allocation=float(s.current_allocation),
            target_allocation=float(s.target_allocation),
            estimated_trade_value=float(s.estimated_trade_value),
            priority=s.priority,
            tax_implication=s.tax_implication,
            reason=s.reason,
        )
        for s in suggestions
    ]


@router.post("/portfolios/{portfolio_id}/rebalancing/what-if", response=WhatIfResponse)
async def what_if_analysis(request, portfolio_id: str, data: WhatIfRequest):
    """
    What-if analysis for proposed rebalancing changes.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)

    proposed = {k: Decimal(str(v)) for k, v in data.allocations.items()}
    result = service.what_if_analysis(proposed)

    return WhatIfResponse(
        valid=result["valid"],
        error=result.get("error"),
        trades=result.get("trades", []),
        total_trades_needed=result.get("total_trades_needed", 0),
        estimated_turnover=result.get("estimated_turnover", 0),
    )


@router.get("/portfolios/{portfolio_id}/rebalancing/tax-loss-harvesting")
async def get_tax_loss_harvesting(request, portfolio_id: str):
    """
    Get tax-loss harvesting opportunities.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)
    opportunities = service.get_tax_loss_harvesting_opportunities()

    return {"opportunities": opportunities}


@router.post("/portfolios/{portfolio_id}/rebalancing/session")
async def create_rebalancing_session(
    request,
    portfolio_id: str,
    name: str,
    max_trades: int = 10,
    tax_efficient: bool = True,
):
    """
    Create a rebalancing session with suggestions.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)
    session = service.create_rebalancing_session(
        name=name, max_trades=max_trades, tax_efficient=tax_efficient
    )

    return {
        "id": str(session.id),
        "name": session.name,
        "status": session.status,
        "total_trades": session.total_trades,
        "estimated_total_value": float(session.estimated_total_value),
        "created_at": session.created_at.isoformat(),
    }


@router.get(
    "/portfolios/{portfolio_id}/rebalancing/sessions",
    response=List[RebalancingSessionResponse],
)
async def get_rebalancing_sessions(request, portfolio_id: str):
    """
    Get rebalancing sessions for portfolio.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    sessions = RebalancingSession.objects.filter(portfolio=portfolio)

    return [
        RebalancingSessionResponse(
            id=str(s.id),
            name=s.name,
            status=s.status,
            total_trades=s.total_trades,
            estimated_total_value=float(s.estimated_total_value),
            created_at=s.created_at.isoformat(),
        )
        for s in sessions
    ]


@router.post("/portfolios/{portfolio_id}/rebalancing/sessions/{session_id}/execute")
async def execute_rebalancing_session(request, portfolio_id: str, session_id: str):
    """
    Execute a rebalancing session.
    """
    portfolio = await Portfolio.objects.aget(id=portfolio_id)

    if not portfolio:
        return {"error": "Portfolio not found"}, 404

    service = RebalancingService(portfolio)
    result = service.execute_rebalancing_session(session_id)

    return result
