from django.db import models
from assets.models.country import Country
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class Exchange(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=10, unique=True)  # e.g., "NYSE"
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    timezone = models.CharField(max_length=50, blank=True)  # e.g., "America/New_York"

    def __str__(self):
        return self.name
