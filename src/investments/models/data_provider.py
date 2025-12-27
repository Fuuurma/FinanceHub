from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel


class DataProvider(UUIDModel, TimestampedModel):
    """
    Model for data providers (e.g., Polygon, CoinGecko).
    Relationships: Assets FK to this for assignment. (Nope. 1 asset, many providers possible.)
    """

    name = models.CharField(max_length=50, unique=True)  # e.g., "polygon", "coingecko"
    display_name = models.CharField(max_length=100)  # e.g., "Polygon.io"
    api_key = models.CharField(
        max_length=200, blank=True
    )  # Encrypted in prod (use django-fernet-fields)
    priority = models.PositiveSmallIntegerField(
        default=10, help_text="Lower is higher priority"
    )

    base_url = models.URLField(blank=True)
    rate_limit_per_minute = models.PositiveIntegerField(blank=True, null=True)
    rate_limit_daily = models.PositiveIntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    config = models.JSONField(
        default=dict, blank=True
    )  # Provider-specific (e.g., {"coin_id_map": {...}})

    def __str__(self):
        return self.name
