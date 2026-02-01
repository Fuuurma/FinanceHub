"""
Alpha Vantage Celery Tasks
Background tasks for fetching fundamental data from Alpha Vantage
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from celery import shared_task
from django.utils import timezone

from assets.models.asset import Asset
from investments.models import DataProvider
from data.data_providers.alphaVantage.scraper import AlphaVantageScraper

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_stock_fundamentals(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch all fundamental data for a single stock from Alpha Vantage.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'IBM')

    Returns:
        Dict with status and data saved
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol=symbol,
                asset_type__name__in=["stock", "etf"],
                is_active=True,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            logger.warning(f"Asset not found for symbol: {symbol}")
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = AlphaVantageScraper()

        async def fetch_data():
            async with scraper:
                overview = await scraper.get_company_overview(symbol)
                income_stmt = await scraper.get_income_statement(symbol)
                balance_sheet = await scraper.get_balance_sheet(symbol)
                cash_flow = await scraper.get_cash_flow(symbol)
                earnings = await scraper.get_earnings(symbol)

                return {
                    "overview": overview,
                    "income_statement": income_stmt,
                    "balance_sheet": balance_sheet,
                    "cash_flow": cash_flow,
                    "earnings": earnings,
                }

        data = asyncio.run(fetch_data())

        data_provider, _ = DataProvider.objects.get_or_create(
            code="alpha_vantage",
            defaults={"name": "Alpha Vantage", "is_active": True},
        )

        asset.last_fundamentals_updated = timezone.now()
        asset.save(update_fields=["last_fundamentals_updated"])

        return {
            "status": "success",
            "symbol": symbol,
            "data_provider": "alpha_vantage",
            "timestamp": timezone.now().isoformat(),
            "has_overview": bool(data["overview"] and "Symbol" in data["overview"]),
            "has_income_statement": bool(
                data["income_statement"]
                and "incomeStatement" in data["income_statement"]
            ),
            "has_balance_sheet": bool(
                data["balance_sheet"] and "balanceSheet" in data["balance_sheet"]
            ),
            "has_cash_flow": bool(
                data["cash_flow"] and "cashFlow" in data["cash_flow"]
            ),
            "has_earnings": bool(
                data["earnings"] and "quarterlyEarnings" in data["earnings"]
            ),
        }

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_all_stocks_fundamentals(self, batch_size: int = 50) -> Dict[str, Any]:
    """
    Fetch fundamentals for all active stocks in batches.

    Args:
        batch_size: Number of stocks to process per batch

    Returns:
        Dict with processing summary
    """
    try:
        from investments.tasks import chunked_task

        stocks = Asset.objects.filter(
            asset_type__name="stock",
            is_active=True,
        ).values_list("symbol", flat=True)[:200]

        total = len(stocks)
        processed = 0
        successful = 0
        failed = 0

        for symbol in stocks:
            try:
                result = fetch_stock_fundamentals.delay(symbol)
                processed += 1
                successful += 1
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                logger.error(f"Failed to queue fetch for {symbol}: {e}")
                failed += 1
                continue

        return {
            "status": "completed",
            "total_stocks": total,
            "queued": successful,
            "failed": failed,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error in batch fundamentals fetch: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_company_overview(self, symbol: str) -> Dict[str, Any]:
    """
    Update company overview/valuation metrics for a stock.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with update status
    """
    try:
        asset = Asset.objects.filter(
            symbol=symbol,
            asset_type__name__in=["stock", "etf"],
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = AlphaVantageScraper()

        async def fetch_overview():
            async with scraper:
                return await scraper.get_company_overview(symbol)

        overview = asyncio.run(fetch_overview())

        if overview and "Symbol" in overview:
            overview_data = overview

            def parse_decimal(value):
                if value is None or value == "" or value == "None":
                    return None
                try:
                    return Decimal(str(value))
                except (ValueError, TypeError):
                    return None

            updates = {}
            if "PERatio" in overview_data:
                updates["pe_ratio"] = parse_decimal(overview_data["PERatio"])
            if "MarketCapitalization" in overview_data:
                updates["market_cap"] = parse_decimal(
                    overview_data["MarketCapitalization"]
                )
            if "DividendYield" in overview_data:
                updates["dividend_yield"] = parse_decimal(
                    overview_data["DividendYield"]
                )
            if "EPS" in overview_data:
                updates["eps"] = parse_decimal(overview_data["EPS"])
            if "Beta" in overview_data:
                updates["beta"] = parse_decimal(overview_data["Beta"])
            if "52WeekHigh" in overview_data:
                updates["high_52w"] = parse_decimal(overview_data["52WeekHigh"])
            if "52WeekLow" in overview_data:
                updates["low_52w"] = parse_decimal(overview_data["52WeekLow"])

            if updates:
                updates["last_fundamentals_updated"] = timezone.now()
                asset.save(update_fields=list(updates.keys()))

            return {
                "status": "success",
                "symbol": symbol,
                "fields_updated": list(updates.keys()),
                "timestamp": timezone.now().isoformat(),
            }

        return {"status": "error", "message": "No overview data returned"}

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error updating company overview for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_income_statement(self, symbol: str, quarterly: bool = True) -> Dict[str, Any]:
    """
    Fetch income statement for a stock.

    Args:
        symbol: Stock ticker symbol
        quarterly: If True, fetch quarterly statements; else annual

    Returns:
        Dict with fetch status
    """
    from fundamentals.equities.financials import IncomeStatement

    try:
        asset = Asset.objects.filter(
            symbol=symbol,
            asset_type__name="stock",
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = AlphaVantageScraper()

        async def fetch_stmt():
            async with scraper:
                return await scraper.get_income_statement(symbol)

        data = asyncio.run(fetch_stmt())

        if data and "incomeStatement" in data:
            reports = (
                data["incomeStatement"].get("quarterlyReports", []) if quarterly else []
            )
            count = 0

            for report in reports[:8]:
                period_end = report.get("fiscalDateEnding", "")
                fiscal_year = int(period_end[:4]) if period_end else 2020

                month = int(period_end[5:7]) if period_end else 1
                if month in [1, 2, 3]:
                    fiscal_period = 2
                elif month in [4, 5, 6]:
                    fiscal_period = 3
                elif month in [7, 8, 9]:
                    fiscal_period = 4
                else:
                    fiscal_period = 1

                period_type = "quarterly"

                def parse_decimal(value):
                    if value is None or value == "" or value == "None":
                        return None
                    try:
                        return Decimal(str(value))
                    except (ValueError, TypeError):
                        return None

                from datetime import datetime

                report_date = (
                    datetime.strptime(period_end, "%Y-%m-%d") if period_end else None
                )

                if report_date:
                    IncomeStatement.objects.update_or_create(
                        asset=asset,
                        period_type=period_type,
                        fiscal_year=fiscal_year,
                        fiscal_period=fiscal_period,
                        defaults={
                            "report_date": report_date,
                            "total_revenue": parse_decimal(report.get("totalRevenue")),
                            "gross_profit": parse_decimal(report.get("grossProfit")),
                            "net_income": parse_decimal(report.get("netIncome")),
                            "ebitda": parse_decimal(report.get("ebitda")),
                            "basic_eps": parse_decimal(report.get("basicEPS")),
                            "diluted_eps": parse_decimal(report.get("dilutedEPS")),
                        },
                    )
                    count += 1

            return {
                "status": "success",
                "symbol": symbol,
                "period_type": period_type,
                "statements_saved": count,
                "timestamp": timezone.now().isoformat(),
            }

        return {"status": "error", "message": "No income statement data returned"}

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error fetching income statement for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_earnings_data(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch earnings data for a stock.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with fetch status
    """
    from fundamentals.equities.earnings import EarningsReport

    try:
        asset = Asset.objects.filter(
            symbol=symbol,
            asset_type__name="stock",
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = AlphaVantageScraper()

        async def fetch_earnings():
            async with scraper:
                return await scraper.get_earnings(symbol)

        data = asyncio.run(fetch_earnings())

        if data and "quarterlyEarnings" in data:
            reports = data["quarterlyEarnings"]
            count = 0

            for report in reports[:8]:
                period_end = report.get("fiscalDateEnding", "")
                fiscal_year = int(period_end[:4]) if period_end else 2020

                month = int(period_end[5:7]) if period_end else 1
                if month in [1, 2, 3]:
                    fiscal_period = 2
                elif month in [4, 5, 6]:
                    fiscal_period = 3
                elif month in [7, 8, 9]:
                    fiscal_period = 4
                else:
                    fiscal_period = 1

                def parse_decimal(value):
                    if value is None or value == "" or value == "None":
                        return None
                    try:
                        return Decimal(str(value))
                    except (ValueError, TypeError):
                        return None

                from datetime import datetime

                report_date = (
                    datetime.strptime(period_end, "%Y-%m-%d") if period_end else None
                )

                if report_date:
                    EarningsReport.objects.update_or_create(
                        asset=asset,
                        period_type="quarterly",
                        fiscal_year=fiscal_year,
                        fiscal_period=fiscal_period,
                        defaults={
                            "report_date": report_date,
                            "eps_actual": parse_decimal(report.get("reportedEPS")),
                            "eps_estimate": parse_decimal(report.get("estimatedEPS")),
                            "eps_surprise_pct": parse_decimal(
                                report.get("surprisePercentage")
                            ),
                        },
                    )
                    count += 1

            return {
                "status": "success",
                "symbol": symbol,
                "earnings_saved": count,
                "timestamp": timezone.now().isoformat(),
            }

        return {"status": "error", "message": "No earnings data returned"}

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error fetching earnings for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task
def sync_alpha_vantage_provider_status() -> Dict[str, Any]:
    """
    Check Alpha Vantage API status and update provider configuration.

    Returns:
        Dict with provider status
    """
    try:
        scraper = AlphaVantageScraper()

        async def check_status():
            async with scraper:
                overview = await scraper.get_company_overview("IBM")
                return "Symbol" in overview

        is_working = asyncio.run(check_status())

        data_provider, created = DataProvider.objects.get_or_create(
            code="alpha_vantage",
            defaults={
                "name": "Alpha Vantage",
                "is_active": is_working,
            },
        )

        if not created:
            data_provider.is_active = is_working
            data_provider.save()

        return {
            "status": "success",
            "provider": "alpha_vantage",
            "is_active": is_working,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error checking Alpha Vantage status: {e}")
        return {"status": "error", "message": str(e)}
