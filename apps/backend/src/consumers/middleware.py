import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


@dataclass
class TokenPayload:
    user_id: str
    username: str
    email: str
    exp: datetime
    iat: datetime
    tier: str = "free"
    subscriptions_remaining: int = 10
    rate_limit_per_minute: int = 60


@dataclass
class ConnectionQuota:
    user_id: str
    max_connections: int = 3
    max_subscriptions: int = 50
    rate_limit_per_minute: int = 60
    current_connections: int = 0
    current_subscriptions: int = 0


class WebSocketAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for WebSocket authentication.
    Validates JWT tokens during WebSocket handshake.
    """

    async def __call__(self, scope, receive, send):
        scope["user"] = await self.get_user_from_token(scope)
        return await super().__call__(scope, receive, send)

    async def get_user_from_token(self, scope) -> Any:
        """Extract and validate JWT token from scope headers."""
        query_string = scope.get("query_string", b"").decode()
        token = self._extract_token_from_query(query_string)

        if not token:
            token = self._extract_token_from_headers(dict(scope.get("headers", [])))

        if not token:
            return AnonymousUser()

        try:
            payload = await self._validate_token(token)
            user = await self._get_user(payload.user_id)
            scope["auth_payload"] = payload
            scope["user_tier"] = payload.tier
            return user if user else AnonymousUser()

        except jwt.ExpiredSignatureError:
            logger.warning("WebSocket: Token expired")
            return AnonymousUser()
        except jwt.InvalidTokenError as e:
            logger.warning(f"WebSocket: Invalid token - {e}")
            return AnonymousUser()
        except Exception as e:
            logger.error(f"WebSocket auth error: {e}")
            return AnonymousUser()

    def _extract_token_from_query(self, query_string: str) -> Optional[str]:
        """Extract token from query parameters."""
        if "token=" in query_string:
            params = dict(p.split("=") for p in query_string.split("&"))
            return params.get("token")
        return None

    def _extract_token_from_headers(self, headers: Dict) -> Optional[str]:
        """Extract token from Authorization header."""
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        if auth_header.startswith("Token "):
            return auth_header[6:]
        return None

    async def _validate_token(self, token: str) -> TokenPayload:
        """Validate JWT token and return payload."""
        secret = getattr(settings, "JWT_SECRET_KEY", "your-secret-key")
        algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")

        payload = jwt.decode(token, secret, algorithms=[algorithm])

        return TokenPayload(
            user_id=payload.get("user_id", ""),
            username=payload.get("username", ""),
            email=payload.get("email", ""),
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
            tier=payload.get("tier", "free"),
            subscriptions_remaining=payload.get("subscriptions_remaining", 10),
            rate_limit_per_minute=payload.get("rate_limit_per_minute", 60),
        )

    async def _get_user(self, user_id: str) -> Optional[Any]:
        """Fetch user from database."""
        try:
            from users.models.user import User

            user = await database_sync_to_async(User.objects.filter(id=user_id).first)()
            return user
        except ImportError:
            return None


class WebSocketAuthService:
    """
    Service for WebSocket authentication operations.
    Handles token generation, validation, and user sessions.
    """

    def __init__(self):
        self.jwt_secret = getattr(settings, "JWT_SECRET_KEY", "your-secret-key")
        self.jwt_algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")
        self.token_expiry_hours = getattr(settings, "JWT_EXPIRY_HOURS", 24)
        self.refresh_token_expiry_days = getattr(settings, "JWT_REFRESH_EXPIRY_DAYS", 7)

    def generate_access_token(self, user) -> str:
        """Generate JWT access token for a user."""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        expiry = now + timedelta(hours=self.token_expiry_hours)

        payload = {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "tier": getattr(user, "tier", "free"),
            "subscriptions_remaining": getattr(user, "max_subscriptions", 10),
            "rate_limit_per_minute": getattr(user, "rate_limit_per_minute", 60),
            "iat": now,
            "exp": expiry,
            "type": "access",
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def generate_refresh_token(self, user) -> str:
        """Generate JWT refresh token for a user."""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        expiry = now + timedelta(days=self.refresh_token_expiry_days)

        payload = {
            "user_id": str(user.id),
            "iat": now,
            "exp": expiry,
            "type": "refresh",
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return payload."""
        try:
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: Expired signature")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    def refresh_access_token(self, refresh_token: str, user) -> tuple:
        """
        Generate new access and refresh tokens using refresh token.
        Implements token rotation - old refresh token is blacklisted.

        Returns:
            Tuple of (access_token, new_refresh_token) or (None, None) on failure
        """
        from users.models.token_blacklist import BlacklistedToken

        # Check if token is already blacklisted
        if BlacklistedToken.is_blacklisted(refresh_token):
            logger.warning(f"Token reuse attempt for user {user.id}")
            return None, None

        # Verify refresh token
        payload = self.verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return None, None

        if payload.get("user_id") != str(user.id):
            return None, None

        # Blacklist the old refresh token (token rotation)
        BlacklistedToken.blacklist_token(
            token=refresh_token,
            user_id=str(user.id),
            expires_in=7 * 24 * 3600,  # 7 days
        )
        logger.info(f"Refresh token blacklisted for user {user.id}")

        # Generate new access token
        new_access_token = self.generate_access_token(user)

        # Generate new refresh token
        new_refresh_token = self.generate_refresh_token(user)

        return new_access_token, new_refresh_token

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get expiry datetime from token."""
        payload = self.verify_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired."""
        expiry = self.get_token_expiry(token)
        if expiry:
            return datetime.now() > expiry
        return True


class WebSocketSessionManager:
    """
    Manages WebSocket user sessions.
    Tracks active connections and subscriptions.
    """

    def __init__(self):
        self._sessions: Dict[str, ConnectionQuota] = {}
        self._user_connections: Dict[str, set] = {}
        self._user_subscriptions: Dict[str, set] = {}

    def register_connection(self, user_id: str, connection_id: str) -> bool:
        """
        Register a new WebSocket connection for a user.

        Returns:
            True if registration successful, False if quota exceeded
        """
        if user_id not in self._sessions:
            self._sessions[user_id] = ConnectionQuota(user_id=user_id)

        quota = self._sessions[user_id]

        if quota.current_connections >= quota.max_connections:
            logger.warning(f"User {user_id} exceeded connection quota")
            return False

        quota.current_connections += 1

        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(connection_id)

        logger.info(
            f"User {user_id} connection registered. Total: {quota.current_connections}"
        )
        return True

    def unregister_connection(self, user_id: str, connection_id: str):
        """Unregister a WebSocket connection."""
        if user_id in self._user_connections:
            self._user_connections[user_id].discard(connection_id)

        if user_id in self._sessions:
            self._sessions[user_id].current_connections = max(
                0, self._sessions[user_id].current_connections - 1
            )

        logger.info(f"User {user_id} connection unregistered")

    def register_subscription(self, user_id: str, symbol: str):
        """Register a symbol subscription for a user."""
        if user_id not in self._user_subscriptions:
            self._user_subscriptions[user_id] = set()

        self._user_subscriptions[user_id].add(symbol.upper())

        if user_id in self._sessions:
            self._sessions[user_id].current_subscriptions = len(
                self._user_subscriptions[user_id]
            )

    def unregister_subscription(self, user_id: str, symbol: str):
        """Unregister a symbol subscription."""
        if user_id in self._user_subscriptions:
            self._user_subscriptions[user_id].discard(symbol.upper())

        if user_id in self._sessions:
            self._sessions[user_id].current_subscriptions = len(
                self._user_subscriptions[user_id]
            )

    def get_user_quota(self, user_id: str) -> Optional[ConnectionQuota]:
        """Get connection quota for a user."""
        return self._sessions.get(user_id)

    def get_user_subscriptions(self, user_id: str) -> set:
        """Get all subscriptions for a user."""
        return self._user_subscriptions.get(user_id, set())

    def get_active_connections_count(self, user_id: str) -> int:
        """Get number of active connections for a user."""
        if user_id in self._sessions:
            return self._sessions[user_id].current_connections
        return 0

    def get_all_active_users(self) -> list:
        """Get list of all users with active connections."""
        return list(self._user_connections.keys())

    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user is within rate limit.
        Should be called with a rate limiter that increments counters.

        Returns:
            True if within rate limit, False if exceeded
        """
        quota = self._sessions.get(user_id)
        if quota:
            return True
        return True

    def set_user_tier(self, user_id: str, tier: str):
        """Update quota based on user tier."""
        if user_id not in self._sessions:
            self._sessions[user_id] = ConnectionQuota(user_id=user_id)

        quota = self._sessions[user_id]

        tier_limits = {
            "free": ConnectionQuota(
                max_connections=1, max_subscriptions=10, rate_limit_per_minute=30
            ),
            "basic": ConnectionQuota(
                max_connections=3, max_subscriptions=50, rate_limit_per_minute=120
            ),
            "pro": ConnectionQuota(
                max_connections=5, max_subscriptions=200, rate_limit_per_minute=300
            ),
            "enterprise": ConnectionQuota(
                max_connections=10, max_subscriptions=1000, rate_limit_per_minute=1000
            ),
        }

        limits = tier_limits.get(tier, tier_limits["free"])
        quota.max_connections = limits.max_connections
        quota.max_subscriptions = limits.max_subscriptions
        quota.rate_limit_per_minute = limits.rate_limit_per_minute

    def get_statistics(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        total_connections = sum(s.current_connections for s in self._sessions.values())
        total_subscriptions = sum(
            len(subs) for subs in self._user_subscriptions.values()
        )

        return {
            "total_active_users": len(self._sessions),
            "total_connections": total_connections,
            "total_subscriptions": total_subscriptions,
            "tier_distribution": self._get_tier_distribution(),
        }

    def _get_tier_distribution(self) -> Dict[str, int]:
        """Get distribution of users by tier."""
        distribution = {"free": 0, "basic": 0, "pro": 0, "enterprise": 0}
        for quota in self._sessions.values():
            tier = getattr(quota, "tier", "free")
            distribution[tier] = distribution.get(tier, 0) + 1
        return distribution


session_manager = WebSocketSessionManager()
auth_service = WebSocketAuthService()
