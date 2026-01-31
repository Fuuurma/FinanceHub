from django.db import models
from django.utils import timezone
from decimal import Decimal


class OrderBookLevel(models.Model):
    """Individual price levels in order book"""

    SIDE_CHOICES = [
        ("bid", "Bid"),
        ("ask", "Ask"),
    ]

    asset_id = models.IntegerField(db_index=True)
    side = models.CharField(max_length=3, choices=SIDE_CHOICES)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    orders_count = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "investments_order_book_level"
        indexes = [
            models.Index(fields=["asset_id", "side", "-price"]),
            models.Index(fields=["asset_id", "-timestamp"]),
            models.Index(fields=["timestamp"]),
        ]
        unique_together = [["asset_id", "side", "price", "timestamp"]]


class OrderBookSnapshot(models.Model):
    """Aggregated order book snapshot at point in time"""

    asset_id = models.IntegerField(db_index=True)
    bids = models.JSONField(default=list)
    asks = models.JSONField(default=list)
    total_bid_volume = models.DecimalField(max_digits=30, decimal_places=8)
    total_ask_volume = models.DecimalField(max_digits=30, decimal_places=8)
    bid_ask_spread = models.DecimalField(max_digits=20, decimal_places=6)
    bid_ask_spread_pct = models.DecimalField(max_digits=10, decimal_places=6)
    top_5_bid_volume = models.DecimalField(max_digits=30, decimal_places=8)
    top_5_ask_volume = models.DecimalField(max_digits=30, decimal_places=8)
    top_10_bid_volume = models.DecimalField(max_digits=30, decimal_places=8)
    top_10_ask_volume = models.DecimalField(max_digits=30, decimal_places=8)
    vwap_bid = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    vwap_ask = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    order_imbalance = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "investments_order_book_snapshot"
        indexes = [
            models.Index(fields=["asset_id", "-timestamp"]),
            models.Index(fields=["-timestamp"]),
        ]


class TimeAndSales(models.Model):
    """Tick-by-tick trade data"""

    TRADE_TYPE_CHOICES = [
        ("buy", "Buy"),
        ("sell", "Sell"),
        ("unknown", "Unknown"),
    ]

    asset_id = models.IntegerField(db_index=True)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    trade_type = models.CharField(
        max_length=10, choices=TRADE_TYPE_CHOICES, default="unknown"
    )
    timestamp = models.DateTimeField(db_index=True)
    trade_id = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        db_table = "investments_time_and_sales"
        indexes = [
            models.Index(fields=["asset_id", "-timestamp"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["trade_id"]),
        ]
        ordering = ["-timestamp"]


class MarketDepthSummary(models.Model):
    """Rolling summary of market depth (calculated periodically)"""

    asset_id = models.OneToOneField(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="depth_summary",
        primary_key=True,
    )
    best_bid = models.DecimalField(max_digits=20, decimal_places=6)
    best_ask = models.DecimalField(max_digits=20, decimal_places=6)
    current_spread = models.DecimalField(max_digits=20, decimal_places=6)
    depth_within_1pct = models.DecimalField(max_digits=30, decimal_places=8)
    depth_within_5pct = models.DecimalField(max_digits=30, decimal_places=8)
    depth_within_10pct = models.DecimalField(max_digits=30, decimal_places=8)
    buy_volume_5min = models.DecimalField(max_digits=30, decimal_places=8)
    sell_volume_5min = models.DecimalField(max_digits=30, decimal_places=8)
    buy_volume_15min = models.DecimalField(max_digits=30, decimal_places=8)
    sell_volume_15min = models.DecimalField(max_digits=30, decimal_places=8)
    price_impact_per_1k = models.DecimalField(
        max_digits=10, decimal_places=6, null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "investments_market_depth_summary"


class LargeOrders(models.Model):
    """Track unusually large orders (whale activity)"""

    asset_id = models.IntegerField(db_index=True)
    side = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    value_usd = models.DecimalField(max_digits=30, decimal_places=2)
    size_multiple = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "investments_large_orders"
        indexes = [
            models.Index(fields=["asset_id", "-timestamp"]),
            models.Index(fields=["-value_usd"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]
