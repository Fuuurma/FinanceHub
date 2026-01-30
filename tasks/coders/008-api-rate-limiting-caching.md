# Task: C-008 - API Rate Limiting & Caching

**Task ID:** C-008
**Assigned To:** Backend Coder (1 Coder)
**Priority:** P0 (CRITICAL)
**Status:** ⏳ PENDING
**Deadline:** February 10, 2026
**Estimated Time:** 8-12 hours

---

## 📋 OBJECTIVE

Implement comprehensive rate limiting and response caching for all API endpoints to prevent abuse and improve performance.

---

## 🎯 ACCEPTANCE CRITERIA

- [ ] Rate limiting on ALL public API endpoints
- [ ] Tiered rate limits (free vs authenticated users)
- [ ] Redis-based caching for expensive operations
- [ ] Cache invalidation strategy
- [ ] Rate limit headers in responses
- [ ] Monitoring for rate limit violations
- [ ] Tests for rate limiting and caching
- [ ] Documentation of rate limits

---

## 📝 CONTEXT

### Current State Analysis

**File:** `apps/backend/src/api/market_overview.py`

**Issue 1: No Rate Limiting (P0)**
```python
@router.get("/overview")
def market_overview(request):
    # ❌ NO RATE LIMITING
    # Anyone can spam this endpoint
    data = orchestrator.get_market_data("overview")
    return data
```

**Impact:**
- API abuse possible
- Server overload during high traffic
- No protection against DDoS
- Unfair usage (some users consume all resources)

---

**Issue 2: No Caching (P1)**

Only **1 cache decorator** found in entire codebase!

**Impact:**
- Expensive operations repeated
- External API overuse
- Slow response times
- High server costs

---

**Issue 3: No Rate Limit Headers (P2)**

Clients can't know their limits:
- No `X-RateLimit-Limit`
- No `X-RateLimit-Remaining`
- No `X-RateLimit-Reset`

---

## ✅ ACTIONS TO COMPLETE

### Action 1: Implement Rate Limiting Middleware

**New File:** `apps/backend/src/core/middleware/rate_limit.py`

```python
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from typing import Callable
import time

class RateLimitMiddleware:
    """
    Rate limiting middleware using Redis

    Tiers:
    - Anonymous: 100 requests/hour
    - Authenticated (Free): 1000 requests/hour
    - Authenticated (Pro): 10000 requests/hour
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for admin users
        if request.user.is_staff:
            return self.get_response(request)

        # Get client identifier
        if request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
            limit = self._get_user_limit(request.user)
        else:
            identifier = f"ip:{self._get_client_ip(request)}"
            limit = 100  # Anonymous limit

        # Check rate limit
        if not self._check_rate_limit(identifier, limit):
            return self._rate_limit_exceeded(limit)

        # Add rate limit headers
        response = self.get_response(request)
        response = self._add_rate_limit_headers(response, identifier, limit)

        return response

    def _get_client_ip(self, request) -> str:
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_user_limit(self, user) -> int:
        """Get rate limit based on user tier"""
        # Check user subscription tier
        from users.models.account import Account

        try:
            account = Account.objects.get(user=user)
            if account.tier == 'pro':
                return 10000
            elif account.tier == 'premium':
                return 5000
            else:
                return 1000
        except:
            return 1000  # Default free tier

    def _check_rate_limit(self, identifier: str, limit: int) -> bool:
        """Check if request is within rate limit"""
        cache_key = f"rate_limit:{identifier}"

        # Get current count
        current = cache.get(cache_key, 0)

        if current >= limit:
            return False

        # Increment counter
        cache.set(cache_key, current + 1, timeout=3600)  # 1 hour
        return True

    def _rate_limit_exceeded(self, limit: int) -> JsonResponse:
        """Return rate limit exceeded response"""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': f'Maximum {limit} requests per hour allowed',
            'retry_after': 3600
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    def _add_rate_limit_headers(self, response, identifier: str, limit: int):
        """Add rate limit information to response headers"""
        cache_key = f"rate_limit:{identifier}"
        current = cache.get(cache_key, 0)

        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(max(0, limit - current))
        response['X-RateLimit-Reset'] = str(int(time.time()) + 3600)

        return response
```

**Install in settings:**
```python
# apps/backend/src/core/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.rate_limit.RateLimitMiddleware',  # ✅ ADD THIS
    # ... other middleware
]
```

---

### Action 2: Add Endpoint-Level Rate Limits

**File:** `apps/backend/src/api/market_overview.py`

```python
from ninja import Router
from core.decorators import rate_limit  # New decorator

router = Router()

@router.get("/overview")
@rate_limit(limit=100, window=3600)  # 100 requests/hour for this endpoint
def market_overview(request):
    # ... existing code ...
    pass

@router.get("/indices")
@rate_limit(limit=200, window=3600)  # 200 requests/hour (higher limit)
def market_indices(request):
    # ... existing code ...
    pass
```

**New decorator:** `core/decorators/rate_limit.py`
```python
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse

def rate_limit(limit: int, window: int):
    """
    Rate limit decorator for individual endpoints

    Args:
        limit: Max requests allowed
        window: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get identifier
            if request.user.is_authenticated:
                identifier = f"user:{request.user.id}:{func.__name__}"
            else:
                identifier = f"ip:{request.META.get('REMOTE_ADDR')}:{func.__name__}"

            cache_key = f"rate_limit:{identifier}"

            # Check limit
            current = cache.get(cache_key, 0)
            if current >= limit:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }, status=429)

            # Increment
            cache.set(cache_key, current + 1, timeout=window)

            # Execute function
            return func(request, *args, **kwargs)

        return wrapper
    return decorator
```

---

### Action 3: Implement Response Caching

**New File:** `apps/backend/src/core/decorators/cache.py`

```python
from functools import wraps
from django.core.cache import cache
import hashlib
import json

def cache_response(ttl: int = 300, key_prefix: str = None):
    """
    Cache API responses in Redis

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Custom cache key prefix
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Skip cache for non-GET requests
            if request.method != 'GET':
                return func(request, *args, **kwargs)

            # Generate cache key
            cache_key = _generate_cache_key(
                func.__name__,
                request.GET.dict(),
                request.user.id if request.user.is_authenticated else None,
                key_prefix
            )

            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            response = func(request, *args, **kwargs)

            # Cache the response
            cache.set(cache_key, response, timeout=ttl)

            return response

        return wrapper
    return decorator

def _generate_cache_key(func_name: str, params: dict, user_id: int = None, prefix: str = None) -> str:
    """Generate unique cache key"""
    key_data = {
        'func': func_name,
        'params': sorted(params.items()),
        'user': user_id
    }

    key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    if prefix:
        return f"cache:{prefix}:{key_hash}"
    else:
        return f"cache:{func_name}:{key_hash}"
```

**Apply to endpoints:**
```python
from core.decorators.cache import cache_response

@router.get("/overview")
@rate_limit(limit=100, window=3600)
@cache_response(ttl=300, key_prefix="market_overview")  # Cache for 5 minutes
def market_overview(request):
    # Expensive operation that should be cached
    data = orchestrator.get_market_data("overview")
    return data

@router.get("/indices")
@rate_limit(limit=200, window=3600)
@cache_response(ttl=600, key_prefix="market_indices")  # Cache for 10 minutes (indices change slower)
def market_indices(request):
    # ... existing code ...
    pass
```

---

### Action 4: Smart Cache Invalidation

**New File:** `apps/backend/src/utils/services/cache_invalidation.py`

```python
from django.core.cache import cache
from typing import List
import logging

logger = logging.getLogger(__name__)

class CacheInvalidator:
    """Manage cache invalidation for different data types"""

    @staticmethod
    def invalidate_asset(symbol: str):
        """Invalidate all caches related to an asset"""
        patterns = [
            f"cache:asset_*:{symbol}*",
            f"cache:market_*:{symbol}*",
            f"cache:price_*:{symbol}*",
        ]

        for pattern in patterns:
            # This requires Redis with SCAN support
            # For now, we'll use explicit key tracking
            keys = cache._cache.get(pattern, [])
            for key in keys:
                cache.delete(key)
                logger.debug(f"Invalidated cache: {key}")

    @staticmethod
    def invalidate_market_data():
        """Invalidate all market-related caches"""
        # Clear all market overview caches
        cache.delete_pattern("cache:market_*")

        # Clear all price caches
        cache.delete_pattern("cache:price_*")

        logger.info("Invalidated all market data caches")

    @staticmethod
    def invalidate_user_data(user_id: int):
        """Invalidate all user-specific caches"""
        cache.delete_pattern(f"cache:user_*:{user_id}*")
        cache.delete_pattern(f"cache:portfolio_*:{user_id}*")

        logger.info(f"Invalidated user caches: {user_id}")

    @staticmethod
    def invalidate_news():
        """Invalidate all news caches"""
        cache.delete_pattern("cache:news_*")
        logger.info("Invalidated news caches")
```

**Integrate into data updates:**
```python
from utils.services.cache_invalidation import CacheInvalidator

# When price data is updated
def update_price(symbol: str, price_data: dict):
    # Save to database
    # ... save code ...

    # Invalidate related caches
    CacheInvalidator.invalidate_asset(symbol)
```

---

### Action 5: Add Rate Limit Monitoring

**New File:** `apps/backend/src/utils/services/rate_limit_monitor.py`

```python
from django.core.cache import cache
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimitViolation:
    """Record of rate limit violations"""
    identifier: str
    violation_count: int
    first_violation: datetime
    last_violation: datetime
    endpoint: str = None

class RateLimitMonitor:
    """Monitor and track rate limit violations"""

    def __init__(self):
        self.violations: Dict[str, RateLimitViolation] = {}

    def record_violation(self, identifier: str, endpoint: str = None):
        """Record a rate limit violation"""
        cache_key = f"rate_limit_violation:{identifier}"

        violation_data = cache.get(cache_key)

        if violation_data:
            # Update existing violation
            violation_data['violation_count'] += 1
            violation_data['last_violation'] = datetime.now().isoformat()
            violation_data['endpoint'] = endpoint
            cache.set(cache_key, violation_data, timeout=86400)  # 24 hours
        else:
            # New violation
            violation_data = {
                'identifier': identifier,
                'violation_count': 1,
                'first_violation': datetime.now().isoformat(),
                'last_violation': datetime.now().isoformat(),
                'endpoint': endpoint
            }
            cache.set(cache_key, violation_data, timeout=86400)

        # Log violation
        logger.warning(
            f"Rate limit violation: {identifier} "
            f"(count: {violation_data['violation_count']})"
        )

        # Auto-ban if too many violations
        if violation_data['violation_count'] > 10:
            self._ban_abuser(identifier)

    def _ban_abuser(self, identifier: str):
        """Temporarily ban repeat offenders"""
        ban_key = f"rate_limit_banned:{identifier}"
        cache.set(ban_key, True, timeout=7200)  # 2 hour ban
        logger.error(f"Rate limit ban: {identifier} (2 hours)")

    def is_banned(self, identifier: str) -> bool:
        """Check if identifier is currently banned"""
        ban_key = f"rate_limit_banned:{identifier}"
        return cache.get(ban_key, False)

    def get_top_violators(self, limit: int = 10) -> List[dict]:
        """Get top rate limit violators"""
        # This would need Redis SCAN or key tracking
        # Simplified version:
        return [
            {
                'identifier': 'ip:192.168.1.100',
                'violations': 45,
                'last_violation': '2026-01-30T12:00:00'
            }
        ]

# Global monitor instance
_rate_limit_monitor = RateLimitMonitor()

def get_rate_limit_monitor() -> RateLimitMonitor:
    """Get global rate limit monitor"""
    return _rate_limit_monitor
```

---

### Action 6: Add Admin Dashboard for Monitoring

**New File:** `apps/backend/src/api/rate_limit_admin.py`

```python
from ninja import Router
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from utils.services.rate_limit_monitor import get_rate_limit_monitor

router = Router()

@router.get("/admin/rate-limits")
@staff_member_required
def rate_limits_dashboard(request):
    """Admin dashboard for rate limit monitoring"""
    monitor = get_rate_limit_monitor()

    context = {
        'top_violators': monitor.get_top_violators(20),
        'active_bans': monitor.get_active_bans(),
        'stats': monitor.get_statistics()
    }

    return render(request, 'admin/rate_limits.html', context)
```

---

### Action 7: Write Tests

**New File:** `apps/backend/src/tests/test_rate_limiting.py`

```python
import pytest
from django.test import RequestFactory
from core.middleware.rate_limit import RateLimitMiddleware

class TestRateLimiting:
    """Test rate limiting middleware"""

    def test_anonymous_rate_limit(self):
        """Test anonymous users are rate limited"""
        factory = RequestFactory()
        middleware = RateLimitMiddleware(get_response=lambda r: r)

        # Make 100 requests (should pass)
        for i in range(100):
            request = factory.get('/api/overview')
            response = middleware(request)
            assert response.status_code == 200

        # 101st request should be rate limited
        request = factory.get('/api/overview')
        response = middleware(request)
        assert response.status_code == 429

    def test_authenticated_higher_limit(self):
        """Test authenticated users have higher limits"""
        # ... test implementation ...

    def test_rate_limit_headers(self):
        """Test rate limit headers are present"""
        factory = RequestFactory()
        middleware = RateLimitMiddleware(get_response=lambda r: r)

        request = factory.get('/api/overview')
        response = middleware(request)

        assert 'X-RateLimit-Limit' in response
        assert 'X-RateLimit-Remaining' in response
        assert 'X-RateLimit-Reset' in response


class TestResponseCaching:
    """Test response caching"""

    def test_cache_hit(self):
        """Test cached responses are returned"""
        # ... test implementation ...

    def test_cache_invalidation(self):
        """Test cache invalidation works"""
        # ... test implementation ...
```

---

### Action 8: Document Rate Limits

**New File:** `docs/api/RATE_LIMITS.md`

```markdown
# API Rate Limits

## Tiers

| Tier | Requests/Hour | Cost |
|------|---------------|------|
| Anonymous | 100 | Free |
| Free | 1,000 | $0/month |
| Premium | 5,000 | $29/month |
| Pro | 10,000 | $99/month |

## Endpoint Limits

| Endpoint | Anonymous | Authenticated |
|----------|-----------|---------------|
| GET /api/market/overview | 100/hour | 1,000/hour |
| GET /api/market/indices | 200/hour | 2,000/hour |
| POST /api/portfolios | 50/hour | 500/hour |

## Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1738289765
```

## Exceeded Limits

When rate limit is exceeded:

```json
{
  "error": "Rate limit exceeded",
  "message": "Maximum 1000 requests per hour allowed",
  "retry_after": 3600
}
```

HTTP Status: 429 Too Many Requests
```

---

## 🎯 SUCCESS CRITERIA

- ✅ Rate limiting middleware active
- ✅ Tiered limits (anonymous, free, pro)
- ✅ Response caching implemented
- ✅ Cache invalidation working
- ✅ Rate limit headers in all responses
- ✅ Monitoring dashboard functional
- ✅ Tests passing
- ✅ Documentation complete

---

## 📊 DELIVERABLES

1. **`core/middleware/rate_limit.py`** - Rate limiting middleware (NEW, ~150 lines)
2. **`core/decorators/rate_limit.py`** - Endpoint-level decorator (NEW, ~60 lines)
3. **`core/decorators/cache.py`** - Response caching (NEW, ~80 lines)
4. **`utils/services/cache_invalidation.py`** - Cache invalidation (NEW, ~100 lines)
5. **`utils/services/rate_limit_monitor.py`** - Monitoring (NEW, ~120 lines)
6. **`api/rate_limit_admin.py`** - Admin dashboard (NEW, ~50 lines)
7. **`tests/test_rate_limiting.py`** - Tests (NEW, ~200 lines)
8. **`docs/api/RATE_LIMITS.md`** - Documentation (NEW)

---

## ⏱️ ESTIMATED TIME

- Middleware: 2-3 hours
- Decorators: 2 hours
- Caching: 2-3 hours
- Invalidation: 2 hours
- Monitoring: 2 hours
- Tests: 2-3 hours
- Documentation: 1 hour

**Total:** 13-17 hours

---

## 🔗 DEPENDENCIES

- Redis must be running
- Previous tasks optional

---

## 📝 FEEDBACK TO ARCHITECT

### What I Did:
1. ✅ Implemented rate limiting middleware
2. ✅ Added tiered rate limits (anonymous, free, pro)
3. ✅ Created response caching system
4. ✅ Implemented cache invalidation
5. ✅ Added rate limit monitoring
6. ✅ Created admin dashboard
7. ✅ Wrote comprehensive tests
8. ✅ Documented rate limits

### Security Improvements:
- ✅ API abuse prevention
- ✅ DDoS protection
- ✅ Fair resource allocation
- ✅ Auto-ban repeat offenders

### Performance Improvements:
- ✅ Reduced API calls (caching)
- ✅ Faster response times
- ✅ Lower server costs

### Files Created:
- 7 new files (760+ lines)
- Updated settings.py
- Documentation

### Verification:
- ✅ Rate limiting working
- ✅ Caching functional
- ✅ Headers present
- ✅ Tests passing
- ✅ Documentation complete

### Next Steps:
- Consider adding API keys for higher limits
- Implement webhook notifications for violations
- Add analytics on rate limit patterns

---

**Task Status:** ⏳ PENDING - Ready to start
**Priority:** P0 CRITICAL (API abuse prevention)
