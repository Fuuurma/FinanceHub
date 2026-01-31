from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .asset import Asset

User = get_user_model()


class EarningsEvent(models.Model):
    QUARTER_CHOICES = [
        ("Q1", "Q1"),
        ("Q2", "Q2"),
        ("Q3", "Q3"),
        ("Q4", "Q4"),
    ]

    TIME_CHOICES = [
        ("pre-market", "Pre-Market"),
        ("after-market", "After-Market"),
        ("during", "During Market"),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="earnings")
    fiscal_quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    fiscal_year = models.IntegerField()
    earnings_date = models.DateTimeField()
    earnings_time = models.CharField(
        max_length=20, choices=TIME_CHOICES, default="during"
    )
    estimated_eps = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    actual_eps = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    estimated_revenue = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    actual_revenue = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    eps_surprise = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    revenue_surprise = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    price_before = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )
    price_after = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )
    price_change_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    conference_call_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-earnings_date"]
        indexes = [
            models.Index(fields=["asset", "-earnings_date"]),
            models.Index(fields=["earnings_date"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} {self.fiscal_quarter} {self.fiscal_year}"


class CorporateAction(models.Model):
    ACTION_TYPE_CHOICES = [
        ("dividend", "Dividend"),
        ("split", "Stock Split"),
        ("reverse_split", "Reverse Split"),
        ("buyback", "Share Buyback"),
        ("spinoff", "Spin-off"),
        ("acquisition", "Acquisition"),
        ("merger", "Merger"),
        ("reorganization", "Reorganization"),
        ("name_change", "Name Change"),
        ("ticker_change", "Ticker Change"),
        ("delisting", "Delisting"),
        ("ipo", "IPO"),
        ("secondary", "Secondary Offering"),
    ]

    STATUS_CHOICES = [
        ("announced", "Announced"),
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="corporate_actions"
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="announced"
    )
    announcement_date = models.DateTimeField()
    record_date = models.DateTimeField(null=True, blank=True)
    ex_date = models.DateTimeField(null=True, blank=True)
    payable_date = models.DateTimeField(null=True, blank=True)
    effective_date = models.DateTimeField(null=True, blank=True)
    details = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-announcement_date"]
        indexes = [
            models.Index(fields=["asset", "-announcement_date"]),
            models.Index(fields=["action_type", "-announcement_date"]),
            models.Index(fields=["ex_date"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} {self.action_type}"


class DividendHistory(models.Model):
    FREQUENCY_CHOICES = [
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("semi-annual", "Semi-Annual"),
        ("annual", "Annual"),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="dividends")
    ex_dividend_date = models.DateTimeField()
    record_date = models.DateTimeField()
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    currency = models.CharField(max_length=3, default="USD")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    adjusted_amount = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    price_on_ex_date = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )
    yield_on_ex_date = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ex_dividend_date"]
        indexes = [
            models.Index(fields=["asset", "-ex_dividend_date"]),
            models.Index(fields=["payment_date"]),
        ]

    def __str__(self):
        return f"{self.asset.symbol} ${self.amount} on {self.ex_dividend_date.date()}"


class EconomicEvent(models.Model):
    IMPORTANCE_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    importance = models.CharField(
        max_length=10, choices=IMPORTANCE_CHOICES, default="medium"
    )
    event_date = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True)
    actual = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    forecast = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )
    previous = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )
    impact_description = models.TextField(blank=True)
    country = models.CharField(max_length=3)
    source = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date"]
        indexes = [
            models.Index(fields=["event_date"]),
            models.Index(fields=["importance", "-event_date"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.event_date.date()})"


class EventAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ("earnings", "Earnings"),
        ("dividend", "Dividend"),
        ("split", "Split"),
        ("economic_event", "Economic Event"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_alerts"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    alert_before_days = models.IntegerField(default=1)
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.alert_type} alert"
