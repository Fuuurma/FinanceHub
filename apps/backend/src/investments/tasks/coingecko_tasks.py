"""
CoinGecko Celery Tasks
Background tasks for fetching cryptocurrency data from CoinGecko
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from celery import shared_task
from django.utils import timezone

from assets.models.asset import Asset
from investments.models.trending import TrendingAsset
from utils.services.cache_manager import get_cache_manager
from utils.services.call_planner import get_call_planner
from utils.services.data_orchestrator import get_data_orchestrator

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_trending_cryptos(self) -> Dict[str, Any]:
    """
    Fetch trending cryptocurrencies from CoinGecko and store in database.

    Returns:
        Dict with count of trending assets fetched
    """
    from utils.services.coingecko_websocket import CoinGeckoRESTClient

    try:
        client = CoinGeckoRESTClient()
        trending_data = asyncio.run(client.get_trending())

        coins = trending_data.get("coins", [])
        count = 0

        for item in coins[:20]:
            try:
                coin = item.get("item", {})
                coin_id = coin.get("id")

                if not coin_id:
                    continue

                asset = Asset.objects.filter(
                    provider_symbols__icontains=coin_id,
                    asset_type="crypto",
                ).first()

                if not asset:
                    logger.debug(f"No asset found for CoinGecko ID: {coin_id}")
                    continue

                TrendingAsset.objects.create(
                    asset=asset,
                    rank=count + 1,
                    market_cap=Decimal(str(coin.get("market_cap_rank", 0)))
                    if coin.get("market_cap_rank")
                    else None,
                    volume_24h=Decimal(str(coin.get("volume_24h", 0)))
                    if coin.get("volume_24h")
                    else None,
                    price_change_percentage_24h=Decimal(
                        str(coin.get("price_change_percentage_24h", 0))
                    )
                    if coin.get("price_change_percentage_24h")
                    else None,
                    sparkline_data=coin.get("sparkline", {}).get("7d", []),
                )
                count += 1

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Error processing trending coin {coin_id}: {e}")
                continue

        logger.info(f"Fetched {count} trending cryptocurrencies")
        return {"count": count, "timestamp": timezone.now().isoformat()}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching trending cryptos: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def update_crypto_prices(self) -> Dict[str, Any]:
    """
    Update cryptocurrency prices from CoinGecko.

    Returns:
        Dict with number of prices updated
    """
    from utils.services.coingecko_websocket import CoinGeckoRESTClient

    try:
        crypto_assets = Asset.objects.filter(
            asset_type="crypto",
            is_active=True,
        ).values_list("provider_symbols", flat=True)[:100]

        all_coin_ids = []
        for symbols in crypto_assets:
            if symbols:
                import json

                try:
                    symbols_dict = json.loads(symbols)
                    if "coingecko" in symbols_dict:
                        all_coin_ids.append(symbols_dict["coingecko"])
                except (json.JSONDecodeError, TypeError):
                    continue

        if not all_coin_ids:
            logger.info("No crypto assets with CoinGecko IDs found")
            return {"count": 0}

        client = CoinGeckoRESTClient()
        prices = asyncio.run(
            client.get_price(
                coin_ids=all_coin_ids[:100],
                currency="usd",
                include_24hr_change=True,
                include_24hr_vol=True,
                include_market_cap=True,
            )
        )

        count = 0
        for coin_id, data in prices.items():
            try:
                asset = Asset.objects.filter(
                    provider_symbols__icontains=coin_id,
                    asset_type="crypto",
                ).first()

                if not asset:
                    continue

                price = data.get("usd", 0)
                if price:
                    cache_manager = get_cache_manager()
                    cache_manager.set_cached_price(
                        symbol=asset.ticker,
                        price=Decimal(str(price)),
                        provider="coingecko",
                        timestamp=timezone.now(),
                    )
                    count += 1

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Error updating price for {coin_id}: {e}")
                continue

        logger.info(f"Updated {count} cryptocurrency prices from CoinGecko")
        return {"count": count, "timestamp": timezone.now().isoformat()}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error updating crypto prices: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_crypto_market_data(self, coin_id: str, days: int = 7) -> Dict[str, Any]:
    """
    Fetch historical market data for a specific cryptocurrency.

    Args:
        coin_id: CoinGecko coin ID
        days: Number of days of historical data

    Returns:
        Dict with market chart data
    """
    from utils.services.coingecko_websocket import CoinGeckoRESTClient

    try:
        client = CoinGeckoRESTClient()
        chart_data = asyncio.run(
            client.get_coin_market_chart(
                coin_id=coin_id,
                currency="usd",
                days=days,
            )
        )

        asset = Asset.objects.filter(
            provider_symbols__icontains=coin_id,
            asset_type="crypto",
        ).first()

        if asset:
            cache_manager = get_cache_manager()
            cache_manager.set_cached_data(
                key=f"cg_market_chart_{coin_id}",
                data=chart_data,
                ttl=3600,
            )

        logger.info(f"Fetched market data for {coin_id}")
        return {
            "coin_id": coin_id,
            "days": days,
            "data_keys": list(chart_data.keys()) if chart_data else [],
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching market data for {coin_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True)
def sync_all_crypto_prices(self) -> Dict[str, Any]:
    """
    Sync all cryptocurrency prices using data orchestrator.

    Returns:
        Dict with sync results
    """
    try:
        orchestrator = get_data_orchestrator()
        assets = Asset.objects.filter(
            asset_type="crypto",
            is_active=True,
        )[:50]

        symbols = [a.ticker for a in assets]

        result = orchestrator.fetch_and_update_prices(
            symbols=symbols,
            provider="coingecko",
            force_refresh=False,
        )

        logger.info(f"Synced {result.get('count', 0)} crypto prices")
        return result

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error syncing crypto prices: {e}")
        return {"error": str(e)}


@shared_task(bind=True)
def refresh_crypto_cache(self) -> Dict[str, Any]:
    """
    Refresh cryptocurrency price cache for all active crypto assets.

    Returns:
        Dict with cache refresh results
    """
    try:
        crypto_assets = Asset.objects.filter(
            asset_type="crypto",
            is_active=True,
        ).exclude(last_price__isnull=True)[:200]

        count = 0
        cache_manager = get_cache_manager()
        for asset in crypto_assets:
            if asset.last_price:
                cache_manager.set_cached_price(
                    symbol=asset.ticker,
                    price=asset.last_price,
                    provider="coingecko",
                    timestamp=asset.last_price_updated or timezone.now(),
                )
                count += 1

        logger.info(f"Refreshed cache for {count} cryptocurrencies")
        return {"count": count, "timestamp": timezone.now().isoformat()}

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error refreshing crypto cache: {e}")
        return {"error": str(e)}


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_dex_trading_pairs(self, dex_name: str = "uniswap-v3") -> Dict[str, Any]:
    """
    Fetch DEX trading pairs from CoinGecko.

    Args:
        dex_name: Name of the DEX to fetch data for

    Returns:
        Dict with trading pairs fetched
    """
    from investments.models.dex_data import DEXTradingPair

    try:
        planner = get_call_planner("coingecko")

        async def fetch_pairs():
            async with planner:
                import aiohttp

                url = f"https://api.coingecko.com/api/v3/dex/pairs/{dex_name}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()

        pairs_data = asyncio.run(fetch_pairs())

        count = 0
        for pair in pairs_data[:50]:
            try:
                base_token_address = pair.get("base_token_address", "").lower()
                quote_token_address = pair.get("quote_token_address", "").lower()

                base_asset = Asset.objects.filter(
                    contract_address__iexact=base_token_address,
                    asset_type="crypto",
                ).first()

                quote_asset = Asset.objects.filter(
                    contract_address__iexact=quote_token_address,
                    asset_type="crypto",
                ).first()

                if not base_asset or not quote_asset:
                    continue

                DEXTradingPair.objects.update_or_create(
                    dex_name=dex_name,
                    pool_address=pair.get("pool_address", "").lower(),
                    defaults={
                        "base_asset": base_asset,
                        "quote_asset": quote_asset,
                        "reserve_base": Decimal(str(pair.get("reserve_base", 0))),
                        "reserve_quote": Decimal(str(pair.get("reserve_quote", 0))),
                        "price": Decimal(str(pair.get("price", 0))),
                        "volume_24h": Decimal(str(pair.get("volume_24h", 0))),
                        "liquidity_usd": Decimal(
                            str(pair.get("liquidity", {}).get("usd", 0))
                        )
                        if pair.get("liquidity")
                        else None,
                        "fee_percentage": Decimal(
                            str(pair.get("fee_percentage", 0.003))
                        ),
                        "token_0_address": base_token_address,
                        "token_1_address": quote_token_address,
                        "last_synced_at": timezone.now(),
                    },
                )
                count += 1

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Error processing DEX pair: {e}")
                continue

        logger.info(f"Fetched {count} trading pairs from {dex_name}")
        return {
            "count": count,
            "dex_name": dex_name,
            "timestamp": timezone.now().isoformat(),
        }

    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        logger.error(f"Error fetching DEX pairs: {e}")
        raise self.retry(exc=e)
