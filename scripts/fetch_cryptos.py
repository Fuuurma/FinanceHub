#!/usr/bin/env python3
"""
Standalone script to fetch top 100 cryptocurrencies from CoinGecko and insert into database.
Run from Backend/src directory.
"""

import asyncio
import aiohttp
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from datetime import datetime

# Setup Django
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_SRC = os.path.join(SCRIPT_DIR, "src")
os.chdir(BACKEND_SRC)
sys.path.insert(0, BACKEND_SRC)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Explicitly load .env file
from dotenv import load_dotenv

dotenv_path = os.path.join(BACKEND_SRC, ".env")
print(f"Loading .env from: {dotenv_path}")
print(f"BACKEND_SRC: {BACKEND_SRC}")
print(f"File exists: {os.path.exists(dotenv_path)}")
load_dotenv(dotenv_path)

# Debug: print DB settings
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(
    f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'NOT SET'}"
)
print(f"DB_HOST: {os.getenv('DB_HOST')}")

import django

django.setup()

from django.db import transaction
from django.utils import timezone


async def fetch_top_coins(session, limit, vs_currency="usd"):
    """Fetch top coins from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": min(limit, 250),
        "page": 1,
        "sparkline": str(False).lower(),
        "price_change_percentage": "24h,7d,30d",
    }

    headers = {"Accept": "application/json", "User-Agent": "FinanceHub/1.0"}

    print(f"Fetching top {limit} coins from CoinGecko...")

    async with session.get(url, params=params, headers=headers) as response:
        if response.status == 429:
            print("Rate limited! Waiting 60s...")
            await asyncio.sleep(60)
            return await fetch_top_coins(session, limit, vs_currency)

        if response.status != 200:
            print(f"Error: HTTP {response.status}")
            return []

        return await response.json()


def insert_coins(coins):
    """Insert fetched coins into the database."""
    from assets.models.asset import Asset
    from assets.models.asset_type import AssetType
    from assets.models.asset_class import AssetClass
    from assets.models.exchange import Exchange

    print(f"\nProcessing {len(coins)} coins...")

    # Get or create Crypto asset class
    crypto_class, _ = AssetClass.objects.get_or_create(
        name="Crypto",
        defaults={
            "description": "Cryptocurrencies and digital assets",
            "risk_level": 8,
        },
    )
    print(f"AssetClass: {crypto_class.name} (id={crypto_class.id})")

    # Get or create Coin asset type
    coin_type, _ = AssetType.objects.get_or_create(
        name="Cryptocurrency",
        asset_class=crypto_class,
        defaults={"symbol_pattern": "^[a-z]+$"},
    )
    print(f"AssetType: {coin_type.name} (id={coin_type.id})")

    # Get major exchanges
    binance, _ = Exchange.objects.get_or_create(
        code="binance",
        defaults={"name": "Binance", "country_id": None},
    )
    coinbase, _ = Exchange.objects.get_or_create(
        code="coinbase",
        defaults={"name": "Coinbase", "country_id": None},
    )

    created = 0
    updated = 0
    skipped = 0
    errors = 0

    for i, coin in enumerate(coins, 1):
        try:
            # Extract data
            coin_id = coin.get("id")
            symbol = coin.get("symbol", "").upper()
            name = coin.get("name")

            # Skip if missing essential data
            if not coin_id or not symbol or not name:
                skipped += 1
                continue

            # Prepare metadata
            metadata = {
                "coingecko_id": coin_id,
                "coingecko_rank": coin.get("coingecko_rank"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "categories": coin.get("categories", []),
                "links": {
                    "homepage": coin.get("links", {}).get("homepage", [""])[0]
                    if coin.get("links")
                    else "",
                    "twitter": coin.get("links", {}).get("twitter_screen_name", ""),
                    "telegram": coin.get("links", {}).get("telegram", ""),
                    "github": coin.get("links", {}).get("github", []),
                },
                "image": coin.get("image"),
                "last_updated": timezone.now().isoformat(),
            }

            with transaction.atomic():
                # Create or update asset
                asset, was_created = Asset.objects.update_or_create(
                    ticker=symbol,
                    defaults={
                        "name": name,
                        "asset_type": coin_type,
                        "asset_class": crypto_class,
                        "status": Asset.Status.ACTIVE,
                        "currency": "USD",
                        "last_price": Decimal(str(coin.get("current_price", 0) or 0)),
                        "last_price_updated_at": timezone.now(),
                        "market_cap": Decimal(str(coin.get("market_cap", 0) or 0)),
                        "volume_24h": Decimal(str(coin.get("total_volume", 0) or 0)),
                        "price_change_24h": Decimal(
                            str(coin.get("price_change_24h", 0) or 0)
                        ),
                        "price_change_24h_pct": Decimal(
                            str(coin.get("price_change_percentage_24h", 0) or 0)
                        ),
                        "ath_price": Decimal(str(coin.get("ath", 0) or 0)),
                        "atl_price": Decimal(str(coin.get("atl", 0) or 0)),
                        "metadata": metadata,
                    },
                )

                # Add exchanges (simplified - add to all)
                asset.exchanges.add(binance)
                asset.exchanges.add(coinbase)

                if was_created:
                    created += 1
                    status = "CREATED"
                else:
                    updated += 1
                    status = "UPDATED"

                if i <= 10 or i % 20 == 0:
                    print(
                        f"  [{i:3d}] {symbol:8s} {name[:30]:30s} ${coin.get('current_price', 0):>12,.2f} - {status}"
                    )

        except Exception as e:
            errors += 1
            symbol = coin.get("symbol", "unknown")
            print(f"  [ERR] {symbol}: {e}")

    print(f"\n{'=' * 60}")
    print(f"Results:")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors:  {errors}")
    print(f"  Total:   {len(coins)}")
    print(f"{'=' * 60}")


async def main():
    """Main entry point."""
    limit = 100
    vs_currency = "usd"

    async with aiohttp.ClientSession() as session:
        coins = await fetch_top_coins(session, limit, vs_currency)

        if not coins:
            print("No coins fetched!")
            return

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=4) as executor:
            await loop.run_in_executor(executor, insert_coins, coins)

        print(f"\nDone at {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())
