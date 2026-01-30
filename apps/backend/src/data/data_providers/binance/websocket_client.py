"""Binance WebSocket Client for Real-Time Data Streaming"""

import asyncio
import json
import websockets
import orjson
from typing import Set, Dict, Optional, Callable
from datetime import datetime
from collections import defaultdict
import logging

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class BinanceWebSocketClient:
    """
    Binance WebSocket client for real-time crypto data streaming
    
    Supports:
    - Real-time price updates (ticker)
    - Order book depth (partial and diff)
    - Trade execution (real-time trades)
    - Candlestick/kline updates
    
    Binance WebSocket Documentation:
    https://binance-docs.github.io/apidocs/websocket_api/en/
    """
    
    BASE_WS_URL = "wss://stream.binance.com:9443/ws"
    BASE_WS_COMBINED_URL = "wss://stream.binance.com:9443/stream"
    
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.is_connected = False
        self.callbacks: Dict[str, Callable] = {}
        self.reconnect_interval = 5
        self.max_reconnect_attempts = 10
        
        # Stream statistics
        self.stats = {
            'messages_received': 0,
            'last_message_time': None,
            'connection_time': None,
            'reconnect_count': 0
        }
    
    async def connect(self) -> bool:
        """Connect to Binance WebSocket"""
        try:
            logger.info("Connecting to Binance WebSocket...")
            
            self.websocket = await websockets.connect(
                self.BASE_WS_URL,
                ping_interval=20,
                ping_timeout=60,
                close_timeout=10
            )
            
            self.is_connected = True
            self.stats['connection_time'] = datetime.now()
            
            logger.info("Successfully connected to Binance WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Binance WebSocket: {str(e)}")
            self.is_connected = False
            return False
    
    async def connect_combined(self, streams: list) -> bool:
        """
        Connect to combined streams endpoint (for multiple symbols)
        
        Args:
            streams: List of stream names (e.g., ['btcusdt@ticker', 'ethusdt@depth'])
        """
        try:
            stream_path = '/'.join(streams)
            url = f"{self.BASE_WS_COMBINED_URL}?streams={stream_path}"
            
            logger.info(f"Connecting to combined Binance WebSocket: {len(streams)} streams")
            
            self.websocket = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=60,
                close_timeout=10
            )
            
            self.is_connected = True
            self.stats['connection_time'] = datetime.now()
            
            logger.info(f"Successfully connected to combined streams: {len(streams)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to combined Binance WebSocket: {str(e)}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Binance WebSocket"""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Disconnected from Binance WebSocket")
            except Exception as e:
                logger.error(f"Error disconnecting: {str(e)}")
            finally:
                self.is_connected = False
    
    async def subscribe_ticker(self, symbol: str, callback: Optional[Callable] = None):
        """
        Subscribe to real-time ticker updates
        
        Stream format: <symbol>@ticker
        Updates every 1 second
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@ticker"
        
        if callback:
            self.callbacks[f'ticker_{symbol}'] = callback
        
        logger.info(f"Subscribing to ticker: {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['ticker'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to ticker: {str(e)}")
    
    async def subscribe_mini_ticker(self, symbol: str, callback: Optional[Callable] = None):
        """
        Subscribe to mini ticker updates (faster, less data)
        
        Stream format: <symbol>@miniTicker
        Updates every 1 second
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@miniTicker"
        
        if callback:
            self.callbacks[f'mini_ticker_{symbol}'] = callback
        
        logger.info(f"Subscribing to mini ticker: {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['mini_ticker'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to mini ticker: {str(e)}")
    
    async def subscribe_depth(self, symbol: str, level: int = 5, callback: Optional[Callable] = None):
        """
        Subscribe to order book depth updates
        
        Stream formats:
        - <symbol>@depth<levels>  (Partial order book snapshots every second)
        - <symbol>@depth@100ms  (Order book diff updates every 100ms)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            level: Depth levels (5, 10, 20)
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@depth{level}"
        
        if callback:
            self.callbacks[f'depth_{symbol}'] = callback
        
        logger.info(f"Subscribing to depth (level {level}): {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['depth'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to depth: {str(e)}")
    
    async def subscribe_depth_diff(self, symbol: str, update_speed: str = '100ms', callback: Optional[Callable] = None):
        """
        Subscribe to order book diff updates (L3 level data)
        
        Stream format: <symbol>@depth@<speed>
        Speed options: 100ms, 250ms, 500ms, 1000ms
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            update_speed: Update speed (100ms, 250ms, 500ms, 1000ms)
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@depth@{update_speed}"
        
        if callback:
            self.callbacks[f'depth_diff_{symbol}'] = callback
        
        logger.info(f"Subscribing to depth diff ({update_speed}): {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['depth_diff'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to depth diff: {str(e)}")
    
    async def subscribe_trade(self, symbol: str, callback: Optional[Callable] = None):
        """
        Subscribe to real-time trade execution data
        
        Stream format: <symbol>@trade
        Each executed trade is pushed immediately
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@trade"
        
        if callback:
            self.callbacks[f'trade_{symbol}'] = callback
        
        logger.info(f"Subscribing to trades: {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['trade'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to trades: {str(e)}")
    
    async def subscribe_agg_trade(self, symbol: str, callback: Optional[Callable] = None):
        """
        Subscribe to aggregated trade data
        
        Stream format: <symbol>@aggTrade
        Aggregates trades that occur at same time/price
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@aggTrade"
        
        if callback:
            self.callbacks[f'agg_trade_{symbol}'] = callback
        
        logger.info(f"Subscribing to agg trades: {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['agg_trade'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to agg trades: {str(e)}")
    
    async def subscribe_kline(self, symbol: str, interval: str, callback: Optional[Callable] = None):
        """
        Subscribe to real-time candlestick/kline updates
        
        Stream format: <symbol>@kline_<interval>
        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '1m', '5m', '1h', '1d')
            callback: Callback function for updates
        """
        stream_name = f"{symbol.lower()}@kline_{interval}"
        
        if callback:
            self.callbacks[f'kline_{symbol}_{interval}'] = callback
        
        logger.info(f"Subscribing to klines ({interval}): {symbol}")
        
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": self.stats['messages_received'] + 1
                }))
                self.subscriptions['kline'].add(symbol)
            except Exception as e:
                logger.error(f"Failed to subscribe to klines: {str(e)}")
    
    async def unsubscribe(self, stream: str):
        """
        Unsubscribe from a stream
        
        Args:
            stream: Stream name (e.g., 'btcusdt@ticker')
        """
        if self.is_connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "method": "UNSUBSCRIBE",
                    "params": [stream],
                    "id": self.stats['messages_received'] + 1
                }))
                logger.info(f"Unsubscribed from: {stream}")
            except Exception as e:
                logger.error(f"Failed to unsubscribe: {str(e)}")
    
    async def listen(self):
        """
        Listen for WebSocket messages and dispatch to callbacks
        This is a blocking call, should be run in a task
        """
        if not self.websocket:
            logger.error("WebSocket not connected")
            return
        
        try:
            logger.info("Listening for Binance WebSocket messages...")
            
            async for message in self.websocket:
                self.stats['messages_received'] += 1
                self.stats['last_message_time'] = datetime.now()
                
                try:
                    # Parse message (orjson is faster than json)
                    if isinstance(message, str):
                        data = orjson.loads(message)
                    else:
                        data = orjson.loads(message.decode())
                    
                    # Handle combined stream format
                    if 'stream' in data:
                        stream = data['stream']
                        payload = data['data']
                        
                        # Dispatch to callback based on stream type
                        if '@ticker' in stream:
                            symbol = stream.split('@')[0].upper()
                            callback = self.callbacks.get(f'ticker_{symbol}')
                            if callback:
                                await self._run_callback(callback, payload)
                        
                        elif '@miniTicker' in stream:
                            symbol = stream.split('@')[0].upper()
                            callback = self.callbacks.get(f'mini_ticker_{symbol}')
                            if callback:
                                await self._run_callback(callback, payload)
                        
                        elif '@depth' in stream and '@depth@' not in stream:
                            symbol = stream.split('@')[0].upper()
                            callback = self.callbacks.get(f'depth_{symbol}')
                            if callback:
                                await self._run_callback(callback, payload)
                        
                        elif '@depth@' in stream:
                            symbol = stream.split('@')[0].upper()
                            callback = self.callbacks.get(f'depth_diff_{symbol}')
                            if callback:
                                await self._run_callback(callback, payload)
                        
                        elif '@trade' in stream and '@aggTrade' not in stream:
                            symbol = stream.split('@')[0].upper()
                            callback = self.callbacks.get(f'trade_{symbol}')
                            if callback:
                                await self._run_callback(callback, payload)
                        
                        elif '@aggTrade' in stream:
                            symbol = stream.split('@')[0].upper()
                            callback = self.callbacks.get(f'agg_trade_{symbol}')
                            if callback:
                                await self._run_callback(callback, payload)
                        
                        elif '@kline' in stream:
                            parts = stream.split('@kline_')
                            symbol = parts[0].upper()
                            interval = parts[1]
                            callback = self.callbacks.get(f'kline_{symbol}_{interval}')
                            if callback:
                                await self._run_callback(callback, payload)
                    
                    # Handle subscription confirmation
                    elif 'result' in data and data['result'] is None:
                        logger.debug(f"Subscription confirmed: {data.get('id')}")
                
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Binance WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in listen loop: {str(e)}")
            self.is_connected = False
    
    async def _run_callback(self, callback: Callable, data: dict):
        """Run callback function with data"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f"Error in callback: {str(e)}")
    
    async def listen_with_reconnect(self):
        """
        Listen for messages with automatic reconnection
        Will attempt to reconnect on connection failure
        """
        reconnect_count = 0
        
        while reconnect_count < self.max_reconnect_attempts:
            if not self.is_connected:
                logger.info(f"Attempting to reconnect... (attempt {reconnect_count + 1})")
                await asyncio.sleep(self.reconnect_interval)
                
                # Reconnect and resubscribe
                if await self._reconnect():
                    reconnect_count = 0
                    continue
                else:
                    reconnect_count += 1
                    self.stats['reconnect_count'] += 1
            
            try:
                await self.listen()
            except Exception as e:
                logger.error(f"Error in listen: {str(e)}")
                self.is_connected = False
        
        logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
    
    async def _reconnect(self) -> bool:
        """Reconnect to Binance WebSocket and resubscribe"""
        try:
            # Store current subscriptions
            ticker_subs = list(self.subscriptions['ticker'])
            depth_subs = list(self.subscriptions['depth'])
            trade_subs = list(self.subscriptions['trade'])
            
            # Disconnect if connected
            if self.is_connected:
                await self.disconnect()
            
            # Reconnect
            if await self.connect():
                # Resubscribe to all streams
                for symbol in ticker_subs:
                    await self.subscribe_ticker(symbol)
                
                for symbol in depth_subs:
                    await self.subscribe_depth(symbol)
                
                for symbol in trade_subs:
                    await self.subscribe_trade(symbol)
                
                logger.info("Successfully reconnected and resubscribed")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error reconnecting: {str(e)}")
            return False
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        uptime = None
        if self.stats['connection_time']:
            uptime = (datetime.now() - self.stats['connection_time']).total_seconds()
        
        return {
            'is_connected': self.is_connected,
            'messages_received': self.stats['messages_received'],
            'last_message_time': self.stats['last_message_time'],
            'uptime_seconds': uptime,
            'reconnect_count': self.stats['reconnect_count'],
            'subscriptions': {
                k: len(v) for k, v in self.subscriptions.items()
            }
        }


# Singleton instance
_binance_ws_client: Optional[BinanceWebSocketClient] = None


def get_binance_ws_client() -> BinanceWebSocketClient:
    """Get singleton Binance WebSocket client instance"""
    global _binance_ws_client
    
    if _binance_ws_client is None:
        _binance_ws_client = BinanceWebSocketClient()
    
    return _binance_ws_client