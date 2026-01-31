from typing import Dict, List, Optional
from decimal import Decimal
import numpy as np


class PerformanceMetrics:
    """
    Calculate performance metrics for backtest results.
    """

    RISK_FREE_RATE = Decimal("0.05")
    TRADING_DAYS_PER_YEAR = 252

    @staticmethod
    def calculate_total_return(
        initial_capital: Decimal, final_value: Decimal
    ) -> Decimal:
        """Calculate total percentage return."""
        if initial_capital == 0:
            return Decimal("0")
        return ((final_value - initial_capital) / initial_capital) * 100

    @staticmethod
    def calculate_sharpe_ratio(
        returns: List[Decimal], risk_free_rate: Decimal = None
    ) -> Optional[float]:
        """Calculate annualized Sharpe ratio."""
        if not returns or len(returns) < 2:
            return None

        returns_array = np.array([float(r) for r in returns])
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array, ddof=1)

        if std_return == 0:
            return 0.0

        rf = float(risk_free_rate or PerformanceMetrics.RISK_FREE_RATE) / 100
        daily_rf = rf / PerformanceMetrics.TRADING_DAYS_PER_YEAR

        sharpe = (
            (mean_return - daily_rf)
            * np.sqrt(PerformanceMetrics.TRADING_DAYS_PER_YEAR)
            / std_return
        )
        return round(float(sharpe), 4)

    @staticmethod
    def calculate_sortino_ratio(
        returns: List[Decimal], risk_free_rate: Decimal = None
    ) -> Optional[float]:
        """Calculate annualized Sortino ratio (uses downside deviation only)."""
        if not returns or len(returns) < 2:
            return None

        returns_array = np.array([float(r) for r in returns])
        mean_return = np.mean(returns_array)

        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) == 0:
            return float("inf")

        downside_std = np.std(downside_returns, ddof=1)
        if downside_std == 0:
            return 0.0

        rf = float(risk_free_rate or PerformanceMetrics.RISK_FREE_RATE) / 100
        daily_rf = rf / PerformanceMetrics.TRADING_DAYS_PER_YEAR

        sortino = (
            (mean_return - daily_rf)
            * np.sqrt(PerformanceMetrics.TRADING_DAYS_PER_YEAR)
            / downside_std
        )
        return round(float(sortino), 4)

    @staticmethod
    def calculate_max_drawdown(equity_curve: List[Decimal]) -> Optional[float]:
        """Calculate maximum drawdown percentage."""
        if not equity_curve:
            return None

        equity_array = np.array([float(e) for e in equity_curve])
        peak = np.maximum.accumulate(equity_array)
        drawdowns = (peak - equity_array) / peak
        max_dd = np.max(drawdowns) * 100
        return round(float(max_dd), 4)

    @staticmethod
    def calculate_win_rate(trades: List[Dict]) -> Optional[float]:
        """Calculate percentage of winning trades."""
        if not trades:
            return None

        winning_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
        total_trades = len(trades)

        if total_trades == 0:
            return 0.0

        return round((winning_trades / total_trades) * 100, 4)

    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> Optional[float]:
        """Calculate profit factor (gross profit / gross loss)."""
        if not trades:
            return None

        gross_profit = sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0)
        gross_loss = abs(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0))

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return round(float(gross_profit / gross_loss), 4)

    @staticmethod
    def calculate_all_metrics(
        equity_curve: List[Dict], trades: List[Dict], initial_capital: Decimal
    ) -> Dict:
        """Calculate all performance metrics at once."""
        equity_values = [e.get("value", 0) for e in equity_curve]
        returns = PerformanceMetrics._calculate_daily_returns(equity_values)

        final_value = equity_values[-1] if equity_values else initial_capital

        metrics = {
            "total_return": float(
                PerformanceMetrics.calculate_total_return(
                    initial_capital, Decimal(str(final_value))
                )
            ),
            "sharpe_ratio": PerformanceMetrics.calculate_sharpe_ratio(returns),
            "sortino_ratio": PerformanceMetrics.calculate_sortino_ratio(returns),
            "max_drawdown": PerformanceMetrics.calculate_max_drawdown(equity_values),
            "win_rate": PerformanceMetrics.calculate_win_rate(trades),
            "profit_factor": PerformanceMetrics.calculate_profit_factor(trades),
        }

        winning_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
        losing_trades = sum(1 for t in trades if t.get("pnl", 0) < 0)

        metrics["total_trades"] = len(trades)
        metrics["winning_trades"] = winning_trades
        metrics["losing_trades"] = losing_trades

        return metrics

    @staticmethod
    def _calculate_daily_returns(equity_values: List[float]) -> List[Decimal]:
        """Calculate daily returns from equity curve."""
        if len(equity_values) < 2:
            return []

        returns = []
        for i in range(1, len(equity_values)):
            if equity_values[i - 1] != 0:
                ret = (equity_values[i] - equity_values[i - 1]) / equity_values[i - 1]
                returns.append(Decimal(str(ret)))
        return returns
