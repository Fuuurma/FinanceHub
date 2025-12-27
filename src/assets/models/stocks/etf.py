from django.db import models

from assets.models.asset import Asset


class ETFAsset(Asset):
    # ETF-specific (e.g., expense_ratio, aum = assets under management)
    expense_ratio = models.DecimalField(
        max_digits=5, decimal_places=4, null=True
    )  # e.g., 0.03
    aum = models.DecimalField(
        max_digits=30, decimal_places=2, null=True
    )  # Assets under management
