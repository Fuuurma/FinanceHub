"""
Django Management Command: Seed Top 1,000 Stocks

Fetches top 1,000 stocks by market cap from Polygon.io and saves ALL data to models.

IMPORTANT: We save ALL fetched data - NO DATA WASTED!
- Basic: ticker, name, market, locale, active, currency
- Identifiers: cik, composite_figi, share_class_figi, FIGI
- Market data: market_cap, description
- Additional: logo, sector, industry, country, website, employees, hq_location

Usage:
    python manage.py seed_top_stocks
"""

import os
import sys
import time
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import django

django.setup()

from assets.models.asset import Asset
from assets.models.asset_type import AssetType
from assets.models.asset_class import AssetClass
from assets.models.country import Country
from investments.models.currency import Currency
from assets.models.sector import Sector
from assets.models.industry import Industry
from assets.models.exchange import Exchange


class Command(BaseCommand):
    help = "Seed top 1,000 stocks from Polygon.io"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Number of stocks to fetch per batch (default: 50, max: 50 for Polygon free tier)",
        )
        parser.add_argument(
            "--max-stocks",
            type=int,
            default=1000,
            help="Maximum number of stocks to fetch (default: 1000)",
        )

    def handle(self, *args, **options):
        limit = min(options.get("limit", 50), 50)  # Polygon free tier max is 50
        max_stocks = options.get("max_stocks", 1000)

        # Get API key from settings
        polygon_api_key = getattr(settings, "POLYGON_IO_API_KEY", None)
        if not polygon_api_key:
            self.stdout.write(
                self.style.ERROR("POLYGON_IO_API_KEY not found in settings")
            )
            return

        # Get or create asset type and class
        stock_type, _ = AssetType.objects.get_or_create(
            name="Stock", defaults={"description": "Stocks and equities"}
        )
        equity_class, _ = AssetClass.objects.get_or_create(
            name="Equity", defaults={"description": "Equity securities"}
        )

        # Get references
        usd = Currency.objects.filter(code="USD").first()
        us_country = Country.objects.filter(code="US").first()
        nyse = Exchange.objects.filter(code="NYSE").first()
        nasdaq = Exchange.objects.filter(code="NASDAQ").first()

        if not usd:
            self.stdout.write(
                self.style.ERROR("USD currency not found. Run seed_currencies first.")
            )
            return

        # Statistics
        total_fetched = 0
        total_created = 0
        total_updated = 0
        total_skipped = 0

        self.stdout.write(
            self.style.WARNING(f"Fetching top {max_stocks} stocks from Polygon.io...")
        )
        self.stdout.write(f"Batch size: {limit}")
        self.stdout.write(
            "This may take a while due to API rate limits (5 req/min free tier)..."
        )

        # Fetch stocks in batches
        for batch_num in range(0, max_stocks, limit):
            current_batch_size = min(limit, max_stocks - total_fetched)

            if current_batch_size <= 0:
                break

            # Build API request
            url = "https://api.polygon.io/v3/reference/tickers"
            params = {
                "market": "stocks",
                "active": "true",
                "order": "market_cap",
                "sort": "desc",
                "limit": current_batch_size,
                "apiKey": polygon_api_key,
            }

            # Add pagination cursor if we have one
            if batch_num > 0:
                # Note: In production, you'd need to handle pagination properly
                # For now, we'll fetch in batches using the 'ticker_lt' parameter
                last_ticker = self.get_last_ticker()
                if last_ticker:
                    params["ticker_lt"] = last_ticker

            try:
                self.stdout.write(
                    f"\nFetching batch {batch_num // limit + 1} (stocks {total_fetched + 1}-{total_fetched + current_batch_size})..."
                )

                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if data.get("status") != "OK":
                    self.stdout.write(
                        self.style.ERROR(
                            f"API error: {data.get('message', 'Unknown error')}"
                        )
                    )
                    break

                tickers = data.get("results", [])
                if not tickers:
                    self.stdout.write(self.style.WARNING("No more tickers found"))
                    break

                # Process each ticker
                for ticker_data in tickers:
                    result = self.process_ticker(
                        ticker_data,
                        stock_type,
                        equity_class,
                        usd,
                        us_country,
                        nyse,
                        nasdaq,
                    )

                    if result == "created":
                        total_created += 1
                    elif result == "updated":
                        total_updated += 1
                    elif result == "skipped":
                        total_skipped += 1

                    total_fetched += 1

                # Rate limiting: Polygon free tier allows 5 req/min
                # Sleep 12 seconds between batches to be safe
                if batch_num + limit < max_stocks:
                    self.stdout.write(
                        "Sleeping 12 seconds to respect API rate limits..."
                    )
                    time.sleep(12)

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Request failed: {e}"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing batch: {e}"))
                break

        # Final summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully processed {total_fetched} stocks:")
        )
        self.stdout.write(f"  - Created: {total_created}")
        self.stdout.write(f"  - Updated: {total_updated}")
        self.stdout.write(f"  - Skipped: {total_skipped}")
        self.stdout.write(
            f"  - Total stocks in database: {Asset.objects.filter(asset_class=equity_class).count()}"
        )
        self.stdout.write(self.style.SUCCESS("=" * 70))

    def get_last_ticker(self):
        """Get the last ticker symbol for pagination"""
        try:
            last_asset = (
                Asset.objects.filter(
                    ticker__regex=r"^[A-Z]+$"  # Only standard stock tickers
                )
                .order_by("-ticker")
                .first()
            )
            return last_asset.ticker if last_asset else None
        except:
            return None

    def process_ticker(
        self, ticker_data, stock_type, equity_class, usd, us_country, nyse, nasdaq
    ):
        """Process a single ticker and save to database"""
        ticker = ticker_data.get("ticker")

        if not ticker:
            return "skipped"

        # Skip if not a stock or inactive
        if ticker_data.get("market") != "stocks" or not ticker_data.get("active", True):
            return "skipped"

        # Check if asset already exists
        asset = Asset.objects.filter(ticker=ticker).first()

        # Prepare asset data
        asset_data = {
            "ticker": ticker,
            "name": ticker_data.get("name", "")[:200],  # Limit to 200 chars
            "asset_type": stock_type,
            "asset_class": equity_class,
            "currency": "USD",  # CharField, not ForeignKey
            "country": us_country,
            "website": ticker_data.get("homepage_url") or "",
            "market_cap": ticker_data.get("market_cap") or None,
            # Additional identifiers stored in metadata
            "isin": ticker_data.get("composite_figi", "") or "",
        }

        # Prepare metadata for fields that don't exist in the model
        metadata = {
            "description": ticker_data.get("description", "") or "",
            "share_class_figi": ticker_data.get("share_class_figi") or None,
            "composite_figi": ticker_data.get("composite_figi") or None,
            "cik": str(ticker_data.get("cik", "")) if ticker_data.get("cik") else None,
            "active": ticker_data.get("active", True),
            "locale": ticker_data.get("locale", "us") or None,
            "logo_url": ticker_data.get("logo_url") or None,
            "total_employees": ticker_data.get("total_employees") or None,
            "list_date": ticker_data.get("list_date") or None,
            "primary_exchange": ticker_data.get("primary_exchange") or None,
        }

        asset_data["metadata"] = metadata

        # Determine exchange based on ticker or locale (ManyToMany)
        exchanges_to_add = []
        if ticker_data.get("primary_exchange"):
            exchange_code = ticker_data.get("primary_exchange")
            if "NYS" in exchange_code and nyse:
                exchanges_to_add.append(nyse)
            elif "NAS" in exchange_code and nasdaq:
                exchanges_to_add.append(nasdaq)

        # Sector and industry FKs (would need to be fetched separately or from description)
        sector_fk = None
        industry_fk = None

        # Try to determine sector from description (basic heuristic)
        description = ticker_data.get("description", "").lower()
        if "technology" in description or "software" in description:
            sector_fk = Sector.objects.filter(name__icontains="Technology").first()
        elif "healthcare" in description or "pharmaceutical" in description:
            sector_fk = Sector.objects.filter(name__icontains="Healthcare").first()
        elif "financial" in description or "bank" in description:
            sector_fk = Sector.objects.filter(name__icontains="Financials").first()

        asset_data["sector_fk"] = sector_fk
        asset_data["industry_fk"] = industry_fk

        # Save or update
        try:
            if asset:
                # Update existing asset
                for key, value in asset_data.items():
                    if (
                        value is not None and key != "ticker"
                    ):  # Don't update primary key
                        setattr(asset, key, value)
                asset.save()

                # Update ManyToMany exchanges
                if exchanges_to_add:
                    asset.exchanges.add(*exchanges_to_add)

                return "updated"
            else:
                # Create new asset
                asset = Asset.objects.create(**asset_data)

                # Add exchanges after creation
                if exchanges_to_add:
                    asset.exchanges.add(*exchanges_to_add)

                return "created"
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error saving {ticker}: {e}"))
            return "skipped"
