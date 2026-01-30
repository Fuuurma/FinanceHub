from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from users.models.user import User
from assets.models.asset import Asset
from portfolios.models.portfolio import Portfolio
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class OrderType(models.TextChoices):
    MARKET = "market", "Market Order"
    LIMIT = "limit", "Limit Order"
    STOP = "stop", "Stop Order"
    STOP_LIMIT = "stop_limit", "Stop-Limit Order"
    OCO = "oco", "One-Cancels-Other"


class OrderSide(models.TextChoices):
    BUY = "buy", "Buy"
    SELL = "sell", "Sell"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    FILLED = "filled", "Filled"
    PARTIALLY_FILLED = "partially_filled", "Partially Filled"
    CANCELLED = "cancelled", "Cancelled"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"


class Order(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Trade order (buy/sell) with advanced order types"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="orders"
    )
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="orders")

    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    side = models.CharField(max_length=10, choices=OrderSide.choices)

    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )

    price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Limit price for limit orders, null for market orders",
    )

    stop_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Stop price for stop/stop-limit orders",
    )

    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )

    filled_quantity = models.DecimalField(
        max_digits=20, decimal_places=8, default=Decimal("0")
    )
    filled_price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )

    average_fill_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Average price for partially filled orders",
    )

    fees = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    time_in_force = models.CharField(
        max_length=20,
        choices=[
            ("day", "Day"),
            ("gtc", "Good Till Cancelled"),
            ("ioc", "Immediate or Cancel"),
            ("fok", "Fill or Kill"),
        ],
        default="day",
    )

    expiry_date = models.DateTimeField(
        null=True, blank=True, help_text="Order expiration date for GTC orders"
    )

    notes = models.TextField(blank=True)

    oco_linked_order = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="oco_orders",
    )

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["portfolio", "status"]),
            models.Index(fields=["asset", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    @property
    def remaining_quantity(self):
        """Calculate unfilled quantity"""
        return self.quantity - self.filled_quantity

    @property
    def is_filled(self):
        """Check if order is completely filled"""
        return self.status == OrderStatus.FILLED

    @property
    def is_active(self):
        """Check if order is still active (pending or partially filled)"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]

    @property
    def is_oco(self):
        """Check if this is an OCO order"""
        return self.order_type == OrderType.OCO

    def __str__(self):
        return f"{self.side.upper()} {self.quantity} {self.asset.symbol} @ {self.price or 'MKT'} ({self.status})"
