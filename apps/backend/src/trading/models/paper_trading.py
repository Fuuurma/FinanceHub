from decimal import Decimal
from django.db import models
from django.utils import timezone
from users.models.user import User
from assets.models.asset import Asset
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class PaperTradingAccount(UUIDModel, TimestampedModel, SoftDeleteModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="paper_trading_account"
    )

    cash_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100000.00"),
        help_text="Virtual cash balance (default: $100,000)",
    )

    starting_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100000.00"),
        help_text="Starting balance when account was created/reset",
    )

    total_trades = models.IntegerField(
        default=0, help_text="Total number of trades executed"
    )

    winning_trades = models.IntegerField(
        default=0, help_text="Number of profitable trades"
    )

    losing_trades = models.IntegerField(
        default=0, help_text="Number of unprofitable trades"
    )

    total_return = models.FloatField(default=0.0, help_text="Total return percentage")

    last_reset_at = models.DateTimeField(
        null=True, blank=True, help_text="Last time account was reset"
    )

    reset_count = models.IntegerField(
        default=0, help_text="Number of times account has been reset"
    )

    class Meta:
        db_table = "paper_trading_accounts"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["total_return"]),
        ]

    def __str__(self):
        return f"{self.user.email} - Paper Trading Account (${self.cash_balance:,.2f})"

    @property
    def portfolio_value(self) -> Decimal:
        from trading.services.paper_trading_service import PaperTradingService

        service = PaperTradingService()
        return service.calculate_portfolio_value(self.user)

    @property
    def total_value(self) -> Decimal:
        return self.cash_balance + self.portfolio_value

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100

    def reset_account(self):
        self.cash_balance = self.starting_balance
        self.last_reset_at = timezone.now()
        self.reset_count += 1
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_return = 0.0
        self.save()

        self.paper_trades.all().delete()


class PaperTrade(UUIDModel, TimestampedModel, SoftDeleteModel):
    account = models.ForeignKey(
        PaperTradingAccount, on_delete=models.CASCADE, related_name="paper_trades"
    )

    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="paper_trades"
    )

    trade_type = models.CharField(
        max_length=10, choices=[("BUY", "Buy"), ("SELL", "Sell")]
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Quantity traded (can be fractional for crypto)",
    )

    price = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Execution price per share/coin"
    )

    executed_at = models.DateTimeField(
        auto_now_add=True, help_text="When the trade was executed"
    )

    slippage = models.FloatField(
        default=0.0, help_text="Simulated slippage percentage (e.g., 0.01 for 1%)"
    )

    total_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Total trade value (quantity * price)",
    )

    is_winning = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether this trade was profitable (for closed positions)",
    )

    profit_loss = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Profit/loss for this trade",
    )

    class Meta:
        db_table = "paper_trades"
        indexes = [
            models.Index(fields=["account", "executed_at"]),
            models.Index(fields=["asset"]),
            models.Index(fields=["trade_type"]),
        ]

    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.asset.symbol} @ ${self.price}"
