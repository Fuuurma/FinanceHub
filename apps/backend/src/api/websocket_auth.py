from datetime import datetime
from typing import Optional, List, Dict, Any

from ninja import Router, Schema
from pydantic import Field, EmailStr

from utils.services.quotas import quota_manager, abuse_detector
from consumers.middleware import auth_service, session_manager

router = Router()


def verify_websocket_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a WebSocket JWT token and return the payload.
    """
    try:
        payload = auth_service.verify_token(token)
        return payload
    except Exception:
        return None


class TokenResponse(Schema):
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "Bearer"
    expires_in: int
    user_id: str
    username: str
    tier: str


class RefreshTokenRequest(Schema):
    refresh_token: str


class TokenVerifyResponse(Schema):
    valid: bool
    user_id: Optional[str]
    username: Optional[str]
    email: Optional[str]
    tier: Optional[str]
    expires_at: Optional[datetime]
    subscriptions_remaining: Optional[int]


class UserQuotaResponse(Schema):
    user_id: str
    tier: str
    connections: Dict[str, Any]
    subscriptions: Dict[str, Any]
    rate_limit: Dict[str, Any]
    messages: Dict[str, Any]


class ConnectionInfo(Schema):
    connection_id: str
    connected_at: datetime
    subscriptions: List[str] = []
    messages_sent: int = 0
    messages_received: int = 0


class UserConnectionsResponse(Schema):
    user_id: str
    total_connections: int
    connections: List[ConnectionInfo]
    max_connections: int


class BlockUserRequest(Schema):
    user_id: str
    reason: str = "Manual block"


class BlockUserResponse(Schema):
    success: bool
    user_id: str
    blocked_until: Optional[datetime]
    message: str


@router.post("/auth/token", response=TokenResponse)
def get_token(request, username: str, password: str):
    """
    Authenticate user and return JWT tokens.
    """
    from django.contrib.auth import authenticate

    user = authenticate(username=username, password=password)

    if not user:
        return {"error": "Invalid credentials"}, 401

    access_token = auth_service.generate_access_token(user)
    refresh_token = auth_service.generate_refresh_token(user)

    tier = getattr(user, "tier", "free")
    expiry_hours = getattr(request, "JWT_EXPIRY_HOURS", 24)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=expiry_hours * 3600,
        user_id=str(user.id),
        username=user.username,
        tier=tier,
    )


@router.post("/auth/token/refresh", response=TokenResponse)
def refresh_token(request, refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    Implements token rotation - old refresh token is blacklisted,
    new refresh token is returned.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    payload = auth_service.verify_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        return {"error": "Invalid refresh token"}, 401

    try:
        user = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return {"error": "User not found"}, 401

    # Implement token rotation - returns (access_token, new_refresh_token)
    new_access_token, new_refresh_token = auth_service.refresh_access_token(
        refresh_data.refresh_token, user
    )

    if not new_access_token:
        # Token reuse detected - potential attack
        logger.warning(f"Token refresh failed - reuse detected for user {user.id}")
        return {"error": "Token refresh failed - possible token reuse detected"}, 401

    tier = getattr(user, "tier", "free")
    expiry_hours = getattr(request, "JWT_EXPIRY_HOURS", 24)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,  # New refresh token for continued rotation
        token_type="Bearer",
        expires_in=expiry_hours * 3600,
        user_id=str(user.id),
        username=user.username,
        tier=tier,
    )


@router.get("/auth/verify", response=TokenVerifyResponse)
def verify_token(request, token: str):
    """
    Verify a JWT token and return its payload.
    """
    payload = auth_service.verify_token(token)

    if not payload:
        return TokenVerifyResponse(valid=False)

    expires_at = datetime.fromtimestamp(payload["exp"]) if "exp" in payload else None

    return TokenVerifyResponse(
        valid=True,
        user_id=payload.get("user_id"),
        username=payload.get("username"),
        email=payload.get("email"),
        tier=payload.get("tier"),
        expires_at=expires_at,
        subscriptions_remaining=payload.get("subscriptions_remaining"),
    )


@router.get("/auth/quota", response=UserQuotaResponse)
def get_user_quota(request, user_id: str):
    """
    Get quota information for a user.
    """
    tier = "free"
    stats = quota_manager.get_user_statistics(user_id, tier)

    return UserQuotaResponse(
        user_id=user_id,
        tier=tier,
        connections={
            "current": 0,
            "max": quota_manager.get_tier_config(tier)["connections"],
        },
        subscriptions=stats["subscriptions"],
        rate_limit=stats["rate_limit"],
        messages=stats["messages"],
    )


@router.get("/auth/connections", response=UserConnectionsResponse)
def get_user_connections(request, user_id: str):
    """
    Get all active connections for a user.
    """
    connections = session_manager.get_user_subscriptions(user_id)
    quota = session_manager.get_user_quota(user_id)

    connection_list = []
    for conn_id in session_manager._user_connections.get(user_id, set()):
        connection_list.append(
            ConnectionInfo(
                connection_id=conn_id,
                connected_at=datetime.now(),
                subscriptions=list(connections),
            )
        )

    max_connections = quota.max_connections if quota else 1

    return UserConnectionsResponse(
        user_id=user_id,
        total_connections=len(connection_list),
        connections=connection_list,
        max_connections=max_connections,
    )


@router.post("/auth/block", response=BlockUserResponse)
def block_user(request, block_data: BlockUserRequest):
    """
    Block a user from WebSocket connections.
    """
    abuse_detector._block_user(block_data.user_id)

    blocked_until = datetime.now()

    return BlockUserResponse(
        success=True,
        user_id=block_data.user_id,
        blocked_until=blocked_until,
        message=f"User {block_data.user_id} blocked. Reason: {block_data.reason}",
    )


@router.post("/auth/unblock")
def unblock_user(request, user_id: str):
    """
    Unblock a user.
    """
    abuse_detector.unblock_user(user_id)

    return {"success": True, "user_id": user_id, "message": "User unblocked"}


@router.get("/auth/blocked")
def get_blocked_users(request):
    """
    Get list of blocked users.
    """
    blocked_users = abuse_detector.get_blocked_users()

    return {"blocked_users": blocked_users, "count": len(blocked_users)}


@router.get("/auth/stats")
def get_auth_stats(request):
    """
    Get WebSocket authentication and quota statistics.
    """
    return {
        "session_stats": session_manager.get_statistics(),
        "quota_stats": quota_manager.get_all_statistics(),
        "blocked_count": len(abuse_detector.get_blocked_users()),
    }


class SubscribeRequest(Schema):
    symbol: str
    channel: str = "price"


@router.post("/auth/subscription/pre-check")
def check_subscription_allowance(request, sub_request: SubscribeRequest):
    """
    Check if user can subscribe to a symbol.
    """
    user_id = "anonymous"
    tier = "free"

    auth_payload = getattr(request, "auth_payload", None)
    if auth_payload:
        user_id = auth_payload.user_id
        tier = auth_payload.tier

    current_subs = len(session_manager.get_user_subscriptions(user_id))

    allowed, message = quota_manager.check_subscription_quota(
        user_id, current_subs, tier
    )

    return {
        "allowed": allowed,
        "symbol": sub_request.symbol,
        "current_subscriptions": current_subs,
        "message": message,
    }
