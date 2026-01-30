"""
Technical Indicators Model
Stores technical analysis indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
"""

from django.db import models
from django.core.validators import MinValueValidator
from assets.models.asset import Asset
from investments.models.data_provider import DataProvider
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class TechnicalIndicator(UUIDModel, TimestampedModel):
    """Technical analysis indicators for assets"""

    INDICATOR_TYPES = [
        ("sma", "Simple Moving Average"),
        ("ema", "Exponential Moving Average"),
        ("rsi", "Relative Strength Index"),
        ("macd", "Moving Average Convergence Divergence"),
        ("bb", "Bollinger Bands"),
        ("stoch", "Stochastic Oscillator"),
        ("adx", "Average Directional Index"),
        ("cci", "Commodity Channel Index"),
        ("atr", "Average True Range"),
        ("obv", "On-Balance Volume"),
        ("vwap", "Volume Weighted Average Price"),
    ]

    SIGNALS = [
        ("buy", "Buy"),
        ("sell", "Sell"),
        ("neutral", "Neutral"),
        ("strong_buy", "Strong Buy"),
        ("strong_sell", "Strong Sell"),
    ]

    TIMEFRAMES = [
        ("1m", "1 Minute"),
        ("5m", "5 Minutes"),
        ("15m", "15 Minutes"),
        ("30m", "30 Minutes"),
        ("1h", "1 Hour"),
        ("4h", "4 Hours"),
        ("1d", "1 Day"),
        ("1w", "1 Week"),
        ("1M", "1 Month"),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="technical_indicators",
        db_index=True,
    )

    indicator_type = models.CharField(
        max_length=20, choices=INDICATOR_TYPES, db_index=True
    )

    timeframe = models.CharField(
        max_length=10, choices=TIMEFRAMES, default="1d", db_index=True
    )

    timestamp = models.DateTimeField(db_index=True)

    # Primary indicator value
    value = models.DecimalField(
        max_digits=30, decimal_places=10, validators=[MinValueValidator(0)]
    )

    # Trading signal
    signal = models.CharField(max_length=20, choices=SIGNALS, blank=True, null=True)

    # For multi-value indicators (MACD, Bollinger Bands, etc.)
    # Stores additional values like:
    # - MACD: {"macd": 0.5, "signal": 0.3, "histogram": 0.2}
    # - Bollinger Bands: {"upper": 150.5, "middle": 145.0, "lower": 139.5, "bandwidth": 7.5}
    # - Stochastic: {"k": 75.5, "d": 70.2}
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional indicator-specific values"
    )

    # Data source
    source = models.ForeignKey(
        DataProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="technical_indicators",
    )

    class Meta:
        db_table = "technical_indicators"
        verbose_name = "Technical Indicator"
        verbose_name_plural = "Technical Indicators"
        ordering = ["-timestamp"]
        unique_together = [["asset", "indicator_type", "timeframe", "timestamp"]]
        indexes = [
            models.Index(fields=["asset", "indicator_type", "timestamp"]),
            models.Index(fields=["indicator_type", "timestamp"]),
            models.Index(fields=["asset", "timeframe", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.asset.ticker} {self.indicator_type.upper()} {self.timeframe}: {self.value}"
