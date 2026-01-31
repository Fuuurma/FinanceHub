from django.db import models
from django.conf import settings
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Stock screener preset for saving and reusing filter configurations.

    Inherits from:
    - UUIDModel: Provides UUID primary key (id field)
    - TimestampedModel: Provides created_at, updated_at timestamps
    - SoftDeleteModel: Provides is_deleted, deleted_at for soft deletion
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="screener_presets",
    )
    name = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ["user", "name"]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "filters": self.filters,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
