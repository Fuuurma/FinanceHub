from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class TradingStrategy(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Trading strategy configuration for backtesting.

    Inherits from:
    - UUIDModel: Provides UUID primary key (id field)
    - TimestampedModel: Provides created_at, updated_at timestamps
    - SoftDeleteModel: Provides is_deleted, deleted_at for soft deletion
    """

    STRATEGY_TYPES = [
        ("sma_crossover", "SMA Crossover"),
        ("rsi_mean_reversion", "RSI Mean Reversion"),
        ("custom", "Custom Python"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trading_strategies"
    )
    name = models.CharField(max_length=255)
    strategy_type = models.CharField(max_length=50, choices=STRATEGY_TYPES)
    config = models.JSONField(default=dict)
    description = models.TextField(blank=True, default="")
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ["user", "name"]

    def __str__(self):
        return f"{self.user.username}'s {self.name} ({self.strategy_type})"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "strategy_type": self.strategy_type,
            "config": self.config,
            "description": self.description,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Backtest(UUIDModel, TimestampedModel):
    """
    Backtest execution result.

    Stores complete backtest results including metrics, equity curve, and trades.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="backtests")
    strategy = models.ForeignKey(
        TradingStrategy,
        on_delete=models.CASCADE,
        related_name="backtests",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    start_date = models.DateField()
    end_date = models.DateField()
    initial_capital = models.DecimalField(max_digits=15, decimal_places=2)

    total_return = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    sortino_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    win_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    profit_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    total_trades = models.IntegerField(null=True)
    winning_trades = models.IntegerField(null=True)
    losing_trades = models.IntegerField(null=True)

    equity_curve = models.JSONField(default=list)
    drawdown_curve = models.JSONField(default=list)
    trades_data = models.JSONField(default=list)

    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s {self.name} ({self.status})"


class BacktestTrade(UUIDModel, TimestampedModel):
    """
    Individual trade record from backtest execution.
    """

    ACTION_CHOICES = [
        ("BUY", "Buy"),
        ("SELL", "Sell"),
    ]

    backtest = models.ForeignKey(
        Backtest, on_delete=models.CASCADE, related_name="trades"
    )
    asset_symbol = models.CharField(max_length=20)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    price = models.DecimalField(max_digits=15, decimal_places=4)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    slippage = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    timestamp = models.DateTimeField()
    pnl = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    pnl_percent = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return (
            f"{self.backtest.name} - {self.action} {self.asset_symbol} @ {self.price}"
        )
