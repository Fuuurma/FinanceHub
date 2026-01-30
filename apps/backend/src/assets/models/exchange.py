from django.db import models
from assets.models.country import Country
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class Exchange(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=10, unique=True)  # e.g., "NYSE"
    name = models.CharField(max_length=100)
    mic = models.CharField(
        max_length=10, unique=True, blank=True, null=True
    )  # ISO 10383 Market Identifier Code
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, related_name="exchanges"
    )
    timezone = models.CharField(max_length=50, blank=True)  # e.g., "America/New_York"
    operating_hours = models.TextField(
        blank=True, help_text="Trading hours in JSON format"
    )
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name
