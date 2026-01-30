"""
Economic Indicator Models for FRED data
Stores economic time series data from Federal Reserve Economic Data (FRED)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from assets.models.asset import Asset
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class EconomicIndicator(UUIDModel, TimestampedModel):
    """Economic indicator metadata from FRED"""

    class Frequency(models.TextChoices):
        DAILY = "d", "Daily"
        WEEKLY = "w", "Weekly"
        BIWEEKLY = "bw", "Biweekly"
        MONTHLY = "m", "Monthly"
        QUARTERLY = "q", "Quarterly"
        SEMIANNUAL = "sa", "Semiannual"
        ANNUAL = "a", "Annual"

    class Units(models.TextChoices):
        LEVEL = "lin", "Levels (No transformation)"
        CHANGE = "chg", "Change"
        CHANGE_FROM_YR_AGO = "ch1", "Change from Year Ago"
        PERCENT_CHANGE = "pch", "Percent Change"
        PERCENT_CHANGE_YR_AGO = "pc1", "Percent Change from Year Ago"
        COMP_ANNUAL_RATE = "pca", "Compounded Annual Rate of Change"
        CONT_COMPOUNDED_RATE = "cch", "Continuously Compounded Rate of Change"
        CONT_ANNUAL_RATE = "cca", "Continuously Compounded Annual Rate of Change"
        LOG = "log", "Natural Log"

    series_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="FRED series ID (e.g., 'GDP', 'CPIAUCSL')",
    )
    title = models.CharField(max_length=500, help_text="Series title")
    description = models.TextField(blank=True, help_text="Series description")
    units = models.CharField(
        max_length=100,
        blank=True,
        help_text="Units of measurement (e.g., 'Billions of Dollars', 'Percent')",
    )
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        blank=True,
        help_text="Data frequency (d, w, m, q, a, etc.)",
    )
    seasonal_adjustment = models.CharField(
        max_length=100,
        blank=True,
        help_text="Seasonal adjustment (e.g., 'Seasonally Adjusted Annual Rate')",
    )
    last_updated = models.DateTimeField(
        null=True, blank=True, help_text="When the series was last updated by FRED"
    )
    observation_start = models.DateField(
        null=True, blank=True, help_text="Earliest available observation date"
    )
    observation_end = models.DateField(
        null=True, blank=True, help_text="Latest available observation date"
    )
    popularity_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Popularity score based on usage",
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorization (e.g., ['gdp', 'inflation', 'employment'])",
    )

    class Meta:
        db_table = "economic_indicators"
        verbose_name = "Economic Indicator"
        verbose_name_plural = "Economic Indicators"
        ordering = ["popularity_score", "series_id"]
        indexes = [
            models.Index(fields=["series_id"]),
            models.Index(fields=["frequency"]),
            models.Index(fields=["popularity_score"]),
            models.Index(fields=["observation_end"]),
        ]

    def __str__(self):
        return f"{self.series_id}: {self.title}"


class EconomicDataPoint(UUIDModel, TimestampedModel):
    """Time series data point for economic indicators"""

    indicator = models.ForeignKey(
        EconomicIndicator,
        on_delete=models.CASCADE,
        related_name="data_points",
        db_index=True,
    )
    date = models.DateField(db_index=True)
    value = models.DecimalField(max_digits=20, decimal_places=6, help_text="Data value")
    realtime_start = models.DateField(
        null=True, blank=True, help_text="Real-time period start date"
    )
    realtime_end = models.DateField(
        null=True, blank=True, help_text="Real-time period end date"
    )

    class Meta:
        db_table = "economic_data_points"
        verbose_name = "Economic Data Point"
        verbose_name_plural = "Economic Data Points"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["indicator", "date"]),
            models.Index(fields=["date"]),
            models.Index(fields=["-date"]),
        ]
        unique_together = [["indicator", "date", "realtime_start"]]

    def __str__(self):
        return f"{self.indicator.series_id}: {self.date} = {self.value}"


class EconomicDataCache(UUIDModel, TimestampedModel):
    """Cache for frequently accessed economic data"""

    cache_key = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Unique cache key (e.g., 'latest_macro_data', 'gdp_2023')",
    )
    data = models.JSONField(help_text="Cached economic data")
    expires_at = models.DateTimeField(
        db_index=True, help_text="When this cache expires"
    )
    last_fetched = models.DateTimeField(
        auto_now=True, help_text="When this cache was last fetched"
    )

    class Meta:
        db_table = "economic_data_cache"
        verbose_name = "Economic Data Cache"
        verbose_name_plural = "Economic Data Caches"
        ordering = ["-last_fetched"]
        indexes = [
            models.Index(fields=["cache_key"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.cache_key} (expires: {self.expires_at})"
