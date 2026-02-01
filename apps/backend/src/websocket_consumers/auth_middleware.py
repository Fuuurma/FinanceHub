from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import DatabaseError, OperationalError

from api.websocket_auth import verify_websocket_token
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


@database_sync_to_async
def get_user(token: str):
    """Get user from JWT token"""
    try:
        payload = verify_websocket_token(token)
        if payload and "user_id" in payload:
            from users.models.user import User

            try:
                return User.objects.get(id=payload["user_id"])
            except User.DoesNotExist:
                return AnonymousUser()
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        logger.error(f"Error authenticating WebSocket: {e}")
    return AnonymousUser()


class JWTAuthMiddleware:
    """
    Middleware to authenticate WebSocket connections using JWT tokens
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = None
        auth_header = dict(scope.get("headers", [])).get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        # Authenticate user
        if token:
            user = await get_user(token)
            scope["user"] = user
            scope["user_id"] = user.id if not isinstance(user, AnonymousUser) else None
        else:
            scope["user"] = AnonymousUser()
            scope["user_id"] = None

        return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
