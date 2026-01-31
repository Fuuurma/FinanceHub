"""
Backtesting Engine
Core engine for running strategy backtests.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtest."""
    initial_capital: float = 100000
    position_size_pct: float = 0.20
    max_positions: int = 5
    stop_loss_pct: float = 0.10
    take_profit_pct: float = 0.20
    transaction_cost_pct: float = 0.001
    slippage_pct: float = 0.0005
    allow_short: bool = False
    allow_leverage: bool = False
    max_leverage: float = 1.0


@dataclass
class Trade:
    """Single trade record."""
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    quantity: float = 0
    direction: str = 'LONG'
    pnl: float = 0
    pnl_pct: float = 0
    status: str = 'OPEN'
    reason: str = ''


@dataclass
class Position:
    """Active position."""
    asset_symbol: str
    quantity: float
    entry_price: float
    entry_date: datetime
    direction: str = 'LONG'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class BacktestResult:
    """Complete backtest results."""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    annual_return_pct: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_trade_duration_days: float
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[Dict] = field(default_factory=list)
    monthly_returns: Dict[str, float] = field(default_factory=dict)


class BacktestingEngine:
    """Core backtesting engine."""

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
        self.cash: float = 0
        self.total_value: float = 0

    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy,
        strategy_name: str = 'Strategy',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> BacktestResult:
        """
        Run backtest on historical data.

        Args:
            data: DataFrame with OHLCV data, indexed by date
            strategy: Strategy object with generate_signals() method
            strategy_name: Name for reporting
            start_date: Start date for backtest
            end_date: End date for backtest

        Returns:
            BacktestResult with all metrics
        """
        logger.info(f"Starting backtest: {strategy_name}")

        df = data.copy()

        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        if df.empty:
            raise ValueError("No data available for backtest period")

        self._initialize_backtest(df)

        for date, row in df.iterrows():
            self._process_date(date, row, strategy)

        self._close_all_positions(df.index[-1], df.iloc[-1])

        result = self._calculate_metrics(df, strategy_name)

        logger.info(f"Backtest complete: {result.total_trades} trades, {result.total_return_pct:.2f}% return")

        return result

    def _initialize_backtest(self, df: pd.DataFrame):
        """Initialize backtest state."""
        self.cash = self.config.initial_capital
        self.total_value = self.config.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = [
            {'date': df.index[0], 'equity': self.config.initial_capital, 'cash': self.cash}
        ]

    def _process_date(self, date: datetime, row: pd.Series, strategy):
        """Process a single date."""
        current_price = row.get('close_price', row.get('close', 0))
        if current_price == 0:
            return

        signals = strategy.generate_signals(df=row.to_dict(), timestamp=date)

        for signal in signals:
            self._execute_signal(signal, date, current_price)

        self._update_positions(date, current_price)
        self._record_equity(date)

    def _execute_signal(self, signal: Dict, date: datetime, price: float):
        """Execute a trading signal."""
        symbol = signal.get('asset_symbol', signal.get('symbol'))
        if not symbol:
            return

        action = signal.get('action', '').upper()
        direction = signal.get('direction', 'LONG').upper()

        if action == 'BUY' and symbol not in self.positions:
            if len(self.positions) >= self.config.max_positions:
                return

            position_size = self._calculate_position_size(price)
            if position_size <= 0:
                return

            self.cash -= position_size * price
            self.positions[symbol] = Position(
                asset_symbol=symbol,
                quantity=position_size,
                entry_price=price,
                entry_date=date,
                direction=direction,
                stop_loss=price * (1 - self.config.stop_loss_pct) if direction == 'LONG' else None,
                take_profit=price * (1 + self.config.take_profit_pct) if direction == 'LONG' else None,
            )

        elif action == 'SELL' and symbol in self.positions:
            position = self.positions[symbol]
            self._close_position(symbol, date, price, signal.get('reason', ''))

    def _calculate_position_size(self, price: float) -> float:
        """Calculate position size based on capital and risk."""
        max_position_value = self.total_value * self.config.position_size_pct
        position_value = min(max_position_value, self.cash)
        return position_value / price

    def _update_positions(self, date: datetime, price: float):
        """Update positions and check stop loss/take profit."""
        closed = []
        for symbol, position in self.positions.items():
            if position.direction == 'LONG':
                if position.stop_loss and price <= position.stop_loss:
                    closed.append((symbol, date, price, 'Stop Loss'))
                elif position.take_profit and price >= position.take_profit:
                    closed.append((symbol, date, price, 'Take Profit'))

        for symbol, exit_date, exit_price, reason in closed:
            self._close_position(symbol, exit_date, exit_price, reason)

    def _close_position(self, symbol: str, date: datetime, price: float, reason: str):
        """Close a position and record trade."""
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        pnl = (price - position.entry_price) * position.quantity
        pnl_pct = ((price - position.entry_price) / position.entry_price) * 100

        trade = Trade(
            entry_date=position.entry_date,
            entry_price=position.entry_price,
            exit_date=date,
            exit_price=price,
            quantity=position.quantity,
            direction=position.direction,
            pnl=pnl,
            pnl_pct=pnl_pct,
            status='CLOSED',
            reason=reason,
        )
        self.trades.append(trade)
        self.cash += position.quantity * price
        del self.positions[symbol]

    def _close_all_positions(self, date: datetime, last_row: pd.Series):
        """Close all open positions at end of backtest."""
        current_price = last_row.get('close_price', last_row.get('close', 0))
        if current_price == 0:
            return

        for symbol in list(self.positions.keys()):
            self._close_position(symbol, date, current_price, 'End of Backtest')

    def _record_equity(self, date: datetime):
        """Record equity curve point."""
        position_value = sum(
            p.quantity * p.entry_price for p in self.positions.values()
        )
        self.total_value = self.cash + position_value
        self.equity_curve.append({
            'date': date,
            'equity': self.total_value,
            'cash': self.cash,
        })

    def _calculate_metrics(self, df: pd.DataFrame, strategy_name: str) -> BacktestResult:
        """Calculate all performance metrics."""
        if not self.equity_curve:
            return BacktestResult(
                strategy_name=strategy_name,
                start_date=df.index[0],
                end_date=df.index[-1],
                initial_capital=self.config.initial_capital,
                final_capital=self.config.initial_capital,
                total_return=0,
                total_return_pct=0,
                annual_return_pct=0,
                max_drawdown=0,
                max_drawdown_pct=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                win_rate=0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_trade_duration_days=0,
                avg_win_pct=0,
                avg_loss_pct=0,
                profit_factor=0,
            )

        equity = [e['equity'] for e in self.equity_curve]
        initial = self.equity_curve[0]['equity']
        final = self.equity_curve[-1]['equity']

        total_return = final - initial
        total_return_pct = (total_return / initial) * 100

        returns = np.diff(equity) / equity[:-1]
        returns = returns[~np.isnan(returns)]

        days = (df.index[-1] - df.index[0]).days
        years = max(days / 365, 0.001)
        annual_return_pct = ((final / initial) ** (1 / years) - 1) * 100

        equity_series = pd.Series(equity)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown_pct = abs(drawdown.min()) * 100
        max_drawdown = abs(drawdown.min()) * initial

        if len(returns) > 1 and np.std(returns) > 0:
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) * 100
            downside_returns = returns[returns < 0]
            sortino_ratio = (np.mean(returns) / np.std(downside_returns) * np.sqrt(252) * 100) if len(downside_returns) > 0 else 0
        else:
            sharpe_ratio = 0
            sortino_ratio = 0

        closed_trades = [t for t in self.trades if t.status == 'CLOSED']
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl <= 0]

        total_trades = len(closed_trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

        avg_win = np.mean([t.pnl_pct for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl_pct for t in losing_trades]) if losing_trades else 0

        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        trade_durations = [
            (t.exit_date - t.entry_date).days for t in closed_trades if t.exit_date
        ]
        avg_trade_duration_days = np.mean(trade_durations) if trade_durations else 0

        return BacktestResult(
            strategy_name=strategy_name,
            start_date=df.index[0],
            end_date=df.index[-1],
            initial_capital=initial,
            final_capital=final,
            total_return=total_return,
            total_return_pct=total_return_pct,
            annual_return_pct=annual_return_pct,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            win_rate=win_rate,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_trade_duration_days=avg_trade_duration_days,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            profit_factor=profit_factor,
            trades=closed_trades,
            equity_curve=self.equity_curve,
        )


class SMACrossoverStrategy:
    """Simple Moving Average Crossover Strategy."""

    def __init__(self, fast_period: int = 10, slow_period: int = 20):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = f"SMA Crossover ({fast_period}/{slow_period})"

    def generate_signals(self, df: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        """Generate trading signals based on SMA crossover."""
        if len(df) < self.slow_period + 1:
            return []

        close_prices = list(df.values())
        sma_fast = np.mean(close_prices[-self.fast_period:])
        sma_slow = np.mean(close_prices[-self.slow_period:])
        prev_fast = np.mean(close_prices[-self.fast_period-1:-1])
        prev_slow = np.mean(close_prices[-self.slow_period-1:-1])

        signals = []
        if prev_fast <= prev_slow and sma_fast > sma_slow:
            signals.append({
                'action': 'BUY',
                'reason': f'SMA {self.fast_period} crossed above SMA {self.slow_period}',
            })
        elif prev_fast >= prev_slow and sma_fast < sma_slow:
            signals.append({
                'action': 'SELL',
                'reason': f'SMA {self.fast_period} crossed below SMA {self.slow_period}',
            })

        return signals


class RSIStrategy:
    """RSI Mean Reversion Strategy."""

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.name = f"RSI ({period}, {oversold}/{overbought})"

    def generate_signals(self, df: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        """Generate signals based on RSI levels."""
        if len(df) < self.period + 1:
            return []

        close_prices = list(df.values())
        deltas = np.diff(close_prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-self.period:])
        avg_loss = np.mean(losses[-self.period:])
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs))

        signals = []
        if rsi < self.oversold:
            signals.append({
                'action': 'BUY',
                'reason': f'RSI {rsi:.1f} oversold',
            })
        elif rsi > self.overbought:
            signals.append({
                'action': 'SELL',
                'reason': f'RSI {rsi:.1f} overbought',
            })

        return signals
