from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class Country(UUIDModel, TimestampedModel, SoftDeleteModel):
    code = models.CharField(max_length=2, unique=True)  # ISO2 e.g., "US"
    name = models.CharField(max_length=100, unique=True)
    alpha_3 = models.CharField(
        max_length=3, unique=True, blank=True, null=True
    )  # ISO3 e.g., "USA"
    numeric_code = models.CharField(
        max_length=3, unique=True, blank=True, null=True
    )  # ISO numeric e.g., "840"
    region = models.CharField(max_length=50, blank=True)  # e.g., "Americas"
    subregion = models.CharField(max_length=100, blank=True)  # e.g., "Northern America"

    def __str__(self):
        return self.name
