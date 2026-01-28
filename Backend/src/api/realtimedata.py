"""
Real-Time Data API
Provides endpoints for real-time price updates and trading data streams
"""
from typing import List, Optional, Dict
from decimal import Decimal
from ninja import Router
from pydantic import BaseModel, Field
from django.utils import timezone
from datetime import timedelta
import asyncio
from ratelimit.decorators import ratelimit
from django.core.cache import cache

from utils.services.data_orchestrator import get_data_orchestrator
from utils.services.cache_manager import get_cache_manager
from utils.helpers.logger.logger import get_logger
from utils.constants.api import RATE_LIMIT_REALTIME, CACHE_TTL_SHORT

logger = get_logger(__name__)

router = Router()


class RealTimePriceUpdate(BaseModel):
    """
    Real-time price update for a specific symbol
    """
    symbol: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int
    timestamp: str
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    spread: Optional[Decimal] = None
    high_52w: Optional[Decimal] = None
    low_52w: Optional[Decimal] = None
    open: Optional[Decimal] = None
    close: Optional[Decimal] = None
    last_update: str
    source: str


class BatchPriceUpdateRequest(BaseModel):
    symbols: List[str]
    include_volume: bool = False
    include_spread: bool = False
    include_orderbook: bool = False


class BatchPriceUpdatesResponse(BaseModel):
    updates: List[RealTimePriceUpdate]
    total_symbols: int
    fetched_at: str
    source: str


class RecentTrade(BaseModel):
    trade_id: str
    symbol: str
    price: Decimal
    quantity: int
    trade_type: str
    timestamp: str
    exchange: str
    is_buy: bool
    maker: bool


class RecentTradesRequest(BaseModel):
    symbol: str
    limit: int = Field(default=20, ge=1, le=100)
    include_makers: bool = False


class RecentTradesResponse(BaseModel):
    symbol: str
    trades: List[RecentTrade]
    count: int
    volume_24h: Optional[int] = None
    avg_trade_size: Optional[Decimal] = None
    fetched_at: str
    source: str


class OrderBookLevel(BaseModel):
    price: Decimal
    volume: int
    total_size: int
    is_spread: bool
    spread: Optional[Decimal] = None
    timestamp: str


class OrderBookResponse(BaseModel):
    symbol: str
    levels: List[OrderBookLevel]
    mid_price: Optional[Decimal] = None
    spread: Decimal
    depth: int
    timestamp: str
    source: str


class WebSocketConnectionInfo(BaseModel):
    connected: bool
    last_heartbeat: str
    subscriptions: List[str]
    connection_time: str
    ping_ms: int


@router.get("/price/{symbol}", response=RealTimePriceUpdate)
async def get_realtime_price(request, symbol: str, source: str = 'market'):
    """
    Get real-time price for a specific symbol

    Fetches the most recent price data from cache or provider
    """
    orchestrator = get_data_orchestrator()
    cache_manager = get_cache_manager()

    try:
        # Try cache first
        cache_key = f"realtime_price:{symbol.upper()}:{source}"
        cached = await cache_manager.get('realtime_data', cache_key)
        
        if cached:
            logger.info(f"Returning cached price for {symbol} from {source}")
            return cached

        # Determine data type based on symbol
        data_type = 'crypto_price' if symbol.upper().endswith('USDT') or symbol.upper().endswith('BTC') else 'stock_price'

        # Fetch from data orchestrator
        response = await orchestrator.get_market_data(
            data_type=data_type,
            symbol=symbol.upper()
        )

        if not response or not response.data:
            return {
                'symbol': symbol.upper(),
                'error': 'Price not available'
            }

        price_data = response.data
        
        return RealTimePriceUpdate(
            symbol=symbol.upper(),
            price=Decimal(str(price_data.get('price', 0))),
            change=Decimal(str(price_data.get('change', 0))),
            change_percent=Decimal(str(price_data.get('change_percent', 0))),
            volume=price_data.get('volume', 0),
            timestamp=price_data.get('timestamp', timezone.now().isoformat()),
            source=source,
            bid=Decimal(str(price_data.get('bid', 0))),
            ask=Decimal(str(price_data.get('ask', 0))),
            spread=Decimal(str(price_data.get('spread', 0))),
            high_52w=Decimal(str(price_data.get('high_52w', 0))),
            low_52w=Decimal(str(price_data.get('low_52w', 0))),
            open=Decimal(str(price_data.get('open', 0))),
            close=Decimal(str(price_data.get('close', 0))),
            last_update=timezone.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error fetching realtime price for {symbol}: {e}")
        return {
            'symbol': symbol.upper(),
            'error': str(e)
        }


@router.post("/prices/batch", response=BatchPriceUpdatesResponse)
async def get_batch_prices(request, data: BatchPriceUpdateRequest):
    """
    Get real-time prices for multiple symbols

    Efficient batch endpoint for dashboard and watchlist
    """
    orchestrator = get_data_orchestrator()
    cache_manager = get_cache_manager()
    
    try:
        results = []
        tasks = []

        for symbol in data.symbols:
            async def fetch_price():
                cache_key = f"realtime_price:{symbol}:market"
                cached = await cache_manager.get('realtime_data', cache_key)

                if cached:
                    results.append(cached)
                    return

                data_type = 'crypto_price' if symbol.upper().endswith('USDT') or symbol.upper().endswith('BTC') else 'stock_price'
                response = await orchestrator.get_market_data(
                    data_type=data_type,
                    symbol=symbol
                )

                if not response or not response.data:
                    results.append({
                        'symbol': symbol,
                        'error': 'Price not available'
                    })
                    return

                price_data = response.data
                
                if not price_data:
                    results.append({
                        'symbol': symbol,
                        'error': 'Price not available'
                    })
                    return
                
                update = RealTimePriceUpdate(
                    symbol=symbol,
                    price=Decimal(str(price_data.get('price', 0))),
                    change=Decimal(str(price_data.get('change', 0))),
                    change_percent=Decimal(str(price_data.get('change_percent', 0))),
                    volume=price_data.get('volume', 0),
                    timestamp=timezone.now().isoformat(),
                    source='market',
                    last_update=timezone.now().isoformat()
                )
                
                # Cache the result with 5 second TTL
                await cache_manager.set(
                    'realtime_data',
                    cache_key,
                    value=update,
                    ttl=5
                )
                results.append(update)
            
        await asyncio.gather(*tasks)
        
        return BatchPriceUpdatesResponse(
            updates=[u for u in results if 'symbol' in u],
            total_symbols=len(data.symbols),
            fetched_at=timezone.now().isoformat(),
            source='market'
        )
        
    except Exception as e:
        logger.error(f"Error fetching batch prices: {e}")
        return BatchPriceUpdatesResponse(
            updates=[],
            total_symbols=len(data.symbols),
            fetched_at= timezone.now().isoformat(),
            source='market',
        )


@router.get("/trades/{symbol}", response=RecentTradesResponse)
async def get_recent_trades(request, symbol: str, limit: int = 20):
    """
    Get recent trades for a symbol

    Provides trade flow data for high-frequency trading
    """
    orchestrator = get_data_orchestrator()

    try:
        response = await orchestrator.get_market_data(
            data_type='trades',
            symbol=symbol.upper(),
            params={'limit': limit}
        )

        if not response or not response.data:
            trades_data = {'trades': [], 'volume_24h': None}
        else:
            trades_data = response.data
        
        trades = [
            RecentTrade(
                trade_id=t.get('trade_id', ''),
                symbol=symbol.upper(),
                price=Decimal(str(t.get('price', 0))),
                quantity=t.get('quantity', 0),
                trade_type=t.get('side', 'unknown'),
                timestamp=t.get('timestamp', timezone.now().isoformat()),
                exchange=t.get('exchange', 'Unknown'),
                is_buy=t.get('side', '').lower() == 'buy',
                maker=t.get('maker', False)
            )
            for t in trades_data.get('trades', [])[:limit]
        ]
        
        # Calculate volume metrics
        volume_24h = trades_data.get('volume_24h', None)
        avg_trade_size = None
        if trades:
            quantities = [t.quantity for t in trades if t.quantity > 0]
            avg_trade_size = Decimal(str(sum(quantities) / len(quantities))) if quantities else None
        
        return RecentTradesResponse(
            symbol=symbol.upper(),
            trades=trades,
            count=len(trades),
            volume_24h=volume_24h,
            avg_trade_size=avg_trade_size,
            fetched_at=timezone.now().isoformat(),
            source='market_data'
        )
        
    except Exception as e:
        logger.error(f"Error fetching recent trades for {symbol}: {e}")
        return RecentTradesResponse(
            symbol=symbol.upper(),
            trades=[],
            count=0,
            volume_24h=None,
            avg_trade_size=None,
            fetched_at=timezone.now().isoformat(),
            source='market_data'
        )


@router.get("/orderbook/{symbol}", response=OrderBookResponse)
async def get_orderbook(
    request,
    symbol: str,
    depth: int = 10
):
    """
    Get order book for a symbol

    Returns current bid/ask levels with volume at each level
    """
    orchestrator = get_data_orchestrator()

    try:
        response = await orchestrator.get_market_data(
            data_type='order_book',
            symbol=symbol.upper(),
            params={'depth': depth}
        )

        if not response or not response.data:
            orderbook = {'levels': [], 'mid_price': None, 'spread': '0', 'depth': 0}
        else:
            orderbook = response.data
        
        levels = [
            OrderBookLevel(
                price=Decimal(str(level.get('price', 0))),
                volume=level.get('volume', 0),
                total_size=level.get('total_size', 0),
                is_spread=level.get('is_spread', False),
                spread=Decimal(str(level.get('spread', 0))) if level.get('spread') else None,
                timestamp=level.get('timestamp', timezone.now().isoformat())
            )
            for level in orderbook.get('levels', [])
        ]
        
        mid_price = orderbook.get('mid_price', None)
        spread = Decimal(str(orderbook.get('spread', 0))) if orderbook.get('spread') else Decimal('0')
        
        return OrderBookResponse(
            symbol=symbol.upper(),
            levels=levels,
            mid_price=mid_price,
            spread=spread,
            depth=orderbook.get('depth', len(levels)),
            timestamp=timezone.now().isoformat(),
            source='market_data'
        )
        
    except Exception as e:
        logger.error(f"Error fetching orderbook for {symbol}: {e}")
        return OrderBookResponse(
            symbol=symbol.upper(),
            levels=[],
            mid_price=None,
            spread=Decimal('0'),
            depth=0,
            timestamp=timezone.now().isoformat(),
            source='market_data'
        )


@router.get("/connection-info", response=WebSocketConnectionInfo)
async def get_websocket_connection_info(request, user_id: Optional[str] = None):
    """
    Get WebSocket connection info for the current user
    """
    try:
        # Check active connections
        cache_manager = get_cache_manager()
        
        connections_key = f"ws_connections:{user_id or 'anonymous'}"
        connections = await cache_manager.get('ws_connections', connections_key)
        
        return WebSocketConnectionInfo(
            connected=connections is not None and len(connections) > 0,
            last_heartbeat=timezone.now().isoformat(),
            subscriptions=list(connections.keys()) if connections else [],
            connection_time=timezone.now().isoformat() if connections else '',
            ping_ms=50
        )
        
    except Exception as e:
        logger.error(f"Error getting WebSocket connection info: {e}")
        return WebSocketConnectionInfo(
            connected=False,
            last_heartbeat=timezone.now().isoformat(),
            subscriptions=[],
            connection_time=timezone.now().isoformat(),
            ping_ms=50
        )
