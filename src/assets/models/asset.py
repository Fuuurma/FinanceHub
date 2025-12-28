from django.db import models
from django.core.validators import MinValueValidator
import orjson

from assets.models.asset_type import AssetType
from utils.helpers.soft_delete_model import SoftDeleteModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from django.utils.text import slugify


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

    asset_class = models.ForeignKey(
        "assets.AssetClass", on_delete=models.PROTECT, related_name="assets"
    )

    exchanges = models.ManyToManyField(
        "assets.Exchange", blank=True, related_name="assets"
    )  # Optional M2M

    country = models.ForeignKey("assets.Country", on_delete=models.SET_NULL, null=True)
    website = models.URLField(blank=True)

    # Base configuration
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    # Tracking the "Latest" state for fast dashboard reads
    last_price = models.DecimalField(
        max_digits=30, decimal_places=10, null=True, blank=True
    )
    last_price_updated_at = models.DateTimeField(null=True, blank=True)

    # Common metrics (updated daily)
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    volume_24h = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    price_change_24h = models.DecimalField(
        max_digits=30, decimal_places=10, null=True, blank=True
    )
    price_change_24h_pct = models.DecimalField(
        max_digits=10, decimal_places=4, null=True
    )

    # ATH/ATL for price and volume
    ath_price = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    ath_price_date = models.DateField(null=True)
    atl_price = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    atl_price_date = models.DateField(null=True)
    ath_volume = models.BigIntegerField(null=True)
    ath_volume_date = models.DateField(null=True)
    atl_volume = models.BigIntegerField(null=True)
    atl_volume_date = models.DateField(null=True)

    metadata = models.JSONField(
        default=dict, blank=True
    )  # Extra data (sector, dividend yield, etc.)

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        db_table = "assets"
        ordering = ["ticker"]
        indexes = [
            models.Index(fields=["status", "ticker"]),
            models.Index(fields=["asset_type", "market_cap"]),
            models.Index(fields=["last_price_updated_at"]),
            models.Index(fields=["last_price"]),
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
