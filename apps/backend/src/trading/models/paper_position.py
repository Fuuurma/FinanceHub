from decimal import Decimal
from django.db import models
from django.conf import settings
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class PaperPosition(UUIDModel, TimestampedModel):
    portfolio = models.ForeignKey(
        "trading.PaperTradingAccount",
        on_delete=models.CASCADE,
        related_name="positions",
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="paper_positions"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=4, help_text="Number of shares/units held"
    )
    avg_price = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Average purchase price"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "paper_trading_positions"
        verbose_name = "Paper Trading Position"
        verbose_name_plural = "Paper Trading Positions"
        unique_together = ["portfolio", "asset"]
        indexes = [
            models.Index(fields=["portfolio", "asset"]),
            models.Index(fields=["asset"]),
        ]

    def __str__(self):
        return f"{self.portfolio.user.email} - {self.asset.symbol}: {self.quantity}"

    @property
    def total_cost(self) -> Decimal:
        return self.quantity * self.avg_price

    def update_quantity(self, quantity: Decimal, price: Decimal):
        total_cost = (self.quantity * self.avg_price) + (quantity * price)
        self.quantity = self.quantity + quantity
        self.avg_price = total_cost / self.quantity
        self.save()
