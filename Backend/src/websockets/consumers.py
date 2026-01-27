"""
WebSocket Consumers for Real-Time Price Streaming
Uses Django Channels for WebSocket support
"""
import json
import orjson
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import UserLazyAuthenticator
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from datetime import datetime
import logging
import asyncio

from assets.models.asset import Asset
from assets.models.historic.prices import AssetPricesHistoric
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)
User = get_user_model()


# Constants
MAX_SUBSCRIPTIONS_PER_USER = 100
PING_INTERVAL = 30  # seconds
CONNECTION_TIMEOUT = 300  # seconds
PRICE_UPDATE_INTERVAL = 5  # seconds


class PriceUpdateMessage:
    """Standardized price update message structure"""
    
    @staticmethod
    def create(symbol: str, price_data: dict) -> dict:
        """Create a price update message"""
        return {
            'type': 'price_update',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'price': price_data.get('close', price_data.get('price', 0)),
                'open': price_data.get('open', 0),
                'high': price_data.get('high', 0),
                'low': price_data.get('low', 0),
                'volume': price_data.get('volume', 0),
                'change': price_data.get('change', 0),
                'change_percent': price_data.get('change_percent', 0),
            }
        }
    
    @staticmethod
    def create_error(symbol: str, error: str) -> dict:
        """Create an error message"""
        return {
            'type': 'error',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'error': error
        }


class PriceStreamConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time price streaming
    
    Features:
    - Multiple symbol subscriptions
    - Authentication required
    - Connection management
    - Automatic reconnection support
    - Rate limiting
    """
    
    async def connect(self):
        """Handle new WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            logger.warning(f"Anonymous connection attempt rejected")
            await self.close(code=4000, reason='Authentication required')
            return
        
        self.channel_name = f"user_{self.user.id}_prices"
        self.subscriptions = set()
        self.last_ping = datetime.now()
        
        # Add user to their personal price channel
        await self.channel_layer.group_add(
            self.channel_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.username} connected to price stream")
        
        # Send welcome message
        await self.send_json({
            'type': 'connected',
            'message': 'Price stream connected',
            'timestamp': datetime.now().isoformat()
        })
        
        # Start ping/pong for connection health
        asyncio.create_task(self._keep_alive())
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            # Remove from channel
            await self.channel_layer.group_discard(
                self.channel_name,
                self.channel_name
            )
            
            # Store subscribed symbols (for reconnection)
            if self.subscriptions:
                await self._store_subscriptions(self.subscriptions)
            
            logger.info(
                f"User {self.user.username} disconnected. "
                f"Code: {close_code}, Subscriptions: {len(self.subscriptions)}"
            )
        
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        try:
            message_type = content.get('type')
            
            if message_type == 'subscribe':
                await self._handle_subscribe(content)
            
            elif message_type == 'unsubscribe':
                await self._handle_unsubscribe(content)
            
            elif message_type == 'ping':
                await self._handle_ping()
            
            elif message_type == 'get_quotes':
                await self._handle_get_quotes(content)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_json({
                    'type': 'error',
                    'error': f'Unknown message type: {message_type}'
                })
            
            # Update last activity
            self.last_ping = datetime.now()
        
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self.send_json({
                'type': 'error',
                'error': f'Error processing message: {str(e)}'
            })
    
    async def _handle_subscribe(self, content: dict):
        """Handle subscription requests"""
        symbols = content.get('symbols', [])
        
        if not symbols:
            await self.send_json({
                'type': 'error',
                'error': 'No symbols provided'
            })
            return
        
        # Check subscription limit
        if len(self.subscriptions) + len(symbols) > MAX_SUBSCRIPTIONS_PER_USER:
            await self.send_json({
                'type': 'error',
                'error': f'Subscription limit exceeded (max {MAX_SUBSCRIPTIONS_PER_USER})'
            })
            return
        
        # Validate and add symbols
        added_symbols = []
        for symbol in symbols:
            # Normalize symbol
            symbol = str(symbol).upper().strip()
            
            # Check if already subscribed
            if symbol in self.subscriptions:
                continue
            
            # Validate asset exists
            asset = await sync_to_async(Asset.objects.filter)(
                symbol__iexact=symbol,
                is_active=True
            ).afirst()
            
            if not asset:
                await self.send_json({
                    'type': 'error',
                    'symbol': symbol,
                    'error': f'Asset not found: {symbol}'
                })
                continue
            
            # Add to subscriptions
            self.subscriptions.add(symbol)
            added_symbols.append(symbol)
            
            # Subscribe to asset's price channel
            asset_channel = f"asset_{symbol}_prices"
            await self.channel_layer.group_add(
                asset_channel,
                self.channel_name
            )
        
        # Send current prices for newly subscribed symbols
        if added_symbols:
            await self._send_initial_prices(added_symbols)
        
        # Send confirmation
        await self.send_json({
            'type': 'subscribed',
            'symbols': added_symbols,
            'total_subscriptions': len(self.subscriptions),
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(
            f"User {self.user.username} subscribed to {len(added_symbols)} symbols. "
            f"Total subscriptions: {len(self.subscriptions)}"
        )
    
    async def _handle_unsubscribe(self, content: dict):
        """Handle unsubscription requests"""
        symbols = content.get('symbols', [])
        
        if not symbols:
            await self.send_json({
                'type': 'error',
                'error': 'No symbols provided'
            })
            return
        
        removed_symbols = []
        for symbol in symbols:
            symbol = str(symbol).upper().strip()
            
            if symbol in self.subscriptions:
                self.subscriptions.remove(symbol)
                removed_symbols.append(symbol)
                
                # Unsubscribe from asset's price channel
                asset_channel = f"asset_{symbol}_prices"
                await self.channel_layer.group_discard(
                    asset_channel,
                    self.channel_name
                )
        
        # Send confirmation
        await self.send_json({
            'type': 'unsubscribed',
            'symbols': removed_symbols,
            'total_subscriptions': len(self.subscriptions),
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(
            f"User {self.user.username} unsubscribed from {len(removed_symbols)} symbols. "
            f"Total subscriptions: {len(self.subscriptions)}"
        )
    
    async def _handle_ping(self):
        """Handle ping/pong for connection health"""
        await self.send_json({
            'type': 'pong',
            'timestamp': datetime.now().isoformat()
        })
        self.last_ping = datetime.now()
    
    async def _handle_get_quotes(self, content: dict):
        """Handle request for current quotes"""
        symbols = content.get('symbols', list(self.subscriptions))
        
        if not symbols:
            symbols = list(self.subscriptions)
        
        await self._send_initial_prices(symbols)
    
    async def _send_initial_prices(self, symbols: list):
        """Send current prices for requested symbols"""
        quotes = []
        
        for symbol in symbols:
            asset = await sync_to_async(Asset.objects.filter)(
                symbol__iexact=symbol,
                is_active=True
            ).afirst()
            
            if not asset:
                continue
            
            # Get latest price
            latest_price = await sync_to_async(
                AssetPricesHistoric.objects.filter(asset=asset)
            ).order_by('-timestamp').afirst()
            
            if latest_price:
                quotes.append(PriceUpdateMessage.create(symbol, {
                    'open': float(latest_price.open),
                    'high': float(latest_price.high),
                    'low': float(latest_price.low),
                    'close': float(latest_price.close),
                    'volume': float(latest_price.volume)
                }))
        
        if quotes:
            await self.send_json({
                'type': 'quotes',
                'quotes': quotes,
                'count': len(quotes),
                'timestamp': datetime.now().isoformat()
            })
    
    async def _keep_alive(self):
        """Send periodic pings and check connection health"""
        while True:
            try:
                await asyncio.sleep(PING_INTERVAL)
                
                # Check if connection is still active
                if not hasattr(self, 'channel_layer'):
                    break
                
                # Send ping
                await self._handle_ping()
                
                # Check for timeout
                idle_time = (datetime.now() - self.last_ping).total_seconds()
                if idle_time > CONNECTION_TIMEOUT:
                    logger.warning(
                        f"Connection timeout for user {self.user.username}"
                    )
                    await self.close(code=1000, reason='Connection timeout')
                    break
            
            except Exception as e:
                logger.error(f"Error in keep_alive: {str(e)}")
                break
    
    @database_sync_to_async
    def _store_subscriptions(self, subscriptions: set):
        """Store user's subscriptions in database for reconnection"""
        try:
            # This would need a UserSubscription model
            # For now, we'll store in cache
            from django.core.cache import cache
            
            cache_key = f"user_subscriptions_{self.user.id}"
            cache.set(cache_key, list(subscriptions), timeout=3600)
        
        except Exception as e:
            logger.error(f"Error storing subscriptions: {str(e)}")


class MarketDataConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for general market data
    
    Broadcasts market-wide updates to all connected users
    """
    
    async def connect(self):
        """Handle new connection to market data stream"""
        self.user = self.scope.get("user")
        self.channel_name = "market_data"
        
        # Add to market data channel
        await self.channel_layer.group_add(
            self.channel_name,
            self.channel_name
        )
        
        logger.info(f"Connection to market data stream: {self.user.username if not self.user.is_anonymous else 'anonymous'}")
        
        await self.send_json({
            'type': 'connected',
            'message': 'Market data stream connected',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        """Handle disconnection"""
        await self.channel_layer.group_discard(
            self.channel_name,
            self.channel_name
        )
        logger.info(f"Disconnected from market data stream")
    
    async def receive_json(self, content):
        """Handle incoming messages"""
        message_type = content.get('type')
        
        if message_type == 'ping':
            await self.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.warning(f"Unknown message type: {message_type}")
