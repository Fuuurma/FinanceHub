from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from .asset import Asset


class PriceHistory(UUIDModel, TimestampedModel):
    """
    Daily (or intraday) price data for assets.
    Used for charts, valuation, and performance calculations.
    """

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField(db_index=True)
    open = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )
    high = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )
    low = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )
    close = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )
    volume = models.BigIntegerField(null=True, blank=True)
    source = models.CharField(
        max_length=50, default="manual"
    )  # e.g., Yahoo Finance, Polygon, etc.

    class Meta:
        unique_together = ("asset", "date")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["asset", "-date"]),
            models.Index(fields=["date"]),
        ]
        verbose_name_plural = "Price Histories"

    def __str__(self):
        return f"{self.asset.ticker} - {self.date} - ${self.close}"
