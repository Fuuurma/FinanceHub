"""
Backtesting API
Endpoints for running and managing backtests.
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from ninja import Router
from pydantic import BaseModel
from backtesting.engine import BacktestingEngine
from backtesting.strategies.sma_crossover import SMACrossoverStrategy
from backtesting.strategies.rsi_mean_reversion import RSIMeanReversionStrategy
from investments.models import TradingStrategy, Backtest

router = Router(tags=["Backtesting"])
logger = logging.getLogger(__name__)


class BacktestCreateSchema(BaseModel):
    strategy_id: Optional[str] = None
    strategy_type: str = "sma_crossover"
    asset_ids: List[str]
    start_date: str
    end_date: str
    initial_capital: float = 100000
    config: dict = {}


class BacktestResponseSchema(BaseModel):
    id: str
    status: str
    metrics: Optional[dict] = None
    total_trades: Optional[int] = None


@router.get("/strategies")
def list_strategies(request):
    """List available strategy types."""
    return {
        "strategies": [
            {"id": "sma_crossover", "name": "SMA Crossover"},
            {"id": "rsi_mean_reversion", "name": "RSI Mean Reversion"},
        ]
    }


@router.post("/backtests", response=BacktestResponseSchema)
def create_backtest(request, data: BacktestCreateSchema):
    """Create and run a backtest."""
    try:
        start = datetime.strptime(data.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(data.end_date, "%Y-%m-%d").date()

        backtest = Backtest.objects.create(
            user=request.user,
            name=f"Backtest {data.strategy_type} {start} - {end}",
            start_date=start,
            end_date=end,
            initial_capital=Decimal(str(data.initial_capital)),
            status="pending",
        )

        return {"id": str(backtest.id), "status": "pending"}

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Backtest creation error: {e}")
        return {"error": str(e)}, 500


@router.get("/backtests/{backtest_id}")
def get_backtest(request, backtest_id: str):
    """Get backtest results."""
    try:
        backtest = Backtest.objects.get(id=backtest_id, user=request.user)

        return {
            "id": str(backtest.id),
            "name": backtest.name,
            "status": backtest.status,
            "metrics": {
                "total_return": str(backtest.total_return)
                if backtest.total_return
                else None,
                "sharpe_ratio": str(backtest.sharpe_ratio)
                if backtest.sharpe_ratio
                else None,
                "sortino_ratio": str(backtest.sortino_ratio)
                if backtest.sortino_ratio
                else None,
                "max_drawdown": str(backtest.max_drawdown)
                if backtest.max_drawdown
                else None,
                "win_rate": str(backtest.win_rate) if backtest.win_rate else None,
                "profit_factor": str(backtest.profit_factor)
                if backtest.profit_factor
                else None,
            },
            "total_trades": backtest.total_trades,
            "equity_curve": backtest.equity_curve,
            "trades_data": backtest.trades_data,
        }
    except Backtest.DoesNotExist:
        return {"error": "Backtest not found"}, 404


@router.get("/backtests")
def list_backtests(request, limit: int = 20):
    """List user's backtests."""
    backtests = Backtest.objects.filter(user=request.user)[:limit]

    return {
        "backtests": [
            {
                "id": str(b.id),
                "name": b.name,
                "status": b.status,
                "total_return": str(b.total_return) if b.total_return else None,
                "created_at": b.created_at.isoformat(),
            }
            for b in backtests
        ],
        "count": len(backtests),
    }


@router.post("/backtests/{backtest_id}/run")
def run_backtest_async(request, backtest_id: str):
    """Trigger async backtest execution."""
    try:
        backtest = Backtest.objects.get(id=backtest_id, user=request.user)
        backtest.status = "pending"
        backtest.save()

        from investments.tasks import run_backtest_task

        run_backtest_task.send(backtest_id=str(backtest.id))

        return {"status": "started", "backtest_id": str(backtest.id)}

    except Backtest.DoesNotExist:
        return {"error": "Backtest not found"}, 404
