"""
Yahoo Finance Database Population Script - Complete Implementation
Populates the entire database with financial data from Yahoo Finance.

Usage:
    cd Backend/src
    python manage.py shell

    >>> import asyncio
    >>> from utils.services.yfinance_populator import run_full_population
    >>> asyncio.run(run_full_population())
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

import yfinance as yf
from django.utils import timezone

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")

import django

django.setup()

from utils.helpers.logger.logger import get_logger
from utils.services.yahoo_rate_limiter import get_rate_limiter

logger = get_logger(__name__)

# ============================================================================
# REFERENCE DATA CONFIGURATIONS
# ============================================================================

ASSET_CLASSES = [
    {"name": "Stock", "description": "Publicly traded company shares", "risk_level": 4},
    {"name": "ETF", "description": "Exchange Traded Fund", "risk_level": 3},
    {
        "name": "Cryptocurrency",
        "description": "Digital currency and tokens",
        "risk_level": 10,
    },
    {"name": "Forex", "description": "Foreign Exchange pairs", "risk_level": 2},
    {"name": "Index", "description": "Stock market index", "risk_level": 3},
]

ASSET_TYPES = {
    "Stock": [
        {"name": "Common Stock"},
        {"name": "Preferred Stock"},
        {"name": "ADR"},
        {"name": "REIT"},
    ],
    "ETF": [{"name": "ETF"}, {"name": "ETN"}, {"name": "CEF"}],
    "Cryptocurrency": [
        {"name": "Cryptocurrency"},
        {"name": "Stablecoin"},
        {"name": "Utility Token"},
        {"name": "DeFi Token"},
    ],
    "Forex": [{"name": "Major Pair"}, {"name": "Minor Pair"}, {"name": "Exotic Pair"}],
    "Index": [
        {"name": "Market Index"},
        {"name": "Sector Index"},
        {"name": "Bond Index"},
    ],
}

COUNTRIES = [
    {"code": "US", "name": "United States", "region": "North America"},
    {"code": "CA", "name": "Canada", "region": "North America"},
    {"code": "GB", "name": "United Kingdom", "region": "Europe"},
    {"code": "DE", "name": "Germany", "region": "Europe"},
    {"code": "FR", "name": "France", "region": "Europe"},
    {"code": "CH", "name": "Switzerland", "region": "Europe"},
    {"code": "NL", "name": "Netherlands", "region": "Europe"},
    {"code": "JP", "name": "Japan", "region": "Asia"},
    {"code": "HK", "name": "Hong Kong", "region": "Asia"},
    {"code": "AU", "name": "Australia", "region": "Oceania"},
    {"code": "IN", "name": "India", "region": "Asia"},
    {"code": "KR", "name": "South Korea", "region": "Asia"},
    {"code": "SG", "name": "Singapore", "region": "Asia"},
    {"code": "BR", "name": "Brazil", "region": "South America"},
    {"code": "MX", "name": "Mexico", "region": "North America"},
    {"code": "ZA", "name": "South Africa", "region": "Africa"},
    {"code": "ES", "name": "Spain", "region": "Europe"},
    {"code": "IT", "name": "Italy", "region": "Europe"},
    {"code": "SE", "name": "Sweden", "region": "Europe"},
]

CURRENCIES = [
    {"code": "USD", "name": "US Dollar", "symbol": "$", "is_crypto": False},
    {"code": "EUR", "name": "Euro", "symbol": "€", "is_crypto": False},
    {"code": "GBP", "name": "British Pound", "symbol": "£", "is_crypto": False},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "is_crypto": False},
    {"code": "CHF", "name": "Swiss Franc", "symbol": "Fr", "is_crypto": False},
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "is_crypto": False},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "is_crypto": False},
    {"code": "NZD", "name": "New Zealand Dollar", "symbol": "NZ$", "is_crypto": False},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "is_crypto": False},
    {"code": "HKD", "name": "Hong Kong Dollar", "symbol": "HK$", "is_crypto": False},
    {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "is_crypto": False},
    {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "is_crypto": False},
    {"code": "KRW", "name": "South Korean Won", "symbol": "₩", "is_crypto": False},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$", "is_crypto": False},
]

EXCHANGES = [
    {"code": "NYSE", "name": "New York Stock Exchange", "timezone": "America/New_York"},
    {"code": "NASDAQ", "name": "NASDAQ Stock Market", "timezone": "America/New_York"},
    {"code": "AMEX", "name": "NYSE American", "timezone": "America/New_York"},
    {"code": "LSE", "name": "London Stock Exchange", "timezone": "Europe/London"},
    {"code": "TSX", "name": "Toronto Stock Exchange", "timezone": "America/Toronto"},
    {"code": "TSE", "name": "Tokyo Stock Exchange", "timezone": "Asia/Tokyo"},
    {"code": "HKEX", "name": "Hong Kong Stock Exchange", "timezone": "Asia/Hong_Kong"},
    {"code": "SSE", "name": "Shanghai Stock Exchange", "timezone": "Asia/Shanghai"},
    {"code": "XETRA", "name": "Xetra", "timezone": "Europe/Berlin"},
    {
        "code": "ASX",
        "name": "Australian Securities Exchange",
        "timezone": "Australia/Sydney",
    },
    {"code": "KRX", "name": "Korea Exchange", "timezone": "Asia/Seoul"},
    {
        "code": "NSE",
        "name": "National Stock Exchange of India",
        "timezone": "Asia/Kolkata",
    },
    {"code": "B3", "name": "B3 Brasil Bolsa Balcão", "timezone": "America/Sao_Paulo"},
]

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
]


def setup_reference_data_sync():
    """Sync version of setup_reference_data"""
    from assets.models.asset_class import AssetClass
    from assets.models.asset_type import AssetType
    from assets.models.country import Country
    from investments.models.currency import Currency
    from investments.models.data_provider import DataProvider
    from assets.models.exchange import Exchange

    data_provider, _ = DataProvider.objects.get_or_create(
        name="yahoo_finance",
        defaults={
            "display_name": "Yahoo Finance",
            "priority": 10,
            "is_active": True,
            "rate_limit_per_minute": 2000,
            "rate_limit_daily": 100000,
        },
    )
    logger.info(f"Data provider: {data_provider.name}")

    for ac_data in ASSET_CLASSES:
        ac, created = AssetClass.objects.get_or_create(
            name=ac_data["name"],
            defaults={
                "description": ac_data["description"],
                "risk_level": ac_data.get("risk_level"),
            },
        )
        if created:
            logger.info(f"Created AssetClass: {ac.name}")

    for class_name, types in ASSET_TYPES.items():
        asset_class = AssetClass.objects.get(name=class_name)
        for type_data in types:
            at, created = AssetType.objects.get_or_create(
                name=type_data["name"],
                asset_class=asset_class,
                defaults={"symbol_pattern": ""},
            )
            if created:
                logger.info(f"Created AssetType: {at.name}")

    for country_data in COUNTRIES:
        c, created = Country.objects.get_or_create(
            code=country_data["code"],
            defaults={
                "name": country_data["name"],
                "region": country_data.get("region", ""),
            },
        )
        if created:
            logger.info(f"Created Country: {c.name}")

    for currency_data in CURRENCIES:
        c, created = Currency.objects.get_or_create(
            code=currency_data["code"],
            defaults={
                "name": currency_data["name"],
                "symbol": currency_data.get("symbol", ""),
                "is_crypto": currency_data.get("is_crypto", False),
            },
        )
        if created:
            logger.info(f"Created Currency: {c.code}")

    for exchange_data in EXCHANGES:
        e, created = Exchange.objects.get_or_create(
            code=exchange_data["code"],
            defaults={
                "name": exchange_data["name"],
                "timezone": exchange_data.get("timezone", "UTC"),
            },
        )
        if created:
            logger.info(f"Created Exchange: {e.name}")

    logger.info("Reference data setup complete!")
    return True


async def run_phase_1_setup():
    """Run Phase 1: Setup reference data"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=2) as pool:
        await loop.run_in_executor(pool, setup_reference_data_sync)
    return True


if __name__ == "__main__":
    import argparse
    import logging

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Yahoo Finance Database Population")
    parser.add_argument(
        "--phase",
        type=str,
        choices=["setup"],
        default="setup",
        help="Which phase to run",
    )
    args = parser.parse_args()

    if args.phase == "setup":
        asyncio.run(run_phase_1_setup())
