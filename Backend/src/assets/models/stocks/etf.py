from django.db import models

from assets.models.asset import Asset


class ETFAsset(Asset):
    # ETF-specific (e.g., expense_ratio, aum = assets under management)
    # These fields are now in Asset model, so no additional fields needed
    class Meta:
        db_table = "asset_etf"
