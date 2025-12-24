from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from assets.models.asset import Asset
from portfolios.models.portfolio import Portfolio
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Holding(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Link between a Portfolio and an Asset with quantity.
    """

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="holdings"
    )
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="holdings")
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )
    average_buy_price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )

    class Meta:
        unique_together = ("portfolio", "asset")
        indexes = [
            models.Index(fields=["portfolio"]),
            models.Index(fields=["asset"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} → {self.asset.ticker}: {self.quantity}"

    @property
    def current_price(self):
        latest = self.asset.prices.order_by("-date").first()
        return latest.close if latest else None

    @property
    def current_value(self):
        price = self.current_price
        return (price * self.quantity) if price else Decimal("0")
