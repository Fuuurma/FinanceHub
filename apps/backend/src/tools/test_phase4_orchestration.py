import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from django.utils import timezone
from django.test import TestCase

from utils.services.call_planner import CallPlanner, Priority, CallRequest, get_call_planner
from utils.services.cache_manager import CacheManager, CacheEntry, CacheLevel, get_cache_manager
from utils.services.data_orchestrator import DataOrchestrator, DataResponse, DataSource, DataFreshness


class TestCallPlanner(TestCase):
    def setUp(self):
        self.planner = CallPlanner()
    
    def test_configure_provider(self):
        limits = {
            'max_calls': 1000,
            'window_seconds': 60,
            'calls_per_window': 10,
            'reset_period_seconds': 3600
        }
        
        self.planner.configure_provider('test_provider', limits)
        
        self.assertIn('test_provider', self.planner.rate_limiters)
        self.assertIn('test_provider', self.planner.provider_limits)
    
    def test_add_request(self):
        async def mock_callback(**kwargs):
            return {'data': 'test'}
        
        request_id = self.planner.add_request(
            provider_name='test_provider',
            endpoint='/test',
            params={'param': 'value'},
            priority=Priority.HIGH,
            callback=mock_callback
        )
        
        self.assertIsNotNone(request_id)
        self.assertEqual(len(self.planner.request_queue), 1)
        self.assertEqual(self.planner.request_queue[0].priority, Priority.HIGH)
    
    def test_get_queue_status(self):
        async def mock_callback(**kwargs):
            return {'data': 'test'}
        
        self.planner.configure_provider('test_provider', {
            'max_calls': 100,
            'window_seconds': 60,
            'calls_per_window': 10,
            'reset_period_seconds': 3600
        })
        
        for i in range(3):
            self.planner.add_request(
                provider_name='test_provider',
                endpoint=f'/test{i}',
                params={},
                priority=Priority.MEDIUM,
                callback=mock_callback
            )
        
        status = self.planner.get_queue_status()
        
        self.assertEqual(status['pending'], 3)
        self.assertEqual(status['processing'], 0)
        self.assertIn('by_priority', status)
    
    def test_batch_buffering(self):
        async def mock_callback(**kwargs):
            return {'data': 'test'}
        
        self.planner.add_request(
            provider_name='test_provider',
            endpoint='/test1',
            params={'batch': 'test'},
            priority=Priority.BATCH,
            batch_key='test_batch'
        )
        
        self.planner.add_request(
            provider_name='test_provider',
            endpoint='/test2',
            params={'batch': 'test2'},
            priority=Priority.BATCH,
            batch_key='test_batch'
        )
        
        self.assertEqual(len(self.planner.batch_buffer['test_batch']), 2)
        self.assertEqual(len(self.planner.request_queue), 0)


class TestRateLimitTracker(TestCase):
    def test_can_make_call(self):
        from utils.services.call_planner import RateLimitTracker
        
        limits = {
            'max_calls': 10,
            'window_seconds': 60,
            'calls_per_window': 5,
            'reset_period_seconds': 3600
        }
        
        tracker = RateLimitTracker('test_provider', limits)
        
        for _ in range(4):
            self.assertTrue(tracker.can_make_call())
            tracker.record_call()
        
        self.assertTrue(tracker.can_make_call())
        
        tracker.record_call()
        self.assertFalse(tracker.can_make_call())


class TestCacheManager(TestCase):
    def setUp(self):
        self.cache = CacheManager(
            l1_max_size=10,
            l1_max_bytes=10000,
            l2_default_ttl=300
        )
    
    @pytest.mark.asyncio
    async def test_generate_key(self):
        key1 = self.cache._generate_key('test', 'arg1', param='value1')
        key2 = self.cache._generate_key('test', 'arg1', param='value1')
        key3 = self.cache._generate_key('test', 'arg1', param='value2')
        
        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)
    
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        test_data = {'symbol': 'BTC', 'price': 50000}
        
        await self.cache.set('test', 'btc', value=test_data, ttl=300)
        
        result = await self.cache.get('test', 'btc')
        
        self.assertEqual(result['symbol'], 'BTC')
        self.assertEqual(result['price'], 50000)
    
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        result = await self.cache.get('test', 'nonexistent')
        
        self.assertIsNone(result)
    
    @pytest.mark.asyncio
    async def test_l1_eviction(self):
        small_cache = CacheManager(l1_max_size=2, l1_max_bytes=1000)
        
        await small_cache.set('test', 'key1', value={'data': 1}, ttl=300)
        await small_cache.set('test', 'key2', value={'data': 2}, ttl=300)
        await small_cache.set('test', 'key3', value={'data': 3}, ttl=300)
        
        self.assertEqual(len(small_cache.l1_cache), 2)
    
    @pytest.mark.asyncio
    async def test_delete(self):
        await self.cache.set('test', 'btc', value={'price': 50000}, ttl=300)
        
        deleted = await self.cache.delete('test', 'btc')
        
        self.assertTrue(deleted)
        
        result = await self.cache.get('test', 'btc')
        self.assertIsNone(result)
    
    @pytest.mark.asyncio
    async def test_statistics(self):
        await self.cache.set('test', 'key1', value={'data': 1}, ttl=300)
        await self.cache.get('test', 'key1')
        await self.cache.get('test', 'key1')
        await self.cache.get('test', 'nonexistent')
        
        stats = await self.cache.get_statistics()
        
        self.assertGreater(stats['statistics']['total_hits'], 0)
        self.assertGreater(stats['statistics']['total_misses'], 0)
        self.assertIn('l1_memory', stats)


class TestCacheEntry(TestCase):
    def test_is_expired(self):
        future_entry = CacheEntry(
            key='test',
            value={'data': 'test'},
            level=CacheLevel.L1_MEMORY,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        self.assertFalse(future_entry.is_expired())
        
        past_entry = CacheEntry(
            key='test',
            value={'data': 'test'},
            level=CacheLevel.L1_MEMORY,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        self.assertTrue(past_entry.is_expired())
    
    def test_age_seconds(self):
        old_entry = CacheEntry(
            key='test',
            value={'data': 'test'},
            level=CacheLevel.L1_MEMORY,
            created_at=timezone.now() - timedelta(seconds=30)
        )
        
        self.assertEqual(old_entry.age_seconds(), 30)


class TestCacheStatistics(TestCase):
    def test_record_hit_miss(self):
        from utils.services.cache_manager import CacheStatistics
        
        stats = CacheStatistics()
        
        stats.record_hit(CacheLevel.L1_MEMORY, 'test_key')
        stats.record_hit(CacheLevel.L1_MEMORY, 'test_key')
        stats.record_miss(CacheLevel.L1_MEMORY, 'test_key')
        
        self.assertEqual(stats.hits, 2)
        self.assertEqual(stats.misses, 1)
        self.assertEqual(stats.get_hit_rate(), 0.6666666666666666)
        
        key_stats = stats.key_stats['test_key']
        self.assertEqual(key_stats['hits'], 2)
        self.assertEqual(key_stats['misses'], 1)


@pytest.mark.django_db
class TestDataOrchestrator(TestCase):
    def setUp(self):
        self.orchestrator = DataOrchestrator()
    
    def test_freshness_requirements(self):
        self.assertIn('crypto_price', self.orchestrator.freshness_requirements)
        self.assertIn('stock_price', self.orchestrator.freshness_requirements)
        self.assertIn('news', self.orchestrator.freshness_requirements)
        
        crypto_price_freshness = self.orchestrator.freshness_requirements['crypto_price']
        self.assertEqual(crypto_price_freshness, DataFreshness.NEAR_REALTIME)
    
    def test_data_response_creation(self):
        response = DataResponse(
            data={'price': 50000},
            source=DataSource.COINGECKO,
            cached=False,
            freshness=DataFreshness.REALTIME,
            metadata={'cache_age': 0}
        )
        
        self.assertEqual(response.data['price'], 50000)
        self.assertEqual(response.source, DataSource.COINGECKO)
        self.assertFalse(response.cached)
        self.assertEqual(response.freshness, DataFreshness.REALTIME)
    
    @pytest.mark.asyncio
    @patch('utils.services.data_orchestrator.UnifiedCryptoProvider')
    async def test_fetch_crypto_data_success(self, mock_provider):
        mock_provider.return_value.get_crypto_price = AsyncMock(return_value={
            'price': 50000,
            'timestamp': datetime.now().isoformat()
        })
        
        response = await self.orchestrator._fetch_crypto_data(
            'crypto_price',
            'BTC',
            {},
            Priority.MEDIUM
        )
        
        self.assertIsNotNone(response)
        self.assertEqual(response.data['price'], 50000)
        self.assertEqual(response.source, DataSource.COINGECKO)
        self.assertFalse(response.cached)
    
    @pytest.mark.asyncio
    @patch('utils.services.data_orchestrator.get_cache_manager')
    async def test_try_cache_hit(self, mock_cache_manager):
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value={'price': 50000, 'timestamp': datetime.now().isoformat()})
        mock_cache_manager.return_value = mock_cache
        
        response = await self.orchestrator._try_cache(
            'crypto_price',
            'BTC',
            {},
            DataFreshness.NEAR_REALTIME
        )
        
        self.assertIsNotNone(response)
        self.assertTrue(response.cached)
        self.assertEqual(response.source, DataSource.CACHE)
    
    @pytest.mark.asyncio
    @patch('utils.services.data_orchestrator.get_cache_manager')
    async def test_try_cache_miss(self, mock_cache_manager):
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache_manager.return_value = mock_cache
        
        response = await self.orchestrator._try_cache(
            'crypto_price',
            'BTC',
            {},
            DataFreshness.NEAR_REALTIME
        )
        
        self.assertIsNone(response)
    
    @pytest.mark.asyncio
    async def test_record_request(self):
        self.orchestrator._record_request('test_request', DataSource.COINGECKO, False)
        
        self.assertEqual(len(self.orchestrator.request_history), 1)
        self.assertEqual(self.orchestrator.request_history[0]['source'], 'coingecko')
        self.assertFalse(self.orchestrator.request_history[0]['cached'])
    
    @pytest.mark.asyncio
    @patch('utils.services.data_orchestrator.UnifiedCryptoProvider')
    async def test_get_statistics(self, mock_provider):
        mock_provider.return_value.get_crypto_price = AsyncMock(return_value={'price': 50000})
        
        self.orchestrator._record_request('test1', DataSource.COINGECKO, True)
        self.orchestrator._record_request('test2', DataSource.FINNHUB, False)
        
        stats = await self.orchestrator.get_statistics()
        
        self.assertIn('total_requests_last_hour', stats)
        self.assertIn('cache_hit_rate', stats)
        self.assertIn('sources_used', stats)
        self.assertIn('cache_stats', stats)
        self.assertIn('call_planner_stats', stats)


class TestDataSourceEnum(TestCase):
    def test_data_source_values(self):
        self.assertEqual(DataSource.CACHE.value, 'cache')
        self.assertEqual(DataSource.COINGECKO.value, 'coingecko')
        self.assertEqual(DataSource.FINNHUB.value, 'finnhub')
        self.assertEqual(DataSource.NEWSAPI.value, 'newsapi')


class TestDataFreshnessEnum(TestCase):
    def test_freshness_values(self):
        self.assertEqual(DataFreshness.REALTIME.value, 0)
        self.assertEqual(DataFreshness.NEAR_REALTIME.value, 30)
        self.assertEqual(DataFreshness.RECENT.value, 300)
        self.assertEqual(DataFreshness.CACHED.value, 3600)
        self.assertEqual(DataFreshness.STALE.value, 86400)


class TestIntegration(TestCase):
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self):
        cache = get_cache_manager()
        planner = get_call_planner()
        
        await cache.set('test', 'integration', value={'data': 'test'}, ttl=300)
        
        result = await cache.get('test', 'integration')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['data'], 'test')
    
    @pytest.mark.asyncio
    async def test_call_planner_cache_integration(self):
        planner = get_call_planner()
        
        call_count = 0
        
        async def test_callback(**kwargs):
            nonlocal call_count
            call_count += 1
            return {'result': 'test'}
        
        planner.configure_provider('integration_test', {
            'max_calls': 100,
            'window_seconds': 60,
            'calls_per_window': 10,
            'reset_period_seconds': 3600
        })
        
        request_id = planner.add_request(
            provider_name='integration_test',
            endpoint='/test',
            params={},
            priority=Priority.HIGH,
            callback=test_callback
        )
        
        self.assertIsNotNone(request_id)
        self.assertEqual(len(planner.request_queue), 1)


@pytest.mark.django_db
class TestAPISchemas(TestCase):
    def test_market_data_request_validation(self):
        from api.unified_market_data import MarketDataRequest
        
        data = MarketDataRequest(
            symbol='BTC',
            data_type='crypto_price',
            params={},
            force_refresh=False,
            priority='medium'
        )
        
        self.assertEqual(data.symbol, 'BTC')
        self.assertEqual(data.data_type, 'crypto_price')
        self.assertFalse(data.force_refresh)
    
    def test_market_data_response_creation(self):
        from api.unified_market_data import MarketDataResponse
        
        response = MarketDataResponse(
            data={'price': 50000},
            source='coingecko',
            cached=False,
            freshness='REALTIME',
            fetched_at=datetime.now()
        )
        
        self.assertEqual(response.source, 'coingecko')
        self.assertEqual(response.data['price'], 50000)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
