from django.db import models
from django.core.validators import MinValueValidator

from assets.models.asset import Asset


class StockAsset(Asset):
    eps = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    industry = models.CharField(max_length=100, blank=True)
    stock_splits = models.JSONField(
        default=list, blank=True
    )  # e.g., [{"date": "2020-08-31", "ratio": 4}]
