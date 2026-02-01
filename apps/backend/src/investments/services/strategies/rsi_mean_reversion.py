from .base_strategy import BaseStrategy
from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime


class RSIMeanReversionStrategy(BaseStrategy):
    """
    RSI Mean Reversion Strategy.

    Buy when RSI is oversold (< 30)
    Sell when RSI is overbought (> 70)
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.period = self.config.get("period", 14)
        self.oversold = self.config.get("oversold", 30)
        self.overbought = self.config.get("overbought", 70)
        self.price_history: Dict[int, List[float]] = {}

    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI from price history."""
        if len(prices) < self.period + 1:
            return 50

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-self.period :])
        avg_loss = np.mean(losses[-self.period :])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        signals = []

        for asset_id in data["asset_id"].unique():
            asset_data = self.get_asset_data(data, asset_id)
            if asset_data.empty:
                continue

            close = float(asset_data.iloc[-1]["close"])

            if asset_id not in self.price_history:
                self.price_history[asset_id] = []
            self.price_history[asset_id].append(close)

            prices = self.price_history[asset_id]

            if len(prices) < self.period + 1:
                continue

            rsi = self._calculate_rsi(prices)

            if rsi < self.oversold:
                signals.append(
                    {
                        "asset_id": asset_id,
                        "action": "BUY",
                        "type": "LONG",
                        "reason": f"RSI {rsi:.1f} oversold ({self.oversold})",
                    }
                )
            elif rsi > self.overbought:
                signals.append(
                    {
                        "asset_id": asset_id,
                        "action": "SELL",
                        "type": "LONG",
                        "reason": f"RSI {rsi:.1f} overbought ({self.overbought})",
                    }
                )

        return signals
