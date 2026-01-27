from django.db import models
from django.core.validators import MinValueValidator

from assets.models.asset import Asset


class StockAsset(Asset):
    """Equity-specific fundamentals."""

    industry = models.CharField(max_length=150, blank=True)
    sector = models.CharField(max_length=150, blank=True)

    # Financial Identifiers
    isin = models.CharField(
        max_length=12,
        blank=True,
        help_text="International Securities Identification Number",
    )
    cusip = models.CharField(max_length=9, blank=True, null=True)
    pe_ratio = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    eps = models.DecimalField(max_digits=15, decimal_places=4, null=True)
    revenue_ttm = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    # todo: balance sheet, cash flow, dividends, etc ect etc

    class Meta:
        db_table = "assets_stocks"
