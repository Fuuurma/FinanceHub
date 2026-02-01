from typing import List, Optional, Dict, Any
from datetime import datetime
from ninja import Router, Query, Schema
from django.shortcuts import get_object_or_404
from django.http import Http404

from utils.helpers.logger.logger import get_logger
from utils.services.data_orchestrator import get_data_orchestrator, Priority, DataFreshness
from utils.api.decorators import api_endpoint
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from core.exceptions import NotFoundException, ValidationException, DatabaseException, ExternalAPIException, ServiceException
from assets.models.asset import Asset

logger = get_logger(__name__)
router = Router(tags=["Unified Market Data"])
orchestrator = get_data_orchestrator()


class MarketDataRequest(Schema):
    symbol: str
    data_type: str = "price"
    params: Dict[str, Any] = {}
    force_refresh: bool = False
    priority: str = "medium"


class MarketDataResponse(Schema):
    data: Dict[str, Any]
    source: str
    cached: bool
    freshness: str
    fetched_at: datetime
    metadata: Dict[str, Any] = {}


class BatchMarketDataRequest(Schema):
    requests: List[MarketDataRequest]


class BatchMarketDataResponse(Schema):
    results: List[MarketDataResponse]
    total: int
    successful: int
    failed: int


class MarketStatisticsResponse(Schema):
    total_requests_last_hour: int
    cache_hit_rate: float
    sources_used: Dict[str, int]
    active_requests: int
    cache_stats: Dict[str, Any]
    call_planner_stats: Dict[str, Any]


class ProviderHealthResponse(Schema):
    provider: str
    healthy: bool
    last_checked: Optional[str] = None
    error: Optional[str] = None


@router.post("/market-data", response=MarketDataResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="market")
async def get_unified_market_data(request, payload: MarketDataRequest):
    """
    Unified endpoint to fetch any type of market data
    
    Data types: crypto_price, stock_price, crypto_historical, stock_historical,
                stock_fundamentals, news, technical_indicators, order_book, trades
    
    Priorities: urgent, high, medium, low, batch
    """
    priority_map = {
        'urgent': Priority.URGENT,
        'high': Priority.HIGH,
        'medium': Priority.MEDIUM,
        'low': Priority.LOW,
        'batch': Priority.BATCH
    }
    
    priority = priority_map.get(payload.priority, Priority.MEDIUM)
    
    try:
        response = await orchestrator.get_market_data(
            data_type=payload.data_type,
            symbol=payload.symbol,
            params=payload.params,
            force_refresh=payload.force_refresh,
            priority=priority
        )
        
        if not response or not response.data:
            raise ExternalAPIException(
                f"Unable to fetch market data for {payload.symbol}",
                "market_data_provider"
            )
        
        return MarketDataResponse(
            data=response.data,
            source=response.source.value,
            cached=response.cached,
            freshness=response.freshness.name,
            fetched_at=response.fetched_at,
            metadata=response.metadata
        )
        
    except ExternalAPIException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to fetch market data for {payload.symbol}: {e}")
        raise ServiceException(f"Failed to fetch market data for {payload.symbol}")


@router.post("/market-data/batch", response=BatchMarketDataResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="market_batch")
async def get_batch_market_data(request, payload: BatchMarketDataRequest):
    """
    Fetch multiple data points in a single batch request
    """
    from utils.services.data_orchestrator import DataRequest
    
    requests = []
    priority_map = {
        'urgent': Priority.URGENT,
        'high': Priority.HIGH,
        'medium': Priority.MEDIUM,
        'low': Priority.LOW,
        'batch': Priority.BATCH
    }
    
    for req in payload.requests:
        priority = priority_map.get(req.priority, Priority.MEDIUM)
        requests.append(DataRequest(
            data_type=req.data_type,
            symbol=req.symbol,
            params=req.params,
            freshness_required=orchestrator.freshness_requirements.get(req.data_type, DataFreshness.CACHED),
            priority=priority
        ))
    
    try:
        responses = await orchestrator.batch_fetch_market_data(requests)
        
        successful = 0
        failed = 0
        results = []
        
        for response in responses:
            if isinstance(response, Exception):
                failed += 1
                results.append({
                    "error": str(response),
                    "data_type": "unknown",
                    "symbol": "unknown"
                })
            else:
                successful += 1
                results.append(MarketDataResponse(
                    data=response.data,
                    source=response.source.value,
                    cached=response.cached,
                    freshness=response.freshness.name,
                    fetched_at=response.fetched_at,
                    metadata=response.metadata
                ))
        
        return BatchMarketDataResponse(
            results=results,
            total=len(requests),
            successful=successful,
            failed=failed
        )
        
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Batch market data fetch failed: {e}")
        raise ServiceException("Batch market data fetch failed")


@router.get("/price/{symbol}")
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['realtime'], key_prefix="price")
async def get_price(request, symbol: str, force_refresh: bool = False):
    """
    Get current price for a symbol (auto-detects crypto or stock)
    """
    try:
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        is_crypto = asset.asset_type.name.lower() in ['crypto', 'cryptocurrency']
        data_type = 'crypto_price' if is_crypto else 'stock_price'
        
        response = await orchestrator.get_market_data(
            data_type=data_type,
            symbol=symbol,
            force_refresh=force_refresh
        )
        
        if not response or not response.data:
            raise NotFoundException("Price data", symbol)
        
        price = response.data.get('price') or response.data.get('c', response.data.get('current_price'))
        if price is None:
            raise NotFoundException("Price data", symbol)
        
        return {
            "symbol": symbol,
            "price": price,
            "change": response.data.get('change', 0),
            "change_percent": response.data.get('change_percent', response.data.get('p', 0)),
            "timestamp": response.data.get('timestamp') or response.data.get('t'),
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Http404:
        raise NotFoundException("Asset", symbol)
    except NotFoundException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to fetch price for {symbol}: {e}")
        raise ServiceException(f"Failed to fetch price for {symbol}")


@router.get("/historical/{symbol}")
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['read'], key_prefix="historical")
async def get_historical(request, symbol: str, days: int = 30, timespan: str = 'day'):
    """
    Get historical price data for a symbol
    Timespan: minute, hour, day, week, month, quarter, year
    """
    try:
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        is_crypto = asset.asset_type.name.lower() in ['crypto', 'cryptocurrency']
        data_type = 'crypto_historical' if is_crypto else 'stock_historical'
        
        response = await orchestrator.get_market_data(
            data_type=data_type,
            symbol=symbol,
            params={'days': days, 'timespan': timespan}
        )
        
        if not response or not response.data:
            raise NotFoundException("Historical data", symbol)
        
        return {
            "symbol": symbol,
            "data": response.data,
            "source": response.source.value,
            "cached": response.cached,
            "metadata": response.metadata
        }
        
    except Http404:
        raise NotFoundException("Asset", symbol)
    except NotFoundException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to fetch historical data for {symbol}: {e}")
        raise ServiceException(f"Failed to fetch historical data for {symbol}")


@router.get("/news")
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="news")
async def get_news(
    request,
    query: Optional[str] = None,
    category: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 20
):
    """
    Get news articles
    Categories: business, entertainment, general, health, science, sports, technology
    """
    try:
        if symbol:
            asset = get_object_or_404(Asset, symbol__iexact=symbol)
            query = query or asset.name
        
        response = await orchestrator.get_market_data(
            data_type='news',
            symbol=symbol or 'general',
            params={
                'query': query,
                'category': category,
                'page_size': limit
            }
        )
        
        if not response:
            raise ExternalAPIException("News API", "Unable to fetch news")
        
        return {
            "articles": response.data.get('articles', []),
            "total": response.data.get('totalResults', 0),
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Http404:
        raise NotFoundException("Asset", symbol)
    except ExternalAPIException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to fetch news: {e}")
        raise ServiceException("Failed to fetch news")


@router.get("/technical/{symbol}")
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="technical")
async def get_technical_indicators(
    request,
    symbol: str,
    indicator: str = 'sma',
    **kwargs
):
    """
    Get technical indicators for a symbol
    Indicators: sma, ema, rsi, macd, bollinger
    """
    try:
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        response = await orchestrator.get_market_data(
            data_type='technical_indicators',
            symbol=symbol,
            params={'indicator': indicator, **kwargs}
        )
        
        if not response or not response.data:
            raise NotFoundException("Technical indicators", symbol)
        
        return {
            "symbol": symbol,
            "indicator": indicator,
            "data": response.data,
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Http404:
        raise NotFoundException("Asset", symbol)
    except NotFoundException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to fetch technical indicators for {symbol}: {e}")
        raise ServiceException(f"Failed to fetch technical indicators for {symbol}")


@router.get("/fundamentals/{symbol}")
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['read'], key_prefix="fundamentals")
async def get_fundamentals(request, symbol: str):
    """
    Get fundamental data for a stock
    """
    try:
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        response = await orchestrator.get_market_data(
            data_type='stock_fundamentals',
            symbol=symbol
        )
        
        if not response or not response.data:
            raise NotFoundException("Fundamental data", symbol)
        
        return {
            "symbol": symbol,
            "data": response.data,
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Http404:
        raise NotFoundException("Asset", symbol)
    except NotFoundException:
        raise
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to fetch fundamentals for {symbol}: {e}")
        raise ServiceException(f"Failed to fetch fundamentals for {symbol}")


@router.get("/cache/stats", response=Dict[str, Any])
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="cache_stats")
async def get_cache_statistics(request):
    """Get cache statistics"""
    try:
        return await orchestrator.cache_manager.get_statistics()
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise DatabaseException("Failed to retrieve cache statistics")


@router.post("/cache/clear")
@api_endpoint(rate=RATE_LIMITS['write'])
async def clear_cache(request, pattern: Optional[str] = None):
    """Clear cache, optionally by pattern"""
    try:
        if pattern:
            count = await orchestrator.cache_manager.invalidate_pattern(pattern)
            return {"message": f"Invalidated {count} cache entries matching '{pattern}'"}
        else:
            await orchestrator.cache_manager.clear_all()
            return {"message": "All cache cleared"}
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to clear cache: {e}")
        raise DatabaseException("Failed to clear cache")


@router.get("/stats", response=MarketStatisticsResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="market_stats")
async def get_market_statistics(request):
    """Get overall system statistics"""
    try:
        stats = await orchestrator.get_statistics()
        
        return MarketStatisticsResponse(
            total_requests_last_hour=stats['total_requests_last_hour'],
            cache_hit_rate=stats['cache_hit_rate'],
            sources_used=stats['sources_used'],
            active_requests=stats['active_requests'],
            cache_stats=stats['cache_stats'],
            call_planner_stats=stats['call_planner_stats']
        )
        
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to get market statistics: {e}")
        raise ServiceException("Failed to get market statistics")


@router.get("/health", response=List[ProviderHealthResponse])
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['read'], key_prefix="provider_health")
async def get_provider_health(request):
    """Get health status of all data providers"""
    try:
        health_status = await orchestrator.get_provider_health()
        
        responses = []
        for provider, health in health_status.items():
            responses.append(ProviderHealthResponse(
                provider=provider,
                healthy=health.get('healthy', False),
                last_checked=health.get('last_checked'),
                error=health.get('error')
            ))
        
        return responses
        
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to get provider health: {e}")
        raise ServiceException("Failed to get provider health")


@router.post("/prefetch")
@api_endpoint(rate=RATE_LIMITS['write'])
async def prefetch_data(request, symbols: List[str], data_types: List[str]):
    """
    Prefetch data for multiple symbols and data types
    Useful for warming the cache
    """
    try:
        count = await orchestrator.prefetch_data(symbols, data_types)
        
        return {
            "message": f"Prefetched data for {count} data points",
            "symbols": symbols,
            "data_types": data_types
        }
        
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        logger.error(f"Failed to prefetch data: {e}")
        raise ServiceException("Failed to prefetch data")
