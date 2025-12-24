from django.db import models


from assets.models.asset_class import AssetClass


class AssetType(models.Model):
    """
    More specific: Common Stock, ETF, Bitcoin, Corporate Bond, etc.
    Belongs to one AssetClass.
    """

    name = models.CharField(max_length=100)
    asset_class = models.ForeignKey(
        AssetClass, on_delete=models.PROTECT, related_name="types"
    )
    symbol_pattern = models.CharField(
        max_length=50, blank=True, help_text="e.g., '^.[A-Z]{1,5}$' for stocks"
    )

    class Meta:
        unique_together = ("name", "asset_class")
        ordering = ["asset_class__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.asset_class})"
