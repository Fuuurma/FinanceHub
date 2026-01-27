"""
WebSocket Application Configuration
ASGI application for WebSocket support
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_app = get_asgi_application()

# Import WebSocket routing
from websockets.routing import ws_urlpatterns

# Configure allowed hosts
allowed_hosts = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Create WebSocket application
application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(ws_urlpatterns),
            AllowedHostsOriginValidator(allowed_hosts)
        ),
        "http": django_asgi_app,
    }
)
