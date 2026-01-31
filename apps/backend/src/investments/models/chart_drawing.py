from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class ChartDrawingModel(UUIDModel, TimestampedModel):
    """User drawings on charts (trendlines, support/resistance, etc.)"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chart_drawings"
    )
    symbol = models.CharField(max_length=20, db_index=True)
    timeframe = models.CharField(max_length=10, default="1d")

    DRAWING_TYPE_CHOICES = [
        ("horizontal_line", "Horizontal Line"),
        ("vertical_line", "Vertical Line"),
        ("trend_line", "Trend Line"),
        ("support", "Support Line"),
        ("resistance", "Resistance Line"),
        ("fibonacci", "Fibonacci Retracement"),
        ("rectangle", "Rectangle"),
        ("text", "Text Annotation"),
    ]

    drawing_type = models.CharField(max_length=20, choices=DRAWING_TYPE_CHOICES)
    coordinates = models.JSONField(
        help_text="Drawing coordinates {x1, y1, x2, y2, etc.}"
    )
    parameters = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional parameters (text content, fib levels, etc.)",
    )
    color = models.CharField(max_length=20, default="#3b82f6")
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = "chart_drawings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "symbol"]),
            models.Index(fields=["symbol", "timeframe"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.symbol} - {self.drawing_type}"


class ChartLayoutModel(UUIDModel, TimestampedModel):
    """Saved chart layouts with indicator configurations"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chart_layouts"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    layout_config = models.JSONField(
        default=dict,
        help_text="Layout configuration with indicators, drawings, settings",
    )

    class Meta:
        db_table = "chart_layouts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class TechnicalIndicator(UUIDModel, TimestampedModel):
    """Stored technical indicator calculations"""

    symbol = models.CharField(max_length=20, db_index=True)
    timeframe = models.CharField(max_length=10, default="1d")
    indicator_type = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    value = models.DecimalField(max_digits=20, decimal_places=8)
    signal = models.CharField(max_length=20, null=True, blank=True)
    additional_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "technical_indicators"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["symbol", "indicator_type", "timeframe"]),
            models.Index(fields=["symbol", "timeframe", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.symbol} {self.indicator_type} @ {self.timestamp}"


class ChartScreenshot(UUIDModel, TimestampedModel):
    """Saved chart screenshots for sharing"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chart_screenshots"
    )
    symbol = models.CharField(max_length=20, db_index=True)
    timeframe = models.CharField(max_length=10, default="1d")
    share_id = models.CharField(max_length=20, unique=True, db_index=True)
    image_data = models.BinaryField(
        null=True,
        blank=True,
        help_text="PNG image data for the chart screenshot",
    )
    drawings = models.JSONField(
        default=list,
        blank=True,
        help_text="List of drawing objects included in the screenshot",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the shared screenshot expires",
    )
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = "chart_screenshots"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["share_id"]),
            models.Index(fields=["user", "symbol"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Screenshot: {self.symbol} ({self.share_id})"
