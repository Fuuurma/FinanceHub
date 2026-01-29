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

    country = models.ForeignKey(
        "assets.Country", on_delete=models.SET_NULL, null=True, blank=True
    )
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

    # Type-specific fields (nullable - used for Stock, Crypto, ETF, etc.)
    industry = models.CharField(
        max_length=150, blank=True, null=True, help_text="Industry for stocks/ETFs"
    )
    sector = models.CharField(
        max_length=150, blank=True, null=True, help_text="Sector for stocks/ETFs"
    )
    country_of_incorporation = models.CharField(
        max_length=100, blank=True, null=True, help_text="Country for stocks"
    )

    # Stock-specific
    isin = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text="International Securities Identification Number",
    )
    cusip = models.CharField(
        max_length=9, blank=True, null=True, help_text="CUSIP for US stocks"
    )
    ticker_symbol = models.CharField(
        max_length=20, blank=True, null=True, help_text="Ticker symbol for stocks"
    )
    exchange = models.CharField(
        max_length=100, blank=True, null=True, help_text="Exchange name"
    )

    # Valuation metrics (nullable - available for stocks/crypto)
    pe_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price-to-Earnings ratio",
    )
    pb_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price-to-Book ratio",
    )
    ps_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Price-to-Sales ratio",
    )
    dividend_yield = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Dividend yield percentage",
    )
    eps = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Earnings per share",
    )
    revenue_ttm = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Revenue Trailing Twelve Months",
    )

    # Market cap (nullable - for stocks/crypto)
    market_cap_usd = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Market cap in USD",
    )
    circulating_supply = models.BigIntegerField(
        null=True, blank=True, help_text="Circulating supply (for crypto)"
    )
    total_supply = models.BigIntegerField(
        null=True, blank=True, help_text="Total supply (for crypto)"
    )

    # Crypto-specific
    contract_address = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Blockchain contract address (for crypto)",
    )
    price_btc = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True, help_text="Price in BTC"
    )

    # ETF-specific
    expense_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Expense ratio percentage",
    )
    aum = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Assets Under Management",
    )

    # Forex-specific
    base_currency = models.CharField(
        max_length=3, blank=True, null=True, help_text="Base currency for forex pairs"
    )
    quote_currency = models.CharField(
        max_length=3, blank=True, null=True, help_text="Quote currency for forex pairs"
    )
    pip_size = models.DecimalField(
        max_digits=10, decimal_places=5, null=True, blank=True, help_text="PIP size"
    )

    # Index-specific
    index_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type of index (e.g., 'Sector Index', 'Market Index')",
    )
    underlying_tickers = models.JSONField(
        default=list, blank=True, help_text="Underlying assets/tickers"
    )
    rebalance_frequency = models.CharField(
        max_length=50, blank=True, null=True, help_text="Rebalance frequency"
    )

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
