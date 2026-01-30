from django.contrib import admin

from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from assets.models.asset_metrics import AssetMetrics
from assets.models.asset_provider import AssetProviderMapping
from assets.models.asset_type import AssetType
from assets.models.common.top_holder import AssetTopHolder
from assets.models.country import Country
from assets.models.crypto.asset import CryptoAsset
from assets.models.exchange import Exchange
from assets.models.historic.metrics import AssetMetricsHistoric
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.stocks.asset import StockAsset
from assets.models.stocks.corporate_action import CorporateAction
from assets.models.stocks.etf import ETFAsset
from assets.models.stocks.index import IndexAsset
from assets.models.stocks.recommendation import AssetRecommendation

admin.site.register(Country)
admin.site.register(Exchange)
admin.site.register(AssetType)
admin.site.register(AssetClass)
admin.site.register(Asset)
admin.site.register(AssetPricesHistoric)
admin.site.register(AssetMetricsHistoric)
admin.site.register(AssetProviderMapping)
admin.site.register(AssetMetrics)
admin.site.register(StockAsset)
admin.site.register(CryptoAsset)
admin.site.register(CorporateAction)
admin.site.register(IndexAsset)
admin.site.register(AssetRecommendation)
admin.site.register(AssetTopHolder)
admin.site.register(ETFAsset)
