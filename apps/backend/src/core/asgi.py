"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()

from websocket_consumers.routing import websocket_urlpatterns
from websocket_consumers.auth_middleware import JWTAuthMiddleware

allowed_hosts = os.environ.get("ALLOWED_HOSTS", "*").split(",")

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
        "http": django_asgi_app,
    }
)
