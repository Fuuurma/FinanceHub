from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel

from django.db import models


class TopHolder(UUIDModel, TimestampedModel):
    """Significant institutional or individual owners."""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="major_holders"
    )
    holder_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=30, decimal_places=4)
    percentage_owned = models.DecimalField(max_digits=7, decimal_places=4)
    report_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "asset_top_holders"
        unique_together = ("asset", "holder_name", "report_date")
