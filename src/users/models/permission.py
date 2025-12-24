from django.db import models
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Permission(UUIDModel, TimestampedModel):
    """Permission model for granular access control"""

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique permission code (e.g., 'users.create')",
    )
    name = models.CharField(max_length=150, help_text="Human-readable permission name")
    description = models.TextField(
        blank=True, help_text="Detailed description of what this permission allows"
    )
    module = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Module this permission belongs to (e.g., 'users', 'investments')",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this permission is active"
    )

    class Meta:
        db_table = "permissions"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ["module", "code"]
        indexes = [
            models.Index(fields=["module", "is_active"]),
        ]

    def __str__(self):
        return f"{self.module}.{self.code}"
