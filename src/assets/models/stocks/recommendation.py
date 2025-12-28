from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel

from django.db import models


class AssetRecommendation(UUIDModel, TimestampedModel):
    """Analyst ratings and price targets."""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="analyst_ratings"
    )
    analyst_firm = models.CharField(max_length=150)
    rating = models.CharField(max_length=50, help_text="e.g. Overweight, Buy, Hold")
    target_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    rating_date = models.DateField(db_index=True)
    source_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "asset_recommendations"
