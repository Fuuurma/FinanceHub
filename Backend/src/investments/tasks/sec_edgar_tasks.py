"""
SEC Edgar Celery Tasks
Background tasks for fetching SEC filings and company disclosures
"""

import logging
from typing import Any, Dict, List, Optional

from celery import shared_task
from django.utils import timezone
from datetime import datetime

from assets.models.asset import Asset
from investments.models import DataProvider
from data.data_providers.sec_edgar.scraper import SECEDGARScraper

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_company_info_sec(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch company information from SEC Edgar.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'IBM')

    Returns:
        Dict with status and company info
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            logger.warning(f"Asset not found for symbol: {symbol}")
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        company_info = scraper.get_company_info(symbol)

        if company_info:
            logger.info(f"Fetched SEC company info for {symbol}")
            return {
                "status": "success",
                "data": company_info,
                "symbol": symbol,
            }
        else:
            return {"status": "error", "message": f"No company info found for {symbol}"}

    except Exception as e:
        logger.error(f"Error fetching SEC company info for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_company_filings_sec(
    self, symbol: str, filing_type: str = "10-K", count: int = 10
) -> Dict[str, Any]:
    """
    Fetch company filings from SEC Edgar.

    Args:
        symbol: Stock ticker symbol
        filing_type: Type of filing (10-K, 10-Q, 8-K, 4, etc.)
        count: Number of filings to return

    Returns:
        Dict with status and filings list
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        filings = scraper.get_company_filings(symbol, filing_type=filing_type)

        logger.info(f"Fetched {len(filings)} {filing_type} filings for {symbol}")
        return {
            "status": "success",
            "data": filings,
            "symbol": symbol,
            "filing_type": filing_type,
            "count": len(filings),
        }

    except Exception as e:
        logger.error(f"Error fetching SEC filings for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_all_filings_sec(self, symbol: str, count: int = 20) -> Dict[str, Any]:
    """
    Fetch all recent filings for a company.

    Args:
        symbol: Stock ticker symbol
        count: Number of recent filings to return

    Returns:
        Dict with status and filings list
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        filings = scraper.get_recent_filings_all(symbol, count=count)
        summary = scraper.get_filings_summary(symbol)

        logger.info(f"Fetched {len(filings)} recent filings for {symbol}")
        return {
            "status": "success",
            "data": {
                "recent_filings": filings,
                "summary": summary,
            },
            "symbol": symbol,
            "count": len(filings),
        }

    except Exception as e:
        logger.error(f"Error fetching all SEC filings for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_insider_transactions_sec(
    self, symbol: str, count: int = 50
) -> Dict[str, Any]:
    """
    Fetch insider transactions (Form 4) from SEC Edgar.

    Args:
        symbol: Stock ticker symbol
        count: Number of transactions to return

    Returns:
        Dict with status and insider transactions
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        transactions = scraper.get_insider_transactions(symbol, count=count)

        logger.info(f"Fetched {len(transactions)} insider transactions for {symbol}")
        return {
            "status": "success",
            "data": transactions,
            "symbol": symbol,
            "count": len(transactions),
        }

    except Exception as e:
        logger.error(f"Error fetching insider transactions for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_quarterly_reports_sec(self, symbol: str, count: int = 8) -> Dict[str, Any]:
    """
    Fetch quarterly reports (10-Q) from SEC Edgar.

    Args:
        symbol: Stock ticker symbol
        count: Number of quarters to return

    Returns:
        Dict with status and quarterly reports
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        reports = scraper.get_quarterly_reports(symbol, count=count)

        logger.info(f"Fetched {len(reports)} quarterly reports for {symbol}")
        return {
            "status": "success",
            "data": reports,
            "symbol": symbol,
            "count": len(reports),
        }

    except Exception as e:
        logger.error(f"Error fetching quarterly reports for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_annual_reports_sec(self, symbol: str, count: int = 5) -> Dict[str, Any]:
    """
    Fetch annual reports (10-K) from SEC Edgar.

    Args:
        symbol: Stock ticker symbol
        count: Number of years to return

    Returns:
        Dict with status and annual reports
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        reports = scraper.get_annual_reports(symbol, count=count)

        logger.info(f"Fetched {len(reports)} annual reports for {symbol}")
        return {
            "status": "success",
            "data": reports,
            "symbol": symbol,
            "count": len(reports),
        }

    except Exception as e:
        logger.error(f"Error fetching annual reports for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_current_reports_sec(self, symbol: str, count: int = 10) -> Dict[str, Any]:
    """
    Fetch current reports (8-K) from SEC Edgar.

    Args:
        symbol: Stock ticker symbol
        count: Number of reports to return

    Returns:
        Dict with status and current reports
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        reports = scraper.get_current_reports(symbol, count=count)

        logger.info(f"Fetched {len(reports)} current reports for {symbol}")
        return {
            "status": "success",
            "data": reports,
            "symbol": symbol,
            "count": len(reports),
        }

    except Exception as e:
        logger.error(f"Error fetching current reports for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_filings_summary_sec(self, symbol: str) -> Dict[str, Any]:
    """
    Get summary of all filing types for a company.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and filing summary
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = SECEDGARScraper()
        summary = scraper.get_filings_summary(symbol)

        logger.info(f"Fetched SEC filings summary for {symbol}")
        return {
            "status": "success",
            "data": summary,
            "symbol": symbol,
        }

    except Exception as e:
        logger.error(f"Error fetching filings summary for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_filing_document_sec(self, url: str) -> Dict[str, Any]:
    """
    Download a specific filing document.

    Args:
        url: URL of the filing document

    Returns:
        Dict with status and document content
    """
    try:
        scraper = SECEDGARScraper()
        content = scraper.get_filing_document(url)

        if content:
            logger.info(f"Downloaded filing document from {url}")
            return {
                "status": "success",
                "url": url,
                "content_length": len(content),
            }
        else:
            return {"status": "error", "message": "Failed to download document"}

    except Exception as e:
        logger.error(f"Error downloading filing document: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_sec_provider_status(self) -> Dict[str, Any]:
    """
    Check SEC Edgar provider status.

    Returns:
        Dict with provider status
    """
    try:
        scraper = SECEDGARScraper()
        test_result = scraper.get_company_info("AAPL")

        status = "healthy" if test_result else "degraded"

        return {
            "status": status,
            "provider": "sec_edgar",
            "message": "SEC Edgar API reachable"
            if test_result
            else "Failed to reach SEC Edgar",
            "checked_at": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error checking SEC Edgar status: {e}")
        return {
            "status": "error",
            "provider": "sec_edgar",
            "message": str(e),
            "checked_at": timezone.now().isoformat(),
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_filings_batch_sec(
    self, symbols: List[str] = None, filing_types: List[str] = None
) -> Dict[str, Any]:
    """
    Fetch filings for multiple symbols.

    Args:
        symbols: List of stock ticker symbols (defaults to active stocks)
        filing_types: List of filing types to fetch

    Returns:
        Dict with results for each symbol
    """
    if not symbols:
        symbols = list(
            Asset.objects.filter(
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            ).values_list("symbol", flat=True)[:100]
        )

    if not filing_types:
        filing_types = ["10-K", "10-Q", "8-K", "4"]

    results = {}
    scraper = SECEDGARScraper()

    for symbol in symbols:
        try:
            summary = scraper.get_filings_summary(symbol)
            results[symbol] = {
                "status": "success",
                "summary": summary,
            }
        except Exception as e:
            results[symbol] = {
                "status": "error",
                "message": str(e),
            }

    logger.info(f"Batch SEC sync for {len(symbols)} symbols complete")
    return {
        "status": "success",
        "symbols_processed": len(symbols),
        "results": results,
    }
