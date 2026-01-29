from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class Industry(UUIDModel, TimestampedModel):
    """
    GICS Industry classification for stocks and ETFs.
    Industries belong to a Sector.
    """

    code = models.CharField(
        max_length=20, help_text="Industry code (e.g., 'Semiconductors', 'Banks')"
    )
    name = models.CharField(max_length=150, help_text="Industry name")
    sector = models.ForeignKey(
        "assets.Sector",
        on_delete=models.CASCADE,
        related_name="industries",
        help_text="Parent sector",
    )
    gics_code = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="GICS industry code"
    )
    description = models.TextField(blank=True, help_text="Description of the industry")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "industries"
        unique_together = ("sector", "code")
        ordering = ["sector__name", "name"]
        verbose_name = "Industry"
        verbose_name_plural = "Industries"

    def __str__(self):
        return f"{self.code} ({self.sector.name})"
