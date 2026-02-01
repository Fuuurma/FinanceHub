"""
ETF Population Script
Populates ETF assets with 1-year historical data from Yahoo Finance (free tier).
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import yfinance as yf
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/apps/backend/src")

import django

django.setup()

from utils.helpers.logger.logger import get_logger
from utils.services.yahoo_rate_limiter import get_rate_limiter

from assets.models.asset import Asset
from assets.models.asset_class import AssetClass
from assets.models.asset_type import AssetType
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.asset_metrics import AssetMetrics
from assets.models.sector import Sector
from assets.models.industry import Industry
from investments.models.data_provider import DataProvider

logger = get_logger(__name__)

# Popular ETFs (50 major ETFs)
POPULAR_ETFS = [
    # Broad Market
    "SPY",
    "QQQ",
    "IWM",
    "VTI",
    "VOO",
    "VTV",
    "VUG",
    "VYM",
    "VWO",
    "EFA",
    "EEM",
    "VEA",
    "VXUS",
    "BND",
    "AGG",
    "TLT",
    "GLD",
    "SLV",
    "XLF",
    "XLK",
    "XLE",
    "XLV",
    "XLI",
    "XLU",
    "XLRE",
    "XLB",
    "XLY",
    "XLP",
    "XBI",
    "IJH",
    "IJR",
    "DIA",
    "IWM",
    "MDY",
    "OIH",
    "KBE",
    "KRE",
    "XRT",
    "SMH",
    "SOXX",
    "IBB",
    "GDX",
    "EEMV",
    "VSS",
    "VGK",
    "VNQ",
    "SCHD",
    "DGRO",
    "QUAL",
    "MTUM",
]


def populate_etfs_sync(historical_years: int = 1):
    """Populate ETF assets with historical data."""
    rate_limiter = get_rate_limiter()

    data_provider, _ = DataProvider.objects.get_or_create(
        name="yahoo_finance",
        defaults={
            "display_name": "Yahoo Finance",
            "priority": 10,
            "is_active": True,
        },
    )

    etf_type = AssetType.objects.get(name="ETF")
    asset_class = AssetClass.objects.get(name="ETF")

    total = len(POPULAR_ETFS)

    for i, symbol in enumerate(POPULAR_ETFS):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            # Look up sector and industry from info
            sector_name = info.get("sector")
            industry_name = info.get("industry")

            sector_fk = None
            if sector_name:
                sector_fk = Sector.objects.filter(
                    Q(name__iexact=sector_name) | Q(code__iexact=sector_name)
                ).first()

            industry_fk = None
            if industry_name:
                industry_fk = Industry.objects.filter(
                    Q(name__iexact=industry_name) | Q(code__iexact=industry_name)
                ).first()
                if not industry_fk and sector_fk:
                    industry_fk = Industry.objects.filter(
                        sector=sector_fk,
                        Q(name__iexact=industry_name) | Q(code__iexact=industry_name)
                    ).first()

            asset, created = Asset.objects.update_or_create(
                ticker=symbol,
                defaults={
                    "name": info.get("longName", info.get("shortName", symbol)),
                    "asset_type": etf_type,
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
                    "expense_ratio": Decimal(
                        str(info.get("annualReportExpenseRatio", 0))
                    )
                    * 100
                    if info.get("annualReportExpenseRatio")
                    else None,
                    "aum": Decimal(str(info.get("totalAssets", 0)))
                    if info.get("totalAssets")
                    else None,
                    "sector_fk": sector_fk,
                    "industry_fk": industry_fk,
                    "sector": sector_name,  # Keep for backward compatibility
                    "industry": industry_name,
                    "metadata": {
                        "holdings_count": info.get("holdingsCount"),
                        "yield": info.get("yield"),
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

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error processing {symbol}: {e}")
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

    populate_etfs_sync(historical_years=historical_years)
    print("ETF population complete!")
