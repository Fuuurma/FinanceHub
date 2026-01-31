from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime
from .base_strategy import BaseStrategy


class RSIMeanReversionStrategy(BaseStrategy):
    """
    RSI Mean Reversion Strategy.

    Buy: RSI drops below oversold threshold then crosses back up
    Sell: RSI rises above overbought threshold then crosses back down

    Configuration:
    - period: RSI period (default: 14)
    - oversold: Oversold threshold (default: 30)
    - overbought: Overbought threshold (default: 70)
    - position_size: Percentage of portfolio per trade (default: 0.1 = 10%)
    """

    def _initialize(self):
        self.period = self.config.get("period", 14)
        self.oversold = self.config.get("oversold", 30)
        self.overbought = self.config.get("overbought", 70)
        self.position_size = self.config.get("position_size", 0.1)
        self._rsi_history: Dict[str, List[float]] = {}
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
            signal = self._check_rsi(data, asset_symbol, timestamp)
            if signal:
                signals.append(signal)

        return signals

    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI from price series."""
        if len(prices) < self.period + 1:
            return 50.0

        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-self.period :]]
        losses = [-d if d < 0 else 0 for d in deltas[-self.period :]]

        avg_gain = sum(gains) / self.period
        avg_loss = sum(losses) / self.period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _check_rsi(
        self, data: pd.DataFrame, asset_symbol: str, timestamp: datetime
    ) -> Dict:
        asset_data = self.get_asset_data(data, asset_symbol)
        if asset_data.empty or len(asset_data) < self.period + 1:
            return {}

        prices = asset_data["close"].tolist()
        current_price = prices[-1]

        if asset_symbol not in self._rsi_history:
            self._rsi_history[asset_symbol] = []

        rsi_values = self._rsi_history[asset_symbol]
        current_rsi = self._calculate_rsi(prices)
        rsi_values.append(current_rsi)

        if len(rsi_values) < 2:
            return {}

        prev_rsi = rsi_values[-2]
        last_signal = self._last_signal.get(asset_symbol, None)

        if (
            prev_rsi <= self.oversold
            and current_rsi > self.oversold
            and last_signal != "BUY"
        ):
            self._last_signal[asset_symbol] = "BUY"
            return {
                "asset_symbol": asset_symbol,
                "action": "BUY",
                "type": "LONG",
                "reason": f"RSI ({current_rsi:.1f}) crossed above oversold ({self.oversold})",
                "price": current_price,
                "position_size": self.position_size,
            }
        elif (
            prev_rsi >= self.overbought
            and current_rsi < self.overbought
            and last_signal == "BUY"
        ):
            self._last_signal[asset_symbol] = "SELL"
            return {
                "asset_symbol": asset_symbol,
                "action": "SELL",
                "type": "LONG",
                "reason": f"RSI ({current_rsi:.1f}) crossed below overbought ({self.overbought})",
                "price": current_price,
                "position_size": self.position_size,
            }

        return {}

    def reset(self):
        """Reset strategy state for new backtest."""
        self._rsi_history = {}
        self._last_signal = {}
