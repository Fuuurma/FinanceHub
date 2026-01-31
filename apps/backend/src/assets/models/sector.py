from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class Sector(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    GICS Sector classification for stocks and ETFs.
    11 primary sectors in GICS taxonomy.
    """

    code = models.CharField(
        max_length=20, unique=True, help_text="GICS sector code (e.g., 'XLK', 'XLF')"
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Sector name (e.g., 'Technology', 'Financials')",
    )
    description = models.TextField(blank=True, help_text="Description of the sector")
    gics_code = models.PositiveSmallIntegerField(
        unique=True, null=True, blank=True, help_text="GICS sector code (1-11)"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "sectors"
        ordering = ["gics_code", "name"]
        verbose_name = "Sector"
        verbose_name_plural = "Sectors"

    def __str__(self):
        return f"{self.code} - {self.name}"
