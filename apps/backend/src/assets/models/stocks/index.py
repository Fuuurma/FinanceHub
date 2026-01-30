from django.db import models

from assets.models.asset import Asset


class IndexAsset(Asset):
    # Index-specific fields are now in Asset model
    # These fields are nullable and used for index metadata
    class Meta:
        db_table = "asset_indexes"
