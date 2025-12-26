import os
from decimal import Decimal
from datetime import date, timedelta
from typing import Optional

# from polygon import RESTClient
# from pycoingecko import CoinGeckoAPI
from django.db import transaction

from assets.models.asset import Asset
from assets.models.price_history import PriceHistory
from investments.models.data_provider import DataProviderConfig
from utils.helpers.error_handler.exceptions import ValidationException
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class PriceFetcher:
    @classmethod
    def get_provider_client(cls, provider_name: str):
        config = DataProviderConfig.objects.get(name=provider_name)
        if provider_name == "polygon":
            print("Polygon client would be initialized here")
            # return RESTClient(config.api_key)
        elif provider_name == "coingecko":
            print("CoinGecko client would be initialized here")
            # return CoinGeckoAPI()
        raise ValueError(f"Unknown provider: {provider_name}")

    @classmethod
    @transaction.atomic
    def fetch_stock_price(cls, asset: Asset, date_: date, client):
        """
        Fetch from Polygon (stocks, forex, commodities, derivatives).
        """
        try:
            # Endpoint: /v1/open-close/{ticker}/{date}
            agg = client.get_daily_open_close_agg(
                asset.ticker, date_.strftime("%Y-%m-%d")
            )
            if agg:
                PriceHistory.objects.update_or_create(
                    asset=asset,
                    date=date_,
                    defaults={
                        "open": Decimal(str(agg.open)),
                        "high": Decimal(str(agg.high)),
                        "low": Decimal(str(agg.low)),
                        "close": Decimal(str(agg.close)),
                        "volume": agg.volume if agg.volume else None,
                        "source": "polygon",
                    },
                )
                logger.info(f"Fetched price for {asset.ticker} on {date_}")
        except Exception as e:
            logger.error(f"Polygon fetch failed for {asset.ticker}: {str(e)}")
            # Fallback to latest cached
            return cls.get_fallback_price(asset)

    @classmethod
    @transaction.atomic
    def fetch_crypto_price(cls, asset: Asset, date_: date, client: str):
        """
        Fetch from CoinGecko (crypto).
        Coin ID mapping: e.g., 'bitcoin' for BTC-USD
        """
        coin_id = asset.ticker.split("-")[0].lower()  # e.g., 'btc-usd' → 'btc'
        try:
            # Endpoint: /coins/{id}/history?date=dd-mm-yyyy
            data = client.get_coin_history_by_id(
                coin_id, date=date_.strftime("%d-%m-%Y")
            )
            if data and (
                price := data.get("market_data", {}).get("current_price", {}).get("usd")
            ):
                PriceHistory.objects.update_or_create(
                    asset=asset,
                    date=date_,
                    defaults={"close": Decimal(str(price)), "source": "coingecko"},
                )
                logger.info(f"Fetched price for {asset.ticker} on {date_}")
        except Exception as e:
            logger.error(f"CoinGecko fetch failed for {asset.ticker}: {str(e)}")
            return cls.get_fallback_price(asset)

    @classmethod
    def get_fallback_price(cls, asset: Asset) -> Optional[PriceHistory]:
        """
        Fallback to latest cached price if fetch fails.
        """
        latest = PriceHistory.objects.filter(asset=asset).order_by("-date").first()
        if latest:
            logger.warning(
                f"Using fallback cached price for {asset.ticker} from {latest.date}"
            )
            return latest
        raise ValidationException("No price data available for asset")

    @classmethod
    def fetch_price(cls, asset: Asset, date_: date = date.today()):
        """
        Main entry: Dispatch based on asset type.
        """
        if asset.asset_type.name == "Stock":  # or forex/commodities/derivatives
            client = cls.get_provider_client("polygon")
            cls.fetch_stock_price(asset, date_, client)
        elif asset.asset_type.name == "Cryptocurrency":
            client = cls.get_provider_client("coingecko")
            cls.fetch_crypto_price(asset, date_, client)
        else:
            raise ValueError(f"No fetcher for asset type: {asset.asset_type.name}")
