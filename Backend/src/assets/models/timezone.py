from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class Timezone(UUIDModel, TimestampedModel):
    """
    Timezone reference table for market data and trading sessions.
    """

    name = models.CharField(
        max_length=50, unique=True, help_text="Timezone name (e.g., 'America/New_York')"
    )
    utc_offset = models.IntegerField(help_text="UTC offset in hours (e.g., -5 for EST)")
    utc_offset_str = models.CharField(
        max_length=10, help_text="UTC offset string (e.g., 'UTC-5')"
    )
    abbreviation = models.CharField(
        max_length=10, help_text="Timezone abbreviation (e.g., 'EST', 'PST')"
    )
    is_active = models.BooleanField(default=True)
    is_dst_observed = models.BooleanField(
        default=True, help_text="Whether Daylight Saving Time is observed"
    )

    class Meta:
        db_table = "timezones"
        ordering = ["utc_offset", "name"]
        verbose_name = "Timezone"
        verbose_name_plural = "Timezones"

    def __str__(self):
        return f"{self.name} ({self.utc_offset_str})"
