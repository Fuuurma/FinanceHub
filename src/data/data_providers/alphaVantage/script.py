# executable script for jobs for data provider: Alpha Vantage

# Steps:

# Get Tickets / Id's from DB of assets suported by Alpha Vantage.

# From there, it depends on the job - fetch current prices, fetch historical prices, fetch metrics, etc.

from assets.models.asset import Asset
from investments.models.data_provider import DataProvider
from datetime import date, timedelta
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


async def run_alpha_vantage_job(job_type: str):

    # Get Alpha Vantage data provider config
    try:
        data_provider = DataProvider.objects.get(name="Alpha Vantage")
    except DataProvider.DoesNotExist:
        logger.error("Alpha Vantage DataProvider configuration not found.")
        return

    # Initialize fetcher
    async with AlphaVantageFetcher(config=data_provider) as fetcher:
        # Get all assets supported by Alpha Vantage
        assets = Asset.objects.filter(data_providers=data_provider)

        for asset in assets:
            if job_type == "current_price":
                data = await fetcher.fetch_price(asset)
                fetcher.update_price(asset, data, date.today())
                logger.info(f"Updated current price for {asset.ticker}")

            elif job_type == "historical_prices":
                end_date = date.today()
                start_date = end_date - timedelta(days=30)  # Last 30 days
                historical_data = await fetcher.fetch_historical(
                    asset, start_date, end_date
                )
                for daily_data in historical_data:
                    fetcher.update_price(asset, daily_data, daily_data["date"])
                logger.info(f"Updated historical prices for {asset.ticker}")

            elif job_type == "metrics":
                metrics_data = await fetcher.fetch_metrics(asset)
                fetcher.update_metrics(asset, metrics_data, date.today())
                logger.info(f"Updated metrics for {asset.ticker}")

            else:
                logger.warning(f"Unknown job type: {job_type}")
