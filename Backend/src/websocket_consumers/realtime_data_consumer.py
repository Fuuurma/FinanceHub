import asyncio
import orjson
from typing import Dict, Set, Optional, Any
from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from utils.helpers.logger.logger import get_logger
from utils.services.data_orchestrator import get_data_orchestrator
from utils.services.cache_manager import get_cache_manager

logger = get_logger(__name__)


class RealTimeDataStreamConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time market data streaming
    Handles subscriptions to price updates, trades, and order books
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id: Optional[str] = None
        self.subscriptions: Set[str] = set()
        self.orchestrator = get_data_orchestrator()
        self.cache_manager = get_cache_manager()
        self._tasks: Set[asyncio.Task] = set()

    async def connect(self):
        await self.accept()
        
        user_id = self.scope.get('user_id')
        if user_id:
            self.user_id = str(user_id)
        else:
            self.user_id = 'anonymous'
        
        logger.info(f"WebSocket connected for user {self.user_id}")
        
        # Register connection in cache
        await self._register_connection()

    async def disconnect(self, close_code):
        await self._unregister_connection()
        
        # Cancel all running tasks
        for task in self._tasks:
            task.cancel()
        
        logger.info(f"WebSocket disconnected for user {self.user_id} with code {close_code}")

    async def receive_json(self, content: dict):
        message_type = content.get('type')
        
        try:
            if message_type == 'subscribe':
                await self._handle_subscribe(content)
            elif message_type == 'unsubscribe':
                await self._handle_unsubscribe(content)
            elif message_type == 'ping':
                await self._handle_ping(content)
            else:
                await self._send_error(f"Unknown message type: {message_type}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error(f"Internal error: {str(e)}")

    async def _handle_subscribe(self, content: dict):
        symbols = content.get('symbols', [])
        data_types = content.get('data_types', ['price'])
        
        for symbol in symbols:
            symbol = symbol.upper()
            
            for data_type in data_types:
                subscription_key = f"{symbol}:{data_type}"
                
                if subscription_key not in self.subscriptions:
                    self.subscriptions.add(subscription_key)
                    
                    # Start streaming task for this subscription
                    task = asyncio.create_task(
                        self._stream_data(symbol, data_type)
                    )
                    self._tasks.add(task)
                    
                    # Send initial data
                    await self._send_initial_data(symbol, data_type)
        
        await self._update_connections_cache()
        
        await self.send_json({
            'type': 'subscription_ack',
            'subscriptions': list(self.subscriptions),
            'timestamp': datetime.utcnow().isoformat()
        })

    async def _handle_unsubscribe(self, content: dict):
        symbols = content.get('symbols', [])
        data_types = content.get('data_types', [])
        
        to_remove = set()
        
        for symbol in symbols:
            symbol = symbol.upper()
            
            for data_type in data_types:
                subscription_key = f"{symbol}:{data_type}"
                
                if subscription_key in self.subscriptions:
                    self.subscriptions.discard(subscription_key)
                    to_remove.add(subscription_key)
        
        # Cancel tasks for removed subscriptions
        for task in list(self._tasks):
            if task.done():
                self._tasks.discard(task)
        
        await self._update_connections_cache()
        
        await self.send_json({
            'type': 'unsubscribe_ack',
            'removed_subscriptions': list(to_remove),
            'timestamp': datetime.utcnow().isoformat()
        })

    async def _handle_ping(self, content: dict):
        await self.send_json({
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        })

    async def _stream_data(self, symbol: str, data_type: str):
        """
        Stream real-time data for a symbol
        Runs in a continuous loop until unsubscribed
        """
        subscription_key = f"{symbol}:{data_type}"
        interval = 2.0 if data_type == 'price' else 5.0
        
        while subscription_key in self.subscriptions:
            try:
                response = await self.orchestrator.get_market_data(
                    data_type=f"{data_type}_price" if data_type == 'price' else data_type,
                    symbol=symbol
                )
                
                if response and response.data:
                    message = {
                        'type': 'data_update',
                        'symbol': symbol,
                        'data_type': data_type,
                        'data': response.data,
                        'source': response.source.value,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    await self.send_json(message)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error streaming {data_type} for {symbol}: {e}")
                await asyncio.sleep(interval)

    async def _send_initial_data(self, symbol: str, data_type: str):
        """Send initial data snapshot upon subscription"""
        try:
            response = await self.orchestrator.get_market_data(
                data_type=f"{data_type}_price" if data_type == 'price' else data_type,
                symbol=symbol
            )
            
            if response and response.data:
                message = {
                    'type': 'initial_data',
                    'symbol': symbol,
                    'data_type': data_type,
                    'data': response.data,
                    'source': response.source.value,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self.send_json(message)
        except Exception as e:
            logger.error(f"Error sending initial data for {symbol}: {e}")

    async def _send_error(self, message: str):
        await self.send_json({
            'type': 'error',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def _register_connection(self):
        """Register this connection in cache"""
        try:
            connections_key = f"ws_connections:{self.user_id}"
            connection_info = {
                'channel_name': self.channel_name,
                'subscriptions': list(self.subscriptions),
                'connected_at': datetime.utcnow().isoformat()
            }
            
            await self.cache_manager.set(
                'ws_connections',
                connections_key,
                connection_info,
                ttl=3600
            )
        except Exception as e:
            logger.error(f"Error registering connection: {e}")

    async def _unregister_connection(self):
        """Unregister this connection from cache"""
        try:
            connections_key = f"ws_connections:{self.user_id}"
            await self.cache_manager.delete('ws_connections', connections_key)
        except Exception as e:
            logger.error(f"Error unregistering connection: {e}")

    async def _update_connections_cache(self):
        """Update subscriptions in cache"""
        try:
            connections_key = f"ws_connections:{self.user_id}"
            
            # Get current connection info
            current = await self.cache_manager.get('ws_connections', connections_key)
            
            if current:
                current['subscriptions'] = list(self.subscriptions)
                current['last_updated'] = datetime.utcnow().isoformat()
                
                await self.cache_manager.set(
                    'ws_connections',
                    connections_key,
                    current,
                    ttl=3600
                )
        except Exception as e:
            logger.error(f"Error updating connections cache: {e}")
