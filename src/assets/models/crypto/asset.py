from django.db import models

from assets.models.asset import Asset


class CryptoAsset(Asset):
    circulating_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    total_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True)
    fdv = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    # crypto related fields like blockchain,
