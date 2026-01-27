"""
Binance WebSocket Background Tasks
Real-time crypto data streaming via WebSocket
"""
import dramatiq
import asyncio
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries
from datetime import datetime
import logging
from typing import List, Dict, Optional

from data.data_providers.binance.websocket_client import get_binance_ws_client
from data.data_providers.binance.order_book_service import get_binance_order_book_service
from data.data_providers.binance.trade_service import get_binance_trade_service
from utils.helpers.logger.logger import get_logger
from channels.layers import get_channel_layer

logger = get_logger(__name__)

# Initialize Dramatiq broker
broker = StubBroker()
broker.add_middleware(AgeLimit(max_age=1000 * 60 * 60))
broker.add_middleware(TimeLimit(limit=1000 * 60 * 30))
broker.add_middleware(Retries(max_retries=3))

# Popular crypto pairs for real-time streaming
POPULAR_CRYPTO_PAIRS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
    'DOGEUSDT', 'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'LTCUSDT',
    'AVAXUSDT', 'LINKUSDT', 'ATOMUSDT', 'XLMUSDT', 'UNIUSDT'
]

# Channel layer for broadcasting to frontend
channel_layer = get_channel_layer()


@dramatiq.actor(broker=broker, max_retries=3)
async def start_binance_websocket_stream(symbols: Optional[List[str]] = None) -> dict:
    """
    Start Binance WebSocket stream for real-time data
    
    Streams:
    - Mini ticker updates (fast price updates)
    - Trade execution data
    - Order book depth (optional)
    
    Args:
        symbols: List of trading pairs (default: POPULAR_CRYPTO_PAIRS)
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTO_PAIRS
        
        logger.info(f"Starting Binance WebSocket stream for {len(symbols)} symbols")
        
        # Get WebSocket client
        ws_client = get_binance_ws_client()
        
        # Connect to WebSocket
        if not ws_client.is_connected:
            success = await ws_client.connect()
            if not success:
                raise Exception("Failed to connect to Binance WebSocket")
        
        # Subscribe to mini ticker updates for all symbols
        for symbol in symbols:
            await ws_client.subscribe_mini_ticker(
                symbol,
                callback=lambda data: _broadcast_ticker_update(symbol, data)
            )
        
        # Subscribe to trade updates
        trade_service = get_binance_trade_service()
        for symbol in symbols:
            await trade_service.subscribe_agg_trades(
                symbol,
                callback=lambda data: _broadcast_trade_update(symbol, data)
            )
        
        # Start listening in background
        asyncio.create_task(ws_client.listen_with_reconnect())
        
        logger.info(f"Binance WebSocket stream started for {len(symbols)} symbols")
        
        return {
            'source': 'binance_websocket',
            'status': 'started',
            'symbols': symbols,
            'count': len(symbols),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error starting Binance WebSocket stream: {str(e)}")
        return {'error': str(e)}


async def _broadcast_ticker_update(symbol: str, data: dict):
    """Broadcast ticker update to Django Channels"""
    try:
        # Parse mini ticker data
        price = float(data.get('c', 0))  # Current close price
        open_price = float(data.get('o', 0))
        high = float(data.get('h', 0))
        low = float(data.get('l', 0))
        volume = float(data.get('v', 0))
        quote_volume = float(data.get('q', 0))
        change = float(data.get('p', 0))  # Price change
        change_percent = float(data.get('P', 0))  # Price change percent
        
        # Create price update message
        message = {
            'type': 'price_update',
            'symbol': symbol,
            'data': {
                'price': price,
                'open': open_price,
                'high': high,
                'low': low,
                'volume': volume,
                'quote_volume': quote_volume,
                'change': change,
                'change_percent': change_percent,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Broadcast to symbol channel
        await channel_layer.group_send(
            f'asset_{symbol}_prices',
            {
                'type': 'price_update',
                'message': message
            }
        )
        
        logger.debug(f"Broadcasted ticker update for {symbol}: {price}")
    
    except Exception as e:
        logger.error(f"Error broadcasting ticker update: {str(e)}")


async def _broadcast_trade_update(symbol: str, data: dict):
    """Broadcast trade update to Django Channels"""
    try:
        # Parse trade data
        price = float(data.get('p', 0))
        quantity = float(data.get('q', 0))
        time = data.get('T', 0)
        is_buyer_maker = data.get('m', False)
        
        # Create trade message
        message = {
            'type': 'trade_update',
            'symbol': symbol,
            'data': {
                'price': price,
                'quantity': quantity,
                'value': price * quantity,
                'time': datetime.fromtimestamp(time / 1000).isoformat(),
                'side': 'sell' if is_buyer_maker else 'buy',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Broadcast to trade channel
        await channel_layer.group_send(
            f'asset_{symbol}_trades',
            {
                'type': 'trade_update',
                'message': message
            }
        )
        
        logger.debug(f"Broadcasted trade update for {symbol}: {quantity} @ {price}")
    
    except Exception as e:
        logger.error(f"Error broadcasting trade update: {str(e)}")


@dramatiq.actor(broker=broker, max_retries=3)
async def start_binance_order_book_stream(symbols: Optional[List[str]] = None, level: int = 20) -> dict:
    """
    Start Binance order book stream for L2/L3 depth data
    
    Args:
        symbols: List of trading pairs
        level: Depth levels (5, 10, 20, 50, 100)
    """
    try:
        if symbols is None:
            symbols = POPULAR_CRYPTO_PAIRS[:10]  # Top 10 for order book
        
        logger.info(f"Starting Binance order book stream for {len(symbols)} symbols (level {level})")
        
        # Get order book service
        order_book_service = get_binance_order_book_service()
        
        # Initialize order books for all symbols
        for symbol in symbols:
            await order_book_service.initialize_depth(symbol, level)
        
        logger.info(f"Order book stream started for {len(symbols)} symbols")
        
        return {
            'source': 'binance_order_book',
            'status': 'started',
            'symbols': symbols,
            'level': level,
            'count': len(symbols),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error starting Binance order book stream: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=0)
async def get_order_book_snapshot(symbol: str, levels: int = 10) -> Optional[dict]:
    """
    Get current order book snapshot for a symbol
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        levels: Number of depth levels to return
    
    Returns:
        Order book data with bids/asks
    """
    try:
        order_book_service = get_binance_order_book_service()
        
        order_book = await order_book_service.get_order_book(symbol, levels)
        
        if order_book:
            logger.debug(f"Retrieved order book for {symbol}: {len(order_book['bids'])} bids, {len(order_book['asks'])} asks")
        else:
            logger.warning(f"No order book found for {symbol}")
        
        return order_book
    
    except Exception as e:
        logger.error(f"Error getting order book snapshot for {symbol}: {str(e)}")
        return None


@dramatiq.actor(broker=broker, max_retries=0)
async def get_trade_stats(symbol: str) -> Optional[dict]:
    """
    Get trade statistics for a symbol
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
    
    Returns:
        Trade statistics including buy/sell ratio, VWAP, etc.
    """
    try:
        trade_service = get_binance_trade_service()
        
        stats = await trade_service.get_trade_stats(symbol)
        
        if stats:
            logger.debug(f"Retrieved trade stats for {symbol}: {stats['total_trades']} trades")
        else:
            logger.warning(f"No trade stats found for {symbol}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting trade stats for {symbol}: {str(e)}")
        return None


@dramatiq.actor(broker=broker, max_retries=0)
async def get_trade_flow(symbol: str, window: int = 100) -> Optional[dict]:
    """
    Analyze trade flow direction for a symbol
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        window: Number of recent trades to analyze
    
    Returns:
        Trade flow analysis with direction indicator
    """
    try:
        trade_service = get_binance_trade_service()
        
        flow = await trade_service.get_trade_flow(symbol, window)
        
        if flow:
            logger.debug(f"Trade flow for {symbol}: {flow['direction']} (ratio: {flow['buy_ratio_volume']:.2f})")
        else:
            logger.warning(f"No trade flow found for {symbol}")
        
        return flow
    
    except Exception as e:
        logger.error(f"Error getting trade flow for {symbol}: {str(e)}")
        return None


@dramatiq.actor(broker=broker, max_retries=0)
async def get_large_trades(symbol: str, threshold: float = 5.0, limit: int = 20) -> List[dict]:
    """
    Find unusually large trades (whale activity)
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        threshold: Multiplier of average trade size
        limit: Maximum number of trades to return
    
    Returns:
        List of large trades
    """
    try:
        trade_service = get_binance_trade_service()
        
        large_trades = await trade_service.get_large_trades(symbol, threshold, limit)
        
        if large_trades:
            logger.info(f"Found {len(large_trades)} large trades for {symbol}")
        
        return large_trades
    
    except Exception as e:
        logger.error(f"Error finding large trades for {symbol}: {str(e)}")
        return []


@dramatiq.actor(broker=broker, max_retries=0)
async def get_volume_profile(symbol: str, interval: str = '1h', bins: int = 50) -> Optional[dict]:
    """
    Calculate volume profile for a symbol
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        interval: Time interval for aggregation
        bins: Number of price bins
    
    Returns:
        Volume profile with price levels and volumes
    """
    try:
        trade_service = get_binance_trade_service()
        
        volume_profile = await trade_service.get_volume_profile(symbol, interval, bins)
        
        if volume_profile:
            logger.debug(f"Calculated volume profile for {symbol}: {bins} bins")
        
        return volume_profile
    
    except Exception as e:
        logger.error(f"Error calculating volume profile for {symbol}: {str(e)}")
        return None


@dramatiq.actor(broker=broker, max_retries=3)
async def get_binance_websocket_stats() -> dict:
    """
    Get Binance WebSocket connection statistics
    
    Returns:
        Connection stats including uptime, message count, etc.
    """
    try:
        ws_client = get_binance_ws_client()
        stats = ws_client.get_stats()
        
        logger.info(f"Binance WebSocket stats: connected={stats['is_connected']}, messages={stats['messages_received']}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {str(e)}")
        return {'error': str(e)}


@dramatiq.actor(broker=broker, max_retries=3)
async def stop_binance_websocket() -> dict:
    """
    Stop Binance WebSocket stream
    
    Disconnects from all Binance WebSocket connections
    """
    try:
        logger.info("Stopping Binance WebSocket stream...")
        
        # Stop WebSocket client
        ws_client = get_binance_ws_client()
        await ws_client.disconnect()
        
        # Stop services
        order_book_service = get_binance_order_book_service()
        await order_book_service.stop()
        
        trade_service = get_binance_trade_service()
        await trade_service.stop()
        
        logger.info("Binance WebSocket stream stopped")
        
        return {
            'source': 'binance_websocket',
            'status': 'stopped',
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error stopping Binance WebSocket: {str(e)}")
        return {'error': str(e)}


# Scheduler tasks (to be called from Celery beat)
@dramatiq.actor(broker=broker, max_retries=3)
async def periodic_websocket_health_check() -> dict:
    """
    Periodic health check for WebSocket connections
    Runs every 5 minutes
    """
    try:
        logger.info("Running WebSocket health check...")
        
        ws_client = get_binance_ws_client()
        stats = ws_client.get_stats()
        
        is_healthy = stats['is_connected']
        
        # Reconnect if disconnected
        if not is_healthy:
            logger.warning("WebSocket disconnected, attempting to reconnect...")
            ws_client.reconnect_interval = 1
            success = await ws_client.connect()
            if success:
                logger.info("WebSocket reconnected successfully")
            else:
                logger.error("Failed to reconnect WebSocket")
        
        return {
            'source': 'binance_websocket',
            'type': 'health_check',
            'healthy': is_healthy,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in WebSocket health check: {str(e)}")
        return {'error': str(e), 'healthy': False}