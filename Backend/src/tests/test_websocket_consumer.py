import pytest
import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from channels.testing import WebsocketCommunicator
from websocket_consumers.realtime_data_consumer import RealTimeDataStreamConsumer


@pytest.mark.asyncio
@pytest.mark.django_db
class TestWebSocketConsumer:
    """
    Test WebSocket consumer functionality.
    Tests connection, subscription, message handling, and disconnection.
    """
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock data orchestrator."""
        with patch('websocket_consumers.realtime_data_consumer.get_data_orchestrator') as mock:
            orchestrator = AsyncMock()
            orchestrator.get_market_data = AsyncMock()
            mock.return_value = orchestrator
            yield orchestrator
    
    @pytest.fixture
    def mock_cache_manager(self):
        """Mock cache manager."""
        with patch('websocket_consumers.realtime_data_consumer.get_cache_manager') as mock:
            cache_manager = AsyncMock()
            cache_manager.get = AsyncMock(return_value=None)
            cache_manager.set = AsyncMock()
            cache_manager.delete = AsyncMock()
            mock.return_value = cache_manager
            yield cache_manager
    
    @pytest.fixture
    def communicator(self):
        """Create WebSocket communicator for testing."""
        return WebsocketCommunicator(
            RealTimeDataStreamConsumer.as_asgi(),
            '/ws/realtime/'
        )
    
    @pytest.fixture
    def mock_metrics(self):
        """Mock WebSocket metrics."""
        with patch('websocket_consumers.realtime_data_consumer.get_websocket_metrics') as mock:
            metrics = MagicMock()
            metrics.record_connection = MagicMock()
            metrics.record_disconnection = MagicMock()
            metrics.add_subscription = MagicMock()
            metrics.remove_subscription = MagicMock()
            metrics.update_activity = MagicMock()
            mock.return_value = metrics
            yield metrics
    
    async def test_connect_success(self, communicator, mock_cache_manager, mock_metrics):
        """Test successful WebSocket connection."""
        connected, _ = await communicator.connect()
        assert connected
        
        await communicator.disconnect()
    
    async def test_connect_with_user_id(self, communicator, mock_cache_manager, mock_metrics):
        """Test WebSocket connection with user ID."""
        scope = {
            'type': 'websocket',
            'path': '/ws/realtime/',
            'user_id': 'test-user-123',
            'user_agent': 'Mozilla/5.0'
        }
        
        comm = WebsocketCommunicator(
            RealTimeDataStreamConsumer.as_asgi(scope),
            '/ws/realtime/'
        )
        
        connected, _ = await comm.connect()
        assert connected
        
        mock_metrics.record_connection.assert_called_once_with(
            'test-user-123',
            Any,
            user_agent='Mozilla/5.0'
        )
        
        await comm.disconnect()
    
    async def test_subscribe_to_price(self, communicator, mock_orchestrator, mock_cache_manager, mock_metrics):
        """Test subscribing to price updates."""
        await communicator.connect()
        
        subscribe_message = {
            'type': 'subscribe',
            'symbols': ['BTCUSDT', 'ETHUSDT'],
            'data_types': ['price']
        }
        
        await communicator.send_json_to(subscribe_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'subscription_ack'
        assert 'BTCUSDT:price' in response['subscriptions']
        assert 'ETHUSDT:price' in response['subscriptions']
        assert 'timestamp' in response
        
        await communicator.disconnect()
    
    async def test_subscribe_to_multiple_data_types(self, communicator, mock_orchestrator, mock_cache_manager, mock_metrics):
        """Test subscribing to multiple data types."""
        await communicator.connect()
        
        subscribe_message = {
            'type': 'subscribe',
            'symbols': ['AAPL'],
            'data_types': ['price', 'trade', 'orderbook']
        }
        
        await communicator.send_json_to(subscribe_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'subscription_ack'
        assert 'AAPL:price' in response['subscriptions']
        assert 'AAPL:trade' in response['subscriptions']
        assert 'AAPL:orderbook' in response['subscriptions']
        
        await communicator.disconnect()
    
    async def test_unsubscribe(self, communicator, mock_orchestrator, mock_cache_manager, mock_metrics):
        """Test unsubscribing from data types."""
        await communicator.connect()
        
        subscribe_message = {
            'type': 'subscribe',
            'symbols': ['BTCUSDT'],
            'data_types': ['price']
        }
        await communicator.send_json_to(subscribe_message)
        
        unsubscribe_message = {
            'type': 'unsubscribe',
            'symbols': ['BTCUSDT'],
            'data_types': ['price']
        }
        await communicator.send_json_to(unsubscribe_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'unsubscribe_ack'
        assert 'BTCUSDT:price' in response['removed_subscriptions']
        
        await communicator.disconnect()
    
    async def test_ping_pong(self, communicator, mock_cache_manager, mock_metrics):
        """Test ping-pong heartbeat mechanism."""
        await communicator.connect()
        
        ping_message = {
            'type': 'ping'
        }
        await communicator.send_json_to(ping_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'pong'
        assert 'timestamp' in response
        
        await communicator.disconnect()
    
    async def test_unknown_message_type(self, communicator, mock_cache_manager, mock_metrics):
        """Test handling of unknown message types."""
        await communicator.connect()
        
        invalid_message = {
            'type': 'unknown_type'
        }
        await communicator.send_json_to(invalid_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'error'
        assert 'Unknown message type' in response['message']
        
        await communicator.disconnect()
    
    async def test_disconnect(self, communicator, mock_cache_manager, mock_metrics):
        """Test WebSocket disconnection."""
        await communicator.connect()
        await communicator.disconnect()
        
        mock_cache_manager.delete.assert_called_once()
        mock_metrics.record_disconnection.assert_called_once()
    
    async def test_case_insensitive_symbols(self, communicator, mock_orchestrator, mock_cache_manager, mock_metrics):
        """Test that symbols are converted to uppercase."""
        await communicator.connect()
        
        subscribe_message = {
            'type': 'subscribe',
            'symbols': ['btcusdt', 'ethusdt'],
            'data_types': ['price']
        }
        
        await communicator.send_json_to(subscribe_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert 'BTCUSDT:price' in response['subscriptions']
        assert 'ETHUSDT:price' in response['subscriptions']
        
        await communicator.disconnect()
    
    async def test_invalid_subscribe_message(self, communicator, mock_cache_manager, mock_metrics):
        """Test handling of malformed subscribe messages."""
        await communicator.connect()
        
        subscribe_message = {
            'type': 'subscribe',
        }
        
        await communicator.send_json_to(subscribe_message)
        
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'subscription_ack'
        assert response['subscriptions'] == []
        
        await communicator.disconnect()
    
    async def test_concurrent_subscriptions(self, communicator, mock_orchestrator, mock_cache_manager, mock_metrics):
        """Test subscribing to multiple symbols concurrently."""
        await communicator.connect()
        
        tasks = []
        for symbol in ['BTCUSDT', 'ETHUSDT', 'AAPL', 'GOOGL', 'MSFT']:
            message = {
                'type': 'subscribe',
                'symbols': [symbol],
                'data_types': ['price']
            }
            tasks.append(communicator.send_json_to(message))
        
        await asyncio.gather(*tasks)
        
        for _ in range(5):
            response = await communicator.receive_json_from(timeout=2)
            assert response['type'] == 'subscription_ack'
        
        await communicator.disconnect()
