from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Alert(UUIDModel, TimestampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    asset = models.ForeignKey("assets.Asset", on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)  # Price target, % change, etc.
    target_value = models.DecimalField(max_digits=15, decimal_places=6)
    is_active = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alert for {self.user.username} on {self.asset.ticker} - {self.alert_type} at {self.target_value}"
