from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.soft_delete_model import SoftDeleteModel

User = get_user_model()


class BrokerConnection(UUIDModel, TimestampedModel, SoftDeleteModel):
    BROKER_CHOICES = [
        ("alpaca", "Alpaca"),
        ("binance", "Binance"),
        ("coinbase", "Coinbase"),
        ("kraken", "Kraken"),
        ("ibkr", "Interactive Brokers"),
    ]

    ACCOUNT_TYPE_CHOICES = [
        ("paper", "Paper Trading"),
        ("live", "Live Trading"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("error", "Error"),
        ("pending", "Pending Verification"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="broker_connections"
    )
    broker = models.CharField(max_length=20, choices=BROKER_CHOICES)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    account_id = models.CharField(max_length=100, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    api_key_encrypted = models.BinaryField()
    api_secret_encrypted = models.BinaryField()
    passphrase_encrypted = models.BinaryField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    sync_enabled = models.BooleanField(default=True)
    sync_interval_minutes = models.IntegerField(default=15)
    permissions = models.JSONField(default=dict)
    rate_limit_remaining = models.IntegerField(default=0)
    rate_limit_reset_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "broker_connections"
        unique_together = [["user", "broker", "account_id"]]
        indexes = [
            models.Index(fields=["user", "broker"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["broker", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.broker} ({self.account_id})"

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def needs_sync(self):
        if not self.sync_enabled:
            return False
        if not self.last_sync_at:
            return True
        delta = timezone.now() - self.last_sync_at
        return delta.total_seconds() >= self.sync_interval_minutes * 60


class BrokerPosition(UUIDModel, TimestampedModel, SoftDeleteModel):
    SIDE_CHOICES = [
        ("long", "Long"),
        ("short", "Short"),
        ("neutral", "Neutral"),
    ]

    connection = models.ForeignKey(
        BrokerConnection, on_delete=models.CASCADE, related_name="positions"
    )
    symbol = models.CharField(max_length=20)
    asset_id = models.CharField(max_length=100, blank=True)
    side = models.CharField(max_length=10, choices=SIDE_CHOICES, default="long")
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    avg_entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    current_price = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    market_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    unrealized_pl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    unrealized_pl_percent = models.DecimalField(
        max_digits=10, decimal_places=4, default=0
    )
    cost_basis = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    last_price_update = models.DateTimeField(null=True, blank=True)
    external_position_id = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "broker_positions"
        unique_together = [["connection", "symbol", "external_position_id"]]
        indexes = [
            models.Index(fields=["connection", "symbol"]),
            models.Index(fields=["connection", "side"]),
        ]

    def __str__(self):
        return f"{self.connection.account_id} - {self.symbol} ({self.quantity})"


class BrokerTransaction(UUIDModel, TimestampedModel, SoftDeleteModel):
    TRANSACTION_TYPE_CHOICES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
        ("fee", "Fee"),
        ("dividend", "Dividend"),
        ("split", "Stock Split"),
        ("spin_off", "Spin Off"),
        ("merger", "Merger"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("canceled", "Canceled"),
    ]

    connection = models.ForeignKey(
        BrokerConnection, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    symbol = models.CharField(max_length=20, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    total = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    fee = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    executed_at = models.DateTimeField(null=True, blank=True)
    external_transaction_id = models.CharField(max_length=200, blank=True)
    order_id = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "broker_transactions"
        indexes = [
            models.Index(fields=["connection", "executed_at"]),
            models.Index(fields=["connection", "symbol"]),
            models.Index(fields=["connection", "transaction_type"]),
        ]

    def __str__(self):
        return f"{self.connection.account_id} - {self.transaction_type} {self.symbol}"


class BrokerOrder(UUIDModel, TimestampedModel, SoftDeleteModel):
    ORDER_TYPE_CHOICES = [
        ("market", "Market"),
        ("limit", "Limit"),
        ("stop", "Stop"),
        ("stop_limit", "Stop Limit"),
        ("trailing_stop", "Trailing Stop"),
    ]

    SIDE_CHOICES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
    ]

    TIME_IN_FORCE_CHOICES = [
        ("day", "Day"),
        ("gtc", "Good Till Canceled"),
        ("ioc", "Immediate Or Cancel"),
        ("fok", "Fill Or Kill"),
        ("opg", "At The Opening"),
        ("cls", "Close"),
    ]

    STATUS_CHOICES = [
        ("pending_new", "Pending New"),
        ("accepted", "Accepted"),
        ("pending_cancel", "Pending Cancel"),
        ("partial_filled", "Partially Filled"),
        ("filled", "Filled"),
        ("canceled", "Canceled"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    connection = models.ForeignKey(
        BrokerConnection, on_delete=models.CASCADE, related_name="orders"
    )
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    filled_quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    limit_price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    stop_price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    trailing_amount = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    trailing_percent = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    time_in_force = models.CharField(
        max_length=10, choices=TIME_IN_FORCE_CHOICES, default="day"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending_new"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    filled_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    avg_fill_price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    commission = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    external_order_id = models.CharField(max_length=200, blank=True)
    parent_order_id = models.CharField(max_length=200, blank=True)
    legs = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "broker_orders"
        indexes = [
            models.Index(fields=["connection", "status"]),
            models.Index(fields=["connection", "symbol"]),
            models.Index(fields=["connection", "submitted_at"]),
        ]

    def __str__(self):
        return (
            f"{self.connection.account_id} - {self.side} {self.quantity} {self.symbol}"
        )

    @property
    def is_active(self):
        return self.status in [
            "pending_new",
            "accepted",
            "partial_filled",
        ]

    @property
    def remaining_quantity(self):
        return self.quantity - self.filled_quantity


class PortfolioSyncLog(UUIDModel, TimestampedModel):
    SYNC_TYPE_CHOICES = [
        ("full", "Full Sync"),
        ("incremental", "Incremental Sync"),
        ("positions", "Positions Only"),
        ("transactions", "Transactions Only"),
        ("orders", "Orders Only"),
    ]

    STATUS_CHOICES = [
        ("started", "Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    connection = models.ForeignKey(
        BrokerConnection, on_delete=models.CASCADE, related_name="sync_logs"
    )
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="started")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    positions_synced = models.IntegerField(default=0)
    transactions_synced = models.IntegerField(default=0)
    orders_synced = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    errors = models.JSONField(default=list)
    duration_ms = models.IntegerField(default=0)
    api_calls_made = models.IntegerField(default=0)
    data_volume_bytes = models.IntegerField(default=0)

    class Meta:
        db_table = "portfolio_sync_logs"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["connection", "started_at"]),
            models.Index(fields=["connection", "status"]),
        ]

    def __str__(self):
        return f"{self.connection.account_id} - {self.sync_type} ({self.status})"

    def mark_completed(self):
        self.status = "completed"
        self.completed_at = timezone.now()
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)
        self.save()

    def mark_failed(self, error_message):
        self.status = "failed"
        self.completed_at = timezone.now()
        self.errors_count += 1
        self.errors.append(
            {
                "timestamp": timezone.now().isoformat(),
                "message": error_message,
            }
        )
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)
        self.save()
