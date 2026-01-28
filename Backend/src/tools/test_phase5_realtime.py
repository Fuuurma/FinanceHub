import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from django.utils import timezone
from django.test import TestCase

from utils.services.realtime_stream_manager import (
    RealTimeStreamManager,
    get_real_time_stream_manager
)
from utils.services.cache_manager import get_cache_manager


@pytest.mark.django_db
class TestRealTimeStreamManager(TestCase):
    def setUp(self):
        self.stream_manager = RealTimeStreamManager()
    
    def test_initialization(self):
        self.assertIsNotNone(self.stream_manager)
        self.assertFalse(self.stream_manager.running)
        self.assertEqual(len(self.stream_manager.active_streams), 0)
        self.assertEqual(len(self.stream_manager.subscribers), 0)
    
    @pytest.mark.asyncio
    @patch('utils.services.realtime_stream_manager.BinanceWebSocketClient')
    async def test_start_stream_manager(self, mock_binance_client):
        mock_client_instance = MagicMock()
        mock_client_instance.connect = AsyncMock()
        mock_client_instance.subscribe_ticker = AsyncMock()
        mock_client_instance.subscribe_trade = AsyncMock()
        mock_client_instance.subscribe_order_book = AsyncMock()
        mock_binance_client.return_value = mock_client_instance
        
        await self.stream_manager.start()
        
        self.assertTrue(self.stream_manager.running)
        self.assertIsNotNone(self.stream_manager.binance_client)
        
        await self.stream_manager.stop()
    
    @pytest.mark.asyncio
    async def test_stop_stream_manager(self):
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        self.stream_manager.binance_client = mock_client
        
        self.stream_manager.running = True
        
        await self.stream_manager.stop()
        
        self.assertFalse(self.stream_manager.running)
        self.assertEqual(len(self.stream_manager.active_streams), 0)
        self.assertEqual(len(self.stream_manager.subscribers), 0)
    
    @pytest.mark.asyncio
    async def test_subscribe_and_unsubscribe(self):
        callback = AsyncMock()
        
        await self.stream_manager.subscribe('test_stream', callback)
        
        self.assertIn('test_stream', self.stream_manager.subscribers)
        self.assertIn(callback, self.stream_manager.subscribers['test_stream'])
        
        await self.stream_manager.unsubscribe('test_stream', callback)
        
        self.assertNotIn('test_stream', self.stream_manager.subscribers)
    
    @pytest.mark.asyncio
    async def test_process_ticker_data(self):
        self.stream_manager.cache_manager = get_cache_manager()
        
        ticker_data = {
            'symbol': 'BTC',
            'price': 50000,
            'change': 250,
            'change_percent': 0.5,
            'volume': 1000000
        }
        
        await self.stream_manager._process_ticker_data(ticker_data, 'binance')
        
        cached_data = await self.stream_manager.cache_manager.get('realtime_price', 'BTC')
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['price'], 50000)
        self.assertEqual(cached_data['source'], 'binance')
    
    @pytest.mark.asyncio
    async def test_process_trade_data(self):
        self.stream_manager.cache_manager = get_cache_manager()
        
        trade_data = {
            'symbol': 'BTC',
            'p': 50000,
            'q': 0.5,
            'T': int(datetime.now().timestamp() * 1000),
            'm': False
        }
        
        await self.stream_manager._process_trade_data(trade_data, 'binance')
        
        trades = await self.stream_manager.get_recent_trades('BTC', limit=10)
        
        self.assertGreater(len(trades), 0)
    
    @pytest.mark.asyncio
    async def test_process_order_book_data(self):
        self.stream_manager.cache_manager = get_cache_manager()
        
        order_book_data = {
            's': 'BTC',
            'lastUpdateId': 123456,
            'b': [[49990, 1.0], [49980, 2.0]],
            'a': [[50010, 1.0], [50020, 2.0]]
        }
        
        await self.stream_manager._process_order_book_data(order_book_data, 'binance')
        
        order_book = await self.stream_manager.get_order_book('BTC')
        
        self.assertIsNotNone(order_book)
        self.assertEqual(len(order_book['bids']), 2)
        self.assertEqual(len(order_book['asks']), 2)
    
    @pytest.mark.asyncio
    async def test_notify_subscribers(self):
        callback1 = AsyncMock()
        callback2 = MagicMock()
        
        await self.stream_manager.subscribe('test_stream', callback1)
        await self.stream_manager.subscribe('test_stream', callback2)
        
        test_data = {'test': 'data'}
        await self.stream_manager._notify_subscribers('test_stream', test_data)
        
        callback1.assert_called_once()
        callback2.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_real_time_price(self):
        self.stream_manager.cache_manager = get_cache_manager()
        
        await self.stream_manager.cache_manager.set(
            'realtime_price',
            'BTC',
            value={'price': 50000, 'timestamp': timezone.now().isoformat()},
            ttl=60
        )
        
        price = await self.stream_manager.get_real_time_price('BTC')
        
        self.assertIsNotNone(price)
        self.assertEqual(price['price'], 50000)
    
    @pytest.mark.asyncio
    async def test_get_order_book(self):
        self.stream_manager.cache_manager = get_cache_manager()
        
        order_book_data = {
            'symbol': 'BTC',
            'bids': [[49990, 1.0]],
            'asks': [[50010, 1.0]],
            'timestamp': timezone.now().isoformat()
        }
        
        await self.stream_manager.cache_manager.set(
            'order_book',
            'BTC',
            value=order_book_data,
            ttl=10
        )
        
        order_book = await self.stream_manager.get_order_book('BTC')
        
        self.assertIsNotNone(order_book)
        self.assertEqual(len(order_book['bids']), 1)
    
    def test_get_status(self):
        status = self.stream_manager.get_status()
        
        self.assertIn('running', status)
        self.assertIn('binance', status)
        self.assertIn('finnhub', status)
        self.assertIn('active_streams', status)
        self.assertIn('total_subscribers', status)
    
    def test_singleton_instance(self):
        instance1 = get_real_time_stream_manager()
        instance2 = get_real_time_stream_manager()
        
        self.assertIs(instance1, instance2)


class TestWebSocketConsumers(TestCase):
    @pytest.mark.asyncio
    async def test_market_data_consumer_connection(self):
        from consummers.market_data import MarketDataConsumer
        
        scope = {
            'url_route': {'kwargs': {'symbol': 'BTC', 'stream_type': 'price'}},
            'user_id': 'test_user'
        }
        
        consumer = MarketDataConsumer(scope)
        
        self.assertIsNotNone(consumer)
        self.assertEqual(consumer.symbol, 'BTC')
        self.assertEqual(consumer.stream_type, 'price')
    
    @pytest.mark.asyncio
    async def test_multi_symbol_consumer_connection(self):
        from consummers.market_data import MultiSymbolConsumer
        
        scope = {
            'user_id': 'test_user'
        }
        
        consumer = MultiSymbolConsumer(scope)
        
        self.assertIsNotNone(consumer)
        self.assertEqual(consumer.user_id, 'test_user')
        self.assertEqual(len(consumer.subscribed_symbols), 0)


@pytest.mark.django_db
class TestIntegration(TestCase):
    @pytest.mark.asyncio
    async def test_full_stream_workflow(self):
        stream_manager = get_real_time_stream_manager()
        cache_manager = get_cache_manager()
        
        received_data = []
        
        async def callback(data):
            received_data.append(data)
        
        await stream_manager.subscribe('price_BTC', callback)
        
        ticker_data = {
            'symbol': 'BTC',
            'price': 50000,
            'timestamp': timezone.now().isoformat()
        }
        
        await stream_manager._process_ticker_data(ticker_data, 'binance')
        await asyncio.sleep(0.1)
        
        cached_price = await cache_manager.get('realtime_price', 'BTC')
        
        self.assertIsNotNone(cached_price)
        self.assertEqual(cached_price['price'], 50000)
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        stream_manager = get_real_time_stream_manager()
        
        results1 = []
        results2 = []
        results3 = []
        
        async def callback1(data):
            results1.append(data)
        
        def callback2(data):
            results2.append(data)
        
        async def callback3(data):
            results3.append(data)
        
        await stream_manager.subscribe('test_stream', callback1)
        await stream_manager.subscribe('test_stream', callback2)
        await stream_manager.subscribe('test_stream', callback3)
        
        test_data = {'test': 'message'}
        await stream_manager._notify_subscribers('test_stream', test_data)
        
        self.assertEqual(len(results1), 1)
        self.assertEqual(len(results2), 1)
        self.assertEqual(len(results3), 1)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
