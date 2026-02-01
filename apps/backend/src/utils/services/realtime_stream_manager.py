import asyncio
from typing import Dict, Optional, Callable, Set
from datetime import datetime
import orjson
from websockets.exceptions import ConnectionClosed

from django.utils import timezone
from utils.helpers.logger.logger import get_logger
from utils.services.data_orchestrator import DataSource
from utils.services.cache_manager import get_cache_manager
from data.data_providers.binance.websocket_client import BinanceWebSocketClient
from data.data_providers.binance.trade_service import BinanceTradeService as TradeService
from data.data_providers.binance.order_book_service import BinanceOrderBookService as OrderBookService
from data.data_providers.finnHub.scraper import FinnhubScraper

logger = get_logger(__name__)


class RealTimeStreamManager:
    def __init__(self):
        self.active_streams: Dict[str, any] = {}
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.binance_client: Optional[BinanceWebSocketClient] = None
        self.finnhub_client: Optional[any] = None
        self.cache_manager = get_cache_manager()
        self.running = False
        self._lock = asyncio.Lock()
    
    async def start(self):
        if self.running:
            logger.warning("RealTimeStreamManager already running")
            return
        
        self.running = True
        logger.info("Starting RealTimeStreamManager")
        
        await self._start_binance_streams()
        await self._start_finnhub_streams()
        
        logger.info("RealTimeStreamManager started")
    
    async def stop(self):
        if not self.running:
            return
        
        self.running = False
        
        if self.binance_client:
            await self.binance_client.disconnect()
        
        if self.finnhub_client:
            await self.finnhub_client.disconnect()
        
        self.active_streams.clear()
        self.subscribers.clear()
        
        logger.info("RealTimeStreamManager stopped")
    
    async def _start_binance_streams(self):
        try:
            self.binance_client = BinanceWebSocketClient()
            
            await self.binance_client.connect()
            
            await self.binance_client.subscribe_ticker('BTCUSDT')
            await self.binance_client.subscribe_ticker('ETHUSDT')
            await self.binance_client.subscribe_ticker('SOLUSDT')
            
            await self.binance_client.subscribe_trade('BTCUSDT')
            await self.binance_client.subscribe_trade('ETHUSDT')
            
            await self.binance_client.subscribe_order_book('BTCUSDT', depth=20)
            await self.binance_client.subscribe_order_book('ETHUSDT', depth=20)
            
            self.binance_client.on_message = self._handle_binance_message
            
            logger.info("Binance WebSocket streams started")
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Failed to start Binance streams: {e}")
    
    async def _start_finnhub_streams(self):
        try:
            self.finnhub_client = FinnhubScraper()
            
            stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META']
            
            for symbol in stocks:
                await self.finnhub_client.subscribe_real_time_price(symbol)
            
            if hasattr(self.finnhub_client, 'on_message'):
                self.finnhub_client.on_message = self._handle_finnhub_message
            
            logger.info("Finnhub WebSocket streams started")
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Failed to start Finnhub streams: {e}")
    
    async def _handle_binance_message(self, message: dict):
        try:
            stream = message.get('stream', '')
            data = message.get('data', {})
            
            if 'ticker' in stream:
                await self._process_ticker_data(data, 'binance')
            elif 'trade' in stream:
                await self._process_trade_data(data, 'binance')
            elif 'depth' in stream:
                await self._process_order_book_data(data, 'binance')
            
            await self._notify_subscribers(stream, data)
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error handling Binance message: {e}")
    
    async def _handle_finnhub_message(self, message: dict):
        try:
            symbol = message.get('s', '')
            data = message
            
            if 'p' in data and 't' in data:
                price_data = {
                    'symbol': symbol,
                    'price': data.get('p'),
                    'timestamp': data.get('t'),
                    'volume': data.get('v')
                }
                await self._process_ticker_data(price_data, 'finnhub')
            
            stream = f'finnhub_{symbol}'
            await self._notify_subscribers(stream, data)
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error handling Finnhub message: {e}")
    
    async def _process_ticker_data(self, data: dict, source: str):
        symbol = data.get('symbol') or data.get('s', 'UNKNOWN')
        price = data.get('price') or data.get('p') or data.get('c')
        change = data.get('change') or data.get('d')
        change_percent = data.get('change_percent') or data.get('P')
        volume = data.get('volume') or data.get('v')
        
        ticker_data = {
            'symbol': symbol.replace('USDT', '').upper(),
            'price': price,
            'change': change,
            'change_percent': change_percent,
            'volume': volume,
            'source': source,
            'timestamp': timezone.now().isoformat()
        }
        
        await self.cache_manager.set(
            'realtime_price',
            symbol,
            value=ticker_data,
            ttl=60
        )
    
    async def _process_trade_data(self, data: dict, source: str):
        symbol = data.get('symbol', 'UNKNOWN').replace('USDT', '').upper()
        price = data.get('p') or data.get('price')
        quantity = data.get('q') or data.get('quantity')
        time = data.get('T') or data.get('time')
        is_buyer_maker = data.get('m', False)
        
        trade_data = {
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'timestamp': datetime.fromtimestamp(time / 1000).isoformat() if time else timezone.now().isoformat(),
            'is_buyer_maker': is_buyer_maker,
            'source': source
        }
        
        await self.cache_manager.set(
            'recent_trade',
            f"{symbol}_{time}",
            value=trade_data,
            ttl=300
        )
    
    async def _process_order_book_data(self, data: dict, source: str):
        symbol = data.get('s', 'UNKNOWN').replace('USDT', '').upper()
        last_update_id = data.get('lastUpdateId', 0)
        bids = data.get('b', [])
        asks = data.get('a', [])
        
        order_book_data = {
            'symbol': symbol,
            'last_update_id': last_update_id,
            'bids': bids[:20],
            'asks': asks[:20],
            'source': source,
            'timestamp': timezone.now().isoformat()
        }
        
        await self.cache_manager.set(
            'order_book',
            symbol,
            value=order_book_data,
            ttl=10
        )
    
    async def subscribe(self, stream: str, callback: Callable):
        async with self._lock:
            if stream not in self.subscribers:
                self.subscribers[stream] = set()
            
            self.subscribers[stream].add(callback)
            logger.debug(f"Added subscriber for stream: {stream}")
    
    async def unsubscribe(self, stream: str, callback: Callable):
        async with self._lock:
            if stream in self.subscribers:
                self.subscribers[stream].discard(callback)
                
                if not self.subscribers[stream]:
                    del self.subscribers[stream]
                    logger.debug(f"Removed stream: {stream}")
    
    async def _notify_subscribers(self, stream: str, data: dict):
        if stream not in self.subscribers:
            return
        
        tasks = []
        for callback in self.subscribers[stream]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(data))
                else:
                    callback(data)
            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                logger.error(f"Error in subscriber callback: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def get_real_time_price(self, symbol: str) -> Optional[dict]:
        try:
            price_data = await self.cache_manager.get('realtime_price', symbol)
            
            if price_data:
                age_seconds = (timezone.now() - timezone.make_aware(
                    datetime.fromisoformat(price_data['timestamp'])
                )).total_seconds()
                
                if age_seconds < 10:
                    return price_data
            
            return None
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error getting real-time price: {e}")
            return None
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> list:
        try:
            trade_keys = []
            
            for i in range(100):
                key = f"recent_trade_{symbol}_{timezone.now().timestamp() - i}"
                trade_keys.append(key)
            
            trades = []
            for key in trade_keys:
                trade_data = await self.cache_manager.get('recent_trade', key)
                if trade_data:
                    trades.append(trade_data)
            
            return trades[:limit]
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error getting recent trades: {e}")
            return []
    
    async def get_order_book(self, symbol: str) -> Optional[dict]:
        try:
            order_book_data = await self.cache_manager.get('order_book', symbol)
            
            if order_book_data:
                age_seconds = (timezone.now() - timezone.make_aware(
                    datetime.fromisoformat(order_book_data['timestamp'])
                )).total_seconds()
                
                if age_seconds < 5:
                    return order_book_data
            
            return None
            
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error getting order book: {e}")
            return None
    
    def get_status(self) -> dict:
        binance_status = 'connected' if self.binance_client and self.binance_client.is_connected() else 'disconnected'
        finnhub_status = 'connected' if self.finnhub_client else 'disconnected'
        
        return {
            'running': self.running,
            'binance': binance_status,
            'finnhub': finnhub_status,
            'active_streams': len(self.active_streams),
            'total_subscribers': sum(len(subs) for subs in self.subscribers.values())
        }


_real_time_stream_manager_instance: Optional[RealTimeStreamManager] = None


def get_real_time_stream_manager() -> RealTimeStreamManager:
    global _real_time_stream_manager_instance
    if _real_time_stream_manager_instance is None:
        _real_time_stream_manager_instance = RealTimeStreamManager()
    return _real_time_stream_manager_instance
