from django.db import models
from django.contrib.auth.models import User
from portfolios.models.portfolio import Portfolio
from assets.models.asset import Asset
from decimal import Decimal


class TargetAllocation(models.Model):
    ASSET_CLASS_CHOICES = [
        ("stock", "Stock"),
        ("bond", "Bond"),
        ("crypto", "Crypto"),
        ("cash", "Cash"),
        ("commodity", "Commodity"),
        ("etf", "ETF"),
        ("real_estate", "Real Estate"),
        ("other", "Other"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="target_allocations"
    )
    asset_class = models.CharField(max_length=50, choices=ASSET_CLASS_CHOICES)
    target_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Target allocation percentage (0-100)"
    )
    tolerance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("5.00"),
        help_text="Tolerance band (+/- percentage)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["portfolio", "asset_class"]
        ordering = ["asset_class"]

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset_class}: {self.target_percentage}%"


class PortfolioDrift(models.Model):
    DRIFT_LEVEL_CHOICES = [
        ("WITHIN_TOLERANCE", "Within Tolerance"),
        ("WARNING", "Warning"),
        ("CRITICAL", "Critical"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="drift_records"
    )
    asset_class = models.CharField(max_length=50)
    current_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    drift_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    drift_level = models.CharField(max_length=20, choices=DRIFT_LEVEL_CHOICES)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-calculated_at"]

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset_class}: {self.drift_level}"


class RebalancingSuggestion(models.Model):
    ACTION_CHOICES = [
        ("BUY", "Buy"),
        ("SELL", "Sell"),
    ]

    PRIORITY_CHOICES = [
        ("HIGH", "High"),
        ("MEDIUM", "Medium"),
        ("LOW", "Low"),
    ]

    TAX_IMPLICATION_CHOICES = [
        ("GAIN", "Capital Gain"),
        ("LOSS", "Capital Loss"),
        ("NEUTRAL", "Neutral"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("EXECUTED", "Executed"),
        ("CANCELLED", "Cancelled"),
        ("SKIPPED", "Skipped"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="rebalancing_suggestions"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rebalancing_suggestions",
    )
    asset_class = models.CharField(max_length=50)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    current_quantity = models.DecimalField(
        max_digits=20, decimal_places=4, default=Decimal("0")
    )
    current_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    suggested_quantity = models.DecimalField(
        max_digits=20, decimal_places=4, default=Decimal("0")
    )
    suggested_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    current_allocation = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    target_allocation = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="MEDIUM"
    )
    tax_implication = models.CharField(
        max_length=20, choices=TAX_IMPLICATION_CHOICES, default="NEUTRAL"
    )
    estimated_trade_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    reason = models.TextField(
        blank=True, help_text="Explanation for this rebalancing suggestion"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.portfolio.name} - {self.action} {self.asset_class}"


class RebalancingSession(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING_REVIEW", "Pending Review"),
        ("APPROVED", "Approved"),
        ("EXECUTING", "Executing"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="rebalancing_sessions"
    )
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    total_trades = models.IntegerField(default=0)
    estimated_total_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    actual_total_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    tax_impact = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.portfolio.name} - {self.name} ({self.status})"


class TaxLot(models.Model):
    """
    Track tax lots for tax-efficient rebalancing (tax-loss harvesting)
    """

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="tax_lots"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="tax_lots")
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    cost_basis = models.DecimalField(max_digits=20, decimal_places=2)
    current_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    purchase_date = models.DateField()
    current_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=Decimal("0")
    )
    unrealized_gain_loss = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0")
    )
    gain_loss_percentage = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    holding_period_days = models.IntegerField(default=0)
    is_long_term = models.BooleanField(default=False)
    wash_sale_risk = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["purchase_date"]

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.symbol} ({self.purchase_date})"
