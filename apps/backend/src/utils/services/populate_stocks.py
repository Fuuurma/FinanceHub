"""
Yahoo Finance Stock Population Script
Populates the database with stocks, historical prices, and fundamentals.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import logging

import yfinance as yf
from django.utils import timezone
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/apps/backend/src")

import django

django.setup()

from utils.helpers.logger.logger import get_logger
from utils.services.yahoo_rate_limiter import get_rate_limiter

logger = get_logger(__name__)

STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "META",
    "NVDA",
    "TSLA",
    "JPM",
    "JNJ",
    "V",
    "PG",
    "UNH",
    "HD",
    "MA",
    "MRK",
    "ABBV",
    "PEP",
    "KO",
    "COST",
    "BAC",
    "CSCO",
    "ACN",
    "TMO",
    "MCD",
    "WMT",
    "CVX",
    "LLY",
    "ADBE",
    "CRM",
    "TXN",
    "NKE",
    "DIS",
    "VZ",
    "CMCSA",
    "INTC",
    "QCOM",
    "AMD",
    "HON",
    "BMY",
    "PM",
    "ORCL",
    "IBM",
    "GE",
    "CAT",
    "AMGN",
    "UNP",
    "LOW",
    "UPS",
    "BLK",
    "BA",
    "AXP",
    "RTX",
    "USB",
    "SCHW",
    "GS",
    "C",
    "MS",
    "PFE",
    "NFLX",
    "NOW",
    "INTU",
    "ISRG",
    "ZTS",
    "REGN",
    "ADI",
    "LRCX",
    "VRTX",
    "MMC",
    "CB",
    "TJX",
    "MDLZ",
    "DOW",
    "CVS",
    "BAX",
    "SLB",
    "SYK",
    "MDT",
    "MMM",
    "AIG",
    "ETN",
    "KLAC",
    "AMAT",
    "MU",
    "BDX",
    "SNPS",
    "CDNS",
    "MCHP",
    "NXPI",
    "MRNA",
    "SNAP",
    "SQ",
    "SHOP",
    "COIN",
    "PLTR",
    "HOOD",
    "RIVN",
    "LCID",
    "DKNG",
    "PENN",
    "MGM",
    "LVS",
    "WYNN",
    "MAR",
    "O",
    "WELL",
    "DLR",
    "PLD",
    "AMT",
    "EQIX",
    "CCI",
    "PSA",
    "SPG",
    "AVB",
    "EQR",
    "ESS",
    "NLY",
    "AGNC",
    "ED",
    "SO",
    "D",
    "SRE",
    "DUK",
    "AEP",
    "EXC",
    "XEL",
    "WEC",
    "FE",
    "NEE",
    "T",
    "TM",
    "HMC",
    "SONY",
    "SANM",
    "MRVL",
    "STN",
    "TER",
    "MXIM",
    "LVRS",
    "Q",
    "BX",
    "STT",
    "BK",
    "NTRS",
    "AMP",
    "EVR",
    "MSCI",
    "CME",
    "ICE",
    "MCO",
    "BCE",
    "T",
    "TMUS",
    "DISH",
    "LUMN",
    "FYBR",
    "USM",
]


def populate_stocks_sync():
    """Sync version of stock population"""
    from assets.models.asset import Asset
    from assets.models.stocks.asset import StockAsset
    from assets.models.asset_class import AssetClass
    from assets.models.asset_type import AssetType
    from assets.models.historic.prices import AssetPricesHistoric
    from assets.models.asset_metrics import AssetMetrics
    from investments.models.dividend import Dividend
    from assets.models.stocks.corporate_action import CorporateAction
    from assets.models.stocks.recommendation import AssetRecommendation
    from assets.models.common.top_holder import AssetTopHolder
    from investments.models.data_provider import DataProvider
    from investments.models.currency import Currency

    rate_limiter = get_rate_limiter()
    data_provider = DataProvider.objects.get(name="yahoo_finance")
    stock_type = AssetType.objects.get(name="Common Stock")
    asset_class = AssetClass.objects.get(name="Stock")

    total = len(STOCKS)

    for i, symbol in enumerate(STOCKS):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Create Asset
            asset, created = Asset.objects.update_or_create(
                ticker=symbol.replace(".", "-"),
                defaults={
                    "name": info.get("longName", info.get("shortName", symbol)),
                    "asset_type": stock_type,
                    "asset_class": asset_class,
                    "currency": info.get("currency", "USD"),
                    "website": info.get("website", ""),
                    "status": Asset.Status.ACTIVE,
                    "last_price": Decimal(str(info.get("currentPrice", 0)))
                    if info.get("currentPrice")
                    else None,
                    "market_cap": Decimal(str(info.get("marketCap", 0)))
                    if info.get("marketCap")
                    else None,
                    "volume_24h": Decimal(str(info.get("volume", 0)))
                    if info.get("volume")
                    else None,
                    "metadata": {
                        "sector": info.get("sector"),
                        "industry": info.get("industry"),
                    },
                },
            )

            # Create StockAsset - use get to check, then create if needed
            # Note: Due to Django multi-table inheritance constraints, we skip StockAsset creation
            # if the Asset already exists (since we can't attach a child to an existing parent)
            stock_asset = None
            if created:
                # Only try to create StockAsset for new Assets
                try:
                    stock_asset = StockAsset.objects.get(asset_ptr_id=asset.id)
                except StockAsset.DoesNotExist:
                    try:
                        # Create StockAsset with explicit asset_ptr_id
                        stock_asset = StockAsset.objects.create(
                            asset_ptr_id=asset.id,
                            industry=info.get("industry", ""),
                            sector=info.get("sector", ""),
                            pe_ratio=Decimal(str(info.get("trailingPE", 0)))
                            if info.get("trailingPE")
                            else None,
                            dividend_yield=Decimal(str(info.get("dividendYield", 0)))
                            if info.get("dividendYield")
                            else None,
                            eps=Decimal(str(info.get("trailingEps", 0)))
                            if info.get("trailingEps")
                            else None,
                            revenue_ttm=Decimal(str(info.get("totalRevenue", 0)))
                            if info.get("totalRevenue")
                            else None,
                        )
                    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                        # If creation fails (e.g., multi-table inheritance issue), continue without StockAsset
                        logger.warning(
                            f"  Warning: Could not create StockAsset for {symbol}: {e}"
                        )

            # Fetch historical prices
            hist = ticker.history(period="5y", auto_adjust=True)
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
                                open=Decimal(str(row["Open"])),
                                high=Decimal(str(row["High"])),
                                low=Decimal(str(row["Low"])),
                                close=Decimal(str(row["Close"])),
                                volume=row["Volume"]
                                if "Volume" in row and row["Volume"]
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
                    "volume_24h": Decimal(str(info.get("volume", 0)))
                    if info.get("volume")
                    else None,
                    "provider": data_provider,
                },
            )

            # Fetch dividends
            dividends = ticker.dividends
            if not dividends.empty:
                # Get the currency for this asset
                usd_currency = Currency.objects.get(code="USD")
                for date, amount in dividends.items():
                    div_date = date.date() if hasattr(date, "date") else date
                    Dividend.objects.update_or_create(
                        asset=asset,
                        ex_date=div_date,
                        defaults={
                            "pay_date": div_date,
                            "amount_per_share": Decimal(str(amount)),
                            "currency": usd_currency,
                        },
                    )

            # Fetch splits
            splits = ticker.splits
            if not splits.empty:
                for date, ratio in splits.items():
                    split_date = date.date() if hasattr(date, "date") else date
                    CorporateAction.objects.update_or_create(
                        asset=asset,
                        action_type=CorporateAction.ActionType.SPLIT,
                        execution_date=split_date,
                        defaults={
                            "ratio": Decimal(str(ratio)),
                            "description": f"{ratio}-for-1 stock split",
                        },
                    )

            logger.info(
                f"[{i + 1}/{total}] {symbol}: {info.get('longName', symbol)} - {len(hist)} prices"
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"[{i + 1}/{total}] ERROR {symbol}: {e}")
            continue


async def populate_stocks():
    """Run stock population in thread pool"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=2) as pool:
        await loop.run_in_executor(pool, populate_stocks_sync)
    logger.info("Stock population complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(populate_stocks())
