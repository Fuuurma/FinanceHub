from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Watchlist(UUIDModel, TimestampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="watchlists"
    )
    name = models.CharField(max_length=100)
    assets = models.ManyToManyField("assets.Asset")

    class Meta:
        unique_together = ("user", "name")
