"""
CoinMarketCap Celery Tasks
Background tasks for fetching cryptocurrency data from CoinMarketCap
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
from data.data_providers.coinmarketcap.scraper import CoinMarketCapScraper

logger = logging.getLogger(__name__)


def parse_decimal(value: Any) -> Optional[Decimal]:
    """Parse value to Decimal, returning None for invalid values"""
    if value is None or value == "" or value == "None":
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_crypto_data_cmc(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch all data for a cryptocurrency from CoinMarketCap.

    Args:
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')

    Returns:
        Dict with status and data saved
    """
    try:
        asset = (
            Asset.objects.filter(
                symbol__iexact=symbol,
                asset_type__name__in=["crypto", "token"],
                is_deleted=False,
            )
            .select_related("asset_type")
            .first()
        )

        if not asset:
            logger.warning(f"Asset not found for symbol: {symbol}")
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = CoinMarketCapScraper()

        async def fetch_data():
            async with scraper:
                info = await scraper.get_cryptocurrency_info(symbol)
                quotes = await scraper.get_quotes_latest(symbol=symbol)
                return {
                    "info": info,
                    "quotes": quotes,
                }

        data = asyncio.run(fetch_data())

        data_provider, _ = DataProvider.objects.get_or_create(
            code="coinmarketcap",
            defaults={"name": "CoinMarketCap", "is_active": True},
        )

        # Update asset with quote data
        if data["quotes"] and len(data["quotes"]) > 0:
            quote = data["quotes"][0]
            quote_data = quote.get("quote", {}).get("USD", {})

            if quote_data.get("price"):
                asset.last_price = parse_decimal(quote_data.get("price"))
            if quote_data.get("market_cap"):
                asset.market_cap = parse_decimal(quote_data.get("market_cap"))
            if quote_data.get("volume_24h"):
                asset.volume_24h = parse_decimal(quote_data.get("volume_24h"))
            if quote_data.get("percent_change_24h"):
                asset.price_change_24h_pct = parse_decimal(
                    quote_data.get("percent_change_24h")
                )
            if quote_data.get("circulating_supply"):
                asset.circulating_supply = parse_decimal(
                    quote_data.get("circulating_supply")
                )
            if quote_data.get("total_supply"):
                asset.total_supply = parse_decimal(quote_data.get("total_supply"))

            asset.last_updated = timezone.now()
            asset.save()

        # Update with info data
        if data["info"] and symbol in data["info"]:
            info = data["info"][symbol]

            if info.get("name"):
                asset.name = info.get("name")
            if info.get("description"):
                asset.description = info.get("description", "")[:2000]

            urls = info.get("urls", {})
            if urls.get("website"):
                asset.website = urls["website"][0] if urls["website"] else ""
            if urls.get("explorer"):
                asset.explorer = urls["explorer"][0] if urls["explorer"] else ""

            if info.get("logo"):
                asset.logo_url = info.get("logo")

            asset.save()

        return {
            "status": "success",
            "symbol": symbol,
            "data_provider": "coinmarketcap",
            "timestamp": timezone.now().isoformat(),
            "has_info": bool(data["info"]),
            "has_quotes": bool(data["quotes"]),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching crypto data for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_crypto_listings_cmc(
    self, start: int = 1, limit: int = 100, sort: str = "market_cap"
) -> Dict[str, Any]:
    """
    Fetch latest cryptocurrency listings from CoinMarketCap.

    Args:
        start: Starting position
        limit: Number of results
        sort: Sort field

    Returns:
        Dict with listings data
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_listings():
            async with scraper:
                return await scraper.get_listings(start=start, limit=limit, sort=sort)

        listings = asyncio.run(fetch_listings())

        if not listings:
            return {"status": "error", "message": "No listings data returned"}

        # Queue individual crypto fetches
        queued = 0
        for item in listings[:50]:
            symbol = item.get("symbol")
            if symbol:
                fetch_crypto_data_cmc.delay(symbol)
                queued += 1

        return {
            "status": "success",
            "listings_count": len(listings),
            "queued_for_fetch": queued,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching crypto listings: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_global_metrics_cmc(self) -> Dict[str, Any]:
    """
    Fetch global cryptocurrency market metrics.

    Returns:
        Dict with global metrics
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_metrics():
            async with scraper:
                return await scraper.get_global_metrics()

        metrics = asyncio.run(fetch_metrics())

        if not metrics:
            return {"status": "error", "message": "No global metrics returned"}

        return {
            "status": "success",
            "data": metrics,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching global metrics: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_trending_cryptos_cmc(
    self, sort: str = "percent_change_24h", limit: int = 50
) -> Dict[str, Any]:
    """
    Fetch trending cryptocurrencies (gainers/losers).

    Args:
        sort: Sort field
        limit: Number of results

    Returns:
        Dict with trending data
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_trending():
            async with scraper:
                return await scraper.get_trending_gainers_losers(sort=sort, limit=limit)

        trending = asyncio.run(fetch_trending())

        if not trending:
            return {"status": "error", "message": "No trending data returned"}

        # Extract symbols and queue fetches
        symbols = []
        if isinstance(trending, list):
            for item in trending:
                if isinstance(item, dict) and "symbol" in item:
                    symbols.append(item["symbol"])
        elif isinstance(trending, dict) and "crypto" in trending:
            for item in trending.get("crypto", [])[:50]:
                if "symbol" in item:
                    symbols.append(item["symbol"])

        queued = 0
        for symbol in symbols[:30]:
            fetch_crypto_data_cmc.delay(symbol)
            queued += 1

        return {
            "status": "success",
            "trending_count": len(symbols),
            "queued_for_fetch": queued,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching trending cryptos: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_exchange_listings_cmc(
    self, start: int = 1, limit: int = 50
) -> Dict[str, Any]:
    """
    Fetch exchange listings from CoinMarketCap.

    Args:
        start: Starting position
        limit: Number of results

    Returns:
        Dict with exchange listings
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_exchanges():
            async with scraper:
                return await scraper.get_exchange_listings(start=start, limit=limit)

        exchanges = asyncio.run(fetch_exchanges())

        if not exchanges:
            return {"status": "error", "message": "No exchange data returned"}

        exchange_data = []
        for ex in exchanges[:20]:
            exchange_data.append(
                {
                    "name": ex.get("name"),
                    "slug": ex.get("slug"),
                    "volume_24h": ex.get("volume_24h"),
                    "num_market_pairs": ex.get("num_market_pairs"),
                    "rank": ex.get("cmc_rank"),
                }
            )

        return {
            "status": "success",
            "exchanges_count": len(exchanges),
            "exchanges": exchange_data,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching exchange listings: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def fetch_market_pairs_cmc(self, crypto_id: str) -> Dict[str, Any]:
    """
    Fetch market pairs for a cryptocurrency.

    Args:
        crypto_id: CoinMarketCap cryptocurrency ID

    Returns:
        Dict with market pairs
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_pairs():
            async with scraper:
                return await scraper.get_market_pairs(id=crypto_id)

        pairs = asyncio.run(fetch_pairs())

        if not pairs:
            return {"status": "error", "message": "No market pairs returned"}

        return {
            "status": "success",
            "crypto_id": crypto_id,
            "pairs_count": len(pairs),
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching market pairs for {crypto_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_crypto_quote_cmc(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch latest quote for a cryptocurrency.

    Args:
        symbol: Crypto symbol

    Returns:
        Dict with quote data
    """
    try:
        asset = Asset.objects.filter(
            symbol__iexact=symbol,
            asset_type__name__in=["crypto", "token"],
        ).first()

        if not asset:
            return {"status": "error", "message": f"Asset not found: {symbol}"}

        scraper = CoinMarketCapScraper()

        async def fetch_quote():
            async with scraper:
                return await scraper.get_quotes_latest(symbol=symbol)

        quotes = asyncio.run(fetch_quote())

        if not quotes:
            return {"status": "error", "message": "No quote data returned"}

        quote = quotes[0]
        quote_data = quote.get("quote", {}).get("USD", {})

        updates = {}
        if quote_data.get("price"):
            updates["last_price"] = parse_decimal(quote_data.get("price"))
        if quote_data.get("market_cap"):
            updates["market_cap"] = parse_decimal(quote_data.get("market_cap"))
        if quote_data.get("volume_24h"):
            updates["volume_24h"] = parse_decimal(quote_data.get("volume_24h"))
        if quote_data.get("percent_change_24h"):
            updates["price_change_24h_pct"] = parse_decimal(
                quote_data.get("percent_change_24h")
            )

        if updates:
            updates["last_updated"] = timezone.now()
            asset.save(update_fields=list(updates.keys()))

        return {
            "status": "success",
            "symbol": symbol,
            "price": quote_data.get("price"),
            "market_cap": quote_data.get("market_cap"),
            "volume_24h": quote_data.get("volume_24h"),
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise self.retry(exc=e)


@shared_task
def sync_coinmarketcap_provider_status() -> Dict[str, Any]:
    """
    Check CoinMarketCap API status and update provider configuration.

    Returns:
        Dict with provider status
    """
    try:
        scraper = CoinMarketCapScraper()

        async def check_status():
            async with scraper:
                listings = await scraper.get_listings(limit=1)
                return bool(listings)

        is_working = asyncio.run(check_status())

        data_provider, created = DataProvider.objects.get_or_create(
            code="coinmarketcap",
            defaults={
                "name": "CoinMarketCap",
                "is_active": is_working,
            },
        )

        if not created:
            data_provider.is_active = is_working
            data_provider.save()

        return {
            "status": "success",
            "provider": "coinmarketcap",
            "is_active": is_working,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error checking CoinMarketCap status: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def fetch_top_cryptos_cmc(self, limit: int = 100) -> Dict[str, Any]:
    """
    Fetch top cryptocurrencies by market cap.

    Args:
        limit: Number of cryptos to fetch

    Returns:
        Dict with processing summary
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_listings():
            async with scraper:
                return await scraper.get_listings(limit=limit)

        listings = asyncio.run(fetch_listings())

        if not listings:
            return {"status": "error", "message": "No listings data returned"}

        queued = 0
        for item in listings:
            symbol = item.get("symbol")
            if symbol:
                fetch_crypto_data_cmc.delay(symbol)
                queued += 1

        return {
            "status": "completed",
            "total_cryptos": len(listings),
            "queued_for_fetch": queued,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching top cryptos: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def fetch_crypto_fundamentals_cmc(self, symbol: str) -> Dict[str, Any]:
    """
    Fetch fundamental data for a cryptocurrency (tokenomics, supply).

    Args:
        symbol: Crypto symbol

    Returns:
        Dict with fundamental data
    """
    try:
        scraper = CoinMarketCapScraper()

        async def fetch_tokenomics():
            async with scraper:
                info = await scraper.get_cryptocurrency_info(symbol)
                price_perf = await scraper.get_price_snapshot(
                    id=str(item.get("id", ""))
                    if (item := (info.get(symbol, {}) if info else {}))
                    else ""
                )
                return {
                    "info": info,
                    "price_performance": price_perf,
                }

        data = asyncio.run(fetch_tokenomics())

        if not data["info"]:
            return {"status": "error", "message": "No fundamental data returned"}

        info = data["info"].get(symbol, {}) if isinstance(data["info"], dict) else {}

        return {
            "status": "success",
            "symbol": symbol,
            "circulating_supply": info.get("circulating_supply"),
            "total_supply": info.get("total_supply"),
            "max_supply": info.get("max_supply"),
            "cmc_rank": info.get("cmc_rank"),
            "date_launched": info.get("date_launched"),
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
        raise self.retry(exc=e)
