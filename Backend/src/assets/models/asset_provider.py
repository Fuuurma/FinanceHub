from assets.models.asset import Asset
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.uuid_model import UUIDModel

from django.db import models


class AssetProviderMapping(UUIDModel, TimestampedModel):
    """Maps an internal Asset to its ID in an external provider."""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="provider_mappings"
    )
    provider = models.ForeignKey("investments.DataProvider", on_delete=models.CASCADE)

    # The ID used by the provider (e.g., 'bitcoin' for CoinGecko, 'BTC-USD' for Yahoo)
    external_id = models.CharField(max_length=255)

    # Is this the "preferred" source for this specific asset's price?
    is_primary_source = models.BooleanField(default=False)

    class Meta:
        unique_together = ("provider", "external_id")
        verbose_name = "Asset Provider Mapping"
