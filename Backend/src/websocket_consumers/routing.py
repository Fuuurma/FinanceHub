from django.urls import re_path

from .auth_middleware import JWTAuthMiddlewareStack
from .realtime_data_consumer import RealTimeDataStreamConsumer

websocket_urlpatterns = [
    re_path(r'ws/realtime/$', JWTAuthMiddlewareStack(RealTimeDataStreamConsumer.as_asgi())),
]
