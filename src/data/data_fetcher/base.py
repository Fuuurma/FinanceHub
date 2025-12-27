# data/jobs/base_job.py
"""Base job class for all data fetching jobs"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from django.utils import timezone
from django.db import transaction

from data.data_providers.alphaVantage.script import AlphaVantageJobs
from investments.models.data_provider import DataProvider
from assets.models.asset import Asset
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class BaseDataJob:
    """Base class for data fetching jobs"""

    # use constants
    provider_id: str = None  # Override in subclasses

    def __init__(self):
        self.provider = DataProvider.objects.get(pk=self.provider_id)
        self.stats = {"total": 0, "success": 0, "errors": 0, "skipped": 0}

    # Improve, joins may vary depending on the data provider
    def get_supported_assets(self, limit: Optional[int] = None) -> List[Asset]:
        """Get assets supported by this provider"""
        queryset = Asset.objects.filter(
            primary_source=self.provider, is_active=True
        ).select_related("asset_type", "primary_source")

        if limit:
            queryset = queryset[:limit]

        return list(queryset)

    def log_job_start(self, job_name: str):
        """Log job start"""
        logger.info(f"Starting {job_name} for {self.provider.name}")
        self.stats = {"total": 0, "success": 0, "errors": 0, "skipped": 0}

    def log_job_end(self, job_name: str):
        """Log job completion"""
        logger.info(
            f"Completed {job_name} for {self.provider.name} - "
            f"Total: {self.stats['total']}, "
            f"Success: {self.stats['success']}, "
            f"Errors: {self.stats['errors']}, "
            f"Skipped: {self.stats['skipped']}"
        )

    def should_update_general_data(self, asset: Asset) -> bool:
        """Check if general data needs updating (every 7 days)"""
        if not asset.metadata.get("last_general_update"):
            return True

        last_update = datetime.fromisoformat(asset.metadata["last_general_update"])
        days_since_update = (timezone.now() - last_update).days

        return days_since_update >= 7

    def should_fetch_historical(self, asset: Asset) -> bool:
        """Check if we need to fetch historical data"""
        # Check if we have any prices
        has_prices = AssetPrice.objects.filter(asset=asset).exists()
        return not has_prices

    def get_last_price_date(self, asset: Asset) -> Optional[date]:
        """Get the last date we have price data for"""
        last_price = AssetPrice.objects.filter(asset=asset).order_by("-date").first()
        return last_price.date if last_price else None
