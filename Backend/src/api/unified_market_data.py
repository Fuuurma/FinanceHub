from typing import List, Optional, Dict, Any
from datetime import datetime
from ninja import Router, Query, Schema
from django.shortcuts import get_object_or_404
from ratelimit.decorators import ratelimit
from django.core.cache import cache

from utils.helpers.logger.logger import get_logger
from utils.services.data_orchestrator import get_data_orchestrator, Priority
from utils.services.cache_manager import get_cache_manager
from assets.models.asset import Asset
from utils.constants.api import RATE_LIMIT_READ, RATE_LIMIT_DATA_INTENSIVE, CACHE_TTL_SHORT

logger = get_logger(__name__)
router = Router(tags=["Unified Market Data"])
orchestrator = get_data_orchestrator()
cache_manager = get_cache_manager()


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
    last_checked: Optional[str]
    error: Optional[str] = None


@router.post("/market-data", response=MarketDataResponse)
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
        
        return MarketDataResponse(
            data=response.data,
            source=response.source.value,
            cached=response.cached,
            freshness=response.freshness.name,
            fetched_at=response.fetched_at,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch market data for {payload.symbol}: {e}")
        return {
            "error": str(e),
            "symbol": payload.symbol,
            "data_type": payload.data_type
        }


@router.post("/market-data/batch", response=BatchMarketDataResponse)
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
            freshness_required=orchestrator.freshness_requirements.get(req.data_type, None),
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
        
    except Exception as e:
        logger.error(f"Batch market data fetch failed: {e}")
        return {
            "error": str(e),
            "total": len(requests),
            "successful": 0,
            "failed": len(requests),
            "results": []
        }


@router.get("/price/{symbol}")
async def get_price(request, symbol: str, force_refresh: bool = False):
    """
    Get current price for a symbol (auto-detects crypto or stock)
    """
    try:
        asset = await get_object_or_404(Asset, symbol__iexact=symbol)
        
        is_crypto = asset.asset_type.name.lower() in ['crypto', 'cryptocurrency']
        data_type = 'crypto_price' if is_crypto else 'stock_price'
        
        response = await orchestrator.get_market_data(
            data_type=data_type,
            symbol=symbol,
            force_refresh=force_refresh
        )
        
        return {
            "symbol": symbol,
            "price": response.data.get('price') or response.data.get('c', response.data.get('current_price')),
            "change": response.data.get('change', 0),
            "change_percent": response.data.get('change_percent', response.data.get('p', 0)),
            "timestamp": response.data.get('timestamp') or response.data.get('t'),
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch price for {symbol}: {e}")
        return {"error": str(e), "symbol": symbol}


@router.get("/historical/{symbol}")
async def get_historical(request, symbol: str, days: int = 30, timespan: str = 'day'):
    """
    Get historical price data for a symbol
    Timespan: minute, hour, day, week, month, quarter, year
    """
    try:
        asset = await get_object_or_404(Asset, symbol__iexact=symbol)
        
        is_crypto = asset.asset_type.name.lower() in ['crypto', 'cryptocurrency']
        data_type = 'crypto_historical' if is_crypto else 'stock_historical'
        
        response = await orchestrator.get_market_data(
            data_type=data_type,
            symbol=symbol,
            params={'days': days, 'timespan': timespan}
        )
        
        return {
            "symbol": symbol,
            "data": response.data,
            "source": response.source.value,
            "cached": response.cached,
            "metadata": response.metadata
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch historical data for {symbol}: {e}")
        return {"error": str(e), "symbol": symbol}


@router.get("/news")
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
            asset = await get_object_or_404(Asset, symbol__iexact=symbol)
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
        
        return {
            "articles": response.data.get('articles', []),
            "total": response.data.get('totalResults', 0),
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return {"error": str(e), "articles": []}


@router.get("/technical/{symbol}")
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
        asset = await get_object_or_404(Asset, symbol__iexact=symbol)
        
        response = await orchestrator.get_market_data(
            data_type='technical_indicators',
            symbol=symbol,
            params={'indicator': indicator, **kwargs}
        )
        
        return {
            "symbol": symbol,
            "indicator": indicator,
            "data": response.data,
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch technical indicators for {symbol}: {e}")
        return {"error": str(e), "symbol": symbol}


@router.get("/fundamentals/{symbol}")
async def get_fundamentals(request, symbol: str):
    """
    Get fundamental data for a stock
    """
    try:
        asset = await get_object_or_404(Asset, symbol__iexact=symbol)
        
        response = await orchestrator.get_market_data(
            data_type='stock_fundamentals',
            symbol=symbol
        )
        
        return {
            "symbol": symbol,
            "data": response.data,
            "source": response.source.value,
            "cached": response.cached
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch fundamentals for {symbol}: {e}")
        return {"error": str(e), "symbol": symbol}


@router.get("/cache/stats", response=Dict[str, Any])
async def get_cache_statistics(request):
    """Get cache statistics"""
    try:
        return await cache_manager.get_statistics()
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        return {"error": str(e)}


@router.post("/cache/clear")
async def clear_cache(request, pattern: Optional[str] = None):
    """Clear cache, optionally by pattern"""
    try:
        if pattern:
            count = await cache_manager.invalidate_pattern(pattern)
            return {"message": f"Invalidated {count} cache entries matching '{pattern}'"}
        else:
            await cache_manager.clear_all()
            return {"message": "All cache cleared"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return {"error": str(e)}


@router.get("/stats", response=MarketStatisticsResponse)
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
        
    except Exception as e:
        logger.error(f"Failed to get market statistics: {e}")
        return {"error": str(e)}


@router.get("/health", response=List[ProviderHealthResponse])
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
        
    except Exception as e:
        logger.error(f"Failed to get provider health: {e}")
        return [{"provider": "unknown", "healthy": False, "error": str(e)}]


@router.post("/prefetch")
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
        
    except Exception as e:
        logger.error(f"Failed to prefetch data: {e}")
        return {"error": str(e)}
