"""
Portfolio Optimization API
Provides endpoints for portfolio optimization and strategy backtesting.
"""
from ninja import Router, Schema, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.exceptions import (
    ValidationException,
    ServiceException,
    NotFoundException,
)
from utils.services.optimization import (
    PortfolioOptimizer,
    BacktestEngine,
    OptimizationResult,
    RiskParityResult,
    BacktestResult,
)

router = Router(tags=["Optimization"])


class OptimizeRequest(Schema):
    """Request body for portfolio optimization."""
    returns: Dict[str, List[float]] = Field(
        ..., description="Dictionary mapping symbol to list of returns"
    )
    current_weights: Optional[Dict[str, float]] = Field(
        None, description="Current portfolio weights for turnover calculation"
    )
    method: str = Field(
        default="max_sharpe",
        pattern="^(max_sharpe|min_volatility|risk_parity)$",
        description="Optimization method",
    )
    risk_free_rate: float = Field(default=0.03, ge=0, le=1, description="Risk-free rate")


class OptimizeResponse(Schema):
    """Response for portfolio optimization."""
    success: bool = True
    data: Dict[str, Any] = {
        "weights": {},
        "expected_return": 0.0,
        "expected_volatility": 0.0,
        "sharpe_ratio": 0.0,
        "method": "",
        "interpretation": "",
    }
    fetched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BacktestRequest(Schema):
    """Request body for strategy backtesting."""
    prices: Dict[str, List[float]] = Field(
        ..., description="Dictionary mapping symbol to price series"
    )
    weights: Dict[str, float] = Field(
        ..., description="Target portfolio weights"
    )
    initial_capital: float = Field(
        default=100000, ge=0, description="Starting capital for backtest"
    )
    strategy_name: str = Field(
        default="Strategy", description="Name for the strategy"
    )


class BacktestResponse(Schema):
    """Response for strategy backtest."""
    success: bool = True
    data: Dict[str, Any] = {
        "strategy_name": "",
        "total_return": 0.0,
        "annualized_return": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "win_rate": 0.0,
        "equity_curve": [],
        "interpretation": "",
    }
    fetched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CompareStrategiesRequest(Schema):
    """Request body for comparing multiple strategies."""
    prices: Dict[str, List[float]] = Field(
        ..., description="Dictionary mapping symbol to price series"
    )
    strategies: List[Dict[str, Any]] = Field(
        ...,
        description="List of strategy definitions with name and weights",
    )
    initial_capital: float = Field(default=100000, ge=0)


class CompareStrategiesResponse(Schema):
    """Response comparing multiple strategies."""
    success: bool = True
    data: Dict[str, Any] = {
        "results": {},
        "best_by_sharpe": "",
        "best_by_return": "",
        "best_by_drawdown": "",
    }
    fetched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


@router.post("/optimize", response=OptimizeResponse, summary="Optimize portfolio weights")
async def optimize_portfolio(request, data: OptimizeRequest):
    """
    Find optimal portfolio weights using mean-variance optimization.
    
    Supports three optimization methods:
    - **max_sharpe**: Maximize Sharpe ratio (tangency portfolio)
    - **min_volatility**: Minimize portfolio volatility
    - **risk_parity**: Equal risk contribution across assets
    
    Returns optimal weights, expected return, volatility, and interpretation.
    """
    if len(data.returns) < 2:
        raise ValidationException(
            "At least 2 assets are required for portfolio optimization",
            {"minimum_required": 2, "provided": len(data.returns)},
        )
    
    for symbol, returns in data.returns.items():
        if len(returns) < 10:
            raise ValidationException(
                f"Asset '{symbol}' must have at least 10 return observations",
                {"symbol": symbol, "minimum_required": 10, "provided": len(returns)},
            )
    
    try:
        optimizer = PortfolioOptimizer(
            returns_dict=data.returns,
            current_weights=data.current_weights,
            risk_free_rate=data.risk_free_rate,
        )
        
        if data.method == "max_sharpe":
            result: OptimizationResult = optimizer.optimize_max_sharpe()
        elif data.method == "min_volatility":
            result: OptimizationResult = optimizer.optimize_min_volatility()
        else:
            result: RiskParityResult = optimizer.optimize_risk_parity()
        
        return OptimizeResponse(
            data={
                "weights": result.weights,
                "expected_return": result.expected_return,
                "expected_volatility": result.expected_volatility,
                "sharpe_ratio": result.sharpe_ratio,
                "method": data.method,
                "interpretation": result.interpretation,
            }
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        raise ServiceException(f"Optimization failed: {str(e)}")


@router.post("/backtest", response=BacktestResponse, summary="Backtest trading strategy")
async def backtest_strategy(request, data: BacktestRequest):
    """
    Backtest a trading strategy with given weights.
    
    Calculates comprehensive performance metrics including:
    - Total and annualized returns
    - Sharpe ratio
    - Maximum drawdown
    - Win rate
    - Equity curve
    """
    if len(data.prices) < 1:
        raise ValidationException(
            "At least 1 asset is required for backtesting",
            {"minimum_required": 1, "provided": len(data.prices)},
        )
    
    for symbol, prices in data.prices.items():
        if len(prices) < 30:
            raise ValidationException(
                f"Asset '{symbol}' must have at least 30 price observations",
                {"symbol": symbol, "minimum_required": 30, "provided": len(prices)},
            )
    
    weights_sum = sum(data.weights.values())
    if abs(weights_sum - 1.0) > 0.001:
        raise ValidationException(
            "Portfolio weights must sum to 1.0",
            {"weights_sum": weights_sum, "target": 1.0},
        )
    
    try:
        engine = BacktestEngine(prices=data.prices, initial_capital=data.initial_capital)
        result: BacktestResult = engine.run_strategy(
            weights=data.weights,
            strategy_name=data.strategy_name,
        )
        
        return BacktestResponse(
            data={
                "strategy_name": result.strategy_name,
                "total_return": result.total_return,
                "annualized_return": result.annualized_return,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
                "equity_curve": result.equity_curve,
                "interpretation": result.interpretation,
            }
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        raise ServiceException(f"Backtest failed: {str(e)}")


@router.post("/compare", response=CompareStrategiesResponse, summary="Compare multiple strategies")
async def compare_strategies(request, data: CompareStrategiesRequest):
    """
    Compare multiple trading strategies side by side.
    
    Takes a list of strategies with different weight allocations
    and returns performance comparison with ranking.
    """
    if len(data.strategies) < 2:
        raise ValidationException(
            "At least 2 strategies are required for comparison",
            {"minimum_required": 2, "provided": len(data.strategies)},
        )
    
    try:
        engine = BacktestEngine(prices=data.prices, initial_capital=data.initial_capital)
        
        results = {}
        for strategy in data.strategies:
            name = strategy.get("name", f"Strategy_{len(results)}")
            weights = strategy.get("weights", {})
            if weights:
                result = engine.run_strategy(
                    weights=weights,
                    strategy_name=name,
                )
                results[name] = {
                    "total_return": result.total_return,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "win_rate": result.win_rate,
                }
        
        if not results:
            raise ValidationException("No valid strategies provided")
        
        best_by_sharpe = max(results.keys(), key=lambda k: results[k]["sharpe_ratio"])
        best_by_return = max(results.keys(), key=lambda k: results[k]["total_return"])
        best_by_drawdown = min(
            results.keys(), key=lambda k: results[k]["max_drawdown"]
        )
        
        return CompareStrategiesResponse(
            data={
                "results": results,
                "best_by_sharpe": best_by_sharpe,
                "best_by_return": best_by_return,
                "best_by_drawdown": best_by_drawdown,
            }
        )
    except ValidationException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        raise ServiceException(f"Strategy comparison failed: {str(e)}")
