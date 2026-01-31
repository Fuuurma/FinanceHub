from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from datetime import datetime


class BaseStrategy(ABC):
    """
    Base class for ALL trading strategies.

    Every strategy MUST inherit from this class and implement
    the generate_signals() method.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        """
        Generate trading signals.

        Args:
            data: DataFrame with OHLCV data
            timestamp: Current timestamp

        Returns:
            List of signals:
            [
                {
                    'asset_id': 123,
                    'action': 'BUY',  # or 'SELL'
                    'type': 'LONG',
                    'reason': 'SMA crossover'
                }
            ]
        """
        pass

    def get_asset_data(self, data: pd.DataFrame, asset_id: int) -> pd.DataFrame:
        """Helper: Get data for specific asset."""
        return data[data["asset_id"] == asset_id]
