from django.db import models

from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class CorporateAction(UUIDModel, TimestampedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(
        max_length=50,
        choices=[
            ("split", "Stock Split"),
            ("dividend", "Dividend"),
            ("merger", "Merger"),
        ],
    )
    date = models.DateField()
    ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    description = models.TextField(blank=True)
