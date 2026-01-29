"""
Trending Asset Model
Stores trending cryptocurrency data from CoinGecko
"""

from django.db import models
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class TrendingAsset(UUIDModel, TimestampedModel):
    """Trending cryptocurrencies from CoinGecko"""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="trending_records", db_index=True
    )

    rank = models.IntegerField(db_index=True)
    market_cap = models.DecimalField(
        max_digits=30, decimal_places=2, null=True, blank=True
    )
    volume_24h = models.DecimalField(
        max_digits=30, decimal_places=2, null=True, blank=True
    )
    price_change_24h = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    price_change_percentage_24h = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="24h price change as percentage",
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Sparkline data (7 days of price data)
    sparkline_data = models.JSONField(
        default=list, blank=True, help_text="List of prices for the last 7 days"
    )

    class Meta:
        db_table = "trending_assets"
        verbose_name = "Trending Asset"
        verbose_name_plural = "Trending Assets"
        ordering = ["rank"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["rank"]),
        ]

    def __str__(self):
        return f"#{self.rank} {self.asset.ticker} ({self.asset.name})"
