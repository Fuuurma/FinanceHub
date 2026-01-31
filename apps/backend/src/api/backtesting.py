"""
Backtesting API
Endpoints for running and managing backtests.
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from ninja import Router
from pydantic import BaseModel
from backtesting.engine import BacktestingEngine
from backtesting.strategies.sma_crossover import SMACrossoverStrategy
from backtesting.strategies.rsi_mean_reversion import RSIMeanReversionStrategy

router = Router(tags=["Backtesting"])
logger = logging.getLogger(__name__)


class RunBacktestRequest(BaseModel):
    strategy_type: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    fast_period: int = 10
    slow_period: int = 20
    period: int = 14


@router.get("/strategies")
def list_strategies(request):
    return {
        "strategies": [
            {"id": "sma_crossover", "name": "SMA Crossover"},
            {"id": "rsi_mean_reversion", "name": "RSI Mean Reversion"},
        ]
    }


@router.post("/run")
def run_backtest(request, data: RunBacktestRequest):
    try:
        engine = BacktestingEngine(initial_capital=Decimal(str(data.initial_capital)))

        from assets.models.asset import Asset
        from assets.models.historic.prices import AssetPricesHistoric

        start = datetime.strptime(data.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(data.end_date, "%Y-%m-%d").date()

        try:
            asset = Asset.objects.get(ticker_symbol=data.symbol.upper())
        except Asset.DoesNotExist:
            return {"error": "Asset not found"}, 404

        prices = AssetPricesHistoric.objects.filter(
            asset=asset, date__gte=start, date__lte=end
        ).order_by("date")

        if not prices.exists():
            return {"error": "No price data available"}, 400

        import pandas as pd

        df_data = {
            "date": [p.date for p in prices],
            "open_price": [float(p.open) for p in prices],
            "high_price": [float(p.high) for p in prices],
            "low_price": [float(p.low) for p in prices],
            "close_price": [float(p.close) for p in prices],
            "volume": [float(p.volume) for p in prices]
            if hasattr(p, "volume") and p.volume
            else [0] * prices.count(),
        }
        df = pd.DataFrame(df_data)

        engine.load_data(df)

        config = {}
        if data.strategy_type == "sma_crossover":
            config = {"fast_period": data.fast_period, "slow_period": data.slow_period}
        elif data.strategy_type == "rsi_mean_reversion":
            config = {"period": data.period}

        result = engine.run(
            strategy_type=data.strategy_type,
            config=config,
            start_date=start,
            end_date=end,
        )

        if "error" in result:
            return result

        return {
            "status": "success",
            "metrics": {
                "strategy_name": result["metrics"].get(
                    "strategy_name", data.strategy_type
                ),
                "total_return_pct": result["metrics"].get("total_return_pct", 0),
                "annual_return_pct": result["metrics"].get("annual_return_pct", 0),
                "max_drawdown_pct": result["metrics"].get("max_drawdown_pct", 0),
                "sharpe_ratio": result["metrics"].get("sharpe_ratio", 0),
                "win_rate": result["metrics"].get("win_rate", 0),
                "total_trades": result["metrics"].get("total_trades", 0),
                "profit_factor": result["metrics"].get("profit_factor", 0),
            },
            "trades_count": len(result.get("trades", [])),
        }
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {"error": str(e)}, 500


@router.get("/history")
def get_backtest_history(request, limit: int = 20):
    return {"backtests": [], "count": 0}
