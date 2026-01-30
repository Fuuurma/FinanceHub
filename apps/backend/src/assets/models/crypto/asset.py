from django.db import models

from assets.models.asset import Asset


class CryptoAsset(Asset):
    """Digital Asset-specific supply metrics."""

    # Blockchain/contract info
    blockchain = models.CharField(
        max_length=100, blank=True, null=True, help_text="Blockchain network"
    )

    class Meta:
        db_table = "assets_crypto"
