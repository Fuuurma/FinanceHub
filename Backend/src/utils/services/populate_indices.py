"""
Market Indices Population Script
Populates market index assets with 1-year historical data from Yahoo Finance.
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

import yfinance as yf
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")

import django

django.setup()

from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from assets.models.asset_type import AssetType
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.asset_metrics import AssetMetrics
from investments.models.data_provider import DataProvider

logger = __name__

# Major Market Indices (30 global indices)
MARKET_INDICES = [
    # US Indices
    "^GSPC",
    "^DJI",
    "^IXIC",
    "^RUT",
    "^VIX",
    "^NDX",
    "^MID",
    "^SPX",
    "^OEX",
    "^TNX",
    # European Indices
    "^FTSE",
    "^GDAXI",
    "^FCHI",
    "^MIB",
    "^IBEX",
    "^AEX",
    "^OMX",
    "^SMI",
    "^HEX",
    "^OSE",
    # Asian Indices
    "^N225",
    "^HSI",
    "^000001.SS",
    "^KS11",
    "^TWII",
    "^SET",
    "^KLSE",
    "^PSEI",
    "^JKSE",
    "^BVSP",
]


def populate_indices_sync(historical_years: int = 1):
    """Populate market index assets with historical data."""
    data_provider, _ = DataProvider.objects.get_or_create(
        name="yahoo_finance",
        defaults={"display_name": "Yahoo Finance", "priority": 10, "is_active": True},
    )

    index_types = {
        "Sector Index": "Sector Index",
        "Market Index": "Market Index",
        "Bond Index": "Bond Index",
    }

    # Get market index type
    index_type = AssetType.objects.get(name="Market Index")
    asset_class = AssetClass.objects.get(name="Index")

    total = len(MARKET_INDICES)

    for i, symbol in enumerate(MARKET_INDICES):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            # Determine index type based on symbol
            if "^VIX" in symbol or "TNX" in symbol:
                index_type_name = index_types["Bond Index"]
            elif any(x in symbol for x in ["^XLF", "^XLE", "^XLK", "^XLV", "^XLI"]):
                index_type_name = index_types["Sector Index"]
            else:
                index_type_name = index_types["Market Index"]

            asset, created = Asset.objects.update_or_create(
                ticker=symbol,
                defaults={
                    "name": info.get("longName", info.get("shortName", symbol)),
                    "asset_type": index_type,
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
                    "volume_24h": Decimal(str(info.get("volume", 0)))
                    if info.get("volume")
                    else None,
                    "index_type": index_type_name,
                    "metadata": {
                        "description": info.get("longName"),
                        "exchange": info.get("exchange"),
                    },
                },
            )

            # Fetch historical prices
            period = f"{historical_years}y"
            hist = ticker.history(period=period, auto_adjust=True)

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
                                open=Decimal(str(row["Open"])) if row["Open"] else None,
                                high=Decimal(str(row["High"])) if row["High"] else None,
                                low=Decimal(str(row["Low"])) if row["Low"] else None,
                                close=Decimal(str(row["Close"]))
                                if row["Close"]
                                else None,
                                volume=row["Volume"] if row["Volume"] else None,
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
                    "volume_24h": Decimal(str(info.get("volume", 0)))
                    if info.get("volume")
                    else None,
                    "provider": data_provider,
                },
            )

            print(
                f"[{i + 1}/{total}] {symbol}: {info.get('longName', symbol)} - {len(hist)} prices"
            )

        except Exception as e:
            print(f"[{i + 1}/{total}] ERROR {symbol}: {e}")
            continue


if __name__ == "__main__":
    import logging
    import pandas as pd

    logging.basicConfig(level=logging.INFO)

    historical_years = 1
    if len(sys.argv) > 1:
        historical_years = int(sys.argv[1])
        print(f"Fetching {historical_years} year(s) of historical data")

    populate_indices_sync(historical_years=historical_years)
    print("Index population complete!")
