"""
Data Provider Seeder
Seeds all configured data providers into the database with free tier settings.
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/Users/sergi/Desktop/Projects/FinanceHub/Backend/src")

import django

django.setup()

from investments.models.data_provider import DataProvider

# All data providers configured in the system
DATA_PROVIDERS = [
    {
        "name": "yahoo_finance",
        "display_name": "Yahoo Finance",
        "api_key": "",
        "priority": 10,
        "base_url": "https://query1.finance.yahoo.com",
        "rate_limit_per_minute": 100,
        "rate_limit_daily": 2000,
        "is_active": True,
        "config": {
            "free_tier": True,
            "requires_auth": False,
            "supports_stocks": True,
            "supports_etfs": True,
            "supports_indices": True,
            "supports_forex": True,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": False,
        },
    },
    {
        "name": "coingecko",
        "display_name": "CoinGecko",
        "api_key": "",
        "priority": 5,
        "base_url": "https://api.coingecko.com/api/v3",
        "rate_limit_per_minute": 50,
        "rate_limit_daily": 10000,
        "is_active": True,
        "config": {
            "free_tier": True,
            "requires_auth": False,
            "supports_stocks": False,
            "supports_etfs": False,
            "supports_indices": False,
            "supports_forex": False,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": True,
            "rate_limit_window": 60,
        },
    },
    {
        "name": "coinmarketcap",
        "display_name": "CoinMarketCap",
        "api_key": "",
        "priority": 4,
        "base_url": "https://pro-api.coinmarketcap.com/v1",
        "rate_limit_per_minute": 30,
        "rate_limit_daily": 10000,
        "is_active": False,  # Requires API key for most features
        "config": {
            "free_tier": False,
            "requires_auth": True,
            "supports_stocks": False,
            "supports_etfs": False,
            "supports_indices": False,
            "supports_forex": False,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": False,
        },
    },
    {
        "name": "polygon_io",
        "display_name": "Polygon.io",
        "api_key": "",
        "priority": 7,
        "base_url": "https://api.polygon.io",
        "rate_limit_per_minute": 5,
        "rate_limit_daily": 5000,
        "is_active": False,  # Requires API key
        "config": {
            "free_tier": False,
            "requires_auth": True,
            "supports_stocks": True,
            "supports_etfs": True,
            "supports_indices": True,
            "supports_forex": False,
            "supports_crypto": False,
            "historical_data": True,
            "realtime": True,
            "aggregates": True,
        },
    },
    {
        "name": "iex_cloud",
        "display_name": "IEX Cloud",
        "api_key": "",
        "priority": 6,
        "base_url": "https://cloud.iexapis.com/stable",
        "rate_limit_per_minute": 500,
        "rate_limit_daily": 500000,
        "is_active": False,  # Requires API key
        "config": {
            "free_tier": False,
            "requires_auth": True,
            "supports_stocks": True,
            "supports_etfs": True,
            "supports_indices": True,
            "supports_forex": False,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": True,
        },
    },
    {
        "name": "finnhub",
        "display_name": "Finnhub",
        "api_key": "",
        "priority": 8,
        "base_url": "https://finnhub.io/api/v1",
        "rate_limit_per_minute": 60,
        "rate_limit_daily": 10000,
        "is_active": False,  # Requires API key
        "config": {
            "free_tier": False,
            "requires_auth": True,
            "supports_stocks": True,
            "supports_etfs": False,
            "supports_indices": True,
            "supports_forex": False,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": True,
            "technical_indicators": True,
        },
    },
    {
        "name": "newsapi",
        "display_name": "NewsAPI",
        "api_key": "",
        "priority": 9,
        "base_url": "https://newsapi.org/v2",
        "rate_limit_per_minute": 100,
        "rate_limit_daily": 1000,
        "is_active": False,  # Requires API key
        "config": {
            "free_tier": True,
            "requires_auth": True,
            "supports_stocks": False,
            "supports_etfs": False,
            "supports_indices": False,
            "supports_forex": False,
            "supports_crypto": False,
            "historical_data": False,
            "realtime": False,
            "data_type": "news",
        },
    },
    {
        "name": "binance",
        "display_name": "Binance",
        "api_key": "",
        "priority": 3,
        "base_url": "https://api.binance.com",
        "rate_limit_per_minute": 1200,
        "rate_limit_daily": 100000,
        "is_active": False,  # Requires setup
        "config": {
            "free_tier": True,
            "requires_auth": False,
            "supports_stocks": False,
            "supports_etfs": False,
            "supports_indices": False,
            "supports_forex": False,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": True,
            "websocket": True,
        },
    },
    {
        "name": "alpha_vantage",
        "display_name": "Alpha Vantage",
        "api_key": "",
        "priority": 5,
        "base_url": "https://www.alphavantage.co/query",
        "rate_limit_per_minute": 5,
        "rate_limit_daily": 500,
        "is_active": False,  # Requires API key
        "config": {
            "free_tier": True,
            "requires_auth": True,
            "supports_stocks": True,
            "supports_etfs": True,
            "supports_indices": True,
            "supports_forex": True,
            "supports_crypto": True,
            "historical_data": True,
            "realtime": False,
            "technical_indicators": True,
            "forex_data": True,
        },
    },
]


def seed_data_providers():
    """Seed all data providers into the database."""
    print("Seeding data providers...")

    for provider_data in DATA_PROVIDERS:
        provider, created = DataProvider.objects.get_or_create(
            name=provider_data["name"], defaults=provider_data
        )

        if created:
            print(f"  ✓ Created: {provider.display_name}")
        else:
            # Update existing provider
            for key, value in provider_data.items():
                setattr(provider, key, value)
            provider.save()
            print(f"  ↻ Updated: {provider.display_name}")

    print(f"\nTotal data providers: {DataProvider.objects.count()}")

    # Show active providers
    active = DataProvider.objects.filter(is_active=True)
    print(f"Active providers: {active.count()}")
    for p in active:
        print(f"  - {p.display_name} ({p.name})")


if __name__ == "__main__":
    seed_data_providers()
