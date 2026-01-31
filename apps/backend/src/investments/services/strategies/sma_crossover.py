from .base_strategy import BaseStrategy
from typing import Dict, List
import pandas as pd
from datetime import datetime


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.

    Buy: Fast SMA crosses above Slow SMA
    Sell: Fast SMA crosses below Slow SMA
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.fast_period = self.config.get("fast_period", 10)
        self.slow_period = self.config.get("slow_period", 20)
        self.price_history = {}

    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        signals = []

        for asset_id in data["asset_id"].unique():
            asset_data = self.get_asset_data(data, asset_id)
            if asset_data.empty:
                continue

            close = asset_data.iloc[-1]["close"]

            # Update history
            if asset_id not in self.price_history:
                self.price_history[asset_id] = []
            self.price_history[asset_id].append(close)

            prices = self.price_history[asset_id]

            # Need enough data
            if len(prices) < self.slow_period + 1:
                continue

            # Calculate SMAs
            fast_sma = sum(prices[-self.fast_period :]) / self.fast_period
            slow_sma = sum(prices[-self.slow_period :]) / self.slow_period

            # Previous SMAs
            prev_fast = sum(prices[-self.fast_period - 1 : -1]) / self.fast_period
            prev_slow = sum(prices[-self.slow_period - 1 : -1]) / self.slow_period

            # Crossovers
            if prev_fast <= prev_slow and fast_sma > slow_sma:
                signals.append(
                    {
                        "asset_id": asset_id,
                        "action": "BUY",
                        "type": "LONG",
                        "reason": f"SMA{self.fast_period} > SMA{self.slow_period}",
                    }
                )
            elif prev_fast >= prev_slow and fast_sma < slow_sma:
                signals.append(
                    {
                        "asset_id": asset_id,
                        "action": "SELL",
                        "type": "LONG",
                        "reason": f"SMA{self.fast_period} < SMA{self.slow_period}",
                    }
                )

        return signals
