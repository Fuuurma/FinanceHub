"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_app = get_asgi_application()

# Import WebSocket routing
from websocket_consumers.routing import websocket_urlpatterns

# Configure allowed hosts
allowed_hosts = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Create WebSocket application with HTTP fallback
application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns),
            AllowedHostsOriginValidator(allowed_hosts)
        ),
        "http": django_asgi_app,
    }
)
