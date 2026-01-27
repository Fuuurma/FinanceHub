from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from assets.models.asset import Asset
from investments.models.data_provider import DataProvider
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel

from decimal import Decimal
from statistics import stdev


class AssetPricesHistoric(UUIDModel, TimestampedModel):
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

    volatility = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Calculated volatility (e.g., 30-day std dev)",
    )

    source = models.ForeignKey(
        DataProvider, on_delete=models.CASCADE, related_name="prices"
    )

    class Meta:
        db_table = "asset_prices_historic"
        unique_together = ("asset", "date", "source")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["asset", "-date"]),
            models.Index(fields=["date"]),
            models.Index(fields=["source"]),
        ]
        verbose_name_plural = "Prices Historic"

    def __str__(self):
        return f"{self.asset.ticker} - {self.date} - ${self.close}"

    def calculate_volatility(self, days=30):
        """Calculate volatility from 
        previous prices if not set"""
        if self.volatility is not None:
            return self.volatility

        prices = (
            AssetPricesHistoric.objects.filter(asset=self.asset, date__lte=self.date)
            .order_by("-date")[:days]
            .values_list("close", flat=True)
        )
        if len(prices) < 2:
            return Decimal("0")
        returns = [
            (prices[i] - prices[i + 1]) / prices[i + 1] for i in range(len(prices) - 1)
        ]
        volatility = (
            Decimal(str(stdev(returns) * (252**0.5))) if returns else Decimal("0")
        )
        self.volatility = volatility.quantize(Decimal("0.01"))
        self.save(update_fields=["volatility"])
        return self.volatility
