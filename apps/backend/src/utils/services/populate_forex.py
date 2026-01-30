"""
Forex Population Script
Populates forex pair assets with 1-year historical data from Yahoo Finance.
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

# Major Forex Pairs (30 pairs)
FOREX_PAIRS = [
    # Major Pairs
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X",
    "USDCHF=X",
    "USDCAD=X",
    "AUDUSD=X",
    "NZDUSD=X",
    # Minor/Cross Pairs
    "EURGBP=X",
    "EURJPY=X",
    "EURCHF=X",
    "EURCAD=X",
    "EURAUD=X",
    "EURUSD=X",
    "GBPJPY=X",
    "GBPCHF=X",
    # Commodity Pairs
    "USDCAD=X",
    "AUDUSD=X",
    "NZDUSD=X",
    # Scandinavian
    "USDSEK=X",
    "USDNOK=X",
    # Asian
    "USDHKD=X",
    "USDSGD=X",
    "USDKRW=X",
    "USDMYR=X",
    "USDIDR=X",
    "USDPHP=X",
    "USDCNY=X",
    # Emerging Markets
    "USDZAR=X",
    "USDRUB=X",
    "USDMXN=X",
    "USDBRL=X",
    "USDCLP=X",
    "USDCOP=X",
    "USDPEN=X",
    "USDPYG=X",
    "USDTRY=X",
    "USDINR=X",
]


def populate_forex_sync(historical_years: int = 1):
    """Populate forex pair assets with historical data."""
    data_provider, _ = DataProvider.objects.get_or_create(
        name="yahoo_finance",
        defaults={"display_name": "Yahoo Finance", "priority": 10, "is_active": True},
    )

    # Get Major Pair type (or create if doesn't exist)
    major_pair_type, _ = AssetType.objects.get_or_create(
        name="Major Pair", defaults={"display_name": "Major Forex Pair"}
    )
    asset_class = AssetClass.objects.get(name="Forex")

    total = len(FOREX_PAIRS)

    for i, symbol in enumerate(FOREX_PAIRS):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            # Parse base and quote currencies
            if "USD" in symbol:
                if symbol.startswith("USD"):
                    base_curr = "USD"
                    quote_curr = symbol.replace("USD=", "").replace("X", "")
                else:
                    base_curr = symbol.replace("=X", "").replace("USD", "")
                    quote_curr = "USD"
            else:
                # Parse EURGBP=X format
                pair = symbol.replace("=X", "")
                base_curr = pair[:3]
                quote_curr = pair[3:6] if len(pair) > 3 else pair[3:]

            # Clean up currency codes (remove any special characters)
            base_curr = base_curr.replace("^", "")[:3]
            quote_curr = quote_curr.replace("^", "")[:3]

            # Determine pip size
            pip_size = Decimal("0.0001") if "JPY" not in symbol else Decimal("0.01")

            asset, created = Asset.objects.update_or_create(
                ticker=symbol,
                defaults={
                    "name": f"{base_curr}/{quote_curr}",
                    "asset_type": major_pair_type,
                    "asset_class": asset_class,
                    "currency": quote_curr[:3],  # Ensure max 3 chars
                    "status": Asset.Status.ACTIVE,
                    "last_price": Decimal(str(current_price))
                    if current_price
                    else None,
                    "last_price_updated_at": timezone.now(),
                    "volume_24h": Decimal(str(info.get("volume", 0)))
                    if info.get("volume")
                    else None,
                    "base_currency": base_curr,
                    "quote_currency": quote_curr,
                    "pip_size": pip_size,
                    "metadata": {
                        "pair_name": f"{base_curr}/{quote_curr}",
                        "description": f"{base_curr} to {quote_curr} exchange rate",
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
                    "market_cap": None,  # Forex pairs don't have market cap
                    "volume_24h": Decimal(str(info.get("volume", 0)))
                    if info.get("volume")
                    else None,
                    "provider": data_provider,
                },
            )

            print(
                f"[{i + 1}/{total}] {symbol}: {base_curr}/{quote_curr} - {len(hist)} prices"
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

    populate_forex_sync(historical_years=historical_years)
    print("Forex population complete!")
