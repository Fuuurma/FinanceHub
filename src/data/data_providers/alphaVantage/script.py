# data/jobs/alpha_vantage_jobs.py
"""Alpha Vantage data fetching jobs"""
import asyncio
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from assets.models.asset import Asset, AssetType
from assets.models.price_history import PriceHistory
from data.data_fetcher.base import BaseDataJob
from data.data_providers.alphaVantage.base import AlphaVantageFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class AlphaVantageJobs(BaseDataJob):
    """Alpha Vantage data fetching jobs"""

    provider_code = "alpha_vantage"

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

    # =====================================
    # INITIAL DATA JOBS (Run Once)
    # =====================================

    async def initial_complete_setup(self, symbols: List[str]):
        """
        Complete initial setup for assets
        Fetches: General data + Full historical data
        Run this ONCE when adding new assets
        """
        self.log_job_start("Initial Complete Setup")

        async with AlphaVantageFetcher(self.api_key) as fetcher:
            for symbol in symbols:
                try:
                    self.stats["total"] += 1

                    # 1. Fetch and save general company data
                    logger.info(f"Fetching company overview for {symbol}")
                    overview = await fetcher.get_company_overview(symbol)

                    if not overview or "Symbol" not in overview:
                        logger.warning(f"No data found for {symbol}")
                        self.stats["skipped"] += 1
                        continue

                    # Create/update asset
                    asset = await self._save_company_overview(symbol, overview)

                    # 2. Fetch full historical data (20 years)
                    logger.info(f"Fetching historical data for {symbol}")
                    await self._fetch_full_historical(fetcher, asset)

                    # 3. Fetch fundamental data
                    logger.info(f"Fetching fundamental data for {symbol}")
                    await self._fetch_fundamental_data(fetcher, asset)

                    self.stats["success"] += 1
                    logger.info(f"✓ Completed initial setup for {symbol}")

                except Exception as e:
                    self.stats["errors"] += 1
                    logger.error(f"Error in initial setup for {symbol}: {str(e)}")

        self.log_job_end("Initial Complete Setup")

    async def initial_historical_only(self, limit: Optional[int] = None):
        """
        Fetch ONLY historical data for assets that don't have it
        Run this to backfill historical data
        """
        self.log_job_start("Initial Historical Backfill")

        assets = self.get_supported_assets(limit)

        async with AlphaVantageFetcher(self.api_key) as fetcher:
            for asset in assets:
                try:
                    self.stats["total"] += 1

                    # Check if we already have historical data
                    if not self.should_fetch_historical(asset):
                        logger.info(
                            f"Skipping {asset.ticker} - already has historical data"
                        )
                        self.stats["skipped"] += 1
                        continue

                    logger.info(f"Fetching historical data for {asset.ticker}")
                    await self._fetch_full_historical(fetcher, asset)

                    self.stats["success"] += 1

                except Exception as e:
                    self.stats["errors"] += 1
                    logger.error(
                        f"Error fetching historical for {asset.ticker}: {str(e)}"
                    )

        self.log_job_end("Initial Historical Backfill")

    # =====================================
    # SCHEDULED JOBS (Run Regularly)
    # =====================================

    async def daily_price_update(self, limit: Optional[int] = None):
        """
        Update daily prices for all assets
        Run: DAILY after market close (6 PM EST)
        """
        self.log_job_start("Daily Price Update")

        assets = self.get_supported_assets(limit)
        today = date.today()

        async with AlphaVantageFetcher(self.api_key) as fetcher:
            for asset in assets:
                try:
                    self.stats["total"] += 1

                    # Check if we already have today's price
                    if PriceHistory.objects.filter(asset=asset, date=today).exists():
                        logger.debug(f"Already have today's price for {asset.ticker}")
                        self.stats["skipped"] += 1
                        continue

                    # Get latest price
                    quote = await fetcher.get_quote(asset.ticker)

                    if "Global Quote" not in quote:
                        self.stats["skipped"] += 1
                        continue

                    data = quote["Global Quote"]

                    # Save today's price
                    PriceHistory.objects.create(
                        asset=asset,
                        date=today,
                        source=self.provider,
                        open_price=Decimal(data.get("02. open", 0)),
                        high_price=Decimal(data.get("03. high", 0)),
                        low_price=Decimal(data.get("04. low", 0)),
                        close_price=Decimal(data.get("05. price", 0)),
                        volume=Decimal(data.get("06. volume", 0)),
                    )

                    # Update asset last_price_update
                    asset.last_price_update = timezone.now()
                    asset.save(update_fields=["last_price_update"])

                    self.stats["success"] += 1
                    logger.info(
                        f"✓ Updated price for {asset.ticker}: ${data.get('05. price', 0)}"
                    )

                except Exception as e:
                    self.stats["errors"] += 1
                    logger.error(f"Error updating price for {asset.ticker}: {str(e)}")

        self.log_job_end("Daily Price Update")

    async def weekly_general_data_update(self, limit: Optional[int] = None):
        """
        Update general company data (overview, metrics)
        Run: WEEKLY on Sunday
        """
        self.log_job_start("Weekly General Data Update")

        assets = self.get_supported_assets(limit)

        async with AlphaVantageFetcher(self.api_key) as fetcher:
            for asset in assets:
                try:
                    self.stats["total"] += 1

                    # Check if needs update
                    if not self.should_update_general_data(asset):
                        logger.debug(f"Skipping {asset.ticker} - recently updated")
                        self.stats["skipped"] += 1
                        continue

                    # Fetch and update company overview
                    overview = await fetcher.get_company_overview(asset.ticker)

                    if overview and "Symbol" in overview:
                        await self._update_company_data(asset, overview)
                        self.stats["success"] += 1
                    else:
                        self.stats["skipped"] += 1

                except Exception as e:
                    self.stats["errors"] += 1
                    logger.error(
                        f"Error updating general data for {asset.ticker}: {str(e)}"
                    )

        self.log_job_end("Weekly General Data Update")

    async def quarterly_fundamental_update(self, limit: Optional[int] = None):
        """
        Update fundamental data (earnings, financials)
        Run: QUARTERLY (after earnings season)
        """
        self.log_job_start("Quarterly Fundamental Update")

        assets = self.get_supported_assets(limit)

        async with AlphaVantageFetcher(self.api_key) as fetcher:
            for asset in assets:
                try:
                    self.stats["total"] += 1

                    # Fetch fundamental data
                    await self._fetch_fundamental_data(fetcher, asset)

                    self.stats["success"] += 1
                    logger.info(f"✓ Updated fundamentals for {asset.ticker}")

                except Exception as e:
                    self.stats["errors"] += 1
                    logger.error(
                        f"Error updating fundamentals for {asset.ticker}: {str(e)}"
                    )

        self.log_job_end("Quarterly Fundamental Update")

    # =====================================
    # HELPER METHODS
    # =====================================

    @transaction.atomic
    async def _save_company_overview(self, symbol: str, overview: Dict) -> Asset:
        """Save/update company overview data"""

        # Determine asset type
        asset_type_code = "stock"  # Default
        if "ETF" in overview.get("AssetType", ""):
            asset_type_code = "etf"

        asset_type = AssetType.objects.get(code=asset_type_code)

        # Create or update asset
        asset, created = Asset.objects.update_or_create(
            ticker=symbol,
            exchange=overview.get("Exchange", "NYSE"),
            defaults={
                "name": overview.get("Name", symbol),
                "asset_type": asset_type,
                "primary_source": self.provider,
                "currency": overview.get("Currency", "USD"),
                "country": overview.get("Country", "US"),
                "sector": overview.get("Sector", ""),
                "industry": overview.get("Industry", ""),
                "description": overview.get("Description", ""),
                "is_active": True,
                "metadata": {
                    "market_cap": overview.get("MarketCapitalization"),
                    "pe_ratio": overview.get("PERatio"),
                    "dividend_yield": overview.get("DividendYield"),
                    "eps": overview.get("EPS"),
                    "52_week_high": overview.get("52WeekHigh"),
                    "52_week_low": overview.get("52WeekLow"),
                    "beta": overview.get("Beta"),
                    "last_general_update": timezone.now().isoformat(),
                },
            },
        )

        logger.info(f"{'Created' if created else 'Updated'} asset: {symbol}")
        return asset

    async def _update_company_data(self, asset: Asset, overview: Dict):
        """Update existing asset with new data"""

        asset.name = overview.get("Name", asset.name)
        asset.sector = overview.get("Sector", asset.sector)
        asset.industry = overview.get("Industry", asset.industry)
        asset.description = overview.get("Description", asset.description)

        # Update metadata
        asset.metadata.update(
            {
                "market_cap": overview.get("MarketCapitalization"),
                "pe_ratio": overview.get("PERatio"),
                "dividend_yield": overview.get("DividendYield"),
                "eps": overview.get("EPS"),
                "52_week_high": overview.get("52WeekHigh"),
                "52_week_low": overview.get("52WeekLow"),
                "beta": overview.get("Beta"),
                "last_general_update": timezone.now().isoformat(),
            }
        )

        asset.save()
        logger.info(f"Updated company data for {asset.ticker}")

    async def _fetch_full_historical(self, fetcher: AlphaVantageFetcher, asset: Asset):
        """Fetch full historical data (20 years)"""

        # Get daily adjusted data (includes splits & dividends)
        data = await fetcher.get_daily_adjusted(asset.ticker, outputsize="full")

        if "Time Series (Daily)" not in data:
            logger.warning(f"No historical data for {asset.ticker}")
            return

        time_series = data["Time Series (Daily)"]

        # Batch create prices
        prices_to_create = []

        for date_str, price_data in time_series.items():
            price_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Check if we already have this date
            if PriceHistory.objects.filter(asset=asset, date=price_date).exists():
                continue

            prices_to_create.append(
                PriceHistory(
                    asset=asset,
                    date=price_date,
                    source=self.provider,
                    open_price=Decimal(price_data["1. open"]),
                    high_price=Decimal(price_data["2. high"]),
                    low_price=Decimal(price_data["3. low"]),
                    close_price=Decimal(price_data["4. close"]),
                    volume=Decimal(price_data["6. volume"]),
                    adjusted_close=Decimal(price_data["5. adjusted close"]),
                )
            )

        # Bulk create
        if prices_to_create:
            PriceHistory.objects.bulk_create(prices_to_create, batch_size=1000)
            logger.info(
                f"Created {len(prices_to_create)} historical prices for {asset.ticker}"
            )

        # Update asset
        asset.last_price_update = timezone.now()
        asset.save(update_fields=["last_price_update"])

    async def _fetch_fundamental_data(self, fetcher: AlphaVantageFetcher, asset: Asset):
        """Fetch and save fundamental data"""

        try:
            # Fetch earnings
            earnings = await fetcher.get_earnings(asset.ticker)

            # Fetch income statement
            income_stmt = await fetcher.get_income_statement(asset.ticker)

            # Fetch balance sheet
            balance_sheet = await fetcher.get_balance_sheet(asset.ticker)

            # Fetch cash flow
            cash_flow = await fetcher.get_cash_flow(asset.ticker)

            # Store in metadata
            asset.metadata.update(
                {
                    "earnings": earnings,
                    "income_statement": income_stmt,
                    "balance_sheet": balance_sheet,
                    "cash_flow": cash_flow,
                    "last_fundamental_update": timezone.now().isoformat(),
                }
            )

            asset.save(update_fields=["metadata"])
            logger.info(f"Updated fundamental data for {asset.ticker}")

        except Exception as e:
            logger.error(f"Error fetching fundamentals for {asset.ticker}: {str(e)}")
