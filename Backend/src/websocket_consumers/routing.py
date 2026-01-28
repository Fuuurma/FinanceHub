"""
WebSocket Routing Configuration
Defines URL patterns for WebSocket connections
"""
from django.urls import re_path
from websocket_consumers.consumers import PriceStreamConsumer, MarketDataConsumer

ws_urlpatterns = [
    re_path(r'ws/price-stream/$', PriceStreamConsumer.as_asgi()),
    re_path(r'ws/market-data/$', MarketDataConsumer.as_asgi()),
]
