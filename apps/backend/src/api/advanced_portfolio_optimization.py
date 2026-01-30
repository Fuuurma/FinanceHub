"""
Advanced Portfolio Optimization API
Provides endpoints for Black-Litterman, risk parity, CVaR optimization.
"""
from typing import List, Optional
from decimal import Decimal
from ninja import Router, Query, Field
from pydantic import BaseModel

from utils.services.portfolio import (
    get_portfolio_optimizer,
    OptimizationResult,
    BlackLittermanResult,
    RiskParityResult,
)
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint
from core.exceptions import ValidationException

router = Router(tags=["Advanced Portfolio Optimization"])


class MeanVarianceRequest(BaseModel):
    """Request for mean-variance optimization."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    target_return: Optional[float] = Field(None, description="Target expected return (for efficient frontier)")
    method: str = Field(default="max_sharpe", description="Optimization method: max_sharpe or min_variance")


class MeanVarianceResponse(BaseModel):
    """Response for mean-variance optimization."""
    weights: List[float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    success: bool
    message: str
    computed_in_ms: float


class BlackLittermanRequest(BaseModel):
    """Request for Black-Litterman model."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    market_caps: List[float] = Field(..., description="Market capitalizations")
    tau: float = Field(default=0.25, ge=0.01, le=1.0, description="Shrinkage intensity")
    view_matrix: Optional[List[List[float]]] = Field(None, description="Investor views matrix")
    view_picking: Optional[List[List[float]]] = Field(None, description="View picking matrix")


class BlackLittermanResponse(BaseModel):
    """Response for Black-Litterman model."""
    weights: List[float]
    expected_returns: List[float]
    expected_risk: float
    shrinkage_factor: float
    tau: float
    success: bool
    message: str
    computed_in_ms: float


class RiskParityRequest(BaseModel):
    """Request for risk parity optimization."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    max_iterations: int = Field(default=100, ge=1, le=500, description="Maximum iterations")
    tolerance: float = Field(default=1e-6, gt=0, description="Convergence tolerance")


class RiskParityResponse(BaseModel):
    """Response for risk parity optimization."""
    weights: List[float]
    risk_contributions: List[float]
    marginal_risk_contributions: List[float]
    risk_budget: float
    success: bool
    message: str
    computed_in_ms: float


class CVaROptimizationRequest(BaseModel):
    """Request for CVaR optimization."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    confidence_level: float = Field(default=0.95, ge=0.9, le=0.99, description="CVaR confidence level")
    n_simulations: int = Field(default=10000, ge=1000, le=100000, description="Number of Monte Carlo simulations")
    target_return: Optional[float] = Field(None, description="Target expected return")


class CVaRResponse(BaseModel):
    """Response for CVaR optimization."""
    weights: List[float]
    expected_return: float
    expected_risk: float
    cvar_at_level: float
    sharpe_ratio: float
    success: bool
    message: str
    computed_in_ms: float


class EfficientFrontierRequest(BaseModel):
    """Request for efficient frontier."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    n_portfolios: int = Field(default=20, ge=5, le=100, description="Number of portfolios on frontier")
    method: str = Field(default="max_sharpe", description="Optimization method")


class EfficientFrontierResponse(BaseModel):
    """Response for efficient frontier."""
    frontier: List[dict]
    min_return: float
    max_return: float
    min_risk: float
    max_risk: float
    success: bool
    message: str
    computed_in_ms: float


@router.post("/mean-variance", response=MeanVarianceResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['data_intensive'], key_prefix="portfolio_opt")
def mean_variance_optimization(request, data: MeanVarianceRequest):
    """Mean-variance portfolio optimization.

    Optimizes portfolio weights to maximize Sharpe ratio or minimize variance.
    Supports efficient frontier calculation with target returns.
    """
    if data.method not in ['max_sharpe', 'min_variance']:
        raise ValidationException(
            f"Invalid method '{data.method}'. Must be 'max_sharpe' or 'min_variance'",
            {"valid_methods": ['max_sharpe', 'min_variance']}
        )
    
    # Convert to NumPy array
    import numpy as np
    returns_array = np.array(data.returns)
    
    # Transpose to match expected format (periods x assets)
    if returns_array.shape[1] != len(returns_array[0]):
        returns_array = returns_array.T
    
    optimizer = get_portfolio_optimizer(returns_array, data.risk_free_rate)
    result: OptimizationResult = optimizer.mean_variance_optimization(
        target_return=data.target_return,
        method=data.method
    )
    
    return MeanVarianceResponse(
        weights=result.weights.tolist(),
        expected_return=float(result.expected_return),
        expected_risk=float(result.expected_risk),
        sharpe_ratio=float(result.sharpe_ratio),
        success=result.success,
        message=result.message,
        computed_in_ms=result.compute_time_ms
    )


@router.post("/black-litterman", response=BlackLittermanResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['data_intensive'], key_prefix="portfolio_opt")
def black_litterman_optimization(request, data: BlackLittermanRequest):
    """Black-Litterman model with Bayesian shrinkage.

    Combines market equilibrium with investor views.
    Provides shrinkage towards market-weighted portfolio.
    """
    # Validate inputs
    if len(data.market_caps) != len(data.returns[0]):
        raise ValidationException(
            f"Market caps length ({len(data.market_caps)}) must equal number of assets ({len(data.returns[0])})",
            {"market_caps_count": len(data.market_caps), "assets_count": len(data.returns[0])}
        )
    
    if data.view_matrix is not None and data.view_picking is not None:
        if data.view_matrix[0] != data.view_picking.shape[0]:
            raise ValidationException(
                "View matrix and view picking matrix must have same number of views",
                {"views": len(data.view_matrix[0]), "picking_rows": data.view_picking.shape[0]}
            )
    
    import numpy as np
    returns_array = np.array(data.returns)
    market_caps_array = np.array(data.market_caps)
    
    # Transpose returns if needed
    if returns_array.shape[1] != len(returns_array[0]):
        returns_array = returns_array.T
    
    view_matrix_np = np.array(data.view_matrix) if data.view_matrix else None
    view_picking_np = np.array(data.view_picking) if data.view_picking else None
    
    optimizer = get_portfolio_optimizer(returns_array, data.risk_free_rate)
    result: BlackLittermanResult = optimizer.black_litterman_model(
        market_caps=market_caps_array,
        tau=data.tau,
        view_matrix=view_matrix_np,
        view_picking=view_picking_np,
        omega=None
    )
    
    return BlackLittermanResponse(
        weights=result.weights.tolist(),
        expected_returns=result.expected_returns.tolist(),
        expected_risk=float(result.expected_risk),
        shrinkage_factor=float(result.shrinkage_factor),
        tau=result.tau,
        success=result.success,
        message=result.message,
        computed_in_ms=result.compute_time_ms
    )


@router.post("/risk-parity", response=RiskParityResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['data_intensive'], key_prefix="portfolio_opt")
def risk_parity_optimization(request, data: RiskParityRequest):
    """Risk parity optimization - equalize risk contributions.

    Each asset contributes equal risk to the portfolio.
    Iteratively converges to equal risk contributions.
    """
    import numpy as np
    returns_array = np.array(data.returns)
    
    # Transpose if needed
    if returns_array.shape[1] != len(returns_array[0]):
        returns_array = returns_array.T
    
    optimizer = get_portfolio_optimizer(returns_array, data.risk_free_rate)
    result: RiskParityResult = optimizer.risk_parity_optimization(
        max_iterations=data.max_iterations,
        tolerance=data.tolerance
    )
    
    return RiskParityResponse(
        weights=result.weights.tolist(),
        risk_contributions=result.risk_contributions.tolist(),
        marginal_risk_contributions=result.marginal_risk_contributions.tolist(),
        risk_budget=float(result.risk_budget),
        success=result.success,
        message=result.message,
        computed_in_ms=result.compute_time_ms
    )


@router.post("/cvar-optimization", response=CVaRResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['data_intensive'], key_prefix="portfolio_opt")
def cvar_optimization(request, data: CVaROptimizationRequest):
    """CVaR optimization - minimize expected shortfall.

    Minimizes Conditional Value at Risk for robust portfolio.
    Uses Monte Carlo simulation for risk estimation.
    """
    if data.confidence_level < 0.9 or data.confidence_level > 0.99:
        raise ValidationException(
            f"Confidence level must be between 0.9 and 0.99, got {data.confidence_level}",
            {"valid_range": [0.9, 0.99]}
        )
    
    import numpy as np
    returns_array = np.array(data.returns)
    
    # Transpose if needed
    if returns_array.shape[1] != len(returns_array[0]):
        returns_array = returns_array.T
    
    optimizer = get_portfolio_optimizer(returns_array, data.risk_free_rate)
    result: OptimizationResult = optimizer.cvar_optimization(
        confidence_level=data.confidence_level,
        n_simulations=data.n_simulations,
        target_return=data.target_return
    )
    
    return CVaRResponse(
        weights=result.weights.tolist(),
        expected_return=float(result.expected_return),
        expected_risk=float(result.expected_risk),
        cvar_at_level=float(result.expected_return - result.expected_risk * (1 - data.confidence_level)),
        sharpe_ratio=float(result.sharpe_ratio),
        success=result.success,
        message=result.message,
        computed_in_ms=result.compute_time_ms
    )


@router.post("/efficient-frontier", response=EfficientFrontierResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['data_intensive'], key_prefix="portfolio_opt")
def efficient_frontier(request, data: EfficientFrontierRequest):
    """Calculate efficient frontier of optimal portfolios.

    Generates multiple optimal portfolios along the efficient frontier.
    Shows risk-return trade-off for different target returns.
    """
    if data.method not in ['max_sharpe', 'min_variance']:
        raise ValidationException(
            f"Invalid method '{data.method}'. Must be 'max_sharpe' or 'min_variance'",
            {"valid_methods": ['max_sharpe', 'min_variance']}
        )
    
    if data.n_portfolios < 5 or data.n_portfolios > 100:
        raise ValidationException(
            f"Number of portfolios must be between 5 and 100, got {data.n_portfolios}",
            {"valid_range": [5, 100]}
        )
    
    import numpy as np
    returns_array = np.array(data.returns)
    
    # Transpose if needed
    if returns_array.shape[1] != len(returns_array[0]):
        returns_array = returns_array.T
    
    optimizer = get_portfolio_optimizer(returns_array, data.risk_free_rate)
    frontier = optimizer.efficient_frontier(
        n_portfolios=data.n_portfolios,
        method=data.method
    )
    
    # Extract frontier data
    frontier_data = [
        {
            "weights": f.weights.tolist(),
            "expected_return": float(f.expected_return),
            "expected_risk": float(f.expected_risk),
            "sharpe_ratio": float(f.sharpe_ratio)
        }
        for f in frontier
    ]
    
    returns_list = [float(f.expected_return) for f in frontier]
    risks_list = [float(f.expected_risk) for f in frontier]
    
    return EfficientFrontierResponse(
        frontier=frontier_data,
        min_return=min(returns_list),
        max_return=max(returns_list),
        min_risk=min(risks_list),
        max_risk=max(risks_list),
        success=True,
        message=f"Efficient frontier with {data.n_portfolios} portfolios",
        computed_in_ms=sum(f.compute_time_ms for f in frontier) / len(frontier)
    )
