from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from users.models.user import User
from assets.models.asset import Asset
from portfolios.models.portfolio import Portfolio
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Position(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Open trading position (long/short)"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="positions")
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="positions"
    )
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="positions")

    side = models.CharField(
        max_length=10,
        choices=[
            ("long", "Long"),
            ("short", "Short"),
        ],
        default="long",
    )

    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )

    avg_entry_price = models.DecimalField(max_digits=20, decimal_places=8)

    current_price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )

    unrealized_pnl = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )

    unrealized_pnl_percent = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal("0")
    )

    realized_pnl = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )

    total_fees = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )

    is_open = models.BooleanField(default=True, db_index=True)

    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        db_table = "positions"
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=["user", "is_open"]),
            models.Index(fields=["portfolio", "is_open"]),
            models.Index(fields=["asset", "is_open"]),
            models.Index(fields=["-opened_at"]),
        ]

    @property
    def market_value(self):
        """Current market value of position"""
        if self.current_price:
            return self.quantity * self.current_price
        return Decimal("0")

    @property
    def cost_basis(self):
        """Total cost basis (entry price + fees)"""
        return (self.avg_entry_price * self.quantity) + self.total_fees

    @property
    def total_pnl(self):
        """Total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def total_pnl_percent(self):
        """Total P&L as percentage of cost basis"""
        if self.cost_basis > 0:
            return (self.total_pnl / self.cost_basis) * Decimal("100")
        return Decimal("0")

    @property
    def days_open(self):
        """Number of days position has been open"""
        if self.is_open and self.opened_at:
            from datetime import timezone

            now = timezone.now()
            return (now - self.opened_at).days
        return 0

    def __str__(self):
        return f"{self.side.upper()} {self.quantity} {self.asset.symbol} @ {self.avg_entry_price}"
