from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class PaperTradingOrder(UUIDModel, TimestampedModel):
    ORDER_TYPES = [
        ("market", "Market Order"),
        ("limit", "Limit Order"),
        ("stop", "Stop Order"),
    ]

    SIDES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("filled", "Filled"),
        ("cancelled", "Cancelled"),
        ("rejected", "Rejected"),
    ]

    portfolio = models.ForeignKey(
        "trading.PaperTradingAccount", on_delete=models.CASCADE, related_name="orders"
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="paper_orders"
    )
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    side = models.CharField(max_length=4, choices=SIDES)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Limit price or stop price",
    )
    stop_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stop trigger price",
    )
    filled_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    filled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    rejection_reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "paper_trading_orders"
        verbose_name = "Paper Trading Order"
        verbose_name_plural = "Paper Trading Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["portfolio", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["asset", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.side.upper()} {self.quantity} {self.asset.symbol} @ {self.price or 'MARKET'}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

        if self.order_type in ["limit", "stop"] and not self.price:
            raise ValidationError(
                f"{self.order_type.capitalize()} orders require a price"
            )

        if self.side == "buy" and self.order_type == "limit":
            required = self.quantity * self.price
            if self.portfolio.cash_balance < required:
                raise ValidationError(
                    f"Insufficient funds. Required: ${required}, Available: ${self.portfolio.cash_balance}"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.status in ["pending"]

    @property
    def total_value(self) -> Decimal:
        if self.filled_price:
            return self.quantity * self.filled_price
        return Decimal("0")

    def fill(self, fill_price: Decimal):
        self.filled_price = fill_price
        self.filled_at = timezone.now()
        self.status = "filled"
        self.save()

    def cancel(self):
        if self.status != "pending":
            raise ValidationError("Only pending orders can be cancelled")
        self.status = "cancelled"
        self.save()

    def reject(self, reason: str):
        self.status = "rejected"
        self.rejection_reason = reason
        self.save()
