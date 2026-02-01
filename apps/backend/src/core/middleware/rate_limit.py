"""
Rate Limiting Middleware for Django

Implements tiered rate limiting:
- Anonymous users: 100 requests/hour
- Free authenticated users: 1,000 requests/hour
- Premium users: 5,000 requests/hour
- Pro users: 10,000 requests/hour
"""

from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from typing import Callable
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Rate limiting middleware using Redis cache

    Tiers:
    - Anonymous: 100 requests/hour
    - Authenticated (Free): 1,000 requests/hour
    - Authenticated (Premium): 5,000 requests/hour
    - Authenticated (Pro): 10,000 requests/hour
    """

    RATE_LIMITS = {"anonymous": 100, "free": 1000, "premium": 5000, "pro": 10000}

    WINDOW_SECONDS = 3600  # 1 hour

    EXCLUDED_PATHS = [
        "/admin/",
        "/health/",
        "/api/health",
        "/api/health/",
        "/api/health-check/",
        "/api/monitoring/health",
    ]

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return self.get_response(request)

        if hasattr(request, "user") and request.user.is_staff:
            return self.get_response(request)

        identifier = self._get_identifier(request)
        limit = self._get_rate_limit(request)

        if not self._check_rate_limit(identifier, limit):
            return self._rate_limit_exceeded(request, limit)

        response = self.get_response(request)
        response = self._add_rate_limit_headers(response, identifier, limit)

        return response

    def _get_identifier(self, request) -> str:
        if hasattr(request, "user") and request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            ip = self._get_client_ip(request)
            return f"ip:{ip}"

    def _get_client_ip(self, request) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip

    def _get_rate_limit(self, request) -> int:
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return self.RATE_LIMITS["anonymous"]

        try:
            from users.models.user import User

            user = User.objects.get(id=request.user.id)
            if hasattr(user, "subscription_tier"):
                tier = user.subscription_tier
                return self.RATE_LIMITS.get(tier, self.RATE_LIMITS["free"])
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError):
            pass

        return self.RATE_LIMITS["free"]

    def _check_rate_limit(self, identifier: str, limit: int) -> bool:
        cache_key = f"rate_limit:{identifier}"
        current = cache.get(cache_key, 0)

        if current >= limit:
            return False

        cache.set(cache_key, current + 1, self.WINDOW_SECONDS)
        return True

    def _rate_limit_exceeded(self, request, limit: int) -> JsonResponse:
        logger.warning(
            f"Rate limit exceeded for {self._get_identifier(request)} "
            f"(limit: {limit}/hour, path: {request.path})"
        )

        response = JsonResponse(
            {
                "error": "Rate limit exceeded",
                "message": f"Maximum {limit} requests per hour allowed",
                "retry_after": self.WINDOW_SECONDS,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

        response["Retry-After"] = str(self.WINDOW_SECONDS)
        response["X-RateLimit-Limit"] = str(limit)
        response["X-RateLimit-Remaining"] = "0"
        response["X-RateLimit-Reset"] = str(int(time.time()) + self.WINDOW_SECONDS)

        return response

    def _add_rate_limit_headers(self, response, identifier: str, limit: int):
        cache_key = f"rate_limit:{identifier}"
        current = cache.get(cache_key, 0)

        response["X-RateLimit-Limit"] = str(limit)
        response["X-RateLimit-Remaining"] = str(max(0, limit - current))
        response["X-RateLimit-Reset"] = str(int(time.time()) + self.WINDOW_SECONDS)

        return response
