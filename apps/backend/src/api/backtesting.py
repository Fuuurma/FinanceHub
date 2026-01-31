from ninja import Router, Schema
from typing import List, Optional
from decimal import Decimal
from datetime import date
from pydantic import Field
from django.db import transaction

from investments.models.backtesting import Backtest, TradingStrategy, BacktestTrade
from backtesting.engine import BacktestingEngine
from backtesting.strategies.base_strategy import BaseStrategy

router = Router()


class BacktestCreateSchema(Schema):
    name: str
    strategy_type: str
    config: dict = Field(default_factory=dict)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    initial_capital: Decimal = Decimal("10000")
    asset_symbols: List[str] = Field(default_factory=list)


class BacktestResponseSchema(Schema):
    id: str
    name: str
    status: str
    start_date: date
    end_date: date
    initial_capital: Decimal
    total_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    total_trades: Optional[int] = None
    created_at: str


class BacktestMetricsSchema(Schema):
    total_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    total_trades: Optional[int] = None
    winning_trades: Optional[int] = None
    losing_trades: Optional[int] = None


class BacktestResultSchema(Schema):
    id: str
    name: str
    status: str
    metrics: BacktestMetricsSchema
    equity_curve: List[dict]
    drawdown_curve: List[dict]
    trades: List[dict]
    final_value: float
    total_return: float


class StrategyCreateSchema(Schema):
    name: str
    strategy_type: str
    config: dict = Field(default_factory=dict)
    description: str = ""
    is_public: bool = False


class StrategyResponseSchema(Schema):
    id: str
    name: str
    strategy_type: str
    config: dict
    description: str
    is_public: bool
    created_at: str


@router.post("/backtests", response=BacktestResponseSchema)
def create_backtest(request, data: BacktestCreateSchema):
    """Create and run a new backtest."""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        backtest = Backtest.objects.create(
            user=request.user,
            name=data.name,
            strategy=None,
            start_date=data.start_date or date.today(),
            end_date=data.end_date or date.today(),
            initial_capital=data.initial_capital,
            status="pending",
        )

        return {
            "id": str(backtest.id),
            "name": backtest.name,
            "status": backtest.status,
            "start_date": backtest.start_date,
            "end_date": backtest.end_date,
            "initial_capital": backtest.initial_capital,
            "total_return": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "max_drawdown": None,
            "win_rate": None,
            "profit_factor": None,
            "total_trades": None,
            "created_at": backtest.created_at.isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}, 400


@router.get("/backtests/{backtest_id}", response=BacktestResultSchema)
def get_backtest(request, backtest_id: str):
    """Get backtest results."""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        backtest = Backtest.objects.get(id=backtest_id, user=request.user)
    except Backtest.DoesNotExist:
        return {"error": "Backtest not found"}, 404

    return {
        "id": str(backtest.id),
        "name": backtest.name,
        "status": backtest.status,
        "metrics": {
            "total_return": float(backtest.total_return)
            if backtest.total_return
            else None,
            "sharpe_ratio": float(backtest.sharpe_ratio)
            if backtest.sharpe_ratio
            else None,
            "sortino_ratio": float(backtest.sortino_ratio)
            if backtest.sortino_ratio
            else None,
            "max_drawdown": float(backtest.max_drawdown)
            if backtest.max_drawdown
            else None,
            "win_rate": float(backtest.win_rate) if backtest.win_rate else None,
            "profit_factor": float(backtest.profit_factor)
            if backtest.profit_factor
            else None,
            "total_trades": backtest.total_trades,
            "winning_trades": backtest.winning_trades,
            "losing_trades": backtest.losing_trades,
        },
        "equity_curve": backtest.equity_curve,
        "drawdown_curve": backtest.drawdown_curve,
        "trades": backtest.trades_data,
        "final_value": float(backtest.initial_capital)
        * (1 + float(backtest.total_return) / 100)
        if backtest.total_return
        else float(backtest.initial_capital),
        "total_return": float(backtest.total_return) if backtest.total_return else 0,
    }


@router.get("/backtests", response=List[BacktestResponseSchema])
def list_backtests(request):
    """List all backtests for current user."""
    if not request.user.is_authenticated:
        return []

    backtests = Backtest.objects.filter(user=request.user).order_by("-created_at")

    return [
        {
            "id": str(b.id),
            "name": b.name,
            "status": b.status,
            "start_date": b.start_date,
            "end_date": b.end_date,
            "initial_capital": b.initial_capital,
            "total_return": float(b.total_return) if b.total_return else None,
            "sharpe_ratio": float(b.sharpe_ratio) if b.sharpe_ratio else None,
            "sortino_ratio": float(b.sortino_ratio) if b.sortino_ratio else None,
            "max_drawdown": float(b.max_drawdown) if b.max_drawdown else None,
            "win_rate": float(b.win_rate) if b.win_rate else None,
            "profit_factor": float(b.profit_factor) if b.profit_factor else None,
            "total_trades": b.total_trades,
            "created_at": b.created_at.isoformat(),
        }
        for b in backtests
    ]


@router.post("/strategies", response=StrategyResponseSchema)
def create_strategy(request, data: StrategyCreateSchema):
    """Create a new trading strategy."""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        strategy = TradingStrategy.objects.create(
            user=request.user,
            name=data.name,
            strategy_type=data.strategy_type,
            config=data.config,
            description=data.description,
            is_public=data.is_public,
        )

        return {
            "id": str(strategy.id),
            "name": strategy.name,
            "strategy_type": strategy.strategy_type,
            "config": strategy.config,
            "description": strategy.description,
            "is_public": strategy.is_public,
            "created_at": strategy.created_at.isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}, 400


@router.get("/strategies", response=List[StrategyResponseSchema])
def list_strategies(request):
    """List all strategies for current user."""
    if not request.user.is_authenticated:
        return []

    strategies = TradingStrategy.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    return [
        {
            "id": str(s.id),
            "name": s.name,
            "strategy_type": s.strategy_type,
            "config": s.config,
            "description": s.description,
            "is_public": s.is_public,
            "created_at": s.created_at.isoformat(),
        }
        for s in strategies
    ]


@router.get("/strategies/{strategy_id}", response=StrategyResponseSchema)
def get_strategy(request, strategy_id: str):
    """Get a specific strategy."""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        strategy = TradingStrategy.objects.get(id=strategy_id, user=request.user)
    except TradingStrategy.DoesNotExist:
        return {"error": "Strategy not found"}, 404

    return {
        "id": str(strategy.id),
        "name": strategy.name,
        "strategy_type": strategy.strategy_type,
        "config": strategy.config,
        "description": strategy.description,
        "is_public": strategy.is_public,
        "created_at": strategy.created_at.isoformat(),
    }


@router.delete("/backtests/{backtest_id}")
def delete_backtest(request, backtest_id: str):
    """Delete a backtest."""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        backtest = Backtest.objects.get(id=backtest_id, user=request.user)
        backtest.delete()
        return {"success": True}
    except Backtest.DoesNotExist:
        return {"error": "Backtest not found"}, 404
