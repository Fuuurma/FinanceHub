from django.db import models
from django.core.validators import MinValueValidator
import orjson

from assets.models.asset_type import AssetType
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from django.utils.text import slugify

CHANGE_INTERVAL_CHOICES = [
    ("1h", "1 Hour"),
    ("24h", "24 Hours"),
    ("7d", "7 Days"),
    ("30d", "30 Days"),
    ("1y", "1 Year"),
]


class Asset(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Core tradable/investable asset.
    Examples: AAPL (Apple stock), BTC-USD, SPY (ETF), etc.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        DELISTED = "delisted", "Delisted"

    ticker = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique URL-friendly identifier",
    )
    asset_type = models.ForeignKey(
        AssetType, on_delete=models.PROTECT, related_name="assets"
    )

    exchange = models.ForeignKey(
        "assets.Exchange", on_delete=models.SET_NULL, null=True
    )
    country = models.ForeignKey("assets.Country", on_delete=models.SET_NULL, null=True)

    # Financial Identifiers
    isin = models.CharField(
        max_length=12,
        blank=True,
        help_text="International Securities Identification Number",
    )
    cusip = models.CharField(max_length=9, blank=True, null=True)

    # Base configuration
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    # Common metrics (updated daily)
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    volume_24h = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    price_change_24h_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )
    high_52w = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    low_52w = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    volatility = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )  # e.g., 30-day std dev

    # Tracking the "Latest" state for fast dashboard reads
    last_price = models.DecimalField(
        max_digits=30, decimal_places=10, null=True, blank=True
    )
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    metadata = models.JSONField(
        default=dict, blank=True
    )  # Extra data (sector, dividend yield, etc.)

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        ordering = ["ticker"]
        indexes = [
            models.Index(fields=["ticker"]),
            models.Index(fields=["asset_type"]),
            models.Index(fields=["currency"]),
        ]

    def __str__(self):
        return f"{self.ticker} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.ticker or self.name)
            slug = base_slug
            counter = 1
            while Asset.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def serialize_metadata(self):
        """Fast serialization with orjson"""
        return orjson.dumps(self.metadata).decode()

    # Method for volatility calculation (from historical prices)
    def calculate_volatility(self, days=30):
        from statistics import stdev

        prices = self.prices.order_by("-date")[:days].values_list("close", flat=True)
        if len(prices) < 2:
            return Decimal("0")
        returns = [
            (prices[i] - prices[i + 1]) / prices[i + 1] for i in range(len(prices) - 1)
        ]
        self.volatility = (
            Decimal(str(stdev(returns) * (252**0.5))) if returns else Decimal("0")
        )
        self.save(update_fields=["volatility"])
