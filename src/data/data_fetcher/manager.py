#  src/data/data_fetcher/manager.py

"""Job manager to execute all scheduled jobs"""

import asyncio
from typing import Dict, Callable
from django.conf import settings

from data.data_providers.alphaVantage.script import AlphaVantageJobs
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class JobManager:
    """Manages all data fetching jobs"""

    def __init__(self):
        self.alpha_vantage = AlphaVantageJobs(api_key=settings.ALPHA_VANTAGE_API_KEY)

    # =====================================
    # DAILY JOBS
    # =====================================

    async def run_daily_jobs(self):
        """Run all daily jobs - Execute at 6 PM EST after market close"""
        logger.info("=" * 80)
        logger.info("STARTING DAILY JOBS")
        logger.info("=" * 80)

        # Update daily prices for all providers
        await self.alpha_vantage.daily_price_update()

        # Add other providers here
        # await self.yahoo_finance.daily_price_update()
        # await self.coingecko.daily_price_update()

        logger.info("=" * 80)
        logger.info("DAILY JOBS COMPLETED")
        logger.info("=" * 80)

    # =====================================
    # WEEKLY JOBS
    # =====================================

    async def run_weekly_jobs(self):
        """Run all weekly jobs - Execute on Sunday"""
        logger.info("=" * 80)
        logger.info("STARTING WEEKLY JOBS")
        logger.info("=" * 80)

        # Update general data
        await self.alpha_vantage.weekly_general_data_update()

        logger.info("=" * 80)
        logger.info("WEEKLY JOBS COMPLETED")
        logger.info("=" * 80)

    # =====================================
    # QUARTERLY JOBS
    # =====================================

    async def run_quarterly_jobs(self):
        """Run all quarterly jobs - Execute after earnings season"""
        logger.info("=" * 80)
        logger.info("STARTING QUARTERLY JOBS")
        logger.info("=" * 80)

        # Update fundamental data
        await self.alpha_vantage.quarterly_fundamental_update()

        logger.info("=" * 80)
        logger.info("QUARTERLY JOBS COMPLETED")
        logger.info("=" * 80)

    # =====================================
    # INITIAL SETUP JOBS (Run Once)
    # =====================================

    async def run_initial_setup(self, symbols: list[str]):
        """
        Run complete initial setup for new assets

        Usage:
            manager = JobManager()
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            await manager.run_initial_setup(symbols)
        """
        logger.info("=" * 80)
        logger.info(f"STARTING INITIAL SETUP FOR {len(symbols)} SYMBOLS")
        logger.info("=" * 80)

        await self.alpha_vantage.initial_complete_setup(symbols)

        logger.info("=" * 80)
        logger.info("INITIAL SETUP COMPLETED")
        logger.info("=" * 80)

    async def run_historical_backfill(self):
        """
        Backfill historical data for assets that don't have it

        Usage:
            manager = JobManager()
            await manager.run_historical_backfill()
        """
        logger.info("=" * 80)
        logger.info("STARTING HISTORICAL BACKFILL")
        logger.info("=" * 80)

        await self.alpha_vantage.initial_historical_only()

        logger.info("=" * 80)
        logger.info("HISTORICAL BACKFILL COMPLETED")
        logger.info("=" * 80)
