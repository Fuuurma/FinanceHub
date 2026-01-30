"""
Cryptocurrency Population Script
Populates crypto assets with 1-year historical data from CoinGecko (free tier).
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict
import logging

import yfinance as yf
from django.utils import timezone
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")

import django

django.setup()

from utils.helpers.logger.logger import get_logger
from utils.services.yahoo_rate_limiter import get_rate_limiter

from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from assets.models.asset_type import AssetType
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.asset_metrics import AssetMetrics
from investments.models.data_provider import DataProvider

logger = get_logger(__name__)

# Top 100 cryptocurrencies by market cap
CRYPTOCURRENCIES = [
    "BTC",
    "ETH",
    "BNB",
    "XRP",
    "ADA",
    "SOL",
    "DOGE",
    "DOT",
    "MATIC",
    "SHIB",
    "LTC",
    "AVAX",
    "TRX",
    "LINK",
    "ATOM",
    "UNI",
    "XMR",
    "ETC",
    "XLM",
    "BCH",
    "ALGO",
    "VET",
    "FIL",
    "ICP",
    "NEAR",
    "AAVE",
    "APE",
    "MKR",
    "COMP",
    "SAND",
    "MANA",
    "AXS",
    "GALA",
    "ENJ",
    "IMX",
    "QNT",
    "CHZ",
    "CRV",
    "RUNE",
    "1INCH",
    "ZEC",
    "BAT",
    "SNX",
    "REP",
    "KNC",
    "LRC",
    "DASH",
    "MAST",
    "ZRX",
    "BAL",
    "CRO",
    "FTM",
    "HOT",
    "CEL",
    "NEXO",
    "USDC",
    "USDT",
    "BUSD",
    "DAI",
    "TUSD",
    "FRAX",
    "USTC",
    "LUNA",
    "THETA",
    "TFUEL",
    "FET",
    "AGIX",
    "RNDR",
    "OCEAN",
    "INJ",
    "MINA",
    "ROSE",
    "JASMY",
    "STX",
    "OP",
    "ARB",
    "SUI",
    "SEI",
    "TIA",
    "APT",
    "QNT",
    "HBAR",
    "FLOW",
    "EGLD",
    "ELON",
    "BONK",
    "WIF",
    "PEPE",
    "FLOKI",
]


def populate_crypto_sync(historical_years: int = 1):
    """
    Populate crypto assets with historical data.

    Args:
        historical_years: Number of years of historical data (default: 1)
    """
    from assets.models.asset import Asset
    from assets.models.asset_class import AssetClass
    from assets.models.asset_type import AssetType
    from assets.models.historic.prices import AssetPricesHistoric
    from assets.models.asset_metrics import AssetMetrics
    from investments.models.data_provider import DataProvider

    rate_limiter = get_rate_limiter()

    # Get or create data provider
    data_provider, _ = DataProvider.objects.get_or_create(
        name="yahoo_finance",
        defaults={
            "display_name": "Yahoo Finance (Crypto)",
            "priority": 10,
            "rate_limit_per_minute": 100,
            "rate_limit_daily": 2000,
            "is_active": True,
            "config": {"free_tier": True},
        },
    )

    # Get asset types
    crypto_type = AssetType.objects.get(
        name="Cryptocurrency", asset_class__name="Crypto"
    )
    asset_class = AssetClass.objects.get(name="Crypto")

    total = len(CRYPTOCURRENCIES)
    created_count = 0
    updated_count = 0
    error_count = 0

    for i, symbol in enumerate(CRYPTOCURRENCIES):
        try:
            # Yahoo Finance uses "-USD" suffix for crypto
            ticker = f"{symbol}-USD"

            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            # Get current price
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            # Create or update Asset
            asset, created = Asset.objects.update_or_create(
                ticker=ticker,
                defaults={
                    "name": info.get("longName", info.get("shortName", symbol)),
                    "asset_type": crypto_type,
                    "asset_class": asset_class,
                    "currency": "USD",
                    "status": Asset.Status.ACTIVE,
                    "last_price": Decimal(str(current_price))
                    if current_price
                    else None,
                    "last_price_updated_at": timezone.now(),
                    "market_cap_usd": Decimal(str(info.get("marketCap", 0)))
                    if info.get("marketCap")
                    else None,
                    "volume_24h": Decimal(str(info.get("volume24Hr", 0)))
                    if info.get("volume24Hr")
                    else None,
                    "contract_address": None,  # Would need separate blockchain API
                    "circulating_supply": info.get("circulatingSupply"),
                    "total_supply": info.get("totalSupply"),
                    "price_btc": Decimal(str(info.get("priceInBtc", 0)))
                    if info.get("priceInBtc")
                    else None,
                    "metadata": {
                        "52_week_high": info.get("fiftyTwoWeekHigh"),
                        "52_week_low": info.get("fiftyTwoWeekLow"),
                        "24h_high": info.get("regularMarketDayHigh"),
                        "24h_low": info.get("regularMarketDayLow"),
                    },
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            # Fetch historical prices (1 year by default)
            period = f"{historical_years}y"
            hist = ticker_obj.history(period=period, auto_adjust=True)

            if not hist.empty:
                prices_to_create = []
                for idx, row in hist.iterrows():
                    date = idx.date() if hasattr(idx, "date") else idx
                    if not AssetPricesHistoric.objects.filter(
                        asset=asset, date=date, source=data_provider
                    ).exists():
                        prices_to_create.append(
                            AssetPricesHistoric(
                                asset=asset,
                                date=date,
                                open=Decimal(str(row["Open"]))
                                if pd.notna(row["Open"])
                                else None,
                                high=Decimal(str(row["High"]))
                                if pd.notna(row["High"])
                                else None,
                                low=Decimal(str(row["Low"]))
                                if pd.notna(row["Low"])
                                else None,
                                close=Decimal(str(row["Close"]))
                                if pd.notna(row["Close"])
                                else None,
                                volume=row["Volume"]
                                if pd.notna(row["Volume"])
                                else None,
                                source=data_provider,
                            )
                        )

                if prices_to_create:
                    AssetPricesHistoric.objects.bulk_create(
                        prices_to_create, ignore_conflicts=True
                    )

            # Create daily metrics
            today = datetime.now().date()
            AssetMetrics.objects.update_or_create(
                asset=asset,
                date=today,
                defaults={
                    "market_cap": Decimal(str(info.get("marketCap", 0)))
                    if info.get("marketCap")
                    else None,
                    "volume_24h": Decimal(str(info.get("volume24Hr", 0)))
                    if info.get("volume24Hr")
                    else None,
                    "provider": data_provider,
                },
            )

            print(
                f"[{i + 1}/{total}] {symbol}: {info.get('longName', symbol)} - "
                f"{len(hist) if not hist.empty else 0} prices"
            )

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            print(f"[{i + 1}/{total}] ERROR {symbol}: {e}")
            error_count += 1
            continue

    print(f"\nCrypto population complete!")
    print(f"Created: {created_count}, Updated: {updated_count}, Errors: {error_count}")


if __name__ == "__main__":
    import pandas as pd  # Import here to avoid issues

    logging.basicConfig(level=logging.INFO)

    # Default to 1 year historical data, but can be expanded
    historical_years = 1
    if len(sys.argv) > 1:
        historical_years = int(sys.argv[1])
        print(f"Fetching {historical_years} year(s) of historical data")

    populate_crypto_sync(historical_years=historical_years)
