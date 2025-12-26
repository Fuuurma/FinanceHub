from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


# change to DataProviderConfig & DataProvider w/ rel


class DataProviderConfig(UUIDModel, TimestampedModel):
    """
    Config for data providers (API keys, etc.) - stored securely.
    """

    name = models.CharField(max_length=50, unique=True)  # e.g., "polygon", "coingecko"
    api_key = models.CharField(max_length=100, blank=True)  # Encrypted in production
    base_url = models.URLField(blank=True)
    rate_limit_per_minute = models.PositiveIntegerField(blank=True, null=True)
    rate_limit_daily = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
