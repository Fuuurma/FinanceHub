from django.db import models

from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class Currency(UUIDModel, TimestampedModel, SoftDeleteModel):
    code = models.CharField(
        max_length=10, unique=True
    )  # ISO 4217 code or crypto symbol e.g., "USD", "BTC", "USDT"
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, blank=True)  # e.g., "$", "€", "£"
    numeric_code = models.CharField(
        max_length=3, unique=True, blank=True, null=True
    )  # ISO 4217 numeric e.g., "840"
    is_crypto = models.BooleanField(default=False)
    decimals = models.PositiveSmallIntegerField(default=2)

    # Optional: Link to primary country (many currencies are used by multiple countries)
    country = models.ForeignKey(
        "assets.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="currencies",
    )

    def __str__(self):
        return self.code
