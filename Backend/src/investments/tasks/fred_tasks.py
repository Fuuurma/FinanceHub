"""
Celery tasks for fetching FRED economic data
Federal Reserve Economic Data integration
"""

import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from celery import shared_task
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_series_fred(
    self, series_id: str, observation_start: str = None, observation_end: str = None
) -> Dict[str, Any]:
    """
    Fetch a single economic data series from FRED.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'CPIAUCSL', 'UNRATE')
        observation_start: Start date (YYYY-MM-DD)
        observation_end: End date (YYYY-MM-DD)

    Returns:
        Dict with fetch status and series data
    """
    from investments.models.economic_indicator import (
        EconomicIndicator,
        EconomicDataPoint,
    )
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable not set")

        scraper = FREDScraper(api_key=api_key)

        logger.info(f"Fetching FRED series: {series_id}")

        series_data = scraper.get_series_data(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
        )

        if not series_data or "observations" not in series_data:
            logger.warning(f"No observations found for series {series_id}")
            return {
                "status": "error",
                "message": f"No observations found for {series_id}",
            }

        series_info = scraper.get_series_info(series_id)
        if not series_info or "seriess" not in series_info:
            logger.warning(f"No info found for series {series_id}")

        indicator, created = EconomicIndicator.objects.update_or_create(
            series_id=series_id,
            defaults={
                "title": series_info.get("seriess", [{}])[0].get("title", series_id)
                if series_info.get("seriess")
                else series_id,
                "description": series_info.get("seriess", [{}])[0].get("notes", "")
                if series_info.get("seriess")
                else "",
                "units": series_info.get("seriess", [{}])[0].get("units", "")
                if series_info.get("seriess")
                else "",
                "frequency": series_info.get("seriess", [{}])[0].get("frequency", "")
                if series_info.get("seriess")
                else "",
                "seasonal_adjustment": series_info.get("seriess", [{}])[0].get(
                    "seasonal_adjustment", ""
                )
                or "",
                "last_updated": datetime.now(),
                "observation_start": datetime.strptime(
                    series_info.get("seriess", [{}])[0].get(
                        "observation_start", "1900-01-01"
                    ),
                    "%Y-%m-%d",
                ).date()
                if series_info.get("seriess")
                else None,
                "observation_end": datetime.strptime(
                    series_info.get("seriess", [{}])[0].get(
                        "observation_end", "1900-01-01"
                    ),
                    "%Y-%m-%d",
                ).date()
                if series_info.get("seriess")
                else None,
                "popularity_score": series_info.get("seriess", [{}])[0].get(
                    "popularity", 0
                )
                if series_info.get("seriess")
                else 0,
            },
        )

        observations_added = 0
        for obs in series_data["observations"]:
            if obs.get("value") and obs["value"] != ".":
                EconomicDataPoint.objects.update_or_create(
                    indicator=indicator,
                    date=datetime.strptime(obs["date"], "%Y-%m-%d").date(),
                    realtime_start=datetime.strptime(
                        obs.get("realtime_start", "1900-01-01"), "%Y-%m-%d"
                    ).date(),
                    defaults={
                        "value": obs["value"],
                        "realtime_end": datetime.strptime(
                            obs.get("realtime_end", "1900-01-01"), "%Y-%m-%d"
                        ).date(),
                    },
                )
                observations_added += 1

        logger.info(
            f"Fetched {observations_added} observations for {series_id} (created={created})"
        )

        return {
            "status": "success",
            "series_id": series_id,
            "observations_added": observations_added,
            "indicator_created": created,
        }

    except Exception as e:
        logger.error(f"Error fetching FRED series {series_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_gdp_fred(self, real_gdp: bool = True) -> Dict[str, Any]:
    """Fetch GDP data from FRED"""
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)
        series_id = "GDPC1" if real_gdp else "GDP"

        logger.info(f"Fetching GDP data: {series_id}")

        data = scraper.get_gdp(real_gdp=real_gdp)
        return fetch_series_fred(series_id)

    except Exception as e:
        logger.error(f"Error fetching GDP: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_inflation_fred(self) -> Dict[str, Any]:
    """Fetch inflation indicators (CPI, PCE) from FRED"""
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)

        logger.info("Fetching inflation indicators")

        series_ids = ["CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE"]
        results = []

        for series_id in series_ids:
            result = fetch_series_fred(series_id)
            results.append(result)

        return {"status": "success", "series_fetched": len(results), "results": results}

    except Exception as e:
        logger.error(f"Error fetching inflation data: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_employment_fred(self) -> Dict[str, Any]:
    """Fetch employment indicators from FRED"""
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)

        logger.info("Fetching employment indicators")

        series_ids = ["UNRATE", "PAYEMS", "ICSA", "CIVPART"]
        results = []

        for series_id in series_ids:
            result = fetch_series_fred(series_id)
            results.append(result)

        return {"status": "success", "series_fetched": len(results), "results": results}

    except Exception as e:
        logger.error(f"Error fetching employment data: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_interest_rates_fred(self) -> Dict[str, Any]:
    """Fetch interest rates from FRED"""
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)

        logger.info("Fetching interest rates")

        series_ids = ["FEDFUNDS", "DGS3M", "DGS1", "DGS2", "DGS5", "DGS10", "DGS30"]
        results = []

        for series_id in series_ids:
            result = fetch_series_fred(series_id)
            results.append(result)

        return {"status": "success", "series_fetched": len(results), "results": results}

    except Exception as e:
        logger.error(f"Error fetching interest rates: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_housing_fred(self) -> Dict[str, Any]:
    """Fetch housing indicators from FRED"""
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)

        logger.info("Fetching housing indicators")

        series_ids = ["HOUST", "PERMIT", "MORTGAGE30US", "MORTGAGE15US"]
        results = []

        for series_id in series_ids:
            result = fetch_series_fred(series_id)
            results.append(result)

        return {"status": "success", "series_fetched": len(results), "results": results}

    except Exception as e:
        logger.error(f"Error fetching housing data: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_all_indicators_fred(self) -> Dict[str, Any]:
    """
    Fetch all key economic indicators from FRED.
    This task can be scheduled to run daily/weekly.
    """
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)

        logger.info("Fetching all key FRED indicators")

        key_series_ids = [
            # GDP and Growth
            "GDP",
            "GDPC1",
            # Inflation
            "CPIAUCSL",
            "CPILFESL",
            "PCEPI",
            "PCEPILFE",
            # Employment
            "UNRATE",
            "PAYEMS",
            "ICSA",
            "CIVPART",
            # Interest Rates
            "FEDFUNDS",
            "DGS3M",
            "DGS1",
            "DGS2",
            "DGS5",
            "DGS10",
            "DGS30",
            # Housing
            "HOUST",
            "PERMIT",
            "MORTGAGE30US",
            "MORTGAGE15US",
            # Consumer
            "UMCSENT",
            "RSXFS",
            "PSAVERT",
            # Industrial
            "IPMAN",
            "TCU",
        ]

        results = []
        for series_id in key_series_ids:
            try:
                result = fetch_series_fred(series_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to fetch {series_id}: {e}")
                results.append(
                    {"status": "error", "series_id": series_id, "error": str(e)}
                )

        successful = sum(1 for r in results if r.get("status") == "success")

        logger.info(
            f"Fetched {successful}/{len(key_series_ids)} FRED series successfully"
        )

        return {
            "status": "success",
            "total_series": len(key_series_ids),
            "successful": successful,
            "failed": len(key_series_ids) - successful,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error fetching all indicators: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_macro_dashboard_fred(self) -> Dict[str, Any]:
    """
    Update macro dashboard cache with latest indicators.
    Creates/updates EconomicDataCache entries.
    """
    from investments.models.economic_indicator import EconomicDataCache
    from data.data_providers.fred.scraper import FREDScraper

    try:
        api_key = os.getenv("FRED_API_KEY")
        scraper = FREDScraper(api_key=api_key)

        logger.info("Updating macro dashboard cache")

        macro_data = scraper.get_latest_macro_data()

        cache_entry, created = EconomicDataCache.objects.update_or_create(
            cache_key="latest_macro_data",
            defaults={
                "data": macro_data,
                "expires_at": datetime.now() + timedelta(hours=1),
            },
        )

        logger.info(f"Macro dashboard cache updated (created={created})")

        return {
            "status": "success",
            "cache_key": "latest_macro_data",
            "created": created,
        }

    except Exception as e:
        logger.error(f"Error updating macro dashboard: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_fred_provider_status(self) -> Dict[str, Any]:
    """Health check for FRED API provider"""
    from data.data_providers.fred.scraper import FREDScraper
    from utils.services.provider_status_sync import ProviderStatusSync

    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "message": "FRED_API_KEY not configured",
            }

        scraper = FREDScraper(api_key=api_key)

        test_series = scraper.get_series_info("GDP")
        is_healthy = bool(test_series and "seriess" in test_series)

        status_sync = ProviderStatusSync()
        status_sync.update_provider_status(
            provider_name="fred",
            is_healthy=is_healthy,
            details={"api_key_configured": True, "test_series": "GDP"},
        )

        logger.info(f"FRED provider health check: {is_healthy}")

        return {
            "status": "success" if is_healthy else "error",
            "is_healthy": is_healthy,
        }

    except Exception as e:
        logger.error(f"FRED provider health check failed: {e}")

        status_sync = ProviderStatusSync()
        status_sync.update_provider_status(
            provider_name="fred",
            is_healthy=False,
            details={"error": str(e)},
        )

        return {
            "status": "error",
            "is_healthy": False,
            "error": str(e),
        }
