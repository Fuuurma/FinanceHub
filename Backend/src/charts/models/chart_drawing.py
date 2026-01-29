from django.db import models
from users.models.user import User
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class ChartDrawing(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Chart annotations and drawings saved by users"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chart_drawings"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="drawings")

    drawing_type = models.CharField(
        max_length=50,
        choices=[
            ("horizontal_line", "Horizontal Line"),
            ("vertical_line", "Vertical Line"),
            ("trend_line", "Trend Line"),
            ("support_resistance", "Support/Resistance"),
            ("fibonacci", "Fibonacci Retracement"),
            ("rectangle", "Rectangle"),
            ("text", "Text Annotation"),
        ],
    )

    timeframe = models.CharField(
        max_length=10,
        choices=[
            ("1m", "1 Minute"),
            ("5m", "5 Minutes"),
            ("15m", "15 Minutes"),
            ("1h", "1 Hour"),
            ("4h", "4 Hours"),
            ("1d", "1 Day"),
            ("1w", "1 Week"),
        ],
        default="1d",
    )

    # Coordinates as percentage (0-100) for responsive charts
    start_x = models.DecimalField(max_digits=5, decimal_places=2)
    start_y = models.DecimalField(max_digits=5, decimal_places=2)
    end_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    color = models.CharField(max_length=20, default="#ef4444")
    width = models.IntegerField(default=2)
    line_style = models.CharField(
        max_length=20,
        choices=[("solid", "Solid"), ("dashed", "Dashed")],
        default="solid",
    )

    text = models.TextField(blank=True, null=True)
    fibonacci_levels = models.JSONField(default=list, blank=True)

    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "chart_drawings"
        indexes = [
            models.Index(fields=["user", "asset", "timeframe"]),
            models.Index(fields=["drawing_type"]),
            models.Index(fields=["visible"]),
        ]

    def __str__(self):
        return f"{self.drawing_type} on {self.asset.symbol} ({self.timeframe})"


class TechnicalIndicatorValue(UUIDModel, TimestampedModel):
    """Historical technical indicator values for charts"""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="indicator_values"
    )

    indicator_type = models.CharField(
        max_length=50,
        choices=[
            ("sma", "Simple Moving Average"),
            ("ema", "Exponential Moving Average"),
            ("wma", "Weighted Moving Average"),
            ("bollinger_upper", "Bollinger Upper"),
            ("bollinger_middle", "Bollinger Middle"),
            ("bollinger_lower", "Bollinger Lower"),
            ("rsi", "RSI"),
            ("macd", "MACD"),
            ("macd_signal", "MACD Signal"),
            ("stochastic_k", "Stochastic %K"),
            ("stochastic_d", "Stochastic %D"),
            ("cci", "CCI"),
            ("williams_r", "Williams %R"),
            ("atr", "ATR"),
            ("obv", "OBV"),
            ("mfi", "MFI"),
            ("ad", "A/D Line"),
        ],
    )

    timeframe = models.CharField(
        max_length=10,
        choices=[
            ("1m", "1 Minute"),
            ("5m", "5 Minutes"),
            ("15m", "15 Minutes"),
            ("1h", "1 Hour"),
            ("4h", "4 Hours"),
            ("1d", "1 Day"),
            ("1w", "1 Week"),
        ],
        default="1d",
    )

    timestamp = models.DateTimeField(db_index=True)
    value = models.DecimalField(max_digits=15, decimal_places=6)
    parameters = models.JSONField(default=dict, blank=True)

    # Signal interpretation
    signal = models.CharField(
        max_length=20,
        choices=[("buy", "Buy"), ("sell", "Sell"), ("neutral", "Neutral")],
        null=True,
        blank=True,
    )
    strength = models.IntegerField(
        choices=[(1, "Weak"), (2, "Moderate"), (3, "Strong")], null=True, blank=True
    )

    class Meta:
        db_table = "technical_indicator_values"
        indexes = [
            models.Index(fields=["asset", "indicator_type", "timeframe"]),
            models.Index(fields=["asset", "timestamp"]),
            models.Index(fields=["indicator_type", "signal"]),
        ]

    def __str__(self):
        return f"{self.indicator_type} for {self.asset.symbol} at {self.timestamp}"


class ChartDrawingManager(UUIDModel, TimestampedModel):
    """Workspace/layout configurations for user's chart views"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chart_managers"
    )
    name = models.CharField(max_length=100)

    # Saved chart configuration
    layout = models.JSONField(default=dict)

    # Selected indicators for this chart
    indicators = models.JSONField(default=list)

    # Timeframe preference
    default_timeframe = models.CharField(
        max_length=10,
        choices=[
            ("1m", "1 Minute"),
            ("5m", "5 Minutes"),
            ("15m", "15 Minutes"),
            ("1h", "1 Hour"),
            ("4h", "4 Hours"),
            ("1d", "1 Day"),
            ("1w", "1 Week"),
        ],
        default="1d",
    )

    # Chart type preferences
    chart_type = models.CharField(
        max_length=20,
        choices=[
            ("line", "Line Chart"),
            ("candlestick", "Candlestick"),
            ("area", "Area Chart"),
            ("bar", "Bar Chart"),
        ],
        default="line",
    )

    # Show/hide options
    show_volume = models.BooleanField(default=True)
    show_indicators = models.BooleanField(default=True)
    show_drawings = models.BooleanField(default=true)

    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "chart_layouts"
        unique_together = ("user", "name")
        indexes = [
            models.Index(fields=["user", "is_default"]),
        ]

    def __str__(self):
        return f"{self.name} by {self.user.email}"
