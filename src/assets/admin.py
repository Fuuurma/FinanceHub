from django.contrib import admin

from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from assets.models.asset_type import AssetType
from assets.models.price_history import PriceHistory

admin.site.register(AssetType)
admin.site.register(AssetClass)
admin.site.register(Asset)
admin.site.register(PriceHistory)
