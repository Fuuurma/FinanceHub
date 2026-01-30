# investments/models/transaction.py
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from investments.models.transaction_type import TransactionType
from portfolios.models.holdings import Holding
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Transaction(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Buy/Sell or other cash flow events.
    """

    portfolio = models.ForeignKey(
        "portfolios.Portfolio", on_delete=models.CASCADE, related_name="transactions"
    )
    holding = models.ForeignKey(
        Holding,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transactions",
    )
    transaction_type = models.ForeignKey(
        TransactionType, on_delete=models.PROTECT, related_name="transactions"
    )
    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions",
    )
    date = models.DateTimeField(db_index=True)
    quantity = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    price_per_share = models.DecimalField(max_digits=20, decimal_places=8)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)  # Includes fees
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["portfolio", "-date"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["asset"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} {self.quantity or ''} {self.asset.ticker if self.asset else ''} @ {self.price_per_share} on {self.date.date()}"
