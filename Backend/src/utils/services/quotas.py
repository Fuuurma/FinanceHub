import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    user_id: str
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: datetime
    limit_type: str
    message: str = ""


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for WebSocket connections.
    Uses a sliding window algorithm for accurate rate limiting.
    """

    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._window_size_seconds = 60

    def _cleanup_old_requests(self, user_id: str, now: float):
        """Remove requests outside the current window."""
        cutoff = now - self._window_size_seconds
        self._requests[user_id] = [
            ts for ts in self._requests[user_id] if ts > cutoff
        ]

    def check_rate_limit(
        self,
        user_id: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> RateLimitResult:
        """
        Check if request is within rate limit.

        Args:
            user_id: User identifier
            max_requests: Maximum allowed requests in window
            window_seconds: Time window in seconds

        Returns:
            RateLimitResult with decision and metadata
        """
        now = time.time()
        self._window_size_seconds = window_seconds

        self._cleanup_old_requests(user_id, now)

        request_count = len(self._requests[user_id])

        if request_count >= max_requests:
            oldest = self._requests[user_id][0]
            reset_at = datetime.fromtimestamp(oldest + window_seconds)

            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=reset_at,
                limit_type="minute",
                message=f"Rate limit exceeded. Try again at {reset_at.isoformat()}"
            )

        self._requests[user_id].append(now)

        return RateLimitResult(
            allowed=True,
            remaining=max_requests - request_count - 1,
            reset_at=datetime.fromtimestamp(now + window_seconds),
            limit_type="minute",
            message=""
        )

    def get_usage(self, user_id: str, window_seconds: int = 60) -> Tuple[int, float]:
        """Get current usage statistics for a user."""
        now = time.time()
        self._cleanup_old_requests(user_id, now)
        return (len(self._requests[user_id]), now)

    def reset(self, user_id: str):
        """Reset rate limit for a user."""
        self._requests[user_id] = []

    def get_remaining_requests(self, user_id: str, max_requests: int) -> int:
        """Get remaining requests for a user."""
        now = time.time()
        self._cleanup_old_requests(user_id, now)
        return max(0, max_requests - len(self._requests[user_id]))


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for WebSocket connections.
    Allows burst traffic while maintaining average rate limits.
    """

    def __init__(self):
        self._tokens: Dict[str, float] = defaultdict(float)
        self._last_update: Dict[str, float] = {}

    def _refill_tokens(self, user_id: str, rate_per_second: float, capacity: float):
        """Refill tokens based on elapsed time."""
        now = time.time()

        if user_id in self._last_update:
            elapsed = now - self._last_update[user_id]
            tokens_to_add = elapsed * rate_per_second
            self._tokens[user_id] = min(
                capacity,
                self._tokens[user_id] + tokens_to_add
            )
        else:
            self._tokens[user_id] = capacity

        self._last_update[user_id] = now

    def consume(
        self,
        user_id: str,
        tokens: int = 1,
        rate_per_second: float = 1.0,
        capacity: float = 60.0
    ) -> bool:
        """
        Attempt to consume tokens from the bucket.

        Returns:
            True if tokens were consumed, False if bucket is empty
        """
        self._refill_tokens(user_id, rate_per_second, capacity)

        if self._tokens[user_id] >= tokens:
            self._tokens[user_id] -= tokens
            return True

        return False

    def get_remaining_tokens(self, user_id: str, capacity: float = 60.0) -> float:
        """Get remaining tokens for a user."""
        now = time.time()

        if user_id in self._last_update:
            elapsed = now - self._last_update[user_id]
            rate_per_second = capacity / 60.0
            tokens_to_add = elapsed * rate_per_second
            return min(capacity, self._tokens[user_id] + tokens_to_add)

        return capacity

    def reset(self, user_id: str):
        """Reset token bucket for a user."""
        self._tokens[user_id] = 0
        self._last_update[user_id] = time.time()


class ConnectionRateLimiter:
    """
    Rate limiter specifically for WebSocket connection attempts.
    Limits how frequently users can establish new connections.
    """

    def __init__(self):
        self._connection_attempts: Dict[str, List[float]] = defaultdict(list)
        self._connection_rate = 5  # Max connections per minute
        self._burst_limit = 2  # Burst limit

    def check_connection_rate_limit(self, user_id: str) -> RateLimitResult:
        """Check if connection attempt is within rate limit."""
        now = time.time()
        window = 60  # 1 minute window

        self._connection_attempts[user_id] = [
            ts for ts in self._connection_attempts[user_id] if ts > now - window
        ]

        attempt_count = len(self._connection_attempts[user_id])

        if attempt_count >= self._connection_rate:
            oldest = self._connection_attempts[user_id][0]
            reset_at = datetime.fromtimestamp(oldest + window)

            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=reset_at,
                limit_type="connection",
                message="Too many connection attempts. Please wait."
            )

        self._connection_attempts[user_id].append(now)

        return RateLimitResult(
            allowed=True,
            remaining=self._connection_rate - attempt_count - 1,
            reset_at=datetime.fromtimestamp(now + window),
            limit_type="connection",
            message=""
        )


class SubscriptionRateLimiter:
    """
    Rate limiter for subscription requests.
    Limits how many symbols a user can subscribe to per time period.
    """

    def __init__(self):
        self._subscription_requests: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self._max_subscriptions_per_minute = 20
        self._max_subscriptions_per_hour = 100

    def check_subscription_limit(
        self,
        user_id: str,
        current_subscriptions: int,
        max_subscriptions: int
    ) -> Tuple[bool, str]:
        """
        Check if user can subscribe to more symbols.

        Returns:
            Tuple of (allowed, message)
        """
        now = time.time()
        window_minute = 60
        window_hour = 3600

        minute_requests = [
            (sym, ts) for sym, ts in self._subscription_requests[user_id]
            if ts > now - window_minute
        ]

        if len(minute_requests) >= self._max_subscriptions_per_minute:
            return False, "Too many subscription requests per minute"

        if current_subscriptions >= max_subscriptions:
            return False, f"Subscription limit reached ({max_subscriptions} symbols)"

        return True, ""

    def record_subscription(self, user_id: str, symbol: str):
        """Record a subscription request."""
        now = time.time()
        self._subscription_requests[user_id].append((symbol.upper(), now))

    def record_unsubscription(self, user_id: str, symbol: str):
        """Record an unsubscription."""
        now = time.time()
        self._subscription_requests[user_id] = [
            (sym, ts) for sym, ts in self._subscription_requests[user_id]
            if sym != symbol.upper() or ts < now - 60
        ]

    def get_subscription_stats(self, user_id: str) -> Dict[str, int]:
        """Get subscription statistics for a user."""
        now = time.time()

        recent_subscriptions = [
            (sym, ts) for sym, ts in self._subscription_requests[user_id]
            if ts > now - 60
        ]

        return {
            'requests_last_minute': len(recent_subscriptions),
            'max_per_minute': self._max_subscriptions_per_minute
        }


class MessageRateLimiter:
    """
    Rate limiter for WebSocket messages.
    Limits message frequency for users.
    """

    def __init__(self):
        self._message_timestamps: Dict[str, List[float]] = defaultdict(list)
        self._max_messages_per_second = 10
        self._max_messages_per_minute = 300

    def check_message_limit(self, user_id: str) -> RateLimitResult:
        """Check if message is within rate limit."""
        now = time.time()
        window = 60

        self._message_timestamps[user_id] = [
            ts for ts in self._message_timestamps[user_id]
            if ts > now - window
        ]

        message_count = len(self._message_timestamps[user_id])

        if message_count >= self._max_messages_per_minute:
            oldest = self._message_timestamps[user_id][0]
            reset_at = datetime.fromtimestamp(oldest + window)

            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=reset_at,
                limit_type="message",
                message="Message rate limit exceeded"
            )

        self._message_timestamps[user_id].append(now)

        return RateLimitResult(
            allowed=True,
            remaining=self._max_messages_per_minute - message_count - 1,
            reset_at=datetime.fromtimestamp(now + window),
            limit_type="message",
            message=""
        )

    def get_message_count(self, user_id: str) -> int:
        """Get message count for a user."""
        now = time.time()
        window = 60

        return len([
            ts for ts in self._message_timestamps[user_id]
            if ts > now - window
        ])


class QuotaManager:
    """
    Central quota manager for all WebSocket limits.
    Coordinates rate limiting across different dimensions.
    """

    def __init__(self):
        self._rate_limiter = SlidingWindowRateLimiter()
        self._token_bucket = TokenBucketRateLimiter()
        self._connection_limiter = ConnectionRateLimiter()
        self._subscription_limiter = SubscriptionRateLimiter()
        self._message_limiter = MessageRateLimiter()

        self._tier_config: Dict[str, Dict] = {
            'free': {
                'requests_per_minute': 30,
                'connections': 1,
                'subscriptions': 10,
                'messages_per_minute': 100
            },
            'basic': {
                'requests_per_minute': 120,
                'connections': 3,
                'subscriptions': 50,
                'messages_per_minute': 500
            },
            'pro': {
                'requests_per_minute': 300,
                'connections': 5,
                'subscriptions': 200,
                'messages_per_minute': 1500
            },
            'enterprise': {
                'requests_per_minute': 1000,
                'connections': 10,
                'subscriptions': 1000,
                'messages_per_minute': 5000
            }
        }

    def get_tier_config(self, tier: str) -> Dict:
        """Get configuration for a tier."""
        return self._tier_config.get(tier, self._tier_config['free'])

    def check_connection_quota(self, user_id: str, tier: str = 'free') -> RateLimitResult:
        """Check connection quota for a user."""
        return self._connection_limiter.check_connection_rate_limit(user_id)

    def check_subscription_quota(
        self,
        user_id: str,
        current_count: int,
        tier: str = 'free'
    ) -> Tuple[bool, str]:
        """Check subscription quota for a user."""
        config = self.get_tier_config(tier)
        max_subs = config['subscriptions']

        return self._subscription_limiter.check_subscription_limit(
            user_id, current_count, max_subs
        )

    def check_message_quota(self, user_id: str) -> RateLimitResult:
        """Check message quota for a user."""
        return self._message_limiter.check_message_limit(user_id)

    def check_rate_limit(
        self,
        user_id: str,
        tier: str = 'free'
    ) -> RateLimitResult:
        """Check general rate limit for a user."""
        config = self.get_tier_config(tier)
        rpm = config['requests_per_minute']

        return self._rate_limiter.check_rate_limit(user_id, rpm)

    def record_subscription(self, user_id: str, symbol: str):
        """Record a subscription."""
        self._subscription_limiter.record_subscription(user_id, symbol)

    def record_unsubscription(self, user_id: str, symbol: str):
        """Record an unsubscription."""
        self._subscription_limiter.record_unsubscription(user_id, symbol)

    def get_user_statistics(self, user_id: str, tier: str = 'free') -> Dict:
        """Get comprehensive statistics for a user."""
        config = self.get_tier_config(tier)

        return {
            'rate_limit': {
                'remaining': self._rate_limiter.get_remaining_requests(
                    user_id, config['requests_per_minute']
                ),
                'max_per_minute': config['requests_per_minute']
            },
            'subscriptions': self._subscription_limiter.get_subscription_stats(user_id),
            'messages': {
                'count_last_minute': self._message_limiter.get_message_count(user_id),
                'max_per_minute': config['messages_per_minute']
            }
        }

    def get_all_statistics(self) -> Dict:
        """Get aggregated statistics."""
        return {
            'active_users': len(self._rate_limiter._requests),
            'tier_distribution': self._get_tier_stats()
        }

    def _get_tier_stats(self) -> Dict[str, int]:
        """Get tier distribution stats."""
        return {
            'free': len(self._rate_limiter._requests),
            'basic': 0,
            'pro': 0,
            'enterprise': 0
        }


class AbuseDetector:
    """
    Detects and prevents WebSocket abuse.
    Tracks suspicious patterns and auto-blocks abusers.
    """

    def __init__(self):
        self._suspicious_activity: Dict[str, List[Dict]] = defaultdict(list)
        self._blocked_users: Dict[str, datetime] = {}
        self._block_duration_minutes = 15
        self._suspicious_threshold = 10

    def record_suspicious_activity(
        self,
        user_id: str,
        activity_type: str,
        details: str
    ):
        """Record suspicious activity for a user."""
        now = datetime.now()

        self._suspicious_activity[user_id].append({
            'type': activity_type,
            'details': details,
            'timestamp': now
        })

        recent_count = len([
            a for a in self._suspicious_activity[user_id]
            if (now - a['timestamp']).total_seconds() < 300  # Last 5 minutes
        ])

        if recent_count >= self._suspicious_threshold:
            self._block_user(user_id)

    def _block_user(self, user_id: str):
        """Block a user."""
        expires = datetime.now() + timedelta(minutes=self._block_duration_minutes)
        self._blocked_users[user_id] = expires
        logger.warning(f"User {user_id} blocked for abuse detection")

    def is_blocked(self, user_id: str) -> bool:
        """Check if a user is blocked."""
        if user_id in self._blocked_users:
            expires = self._blocked_users[user_id]
            if datetime.now() < expires:
                return True
            else:
                del self._blocked_users[user_id]
        return False

    def unblock_user(self, user_id: str):
        """Manually unblock a user."""
        if user_id in self._blocked_users:
            del self._blocked_users[user_id]
            logger.info(f"User {user_id} manually unblocked")

    def get_blocked_users(self) -> List[str]:
        """Get list of currently blocked users."""
        now = datetime.now()
        return [
            uid for uid, expires in self._blocked_users.items()
            if now < expires
        ]

    def get_abuse_report(self, user_id: str) -> List[Dict]:
        """Get abuse report for a user."""
        return self._suspicious_activity.get(user_id, [])


rate_limiter = SlidingWindowRateLimiter()
token_bucket = TokenBucketRateLimiter()
connection_rate_limiter = ConnectionRateLimiter()
subscription_rate_limiter = SubscriptionRateLimiter()
message_rate_limiter = MessageRateLimiter()
quota_manager = QuotaManager()
abuse_detector = AbuseDetector()
