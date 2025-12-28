from django.db import models

from assets.models.asset import Asset


class CryptoAsset(Asset):
    """Digital Asset-specific supply metrics."""

    circulating_supply = models.DecimalField(
        max_digits=40, decimal_places=10, null=True
    )
    total_supply = models.DecimalField(max_digits=40, decimal_places=10, null=True)
    max_supply = models.DecimalField(max_digits=40, decimal_places=10, null=True)
    fdv = models.DecimalField(
        max_digits=30, decimal_places=2, null=True, help_text="Fully Diluted Valuation"
    )
    contract_address = models.CharField(max_length=255, blank=True, null=True)
    blockchain = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "fh_assets_crypto"
