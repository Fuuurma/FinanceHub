import asyncio
import json
from typing import Optional, Set, Dict
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.utils import timezone
from django.core.cache import cache

from utils.helpers.logger.logger import get_logger
from utils.services.realtime_stream_manager import get_real_time_stream_manager

logger = get_logger(__name__)


class MarketDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope['url_route']['kwargs'].get('symbol', 'general')
        self.stream_type = self.scope['url_route']['kwargs'].get('stream_type', 'price')
        
        self.room_group_name = f"market_{self.stream_type}_{self.symbol}"
        
        await self.accept()
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        self.stream_manager = get_real_time_stream_manager()
        
        if not self.stream_manager.running:
            await self.stream_manager.start()
        
        await self.stream_manager.subscribe(
            f"{self.stream_type}_{self.symbol}",
            self._handle_stream_data
        )
        
        logger.info(f"WebSocket connected: {self.room_group_name}")
        
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'symbol': self.symbol,
            'stream_type': self.stream_type,
            'timestamp': timezone.now().isoformat()
        }))
        
        if self.stream_type == 'price':
            await self._send_initial_price()
        elif self.stream_type == 'orderbook':
            await self._send_initial_order_book()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        if self.stream_manager:
            await self.stream_manager.unsubscribe(
                f"{self.stream_type}_{self.symbol}",
                self._handle_stream_data
            )
        
        logger.info(f"WebSocket disconnected: {self.room_group_name} (code: {close_code})")
        
        raise StopConsumer()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'subscribe':
                await self._handle_subscribe(data)
            elif action == 'unsubscribe':
                await self._handle_unsubscribe(data)
            elif action == 'ping':
                await self._handle_ping()
            else:
                logger.warning(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await self._send_error('Invalid JSON')
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error receiving message: {e}")
            await self._send_error(str(e))
    
    async def _handle_subscribe(self, data):
        symbol = data.get('symbol', self.symbol)
        stream_type = data.get('stream_type', self.stream_type)
        
        if symbol != self.symbol or stream_type != self.stream_type:
            await self._send_error('Cannot change subscription')
            return
        
        logger.debug(f"Subscription confirmed for {stream_type}_{symbol}")
    
    async def _handle_unsubscribe(self, data):
        logger.debug(f"Unsubscribe request for {self.symbol}")
        
        await self.close()
    
    async def _handle_ping(self):
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def _handle_stream_data(self, data):
        try:
            message = {
                'type': self.stream_type,
                'data': data,
                'timestamp': timezone.now().isoformat()
            }
            
            await self.send(text_data=json.dumps(message))
            
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error sending stream data: {e}")
    
    async def _send_initial_price(self):
        price_data = await self.stream_manager.get_real_time_price(self.symbol)
        
        if price_data:
            await self.send(text_data=json.dumps({
                'type': 'price',
                'data': price_data,
                'timestamp': timezone.now().isoformat()
            }))
    
    async def _send_initial_order_book(self):
        order_book = await self.stream_manager.get_order_book(self.symbol)
        
        if order_book:
            await self.send(text_data=json.dumps({
                'type': 'orderbook',
                'data': order_book,
                'timestamp': timezone.now().isoformat()
            }))
    
    async def _send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def market_data(self, event):
        data = event.get('data')
        
        try:
            await self.send(text_data=json.dumps(data))
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error sending market data: {e}")


class MultiSymbolConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope.get('user_id', 'anonymous')
        self.subscribed_symbols: Set[str] = set()
        
        await self.accept()
        
        self.stream_manager = get_real_time_stream_manager()
        
        if not self.stream_manager.running:
            await self.stream_manager.start()
        
        logger.info(f"Multi-symbol WebSocket connected: user={self.user_id}")
        
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        for symbol in self.subscribed_symbols:
            await self.stream_manager.unsubscribe(
                f"price_{symbol}",
                self._handle_stream_data
            )
        
        logger.info(f"Multi-symbol WebSocket disconnected: user={self.user_id}")
        
        raise StopConsumer()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'subscribe':
                await self._handle_subscribe(data)
            elif action == 'unsubscribe':
                await self._handle_unsubscribe(data)
            elif action == 'ping':
                await self._handle_ping()
            elif action == 'list':
                await self._handle_list()
            else:
                logger.warning(f"Unknown action: {action}")
                await self._send_error(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await self._send_error('Invalid JSON')
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error receiving message: {e}")
            await self._send_error(str(e))
    
    async def _handle_subscribe(self, data):
        symbols = data.get('symbols', [])
        stream_type = data.get('stream_type', 'price')
        
        if not isinstance(symbols, list):
            await self._send_error('symbols must be an array')
            return
        
        for symbol in symbols:
            if symbol not in self.subscribed_symbols:
                await self.stream_manager.subscribe(
                    f"{stream_type}_{symbol}",
                    self._handle_stream_data
                )
                self.subscribed_symbols.add(symbol)
        
        await self.send(text_data=json.dumps({
            'type': 'subscription',
            'action': 'subscribed',
            'symbols': list(self.subscribed_symbols),
            'stream_type': stream_type,
            'timestamp': timezone.now().isoformat()
        }))
        
        logger.info(f"Subscribed to symbols: {list(self.subscribed_symbols)}")
    
    async def _handle_unsubscribe(self, data):
        symbols = data.get('symbols', [])
        
        if not isinstance(symbols, list):
            await self._send_error('symbols must be an array')
            return
        
        for symbol in symbols:
            if symbol in self.subscribed_symbols:
                await self.stream_manager.unsubscribe(
                    f"price_{symbol}",
                    self._handle_stream_data
                )
                self.subscribed_symbols.discard(symbol)
        
        await self.send(text_data=json.dumps({
            'type': 'subscription',
            'action': 'unsubscribed',
            'symbols': symbols,
            'remaining': list(self.subscribed_symbols),
            'timestamp': timezone.now().isoformat()
        }))
    
    async def _handle_ping(self):
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def _handle_list(self):
        await self.send(text_data=json.dumps({
            'type': 'list',
            'subscribed': list(self.subscribed_symbols),
            'timestamp': timezone.now().isoformat()
        }))
    
    async def _handle_stream_data(self, data):
        try:
            symbol = data.get('symbol', 'UNKNOWN')
            
            message = {
                'type': 'data',
                'symbol': symbol,
                'data': data,
                'timestamp': timezone.now().isoformat()
            }
            
            await self.send(text_data=json.dumps(message))
            
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error sending stream data: {e}")
    
    async def _send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        }))


class NewsStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        self.category = self.scope['url_route']['kwargs'].get('category', 'general')
        self.room_group_name = f"news_{self.category}"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        logger.info(f"News WebSocket connected: {self.category}")
        
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'category': self.category,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        logger.info(f"News WebSocket disconnected: {self.category}")
        
        raise StopConsumer()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
                
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error receiving message: {e}")
    
    async def news_update(self, event):
        data = event.get('data')
        
        try:
            await self.send(text_data=json.dumps(data))
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error sending news update: {e}")
