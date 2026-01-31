from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class Benchmark(UUIDModel, TimestampedModel, SoftDeleteModel):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=30, unique=True)  # e.g., ^GSPC for S&P 500
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
