from django.db import models

from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class CorporateAction(UUIDModel, TimestampedModel):
    asset = models.ForeignKey("assets.Asset", on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)  # Split, Merger, Spin-off, etc.
    date = models.DateField()
    ratio = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.asset.ticker} {self.action_type} on {self.date}"
