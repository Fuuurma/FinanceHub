from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from django.db import models


class AssetMetrics(UUIDModel, TimestampedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="metrics")
    date = models.DateField(db_index=True)

    # Valuations
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    fdv = models.DecimalField(
        max_digits=30, decimal_places=2, null=True, help_text="Fully Diluted Valuation"
    )

    # Supply Data
    circulating_supply = models.DecimalField(max_digits=40, decimal_places=8, null=True)
    total_supply = models.DecimalField(max_digits=40, decimal_places=8, null=True)

    # Volume & Liquidity
    volume_24h = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    # Price Change Percentages
    price_change_24h = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        help_text="Percentage price change over the last 24 hours",
    )
    price_change_7d = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        help_text="Percentage price change over the last 7 days",
    )
    price_change_30d = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        help_text="Percentage price change over the last 30 days",
    )
    price_change_1y = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        help_text="Percentage price change over the last 1 year",
    )

    # Metadata for the entry
    provider = models.ForeignKey(
        "investments.DataProvider",
        on_delete=models.SET_NULL,
        null=True,
        related_name="metrics",
    )

    class Meta:
        # Crucial for preventing duplicate data for the same day
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "date"], name="unique_asset_metric_daily"
            )
        ]
        # Partial index for fast lookups of recent data
        indexes = [
            models.Index(fields=["asset", "-date"]),
        ]
