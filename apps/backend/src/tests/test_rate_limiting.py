"""
Tests for Rate Limiting and Caching

Comprehensive tests for the rate limiting middleware, decorators, and caching system.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, override_settings
from django.http import JsonResponse
from django.core.cache import cache

from core.middleware.rate_limit import RateLimitMiddleware
from core.decorators.rate_limit import rate_limit, cache_response, EndpointRateLimit
from utils.services.rate_limit_monitor import RateLimitMonitor, get_rate_limit_monitor
from utils.services.cache_invalidation import CacheInvalidator, SmartCache


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware"""

    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=JsonResponse({"status": "ok"}))

    def teardown_method(self, method):
        """Clean up after tests"""
        cache.clear()

    def test_middleware_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed"""
        middleware = RateLimitMiddleware(self.get_response)

        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False
        request.user.is_staff = False

        response = middleware(request)

        assert response.status_code == 200

    def test_anonymous_rate_limit_enforced(self):
        """Test that anonymous users are rate limited to 100/hour"""
        middleware = RateLimitMiddleware(self.get_response)

        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False
        request.user.is_staff = False

        identifier = "ip:127.0.0.1"
        cache_key = f"rate_limit:{identifier}"
        cache.set(cache_key, 99, 3600)

        response = middleware(request)
        assert response.status_code == 200
        assert response["X-RateLimit-Remaining"] == "0"

    def test_rate_limit_exceeded_returns_429(self):
        """Test that exceeding rate limit returns 429"""
        middleware = RateLimitMiddleware(self.get_response)

        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False
        request.user.is_staff = False

        identifier = "ip:127.0.0.1"
        cache_key = f"rate_limit:{identifier}"
        cache.set(cache_key, 100, 3600)

        response = middleware(request)

        assert response.status_code == 429
        assert "Rate limit exceeded" in response.content.decode()

    def test_admin_users_skip_rate_limiting(self):
        """Test that admin users bypass rate limiting"""
        middleware = RateLimitMiddleware(self.get_response)

        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.user.is_staff = True

        response = middleware(request)

        assert response.status_code == 200

    def test_excluded_paths_skip_rate_limiting(self):
        """Test that excluded paths bypass rate limiting"""
        middleware = RateLimitMiddleware(self.get_response)

        for path in ["/admin/", "/api/health/", "/api/health-check/"]:
            request = self.factory.get(path)
            request.user = MagicMock()
            request.user.is_authenticated = False
            request.user.is_staff = False

            response = middleware(request)

            assert response.status_code == 200

    def test_rate_limit_headers_present(self):
        """Test that rate limit headers are present in response"""
        middleware = RateLimitMiddleware(self.get_response)

        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False
        request.user.is_staff = False

        response = middleware(request)

        assert "X-RateLimit-Limit" in response
        assert "X-RateLimit-Remaining" in response
        assert "X-RateLimit-Reset" in response

    def test_authenticated_user_higher_limit(self):
        """Test that authenticated users have higher rate limits"""
        middleware = RateLimitMiddleware(self.get_response)

        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.user.is_staff = False
        request.user.id = 1

        with patch.object(
            RateLimitMiddleware, "_get_client_ip", return_value="127.0.0.1"
        ):
            response = middleware(request)

        assert response.status_code == 200
        assert int(response["X-RateLimit-Limit"]) > 100


class TestRateLimitDecorator:
    """Tests for the rate_limit decorator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()

    def teardown_method(self, method):
        """Clean up after tests"""
        cache.clear()

    def sample_endpoint(self, request):
        """Sample endpoint for testing"""
        return JsonResponse({"status": "ok"})

    def test_rate_limit_decorator_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed"""
        decorated = rate_limit(limit=5, window=60)(self.sample_endpoint)
        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False

        for i in range(5):
            response = decorated(request)
            assert response.status_code == 200

    def test_rate_limit_decorator_blocks_exceeded_requests(self):
        """Test that exceeding the limit returns 429"""
        decorated = rate_limit(limit=5, window=60)(self.sample_endpoint)
        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False

        ip = request.META.get("REMOTE_ADDR", "unknown")
        cache_key = f"rl:sample_endpoint:ip:{ip}"
        cache.set(cache_key, 5, 60)

        response = decorated(request)

        assert response.status_code == 429
        assert "Rate limit exceeded" in response.content.decode()


class TestCacheResponseDecorator:
    """Tests for the cache_response decorator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()

    def teardown_method(self, method):
        """Clean up after tests"""
        cache.clear()

    def cached_endpoint(self, request):
        """Sample cached endpoint"""
        return JsonResponse({"data": "fresh", "timestamp": "2026-01-30"})

    def test_cache_miss_returns_fresh_response(self):
        """Test that cache miss returns fresh response"""
        decorated = cache_response(ttl=300, key_prefix="test_endpoint")(
            self.cached_endpoint
        )
        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False

        response = decorated(request)

        assert response.status_code == 200
        assert response["X-Cache"] == "MISS"
        assert "fresh" in response.content.decode()

    def test_cache_hit_returns_cached_response(self):
        """Test that cache hit returns cached response"""
        decorated = cache_response(ttl=300, key_prefix="test_endpoint")(
            self.cached_endpoint
        )
        request = self.factory.get("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False

        import hashlib
        import json

        key_data = {"func": "cached_endpoint", "params": [], "user": None}
        key_hash = hashlib.md5(
            json.dumps(key_data, sort_keys=True, default=str).encode()
        ).hexdigest()
        cache_key = f"cache:test_endpoint:{key_hash}"
        cache.set(cache_key, {"data": "cached"}, 300)

        response = decorated(request)

        assert response.status_code == 200
        assert response["X-Cache"] == "HIT"
        assert "cached" in response.content.decode()

    def test_cache_does_not_cache_post_requests(self):
        """Test that POST requests bypass caching"""
        decorated = cache_response(ttl=300, key_prefix="test_endpoint")(
            self.cached_endpoint
        )
        request = self.factory.post("/api/test")
        request.user = MagicMock()
        request.user.is_authenticated = False

        response = decorated(request)

        assert response.status_code == 200
        assert response.get("X-Cache") is None


class TestEndpointRateLimit:
    """Tests for EndpointRateLimit configuration"""

    def test_get_limit_returns_endpoint_specific_limit(self):
        """Test that endpoint-specific limits are returned"""
        limit = EndpointRateLimit.get_limit("market_overview")
        assert limit["limit"] == 100
        assert limit["window"] == 3600

    def test_get_limit_returns_default_for_unknown_endpoint(self):
        """Test that default limits are returned for unknown endpoints"""
        limit = EndpointRateLimit.get_limit("unknown_endpoint", "GET")
        assert limit["limit"] == 1000
        assert limit["window"] == 3600

    def test_get_limit_respects_method(self):
        """Test that limits vary by HTTP method"""
        get_limit = EndpointRateLimit.get_limit("portfolio_list", "GET")
        post_limit = EndpointRateLimit.get_limit("portfolio_create", "POST")

        assert get_limit["limit"] == 100
        assert post_limit["limit"] == 20


class TestRateLimitMonitor:
    """Tests for RateLimitMonitor"""

    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = RateLimitMonitor()

    def teardown_method(self, method):
        """Clean up after tests"""
        cache.clear()

    def test_record_violation_creates_record(self):
        """Test that recording a violation creates a record"""
        self.monitor.record_violation("test_user", "/api/test")

        cache_key = "rl_violation:test_user"
        data = cache.get(cache_key)

        assert data is not None
        assert data["violation_count"] == 1
        assert data["identifier"] == "test_user"

    def test_multiple_violations_increment_count(self):
        """Test that multiple violations increment the count"""
        self.monitor.record_violation("test_user", "/api/test")
        self.monitor.record_violation("test_user", "/api/test")
        self.monitor.record_violation("test_user", "/api/test")

        cache_key = "rl_violation:test_user"
        data = cache.get(cache_key)

        assert data["violation_count"] == 3

    def test_ban_triggered_after_threshold(self):
        """Test that ban is triggered after threshold violations"""
        for i in range(10):
            self.monitor.record_violation("abuser", "/api/test")

        assert self.monitor.is_banned("abuser") is True

    def test_is_banned_returns_false_for_normal_users(self):
        """Test that normal users are not banned"""
        assert self.monitor.is_banned("normal_user") is False

    def test_get_stats_returns_statistics(self):
        """Test that get_stats returns correct statistics"""
        self.monitor.record_violation("user1", "/api/test")
        self.monitor.record_violation("user1", "/api/test")
        self.monitor.record_violation("user2", "/api/test")

        stats = self.monitor.get_stats()

        assert stats["total_violations"] == 3
        assert stats["unique_abusers"] == 2
        assert "active_bans" in stats


class TestCacheInvalidator:
    """Tests for CacheInvalidator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.invalidator = CacheInvalidator()

    def teardown_method(self, method):
        """Clean up after tests"""
        cache.clear()
        CacheInvalidator.TRACKED_KEYS = {
            "market_overview": [],
            "market_indices": [],
            "asset_detail": [],
            "asset_search": [],
            "portfolio": [],
            "watchlist": [],
            "alerts": [],
            "news": [],
        }

    def test_track_cache_key_adds_to_list(self):
        """Test that tracking cache keys works"""
        CacheInvalidator.track_cache_key("market_overview", "key1")
        CacheInvalidator.track_cache_key("market_overview", "key2")

        assert "key1" in CacheInvalidator.TRACKED_KEYS["market_overview"]
        assert "key2" in CacheInvalidator.TRACKED_KEYS["market_overview"]

    def test_invalidate_asset_removes_related_caches(self):
        """Test that invalidating an asset removes related caches"""
        cache.set("cache:asset_detail:symbol1", {"data": "test"}, 300)
        cache.set("cache:asset_search:symbol1", {"data": "test"}, 300)
        CacheInvalidator.track_cache_key("asset_detail", "cache:asset_detail:symbol1")

        CacheInvalidator.invalidate_asset("symbol1")

        assert cache.get("cache:asset_detail:symbol1") is None
        assert cache.get("cache:asset_search:symbol1") is None


class TestSmartCache:
    """Tests for SmartCache"""

    def setup_method(self):
        """Set up test fixtures"""
        self.smart_cache = SmartCache("test_category")

    def teardown_method(self, method):
        """Clean up after tests"""
        cache.clear()
        CacheInvalidator.TRACKED_KEYS = {
            "market_overview": [],
            "market_indices": [],
            "asset_detail": [],
            "asset_search": [],
            "portfolio": [],
            "watchlist": [],
            "alerts": [],
            "news": [],
        }

    def test_set_tracks_key(self):
        """Test that setting a value tracks the key"""
        self.smart_cache.set("test_key", {"data": "test"}, 300)

        assert "test_key" in CacheInvalidator.TRACKED_KEYS["test_category"]

    def test_get_retrieves_value(self):
        """Test that getting a value works"""
        self.smart_cache.set("test_key", {"data": "test"}, 300)

        result = self.smart_cache.get("test_key")

        assert result == {"data": "test"}

    def test_invalidate_all_clears_category(self):
        """Test that invalidating all clears the category"""
        self.smart_cache.set("key1", {"data": "test1"}, 300)
        self.smart_cache.set("key2", {"data": "test2"}, 300)

        self.smart_cache.invalidate_all()

        assert self.smart_cache.get("key1") is None
        assert self.smart_cache.get("key2") is None


class TestRateLimitConfiguration:
    """Tests for rate limit configuration"""

    def test_middleware_rate_limits_are_configured(self):
        """Test that middleware has correct rate limits configured"""
        assert RateLimitMiddleware.RATE_LIMITS["anonymous"] == 100
        assert RateLimitMiddleware.RATE_LIMITS["free"] == 1000
        assert RateLimitMiddleware.RATE_LIMITS["premium"] == 5000
        assert RateLimitMiddleware.RATE_LIMITS["pro"] == 10000

    def test_middleware_window_is_one_hour(self):
        """Test that the rate limit window is one hour"""
        assert RateLimitMiddleware.WINDOW_SECONDS == 3600


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
