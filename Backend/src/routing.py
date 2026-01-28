from django.urls import re_path

from .consumers.market_data import MarketDataConsumer, MultiSymbolConsumer, NewsStreamConsumer

websocket_urlpatterns = [
    re_path(r'^ws/market/(?P<symbol>[A-Z0-9]+)/(?P<stream_type>\w+)/$', MarketDataConsumer.as_asgi()),
    re_path(r'^ws/market-multi/$', MultiSymbolConsumer.as_asgi()),
    re_path(r'^ws/news/(?P<category>\w+)/$', NewsStreamConsumer.as_asgi()),
]
