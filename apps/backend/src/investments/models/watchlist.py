from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Watchlist(UUIDModel, TimestampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="watchlists"
    )
    name = models.CharField(max_length=100)
    assets = models.ManyToManyField("assets.Asset", blank=True)
    is_public = models.BooleanField(
        default=False, help_text="Make this watchlist visible to others"
    )

    class Meta:
        db_table = "watchlists"
        unique_together = ("user", "name")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["user", "is_public"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    @property
    def asset_symbols(self):
        return list(self.assets.values_list("symbol", flat=True))
