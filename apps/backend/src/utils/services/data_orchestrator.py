import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from django.utils import timezone
from utils.helpers.logger.logger import get_logger
from utils.services.call_planner import get_call_planner, Priority
from utils.services.cache_manager import get_cache_manager, CacheManager
from utils.services.coingecko_websocket import (
    CoinGeckoWebSocketClient,
    CoinGeckoPriceUpdate,
)
from data.data_providers.coingecko.scraper import CoinGeckoScraper
from data.data_providers.coinmarketcap.scraper import CoinMarketCapScraper
from data.data_providers.crypto_cross_validator import CryptoCrossValidator
from data.data_providers.unified_crypto_provider import UnifiedCryptoProvider
from data.data_providers.polygon_io.scraper import PolygonIOScraper
from data.data_providers.iex_cloud.scraper import IEXCloudScraper
from data.data_providers.finnHub.scraper import FinnhubScraper
from data.data_providers.newsapi.scraper import NewsAPIScraper
from assets.models.asset import Asset

logger = get_logger(__name__)


class DataFreshness(Enum):
    REALTIME = 0
    NEAR_REALTIME = 30
    RECENT = 300
    CACHED = 3600
    STALE = 86400


class DataSource(Enum):
    CACHE = "cache"
    COINGECKO = "coingecko"
    COINMARKETCAP = "coinmarketcap"
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    POLYGON_IO = "polygon_io"
    IEX_CLOUD = "iex_cloud"
    FINNHUB = "finnhub"
    NEWSAPI = "newsapi"
    BINANCE = "binance"


@dataclass
class DataRequest:
    data_type: str
    symbol: str
    params: dict
    freshness_required: DataFreshness
    priority: Priority = Priority.MEDIUM
    fallback_sources: List[DataSource] = None

    def __post_init__(self):
        if self.fallback_sources is None:
            self.fallback_sources = []


@dataclass
class DataResponse:
    data: Any
    source: DataSource
    cached: bool
    freshness: DataFreshness
    fetched_at: datetime = field(default_factory=timezone.now)
    metadata: Dict = field(default_factory=dict)


class DataOrchestrator:
    def __init__(self):
        self.cache_manager: CacheManager = get_cache_manager()
        self.call_planner = get_call_planner()

        self.scrapers = {
            DataSource.COINGECKO: CoinGeckoScraper,
            DataSource.COINMARKETCAP: CoinMarketCapScraper,
            DataSource.POLYGON_IO: PolygonIOScraper,
            DataSource.IEX_CLOUD: IEXCloudScraper,
            DataSource.FINNHUB: FinnhubScraper,
            DataSource.NEWSAPI: NewsAPIScraper,
        }

        self.unified_crypto = UnifiedCryptoProvider()
        self.cross_validator = CryptoCrossValidator()

        self._ws_client: Optional[CoinGeckoWebSocketClient] = None
        self._ws_subscriptions: Set[str] = set()

        self.active_requests: Set[str] = set()
        self.request_history: List[Dict] = []

        self.freshness_requirements = {
            "crypto_price": DataFreshness.NEAR_REALTIME,
            "stock_price": DataFreshness.RECENT,
            "crypto_historical": DataFreshness.STALE,
            "stock_historical": DataFreshness.STALE,
            "crypto_fundamentals": DataFreshness.CACHED,
            "stock_fundamentals": DataFreshness.CACHED,
            "news": DataFreshness.CACHED,
            "technical_indicators": DataFreshness.RECENT,
            "order_book": DataFreshness.REALTIME,
            "trades": DataFreshness.REALTIME,
        }

    async def get_market_data(
        self,
        data_type: str,
        symbol: str,
        params: Optional[dict] = None,
        force_refresh: bool = False,
        priority: Priority = Priority.MEDIUM,
    ) -> DataResponse:
        params = params or {}
        freshness_required = self.freshness_requirements.get(
            data_type, DataFreshness.RECENT
        )

        request_id = f"{data_type}:{symbol}:{hash(str(params))}"

        if request_id in self.active_requests:
            logger.info(f"Request {request_id} already in progress, waiting...")
            await asyncio.sleep(0.1)
            return await self.get_market_data(
                data_type, symbol, params, force_refresh, priority
            )

        self.active_requests.add(request_id)

        try:
            if not force_refresh:
                cached_response = await self._try_cache(
                    data_type, symbol, params, freshness_required
                )

                if cached_response:
                    self._record_request(request_id, DataSource.CACHE, True)
                    return cached_response

            live_response = await self._fetch_live_data(
                data_type, symbol, params, priority
            )

            self._record_request(request_id, live_response.source, False)

            return live_response

        finally:
            self.active_requests.discard(request_id)

    async def _try_cache(
        self,
        data_type: str,
        symbol: str,
        params: dict,
        freshness_required: DataFreshness,
    ) -> Optional[DataResponse]:
        try:
            cached_data = await self.cache_manager.get(data_type, symbol, **params)

            if cached_data is None:
                return None

            if isinstance(cached_data, dict) and "timestamp" in cached_data:
                cache_age = (
                    timezone.now()
                    - timezone.make_aware(
                        datetime.fromisoformat(cached_data["timestamp"])
                    )
                ).total_seconds()
            else:
                cache_age = 0

            if cache_age <= freshness_required.value:
                return DataResponse(
                    data=cached_data,
                    source=DataSource.CACHE,
                    cached=True,
                    freshness=freshness_required,
                    metadata={"cache_age_seconds": cache_age},
                )

            return None

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Cache lookup failed: {e}")
            return None

    async def _fetch_live_data(
        self, data_type: str, symbol: str, params: dict, priority: Priority
    ) -> DataResponse:
        is_crypto = await self._is_crypto_asset(symbol)

        if data_type in ["crypto_price", "crypto_historical"]:
            return await self._fetch_crypto_data(data_type, symbol, params, priority)
        elif data_type in ["stock_price", "stock_historical", "stock_fundamentals"]:
            return await self._fetch_stock_data(data_type, symbol, params, priority)
        elif data_type == "news":
            return await self._fetch_news(symbol, params, priority)
        elif data_type == "technical_indicators":
            return await self._fetch_technical_indicators(symbol, params, priority)
        elif data_type in ["order_book", "trades"]:
            return await self._fetch_realtime_data(data_type, symbol, params, priority)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    async def _is_crypto_asset(self, symbol: str) -> bool:
        try:
            asset = await asyncio.to_thread(
                Asset.objects.filter(symbol=symbol).select_related("asset_type").first
            )
            if asset and asset.asset_type:
                return asset.asset_type.name.lower() in ["crypto", "cryptocurrency"]
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error checking asset type: {e}")

        return symbol.upper() in ["BTC", "ETH", "SOL", "ADA", "DOGE", "XRP"]

    async def _fetch_crypto_data(
        self, data_type: str, symbol: str, params: dict, priority: Priority
    ) -> DataResponse:
        try:
            if data_type == "crypto_price":
                data = await self.unified_crypto.get_crypto_price(symbol)
                source = DataSource.COINGECKO
            elif data_type == "crypto_historical":
                data = await self.unified_crypto.get_historical_prices(
                    symbol, days=params.get("days", 30)
                )
                source = DataSource.COINGECKO
            else:
                data = {}
                source = DataSource.COINGECKO

            await self.cache_manager.set(
                data_type, symbol, value=data, ttl=params.get("cache_ttl", 300)
            )

            return DataResponse(
                data=data,
                source=source,
                cached=False,
                freshness=DataFreshness.REALTIME
                if data_type == "crypto_price"
                else DataFreshness.CACHED,
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Failed to fetch crypto data: {e}")
            raise

    async def _fetch_stock_data(
        self, data_type: str, symbol: str, params: dict, priority: Priority
    ) -> DataResponse:
        data_source = DataSource.POLYGON_IO

        try:
            scraper = self.scrapers[data_source]()

            if data_type == "stock_price":
                data = await scraper.get_aggregate_bars(
                    symbol, timespan="day", multiplier=1, days=1
                )
                if data and len(data) > 0:
                    data = data[-1]
            elif data_type == "stock_historical":
                data = await scraper.get_aggregate_bars(
                    symbol,
                    timespan=params.get("timespan", "day"),
                    multiplier=params.get("multiplier", 1),
                    days=params.get("days", 30),
                )
            elif data_type == "stock_fundamentals":
                data = await scraper.get_ticker_details(symbol)
            else:
                data = {}

            await self.cache_manager.set(
                data_type, symbol, value=data, ttl=params.get("cache_ttl", 300)
            )

            return DataResponse(
                data=data,
                source=data_source,
                cached=False,
                freshness=DataFreshness.RECENT
                if data_type == "stock_price"
                else DataFreshness.CACHED,
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Failed to fetch stock data from Polygon.io: {e}")

            try:
                finnhub = self.scrapers[DataSource.FINNHUB]()

                if data_type == "stock_price":
                    data = await finnhub.get_real_time_price(symbol)
                elif data_type == "technical_indicators":
                    data = await finnhub.get_technical_indicators(symbol, **params)
                else:
                    data = {}

                await self.cache_manager.set(
                    data_type, symbol, value=data, ttl=params.get("cache_ttl", 300)
                )

                return DataResponse(
                    data=data,
                    source=DataSource.FINNHUB,
                    cached=False,
                    freshness=DataFreshness.RECENT,
                )

            except (NetworkError, TimeoutException, ValueError, KeyError) as e2:
                logger.error(f"Failed to fetch stock data from Finnhub: {e2}")
                raise

    async def _fetch_news(
        self, symbol: str, params: dict, priority: Priority
    ) -> DataResponse:
        try:
            newsapi = self.scrapers[DataSource.NEWSAPI]()

            data = await newsapi.search_news(
                query=params.get("query", symbol),
                category=params.get("category"),
                sources=params.get("sources"),
                language=params.get("language", "en"),
                page=params.get("page", 1),
                page_size=params.get("page_size", 20),
            )

            await self.cache_manager.set("news", symbol, value=data, ttl=3600)

            return DataResponse(
                data=data,
                source=DataSource.NEWSAPI,
                cached=False,
                freshness=DataFreshness.CACHED,
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Failed to fetch news: {e}")
            raise

    async def _fetch_technical_indicators(
        self, symbol: str, params: dict, priority: Priority
    ) -> DataResponse:
        try:
            finnhub = self.scrapers[DataSource.FINNHUB]()

            data = await finnhub.get_technical_indicators(
                symbol,
                indicator=params.get("indicator", "sma"),
                **{k: v for k, v in params.items() if k != "indicator"},
            )

            await self.cache_manager.set(
                "technical_indicators",
                symbol,
                value=data,
                ttl=params.get("cache_ttl", 300),
            )

            return DataResponse(
                data=data,
                source=DataSource.FINNHUB,
                cached=False,
                freshness=DataFreshness.RECENT,
            )

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Failed to fetch technical indicators: {e}")
            raise

    async def _fetch_realtime_data(
        self, data_type: str, symbol: str, params: dict, priority: Priority
    ) -> DataResponse:
        raise NotImplementedError(
            "Real-time data (order book, trades) requires WebSocket connection"
        )

    async def connect_websocket(self) -> bool:
        """Establish WebSocket connection for real-time crypto prices"""
        try:
            if self._ws_client and self._ws_client.is_connected:
                return True

            self._ws_client = CoinGeckoWebSocketClient()
            connected = await self._ws_client.connect()

            if connected:
                self._ws_client.add_price_callback(self._handle_realtime_price)
                logger.info("Connected to CoinGecko WebSocket for real-time prices")

            return connected
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Failed to connect to CoinGecko WebSocket: {e}")
            return False

    async def disconnect_websocket(self) -> None:
        """Close WebSocket connection"""
        if self._ws_client:
            await self._ws_client.disconnect()
            self._ws_client = None
            self._ws_subscriptions.clear()
            logger.info("Disconnected from CoinGecko WebSocket")

    async def subscribe_realtime_prices(self, coin_ids: List[str]) -> bool:
        """Subscribe to real-time price updates for given coin IDs"""
        if not self._ws_client or not self._ws_client.is_connected:
            await self.connect_websocket()

        if self._ws_client:
            success = await self._ws_client.subscribe(coin_ids)
            if success:
                self._ws_subscriptions.update(coin_ids)
                logger.info(f"Subscribed to real-time prices for: {coin_ids}")
            return success
        return False

    async def unsubscribe_realtime_prices(self, coin_ids: List[str]) -> bool:
        """Unsubscribe from real-time price updates"""
        if self._ws_client:
            success = await self._ws_client.unsubscribe(coin_ids)
            if success:
                for coin_id in coin_ids:
                    self._ws_subscriptions.discard(coin_id)
            return success
        return False

    def _handle_realtime_price(self, update: CoinGeckoPriceUpdate) -> None:
        """Handle incoming real-time price update"""
        try:
            symbol = update.coin_id.upper()

            self.cache_manager.set_cached_price(
                symbol=symbol,
                price=Decimal(str(update.price)),
                provider="coingecko_websocket",
                timestamp=timezone.now(),
            )

            logger.debug(f"Real-time price update: {symbol} = ${update.price}")
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
            logger.error(f"Error handling real-time price update: {e}")

    def get_websocket_status(self) -> Dict[str, Any]:
        """Get WebSocket connection status"""
        return {
            "connected": self._ws_client.is_connected if self._ws_client else False,
            "subscriptions": list(self._ws_subscriptions),
        }

    def fetch_and_update_prices(
        self,
        symbols: List[str],
        provider: str = "coingecko",
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Fetch and update prices for given symbols (sync wrapper)"""
        from assets.models.asset import Asset
        from decimal import Decimal
        from django.utils import timezone

        count = 0
        for symbol in symbols:
            try:
                asset = Asset.objects.filter(
                    symbol=symbol,
                    is_active=True,
                ).first()

                if not asset:
                    continue

                price = self.unified_crypto.get_crypto_price(symbol)
                if price:
                    self.cache_manager.set_cached_price(
                        symbol=symbol,
                        price=Decimal(str(price)),
                        provider=provider,
                        timestamp=timezone.now(),
                    )
                    count += 1
            except (
                ValueError,
                KeyError,
                TypeError,
                NetworkError,
                TimeoutException,
            ) as e:
                logger.error(f"Error updating price for {symbol}: {e}")

        return {"count": count, "provider": provider}

    def _record_request(self, request_id: str, source: DataSource, cached: bool):
        record = {
            "request_id": request_id,
            "source": source.value,
            "cached": cached,
            "timestamp": timezone.now().isoformat(),
        }

        self.request_history.append(record)

        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    async def batch_fetch_market_data(
        self, requests: List[DataRequest]
    ) -> List[DataResponse]:
        tasks = [
            self.get_market_data(
                req.data_type, req.symbol, req.params, priority=req.priority
            )
            for req in requests
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def prefetch_data(self, symbols: List[str], data_types: List[str]):
        prefetch_tasks = []

        for symbol in symbols:
            for data_type in data_types:
                prefetch_tasks.append(
                    self.get_market_data(data_type, symbol, priority=Priority.BATCH)
                )

        results = await asyncio.gather(*prefetch_tasks, return_exceptions=True)

        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Prefetched {successful}/{len(results)} data points")

        return successful

    async def get_provider_health(self) -> Dict[str, Dict]:
        health_status = {}

        for source, scraper_class in self.scrapers.items():
            try:
                scraper = scraper_class()
                is_healthy = await self._check_provider_health(scraper)

                health_status[source.value] = {
                    "healthy": is_healthy,
                    "last_checked": timezone.now().isoformat(),
                }
            except (
                ValueError,
                KeyError,
                TypeError,
                NetworkError,
                TimeoutException,
            ) as e:
                health_status[source.value] = {
                    "healthy": False,
                    "error": str(e),
                    "last_checked": timezone.now().isoformat(),
                }

        return health_status

    async def _check_provider_health(self, scraper) -> bool:
        try:
            return hasattr(scraper, "base_url") and scraper.base_url is not None
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError):
            return False

    async def get_statistics(self) -> dict:
        recent_requests = [
            r
            for r in self.request_history
            if timezone.now()
            - timezone.make_aware(datetime.fromisoformat(r["timestamp"]))
            < timedelta(hours=1)
        ]

        source_counts = {}
        for req in recent_requests:
            source = req["source"]
            source_counts[source] = source_counts.get(source, 0) + 1

        cache_hits = sum(1 for r in recent_requests if r["cached"])
        cache_hit_rate = cache_hits / len(recent_requests) if recent_requests else 0

        return {
            "total_requests_last_hour": len(recent_requests),
            "cache_hit_rate": cache_hit_rate,
            "sources_used": source_counts,
            "active_requests": len(self.active_requests),
            "cache_stats": await self.cache_manager.get_statistics(),
            "call_planner_stats": self.call_planner.get_statistics(),
        }


_data_orchestrator_instance: Optional[DataOrchestrator] = None


def get_data_orchestrator() -> DataOrchestrator:
    global _data_orchestrator_instance
    if _data_orchestrator_instance is None:
        _data_orchestrator_instance = DataOrchestrator()
    return _data_orchestrator_instance
