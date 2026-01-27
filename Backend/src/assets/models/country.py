from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class Country(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=2, unique=True)  # ISO2 e.g., "US"
    name = models.CharField(max_length=100, unique=True)
    region = models.CharField(max_length=50, blank=True)  # e.g., "North America"

    def __str__(self):
        return self.name
