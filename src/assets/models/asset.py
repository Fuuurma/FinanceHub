from django.db import models
from django.core.validators import MinValueValidator

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
