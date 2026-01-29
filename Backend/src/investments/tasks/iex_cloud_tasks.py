"""
IEX Cloud Celery Tasks
Background tasks for fetching fundamental data from IEX Cloud
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from celery import shared_task
from django.utils import timezone
from datetime import datetime

from assets.models.asset import Asset
from investments.models import DataProvider
from data.data_providers.iex_cloud.scraper import IEXCloudScraper

logger = logging.getLogger(__name__)


def parse_decimal(value: Any) -> Optional[Decimal]:
    """Parse value to Decimal, returning None for invalid values"""
    if value is None or value == "" or value == "None":
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_stock_fundamentals_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch all fundamental data for a single stock from IEX Cloud.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'IBM')

    Returns:
        Dict with status and data saved
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

        scraper = IEXCloudScraper()

        async def fetch_data():
            async with scraper:
                company = await scraper.get_company(symbol)
                key_stats = await scraper.get_key_stats(symbol)
                estimates = await scraper.get_estimates(symbol)
                financials = await scraper.get_financials(symbol)
                earnings = await scraper.get_earnings(symbol)
                peers = await scraper.get_peers(symbol)

                return {
                    "company": company,
                    "key_stats": key_stats,
                    "estimates": estimates,
                    "financials": financials,
                    "earnings": earnings,
                    "peers": peers,
                }

        data = asyncio.run(fetch_data())

        # Update data provider status
        data_provider, _ = DataProvider.objects.get_or_create(
            code="iex_cloud",
            defaults={"name": "IEX Cloud", "is_active": True},
        )

        # Update asset with company data
        if data["company"]:
            company = data["company"]
            asset.name = company.get("companyName", asset.name)
            asset.description = company.get("description", asset.description)
            asset.website = company.get("website", asset.website)
            asset.country = company.get("country", asset.country)
            asset.industry = company.get("industry", asset.industry)
            asset.sector = company.get("sector", asset.sector)
            asset.employees = company.get("employees", asset.employees)
            if company.get("logo"):
                asset.logo_url = company.get("logo")
            asset.last_fundamentals_updated = timezone.now()
            asset.save()

        # Update asset with key stats
        if data["key_stats"]:
            stats = data["key_stats"]
            if stats.get("marketCap"):
                asset.market_cap = parse_decimal(stats.get("marketCap"))
            if stats.get("peRatio"):
                asset.pe_ratio = parse_decimal(stats.get("peRatio"))
            if stats.get("divYield"):
                asset.dividend_yield = parse_decimal(stats.get("divYield"))
            if stats.get("week52High"):
                asset.high_52w = parse_decimal(stats.get("week52High"))
            if stats.get("week52Low"):
                asset.low_52w = parse_decimal(stats.get("week52Low"))
            asset.save()

        return {
            "status": "success",
            "symbol": symbol,
            "data_provider": "iex_cloud",
            "timestamp": timezone.now().isoformat(),
            "has_company": bool(data["company"]),
            "has_key_stats": bool(data["key_stats"]),
            "has_estimates": bool(data["estimates"]),
            "has_financials": bool(data["financials"]),
            "has_earnings": bool(data["earnings"]),
            "has_peers": bool(data["peers"] and isinstance(data["peers"], list)),
        }

    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_key_stats_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch key statistics for a stock from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and stats
    """
    try:
        asset = Asset.objects.filter(
            symbol__iexact=symbol,
            asset_type__name__in=["stock", "etf"],
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = IEXCloudScraper()

        async def fetch_stats():
            async with scraper:
                return await scraper.get_key_stats(symbol)

        stats = asyncio.run(fetch_stats())

        if not stats:
            return {"status": "error", "message": "No stats data returned"}

        updates = {}

        metric_mapping = {
            "marketCap": "market_cap",
            "peRatio": "pe_ratio",
            "divYield": "dividend_yield",
            "week52High": "high_52w",
            "week52Low": "low_52w",
            "beta": "beta",
            "eps": "eps",
            "revenuePerShare": "revenue_per_share",
            "profitMargin": "profit_margin",
            "priceToBook": "pb_ratio",
            "priceToSales": "ps_ratio",
            "revenueGrowth": "revenue_growth",
            "netIncome": "net_income",
            "sharesOutstanding": "shares_outstanding",
            "avg10Volume": "avg_volume_10d",
            "avg30Volume": "avg_volume_30d",
        }

        for iex_field, model_field in metric_mapping.items():
            if iex_field in stats and stats[iex_field] is not None:
                updates[model_field] = parse_decimal(stats[iex_field])

        if updates:
            updates["last_fundamentals_updated"] = timezone.now()
            asset.save(update_fields=list(updates.keys()))

        return {
            "status": "success",
            "symbol": symbol,
            "stats_saved": len(updates),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching key stats for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=180)
def fetch_analyst_estimates_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch analyst estimates from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and estimates data
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_estimates():
            async with scraper:
                return await scraper.get_estimates(symbol)

        data = asyncio.run(fetch_estimates())

        if not data or "estimates" not in data:
            return {"status": "error", "message": "No estimates data returned"}

        estimates = data["estimates"]

        logger.info(f"Fetched {len(estimates)} estimate periods for {symbol}")

        return {
            "status": "success",
            "symbol": symbol,
            "periods_count": len(estimates),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching estimates for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_peers_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch peer companies from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and peers list
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_peers():
            async with scraper:
                return await scraper.get_peers(symbol)

        peers = asyncio.run(fetch_peers())

        if not peers or not isinstance(peers, list):
            return {"status": "error", "message": "No peers data returned"}

        # Queue fetching for each peer
        for peer_symbol in peers[:10]:
            fetch_stock_fundamentals_iex.delay(peer_symbol)

        return {
            "status": "success",
            "symbol": symbol,
            "peers_count": len(peers),
            "peers": peers[:10],
            "queued_peers": True,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching peers for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def fetch_market_movers_iex(self, list_type: str = "mostactive") -> Dict[str, Any]:
    """
    Fetch market movers from IEX Cloud.

    Args:
        list_type: 'mostactive', 'gainers', 'losers'

    Returns:
        Dict with status and movers list
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_movers():
            async with scraper:
                return await scraper.get_market_list(list_type)

        data = asyncio.run(fetch_movers())

        if not data:
            return {"status": "error", "message": "No market movers data returned"}

        tickers = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "symbol" in item:
                    tickers.append(item["symbol"])
        elif isinstance(data, dict) and "symbols" in data:
            tickers = data["symbols"]

        # Queue fundamental fetch for each ticker
        for ticker in tickers[:20]:
            fetch_stock_fundamentals_iex.delay(ticker)

        return {
            "status": "success",
            "list_type": list_type,
            "tickers_count": len(tickers),
            "tickers": tickers[:10],
            "queued_for_fundamentals": True,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching market movers: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_insider_transactions_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch insider transactions from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and transactions
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_transactions():
            async with scraper:
                return await scraper.get_insider_transactions(symbol)

        data = asyncio.run(fetch_transactions())

        if not data or "transactions" not in data:
            return {"status": "error", "message": "No insider transactions data"}

        transactions = data.get("transactions", [])

        logger.info(f"Fetched {len(transactions)} insider transactions for {symbol}")

        return {
            "status": "success",
            "symbol": symbol,
            "transactions_count": len(transactions),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching insider transactions for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_institutional_ownership_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch institutional ownership from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and ownership data
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_ownership():
            async with scraper:
                return await scraper.get_institutional_ownership(symbol)

        data = asyncio.run(fetch_ownership())

        if not data or "ownership" not in data:
            return {"status": "error", "message": "No ownership data returned"}

        ownership = data.get("ownership", [])

        logger.info(f"Fetched {len(ownership)} institutional holders for {symbol}")

        return {
            "status": "success",
            "symbol": symbol,
            "holders_count": len(ownership),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching institutional ownership for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_fund_ownership_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch fund ownership from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and fund ownership data
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_ownership():
            async with scraper:
                return await scraper.get_fund_ownership(symbol)

        data = asyncio.run(fetch_ownership())

        if not data or "ownership" not in data:
            return {"status": "error", "message": "No fund ownership data returned"}

        ownership = data.get("ownership", [])

        logger.info(f"Fetched {len(ownership)} fund holders for {symbol}")

        return {
            "status": "success",
            "symbol": symbol,
            "funds_count": len(ownership),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching fund ownership for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def fetch_board_members_iex(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch board members from IEX Cloud.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with status and board members
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_board():
            async with scraper:
                return await scraper.get_board_members(symbol)

        data = asyncio.run(fetch_board())

        if not data or "members" not in data:
            return {"status": "error", "message": "No board members data returned"}

        members = data.get("members", [])

        logger.info(f"Fetched {len(members)} board members for {symbol}")

        return {
            "status": "success",
            "symbol": symbol,
            "members_count": len(members),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching board members for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_iex_quote(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch quote from IEX Cloud (sandbox data).

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with quote data
    """
    try:
        asset = Asset.objects.filter(
            symbol__iexact=symbol,
            asset_type__name="stock",
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = IEXCloudScraper()

        async def fetch_quote():
            async with scraper:
                return await scraper.get_quote(symbol)

        quote = asyncio.run(fetch_quote())

        if not quote:
            return {"status": "error", "message": "No quote data returned"}

        # Update asset with quote data
        if quote.get("latestPrice"):
            asset.last_price = parse_decimal(quote.get("latestPrice"))
        if quote.get("volume"):
            asset.last_trade_volume = parse_decimal(quote.get("volume"))
        if quote.get("changePercent"):
            asset.price_change_24h_pct = parse_decimal(quote.get("changePercent"))
        asset.last_updated = timezone.now()
        asset.save(
            update_fields=[
                "last_price",
                "last_trade_volume",
                "price_change_24h_pct",
                "last_updated",
            ]
        )

        return {
            "status": "success",
            "symbol": symbol,
            "price": quote.get("latestPrice"),
            "change": quote.get("change"),
            "change_percent": quote.get("changePercent"),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task
def sync_iex_cloud_provider_status() -> Dict[str, Any]:
    """
    Check IEX Cloud API status and update provider configuration.

    Returns:
        Dict with provider status
    """
    try:
        scraper = IEXCloudScraper()

        async def check_status():
            async with scraper:
                company = await scraper.get_company("AAPL")
                return company and "companyName" in company

        is_working = asyncio.run(check_status())

        data_provider, created = DataProvider.objects.get_or_create(
            code="iex_cloud",
            defaults={
                "name": "IEX Cloud",
                "is_active": is_working,
            },
        )

        if not created:
            data_provider.is_active = is_working
            data_provider.save()

        return {
            "status": "success",
            "provider": "iex_cloud",
            "is_active": is_working,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error checking IEX Cloud status: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def fetch_stocks_batch_iex(self, symbols: List[str]) -> Dict[str, Any]:
    """
    Fetch fundamentals for multiple stocks in batch.

    Args:
        symbols: List of stock tickers

    Returns:
        Dict with processing summary
    """
    try:
        queued = 0
        for symbol in symbols:
            try:
                fetch_stock_fundamentals_iex.delay(symbol)
                queued += 1
            except Exception as e:
                logger.error(f"Failed to queue fetch for {symbol}: {e}")
                continue

        return {
            "status": "completed",
            "total_symbols": len(symbols),
            "queued": queued,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in batch fetch: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def fetch_sector_performance_iex(self) -> Dict[str, Any]:
    """
    Fetch sector performance from IEX Cloud.

    Returns:
        Dict with sector performance data
    """
    try:
        scraper = IEXCloudScraper()

        async def fetch_performance():
            async with scraper:
                return await scraper.get_sector_performance()

        sectors = asyncio.run(fetch_performance())

        if not sectors or not isinstance(sectors, list):
            return {"status": "error", "message": "No sector performance data"}

        return {
            "status": "success",
            "sectors_count": len(sectors),
            "sectors": [
                {
                    "name": s.get("name"),
                    "performance": s.get("performance"),
                }
                for s in sectors[:12]
            ],
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching sector performance: {e}")
        raise self.retry(exc=e)
