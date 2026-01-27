from django.db import models

from assets.models.asset import Asset


class IndexAsset(Asset):
    # Index-specific (e.g., constituents_count, weighting_method)
    constituents_count = models.IntegerField(null=True)
    weighting_method = models.CharField(
        max_length=50, blank=True
    )  # e.g., "Market Cap Weighted"

    class Meta:
        db_table = "asset_indexes"
