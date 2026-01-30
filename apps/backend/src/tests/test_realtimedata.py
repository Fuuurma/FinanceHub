import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from django.utils import timezone

from api.realtimedata import router


@pytest.mark.asyncio
@pytest.mark.django_db
class TestRealTimeDataAPI:
    
    @pytest.fixture
    def mock_orchestrator(self):
        with patch('api.realtimedata.get_data_orchestrator') as mock:
            orchestrator = AsyncMock()
            orchestrator.get_market_data = AsyncMock()
            mock.return_value = orchestrator
            yield orchestrator
    
    @pytest.fixture
    def mock_cache_manager(self):
        with patch('api.realtimedata.get_cache_manager') as mock:
            cache_manager = AsyncMock()
            cache_manager.get = AsyncMock(return_value=None)
            cache_manager.set = AsyncMock()
            mock.return_value = cache_manager
            yield cache_manager
    
    async def test_get_realtime_price_crypto_success(self, mock_orchestrator):
        mock_response = MagicMock()
        mock_response.data = {
            'price': 50000.00,
            'change': 1500.00,
            'change_percent': 3.0,
            'volume': 1000000,
            'timestamp': timezone.now().isoformat(),
            'bid': 49999.00,
            'ask': 50001.00,
            'spread': 2.00,
            'high_52w': 60000.00,
            'low_52w': 40000.00,
            'open': 49500.00,
            'close': 48500.00
        }
        mock_orchestrator.get_market_data.return_value = mock_response
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/price/BTCUSDT")
        
        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'BTCUSDT'
        assert Decimal(data['price']) == Decimal('50000.00')
        assert data['source'] == 'market'
    
    async def test_get_realtime_price_stock_success(self, mock_orchestrator):
        mock_response = MagicMock()
        mock_response.data = {
            'price': 150.25,
            'change': 2.50,
            'change_percent': 1.69,
            'volume': 5000000,
            'timestamp': timezone.now().isoformat(),
            'bid': 150.20,
            'ask': 150.30,
            'spread': 0.10
        }
        mock_orchestrator.get_market_data.return_value = mock_response
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/price/AAPL")
        
        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'AAPL'
        assert Decimal(data['price']) == Decimal('150.25')
    
    async def test_get_realtime_price_not_available(self, mock_orchestrator):
        mock_orchestrator.get_market_data.return_value = None
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/price/INVALID")
        
        assert response.status_code == 200
        data = response.json()
        assert 'error' in data
    
    async def test_get_batch_prices(self, mock_orchestrator, mock_cache_manager):
        mock_response = MagicMock()
        mock_response.data = {
            'price': 50000.00,
            'change': 1500.00,
            'change_percent': 3.0,
            'volume': 1000000,
            'timestamp': timezone.now().isoformat()
        }
        mock_orchestrator.get_market_data.return_value = mock_response
        
        client = TestClient(async_create_app())
        payload = {
            'symbols': ['BTCUSDT', 'ETHUSDT', 'AAPL'],
            'include_volume': True,
            'include_spread': False,
            'include_orderbook': False
        }
        response = client.post("/realtime/prices/batch", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert 'updates' in data
        assert data['total_symbols'] == 3
    
    async def test_get_recent_trades(self, mock_orchestrator):
        mock_response = MagicMock()
        mock_response.data = {
            'trades': [
                {
                    'trade_id': '12345',
                    'price': 50000.50,
                    'quantity': 0.5,
                    'side': 'buy',
                    'timestamp': timezone.now().isoformat(),
                    'exchange': 'Binance',
                    'maker': True
                },
                {
                    'trade_id': '12346',
                    'price': 50001.00,
                    'quantity': 1.0,
                    'side': 'sell',
                    'timestamp': timezone.now().isoformat(),
                    'exchange': 'Binance',
                    'maker': False
                }
            ],
            'volume_24h': 100000000
        }
        mock_orchestrator.get_market_data.return_value = mock_response
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/trades/BTCUSDT?limit=20")
        
        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'BTCUSDT'
        assert len(data['trades']) == 2
        assert data['count'] == 2
        assert data['volume_24h'] == 100000000
    
    async def test_get_recent_trades_empty(self, mock_orchestrator):
        mock_orchestrator.get_market_data.return_value = None
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/trades/BTCUSDT")
        
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == 0
        assert len(data['trades']) == 0
    
    async def test_get_orderbook(self, mock_orchestrator):
        mock_response = MagicMock()
        mock_response.data = {
            'levels': [
                {
                    'price': 49999.00,
                    'volume': 10.5,
                    'total_size': 20.5,
                    'is_spread': False,
                    'spread': 0,
                    'timestamp': timezone.now().isoformat()
                },
                {
                    'price': 50001.00,
                    'volume': 10.0,
                    'total_size': 10.0,
                    'is_spread': False,
                    'spread': 0,
                    'timestamp': timezone.now().isoformat()
                }
            ],
            'mid_price': 50000.00,
            'spread': 2.00,
            'depth': 10
        }
        mock_orchestrator.get_market_data.return_value = mock_response
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/orderbook/BTCUSDT?depth=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'BTCUSDT'
        assert len(data['levels']) == 2
        assert Decimal(data['mid_price']) == Decimal('50000.00')
        assert Decimal(data['spread']) == Decimal('2.00')
    
    async def test_get_orderbook_empty(self, mock_orchestrator):
        mock_orchestrator.get_market_data.return_value = None
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/orderbook/BTCUSDT")
        
        assert response.status_code == 200
        data = response.json()
        assert data['depth'] == 0
        assert len(data['levels']) == 0
    
    async def test_get_websocket_connection_info(self, mock_cache_manager):
        mock_cache_manager.get = AsyncMock(return_value={
            'BTCUSDT': 'active',
            'ETHUSDT': 'active'
        })
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/connection-info?user_id=test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert data['connected'] == True
        assert 'BTCUSDT' in data['subscriptions']
        assert 'ETHUSDT' in data['subscriptions']
    
    async def test_get_websocket_connection_info_no_connection(self, mock_cache_manager):
        mock_cache_manager.get = AsyncMock(return_value=None)
        
        client = TestClient(async_create_app())
        response = client.get("/realtime/connection-info")
        
        assert response.status_code == 200
        data = response.json()
        assert data['connected'] == False
        assert len(data['subscriptions']) == 0


def async_create_app():
    from django.urls import path
    from django.conf import settings
    from ninja import NinjaAPI
    from django.test import AsyncClient
    from django.core.handlers.asgi import ASGIHandler
    from django.test.utils import setup_test_environment
    from django.core.management import call_command
    
    setup_test_environment()
    return None
