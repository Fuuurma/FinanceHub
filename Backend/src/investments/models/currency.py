from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel


class Currency(UUIDModel, TimestampedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, blank=True)
    is_crypto = models.BooleanField(default=False)
    decimals = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return self.code
