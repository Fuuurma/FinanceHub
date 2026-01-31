from typing import Dict, List
import pandas as pd
from datetime import datetime
from .base_strategy import BaseStrategy


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.

    Buy: Fast SMA crosses above Slow SMA
    Sell: Fast SMA crosses below Slow SMA

    Configuration:
    - fast_period: Period for fast SMA (default: 10)
    - slow_period: Period for slow SMA (default: 20)
    - position_size: Percentage of portfolio per trade (default: 0.1 = 10%)
    """

    def _initialize(self):
        self.fast_period = self.config.get("fast_period", 10)
        self.slow_period = self.config.get("slow_period", 20)
        self.position_size = self.config.get("position_size", 0.1)
        self._price_history: Dict[str, List[float]] = {}
        self._last_signal: Dict[str, str] = {}

    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        signals = []

        if not self.validate_data(data):
            return signals

        if "asset_symbol" in data.columns:
            symbols = data["asset_symbol"].unique()
        else:
            symbols = ["DEFAULT"]

        for asset_symbol in symbols:
            signal = self._check_crossover(data, asset_symbol, timestamp)
            if signal:
                signals.append(signal)

        return signals

    def _check_crossover(
        self, data: pd.DataFrame, asset_symbol: str, timestamp: datetime
    ) -> Dict:
        asset_data = self.get_asset_data(data, asset_symbol)
        if asset_data.empty or len(asset_data) < self.slow_period + 1:
            return {}

        prices = asset_data["close"].tolist()
        current_price = prices[-1]

        if asset_symbol not in self._price_history:
            self._price_history[asset_symbol] = prices[:-1]
        else:
            self._price_history[asset_symbol].extend(prices[:-1])

        history = self._price_history[asset_symbol][-self.slow_period - 1 :]

        if len(history) < self.slow_period + 1:
            return {}

        fast_sma = sum(history[-self.fast_period :]) / self.fast_period
        slow_sma = sum(history[-self.slow_period :]) / self.slow_period
        prev_fast = sum(history[-self.fast_period - 1 : -1]) / self.fast_period
        prev_slow = sum(history[-self.slow_period - 1 : -1]) / self.slow_period

        last_signal = self._last_signal.get(asset_symbol, None)

        if prev_fast <= prev_slow and fast_sma > slow_sma:
            self._last_signal[asset_symbol] = "BUY"
            return {
                "asset_symbol": asset_symbol,
                "action": "BUY",
                "type": "LONG",
                "reason": f"SMA{self.fast_period} ({fast_sma:.2f}) > SMA{self.slow_period} ({slow_sma:.2f})",
                "price": current_price,
                "position_size": self.position_size,
            }
        elif prev_fast >= prev_slow and fast_sma < slow_sma and last_signal == "BUY":
            self._last_signal[asset_symbol] = "SELL"
            return {
                "asset_symbol": asset_symbol,
                "action": "SELL",
                "type": "LONG",
                "reason": f"SMA{self.fast_period} ({fast_sma:.2f}) < SMA{self.slow_period} ({slow_sma:.2f})",
                "price": current_price,
                "position_size": self.position_size,
            }

        return {}

    def reset(self):
        """Reset strategy state for new backtest."""
        self._price_history = {}
        self._last_signal = {}
