from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
from copy import deepcopy

from .strategies.base_strategy import BaseStrategy
from .strategies.sma_crossover import SMACrossoverStrategy
from .strategies.rsi_mean_reversion import RSIMeanReversionStrategy
from .metrics import PerformanceMetrics


class BacktestingEngine:
    """
    Core backtesting engine.

    Executes trading strategies on historical data and calculates performance metrics.
    """

    DEFAULT_COMMISSION_RATE = Decimal("0.001")
    DEFAULT_SLIPPAGE_RATE = Decimal("0.0001")
    DEFAULT_POSITION_SIZE = Decimal("0.1")

    def __init__(
        self,
        initial_capital: Decimal,
        commission_rate: Decimal = None,
        slippage_rate: Decimal = None,
    ):
        self.initial_capital = Decimal(str(initial_capital))
        self.cash = self.initial_capital
        self.commission_rate = commission_rate or self.DEFAULT_COMMISSION_RATE
        self.slippage_rate = slippage_rate or self.DEFAULT_SLIPPAGE_RATE

        self.positions: Dict[str, Dict] = {}
        self.equity_curve: List[Dict] = []
        self.drawdown_curve: List[Dict] = []
        self.trades: List[Dict] = []

        self.current_value = self.initial_capital
        self.peak_value = self.initial_capital

        self._strategy: Optional[BaseStrategy] = None
        self._data: pd.DataFrame = pd.DataFrame()

    def set_strategy(self, strategy: BaseStrategy):
        """Set the trading strategy."""
        self._strategy = strategy

    def _get_strategy(self, strategy_type: str, config: Dict = None) -> BaseStrategy:
        """Factory method to create strategy by type."""
        strategies = {
            "sma_crossover": SMACrossoverStrategy,
            "rsi_mean_reversion": RSIMeanReversionStrategy,
        }
        strategy_class = strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        return strategy_class(config)

    def load_data(self, data: pd.DataFrame):
        """Load historical price data."""
        self._data = data.copy()

    def run(
        self,
        strategy_type: str,
        config: Dict = None,
        start_date: date = None,
        end_date: date = None,
    ) -> Dict:
        """
        Execute backtest.

        Args:
            strategy_type: Type of strategy to use
            config: Strategy configuration
            start_date: Filter data by start date
            end_date: Filter data by end date

        Returns:
            Dictionary with backtest results and metrics
        """
        self._strategy = self._get_strategy(strategy_type, config)

        data = self._filter_data_by_date(self._data, start_date, end_date)

        if data.empty:
            return {
                "error": "No data available for specified date range",
                "equity_curve": [],
                "trades": [],
                "metrics": {},
            }

        timestamps = self._get_timestamps(data)

        for timestamp in timestamps:
            day_data = self._get_data_for_timestamp(data, timestamp)

            self._update_portfolio_value(day_data)

            signals = self._strategy.generate_signals(day_data, timestamp)

            for signal in signals:
                self._execute_trade(signal, timestamp)

            self._record_equity(timestamp)

        metrics = PerformanceMetrics.calculate_all_metrics(
            self.equity_curve, self.trades, self.initial_capital
        )

        return {
            "equity_curve": self.equity_curve,
            "drawdown_curve": self.drawdown_curve,
            "trades": self.trades,
            "metrics": metrics,
            "final_value": float(self.current_value),
            "total_return": metrics.get("total_return", 0),
        }

    def _filter_data_by_date(
        self, data: pd.DataFrame, start_date: date = None, end_date: date = None
    ) -> pd.DataFrame:
        """Filter data by date range."""
        if data.empty:
            return data

        df = data.copy()

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            if start_date:
                df = df[df["date"] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df["date"] <= pd.to_datetime(end_date)]

        return df

    def _get_timestamps(self, data: pd.DataFrame) -> List[datetime]:
        """Get sorted list of unique timestamps from data."""
        if data.empty:
            return []

        if "date" in data.columns:
            return sorted(data["date"].unique())
        elif "timestamp" in data.columns:
            return sorted(data["timestamp"].unique())

        return []

    def _get_data_for_timestamp(
        self, data: pd.DataFrame, timestamp: datetime
    ) -> pd.DataFrame:
        """Get all data up to and including the given timestamp."""
        if data.empty:
            return data

        df = data.copy()

        date_col = "date" if "date" in df.columns else "timestamp"
        if date_col not in df.columns:
            return df

        df = df[df[date_col] <= timestamp]
        return df

    def _update_portfolio_value(self, data: pd.DataFrame):
        """Calculate current portfolio value."""
        total_value = self.cash

        for symbol, position in self.positions.items():
            quantity = position.get("quantity", 0)
            current_price = self._get_current_price(data, symbol)

            if current_price:
                position_value = float(quantity) * current_price
                total_value += Decimal(str(position_value))

        self.current_value = Decimal(str(total_value))

        if self.current_value > self.peak_value:
            self.peak_value = self.current_value

    def _get_current_price(self, data: pd.DataFrame, symbol: str) -> Optional[float]:
        """Get the most recent price for an asset."""
        if data.empty:
            return None

        asset_data = data[data.get("asset_symbol", "DEFAULT") == symbol]
        if asset_data.empty:
            return None

        if "close" in asset_data.columns:
            return float(asset_data.iloc[-1]["close"])
        return None

    def _execute_trade(self, signal: Dict, timestamp: datetime):
        """Execute a trade based on signal."""
        symbol = signal.get("asset_symbol", "DEFAULT")
        action = signal.get("action", "BUY")
        price = signal.get("price", 0)
        position_size = signal.get("position_size", 0.1)

        if price <= 0:
            return

        trade_value = float(self.current_value) * position_size
        quantity = trade_value / price

        commission = trade_value * float(self.commission_rate)
        slippage = trade_value * float(self.slippage_rate)
        total_cost = trade_value + commission + slippage

        if action == "BUY":
            if float(self.cash) < total_cost:
                return

            self.cash -= Decimal(str(total_cost))

            if symbol not in self.positions:
                self.positions[symbol] = {"quantity": 0, "avg_price": price}

            current_qty = self.positions[symbol]["quantity"]
            current_avg = self.positions[symbol].get("avg_price", price)

            new_qty = current_qty + quantity
            new_avg = (
                ((current_qty * current_avg) + (quantity * price)) / new_qty
                if new_qty > 0
                else price
            )

            self.positions[symbol]["quantity"] = new_qty
            self.positions[symbol]["avg_price"] = new_avg

            self.trades.append(
                {
                    "asset_symbol": symbol,
                    "action": "BUY",
                    "quantity": round(quantity, 6),
                    "price": round(price, 4),
                    "value": round(trade_value, 2),
                    "commission": round(commission, 4),
                    "slippage": round(slippage, 4),
                    "timestamp": timestamp.isoformat()
                    if isinstance(timestamp, datetime)
                    else str(timestamp),
                    "pnl": None,
                    "pnl_percent": None,
                }
            )

        elif action == "SELL":
            if symbol not in self.positions:
                return

            current_qty = self.positions[symbol]["quantity"]
            if quantity > current_qty:
                quantity = current_qty

            if quantity <= 0:
                return

            sell_value = quantity * price
            net_value = sell_value - commission - slippage

            self.cash += Decimal(str(net_value))
            self.positions[symbol]["quantity"] -= quantity

            entry_price = self.positions[symbol].get("avg_price", price)
            pnl = (price - entry_price) * quantity
            pnl_percent = (
                ((price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
            )

            self.trades.append(
                {
                    "asset_symbol": symbol,
                    "action": "SELL",
                    "quantity": round(quantity, 6),
                    "price": round(price, 4),
                    "value": round(sell_value, 2),
                    "commission": round(commission, 4),
                    "slippage": round(slippage, 4),
                    "timestamp": timestamp.isoformat()
                    if isinstance(timestamp, datetime)
                    else str(timestamp),
                    "pnl": round(pnl, 2),
                    "pnl_percent": round(pnl_percent, 4),
                }
            )

            if self.positions[symbol]["quantity"] <= 0:
                del self.positions[symbol]

    def _record_equity(self, timestamp: datetime):
        """Record current equity for equity curve."""
        self.equity_curve.append(
            {
                "timestamp": timestamp.isoformat()
                if isinstance(timestamp, datetime)
                else str(timestamp),
                "value": float(self.current_value),
                "cash": float(self.cash),
                "positions_value": float(self.current_value) - float(self.cash),
            }
        )

        drawdown = 0
        if self.peak_value > 0:
            drawdown = (
                (float(self.peak_value) - float(self.current_value))
                / float(self.peak_value)
            ) * 100

        self.drawdown_curve.append(
            {
                "timestamp": timestamp.isoformat()
                if isinstance(timestamp, datetime)
                else str(timestamp),
                "drawdown": round(drawdown, 4),
            }
        )

    def reset(self):
        """Reset engine state for new backtest."""
        self.cash = self.initial_capital
        self.positions = {}
        self.equity_curve = []
        self.drawdown_curve = []
        self.trades = []
        self.current_value = self.initial_capital
        self.peak_value = self.initial_capital

        if self._strategy:
            self._strategy.reset()
