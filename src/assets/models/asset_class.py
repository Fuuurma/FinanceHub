from django.db import models


class AssetClass(models.Model):
    """Reference table: e.g., 'Equity', 'Fixed Income', 'Commodity', 'Crypto'"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "asset_classes"
