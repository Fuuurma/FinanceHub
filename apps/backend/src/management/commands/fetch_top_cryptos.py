"""
Management command to fetch top 100 cryptocurrencies from CoinGecko and insert into database.
"""

import asyncio
import aiohttp
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


class Command(BaseCommand):
    help = "Fetch top 100 cryptocurrencies from CoinGecko and insert into database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Number of coins to fetch (default: 100)",
        )
        parser.add_argument(
            "--vs-currency",
            type=str,
            default="usd",
            help="Currency for prices (default: usd)",
        )

    async def fetch_top_coins(self, session, limit, vs_currency):
        """Fetch top coins from CoinGecko."""
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": min(limit, 250),
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h,7d,30d",
        }

        headers = {"Accept": "application/json", "User-Agent": "FinanceHub/1.0"}

        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 429:
                self.stdout.write(self.style.WARNING("Rate limited, waiting 60s..."))
                await asyncio.sleep(60)
                return await self.fetch_top_coins(session, limit, vs_currency)

            response.raise_for_status()
            return await response.json()

    def handle(self, *args, **options):
        limit = options["limit"]
        vs_currency = options["vs_currency"]

        self.stdout.write(f"Fetching top {limit} cryptocurrencies from CoinGecko...")

        async def main():
            async with aiohttp.ClientSession() as session:
                coins = await self.fetch_top_coins(session, limit, vs_currency)
                await self.insert_coins(coins)

        asyncio.run(main())

        self.stdout.write(self.style.SUCCESS("Done!"))

    async def insert_coins(self, coins):
        """Insert fetched coins into the database."""
        from assets.models.asset import Asset
        from assets.models.asset_type import AssetType
        from assets.models.asset_class import AssetClass
        from assets.models.exchange import Exchange

        # Get or create Crypto asset class
        crypto_class, _ = AssetClass.objects.get_or_create(
            name="Crypto",
            defaults={
                "description": "Cryptocurrencies and digital assets",
                "risk_level": 8,
            },
        )
        self.stdout.write(f"AssetClass: {crypto_class.name}")

        # Get or create Coin asset type
        coin_type, _ = AssetType.objects.get_or_create(
            name="Cryptocurrency",
            asset_class=crypto_class,
            defaults={"symbol_pattern": "^[a-z]+$"},
        )
        self.stdout.write(f"AssetType: {coin_type.name}")

        # Get major exchanges
        binance, _ = Exchange.objects.get_or_create(
            name="Binance", defaults={"code": "binance", "country": "KY"}
        )
        coinbase, _ = Exchange.objects.get_or_create(
            name="Coinbase", defaults={"code": "coinbase", "country": "US"}
        )

        created = 0
        updated = 0
        errors = 0

        for coin in coins:
            try:
                with transaction.atomic():
                    # Extract data
                    coin_id = coin.get("id")
                    symbol = coin.get("symbol", "").upper()
                    name = coin.get("name")

                    # Skip if missing essential data
                    if not coin_id or not symbol or not name:
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
                            "twitter": coin.get("links", {}).get(
                                "twitter_screen_name", ""
                            ),
                            "telegram": coin.get("links", {}).get("telegram", ""),
                            "github": coin.get("links", {}).get("github", []),
                        },
                        "image": coin.get("image"),
                        "last_updated": timezone.now().isoformat(),
                    }

                    # Create or update asset
                    asset, was_created = Asset.objects.update_or_create(
                        ticker=symbol,
                        defaults={
                            "name": name,
                            "asset_type": coin_type,
                            "asset_class": crypto_class,
                            "status": Asset.Status.ACTIVE,
                            "currency": "USD",
                            "last_price": Decimal(
                                str(coin.get("current_price", 0) or 0)
                            ),
                            "last_price_updated_at": timezone.now(),
                            "market_cap": Decimal(str(coin.get("market_cap", 0) or 0)),
                            "volume_24h": Decimal(
                                str(coin.get("total_volume", 0) or 0)
                            ),
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

                    # Add exchanges
                    if "binance" in str(coin.get("tickers", [])).lower():
                        asset.exchanges.add(binance)
                    if (
                        "gdax" in str(coin.get("tickers", [])).lower()
                        or "coinbase" in str(coin.get("tickers", [])).lower()
                    ):
                        asset.exchanges.add(coinbase)

                    if was_created:
                        created += 1
                    else:
                        updated += 1

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error inserting {coin.get('symbol', 'unknown')}: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"\nResults:"))
        self.stdout.write(f"  Created: {created}")
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Errors: {errors}")
        self.stdout.write(f"  Total: {len(coins)}")


if __name__ == "__main__":
    import django
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage.py", "fetch_top_cryptos"])
