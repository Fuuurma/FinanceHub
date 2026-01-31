from django.db import models
from django.utils import timezone
from decimal import Decimal

STATUS_CHOICES = [
    ("upcoming", "Upcoming"),
    ("filed", "S-1 Filed"),
    ("updated", "Amended"),
    ("priced", "Priced"),
    ("listed", "Listed"),
    ("withdrawn", "Withdrawn"),
    ("postponed", "Postponed"),
]


class IPOCalendar(models.Model):
    company_name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=20, blank=True, default="")
    exchange = models.CharField(max_length=50, blank=True, default="")

    expected_price_min = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    expected_price_max = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    actual_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    shares_offered = models.IntegerField(null=True, blank=True)
    deal_size = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    filed_date = models.DateField(null=True, blank=True)
    expected_date = models.DateField(null=True, blank=True)
    priced_date = models.DateField(null=True, blank=True)
    listed_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")

    sector = models.CharField(max_length=100, blank=True, default="")
    industry = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")

    lead_underwriter = models.CharField(max_length=200, blank=True, default="")
    underwriters = models.JSONField(default=list)

    expected_valuation = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    raised_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    market_cap_estimate = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    ipo_day_change = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    ipo_day_change_pct = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_ipo_calendar"
        ordering = ["expected_date"]
        indexes = [
            models.Index(fields=["status", "-expected_date"]),
            models.Index(fields=["-expected_date"]),
            models.Index(fields=["sector"]),
            models.Index(fields=["exchange"]),
        ]


class IPOAlert(models.Model):
    user_id = models.IntegerField()

    ALERT_TYPE_CHOICES = [
        ("upcoming", "Upcoming IPO"),
        ("filing", "New Filing"),
        ("priced", "IPO Priced"),
        ("listed", "IPO Listed"),
        ("price_range", "Price Range Update"),
        ("all", "All IPO Activity"),
    ]

    alert_type = models.CharField(
        max_length=20, choices=ALERT_TYPE_CHOICES, default="upcoming"
    )

    company_name_contains = models.CharField(max_length=200, blank=True, default="")
    sector = models.CharField(max_length=100, blank=True, default="")
    exchange = models.CharField(max_length=50, blank=True, default="")

    min_deal_size = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    max_deal_size = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    is_active = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_ipo_alert"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id", "is_active"]),
        ]


class IPOWatchlist(models.Model):
    user_id = models.IntegerField()
    ipo_id = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "investments_ipo_watchlist"
        unique_together = ["user_id", "ipo_id"]
        indexes = [
            models.Index(fields=["user_id", "-added_at"]),
        ]


class SPACTracker(models.Model):
    STATUS_CHOICES = [
        ("searching", "Searching for Target"),
        ("announced", "Target Announced"),
        ("merger", "Merger Filed"),
        ("completed", "Merger Completed"),
        ("liquidated", "Liquidated"),
    ]

    ticker = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)

    trust_size = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    redemption_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    target_sector = models.CharField(max_length=100, blank=True, default="")
    target_industry = models.CharField(max_length=100, blank=True, default="")

    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="searching"
    )

    current_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    nav_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    partner = models.CharField(max_length=200, blank=True, default="")
    sponsor = models.CharField(max_length=200, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_spac_tracker"
        ordering = ["-trust_size"]
        indexes = [
            models.Index(fields=["status", "-trust_size"]),
            models.Index(fields=["target_sector"]),
        ]
