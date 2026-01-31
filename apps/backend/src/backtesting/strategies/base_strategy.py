from abc import ABC, abstractmethod
from typing import Dict, List, Optional
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
        self._initialize()

    def _initialize(self):
        """Override in subclasses for strategy-specific initialization."""
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        """
        Generate trading signals.

        Args:
            data: DataFrame with OHLCV data (must have 'close', 'open', 'high', 'low', 'volume')
            timestamp: Current timestamp

        Returns:
            List of signals:
            [
                {
                    'asset_symbol': 'AAPL',
                    'action': 'BUY',  # or 'SELL'
                    'type': 'LONG',
                    'reason': 'SMA crossover'
                }
            ]
        """
        pass

    def get_asset_data(self, data: pd.DataFrame, asset_symbol: str) -> pd.DataFrame:
        """Helper: Get data for specific asset."""
        if data.empty:
            return pd.DataFrame()
        if "asset_symbol" in data.columns:
            return data[data["asset_symbol"] == asset_symbol].copy()
        return data.copy()

    def calculate_price_history(
        self, data: pd.DataFrame, asset_symbol: str
    ) -> List[float]:
        """Get price history for an asset."""
        asset_data = self.get_asset_data(data, asset_symbol)
        if asset_data.empty or "close" not in asset_data.columns:
            return []
        return asset_data["close"].tolist()

    def get_current_price(
        self, data: pd.DataFrame, asset_symbol: str
    ) -> Optional[float]:
        """Get the most recent price for an asset."""
        asset_data = self.get_asset_data(data, asset_symbol)
        if asset_data.empty or "close" not in asset_data.columns:
            return None
        return float(asset_data.iloc[-1]["close"])

    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate that data has required columns."""
        if data.empty:
            return False
        required_columns = ["close", "open", "high", "low"]
        return all(col in data.columns for col in required_columns)

    def get_required_columns(self) -> List[str]:
        """Return list of required data columns."""
        return ["close", "open", "high", "low", "volume"]

    def __repr__(self):
        return f"{self.name}(config={self.config})"
