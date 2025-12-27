from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel

from django.db import models


class TopHolder(UUIDModel, TimestampedModel):
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="top_holders"
    )
    holder_name = models.CharField(max_length=200)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    shares = models.BigIntegerField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
