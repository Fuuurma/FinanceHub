"""
Dramatiq tasks for backtesting operations.
"""

import logging
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
import dramatiq

from investments.models import Backtest, BacktestTrade, TradingStrategy
from investments.services.backtesting.backtesting_engine import (
    BacktestingEngine,
    BacktestConfig,
)
from investments.services.strategies.sma_crossover import SMACrossoverStrategy
from investments.services.strategies.rsi_mean_reversion import RSIMeanReversionStrategy

logger = logging.getLogger(__name__)


def get_strategy_instance(strategy_type: str, config: dict):
    """Factory function to get strategy instance."""
    if strategy_type == "sma_crossover":
        return SMACrossoverStrategy(config)
    elif strategy_type == "rsi_mean_reversion":
        return RSIMeanReversionStrategy(config)
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")


def load_historical_data(
    asset_ids: list, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    """Load historical price data for backtesting."""
    from assets.models.asset import Asset
    from assets.models.historic.prices import AssetPricesHistoric

    dataframes = []

    for asset_id in asset_ids:
        try:
            asset = Asset.objects.get(id=asset_id)
            prices = AssetPricesHistoric.objects.filter(
                asset=asset,
                date__gte=start_date,
                date__lte=end_date,
            ).order_by("date")

            if prices.exists():
                df = pd.DataFrame(
                    {
                        "date": [p.date for p in prices],
                        "asset_id": asset_id,
                        "open": [float(p.open) for p in prices],
                        "high": [float(p.high) for p in prices],
                        "low": [float(p.low) for p in prices],
                        "close": [float(p.close) for p in prices],
                        "volume": [
                            float(p.volume) if hasattr(p, "volume") and p.volume else 0
                            for p in prices
                        ],
                    }
                )
                dataframes.append(df)

        except Asset.DoesNotExist:
            logger.warning(f"Asset {asset_id} not found")
            continue

    if not dataframes:
        raise ValueError("No price data available for the specified assets")

    return pd.concat(dataframes, ignore_index=True)


@dramatiq.actor
def run_backtest_task(backtest_id: str):
    """
    Execute backtest asynchronously.

    This task is designed to be run via Dramatiq for non-blocking backtest execution.
    """
    try:
        logger.info(f"Starting async backtask for ID: {backtest_id}")

        backtest = Backtest.objects.get(id=backtest_id)
        backtest.status = "running"
        backtest.save()

        config = BacktestConfig(
            initial_capital=float(backtest.initial_capital),
            position_size_pct=0.10,
            max_positions=5,
            stop_loss_pct=0.10,
            take_profit_pct=0.20,
            transaction_cost_pct=0.001,
            slippage_pct=0.0005,
        )

        engine = BacktestingEngine(config=config)

        data = load_historical_data(
            asset_ids=[backtest.id],
            start_date=backtest.start_date,
            end_date=backtest.end_date,
        )

        if data.empty:
            backtest.status = "failed"
            backtest.error_message = "No data available for backtest period"
            backtest.save()
            return

        strategy = get_strategy_instance(
            strategy_type="sma_crossover",
            config={"fast_period": 10, "slow_period": 20},
        )

        result = engine.run_backtest(
            data=data,
            strategy=strategy,
            strategy_name=backtest.name,
            start_date=backtest.start_date,
            end_date=backtest.end_date,
        )

        backtest.status = "completed"
        backtest.total_return = Decimal(str(result.total_return_pct))
        backtest.sharpe_ratio = Decimal(str(result.sharpe_ratio))
        backtest.sortino_ratio = Decimal(str(result.sortino_ratio))
        backtest.max_drawdown = Decimal(str(result.max_drawdown_pct))
        backtest.win_rate = Decimal(str(result.win_rate))
        backtest.profit_factor = Decimal(str(result.profit_factor))
        backtest.total_trades = result.total_trades
        backtest.winning_trades = result.winning_trades
        backtest.losing_trades = result.losing_trades
        backtest.equity_curve = result.equity_curve
        backtest.trades_data = [
            {
                "entry_date": t.entry_date.isoformat() if t.entry_date else None,
                "exit_date": t.exit_date.isoformat() if t.exit_date else None,
                "pnl": t.pnl,
                "pnl_pct": t.pnl_pct,
            }
            for t in result.trades
        ]
        backtest.save()

        logger.info(
            f"Backtest {backtest_id} completed: {result.total_trades} trades, {result.total_return_pct:.2f}%"
        )

    except Backtest.DoesNotExist:
        logger.error(f"Backtest {backtest_id} not found")
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Backtest {backtest_id} failed: {e}")
        try:
            backtest = Backtest.objects.get(id=backtest_id)
            backtest.status = "failed"
            backtest.error_message = str(e)
            backtest.save()
        except Backtest.DoesNotExist:
            pass
