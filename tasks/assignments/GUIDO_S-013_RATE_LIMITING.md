# 📋 Task Assignment: S-013 Rate Limiting

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Guido (Backend Coder)
**Priority:** HIGH - Security Critical
**Estimated Effort:** 3-5 hours
**Timeline:** Start after S-012, no deadline (quality-driven)

---

## 🎯 OVERVIEW

Implement rate limiting on all public API endpoints to prevent abuse, DDoS attacks, and ensure fair usage.

**Context:**
- Security audit identified missing rate limits
- Charo approved this task as P1 HIGH priority
- Prevents API abuse, protects backend resources

---

## 📋 YOUR TASKS

### Task 1: Identify Endpoints to Rate Limit (1h)

**High Priority (Public endpoints):**
```
POST /api/auth/login - 5 requests/minute
POST /api/auth/register - 3 requests/hour
POST /api/auth/forgot-password - 3 requests/hour
GET /api/assets/search - 60 requests/minute
GET /api/sentiment/trending - 30 requests/minute
POST /api/sentiment/analyze - 20 requests/minute
```

**Medium Priority (Authenticated endpoints):**
```
POST /api/trading/orders - 60 requests/minute
GET /api/portfolio - 120 requests/minute
POST /api/sentiment/alerts - 10 requests/minute
```

**Create prioritized list:**
- Public endpoints (no auth required) - STRICT limits
- Authenticated endpoints - Moderate limits
- Admin endpoints - Per-user limits

### Task 2: Install Rate Limiting Library (30m)

**Use Django Ratelimit:**
```bash
pip install django-ratelimit
```

**Add to settings:**
```python
# apps/backend/settings.py
INSTALLED_APPS = [
    ...
    'ratelimit',
]

# Cache backend for rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Task 3: Implement Rate Limiting (2-3h)

**Option A: Decorator-based (simple)**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    """Limit to 5 login attempts per minute per IP"""
    if request.limited:
        return JsonResponse({'error': 'Too many attempts'}, status=429)
    # ... login logic
```

**Option B: Django Ninja integration (better)**
```python
from ninja import Router
from django_ratelimit.decorators import ratelimit

router = Router()

@router.post("/login")
@ratelimit(key='ip', rate='5/m', method='POST')
def login(request, data: LoginSchema):
    """Login with rate limiting"""
    if getattr(request, 'limited', False):
        return 429, {'error': 'Too many attempts'}
    # ... login logic
```

**Rate Limiting Keys:**
- `key='ip'` - Rate limit by IP address
- `key='user'` - Rate limit by authenticated user
- `key='header:X-API-Key'` - Rate limit by API key

**Rate Formats:**
- `5/m` - 5 requests per minute
- `100/h` - 100 requests per hour
- `1000/d` - 1000 requests per day

**Implementation Examples:**

**Auth endpoints (strict):**
```python
@router.post("/auth/login")
@ratelimit(key='ip', rate='5/m', method='POST')
def login(request, data: LoginSchema):
    if getattr(request, 'limited', False):
        return 429, {
            'error': 'Too many login attempts',
            'retry_after': 60  # seconds
        }
    # ... login logic
```

**Search endpoints (moderate):**
```python
@router.get("/assets/search")
@ratelimit(key='user_or_ip', rate='60/m')
def search_assets(request, q: str):
    if getattr(request, 'limited', False):
        return 429, {'error': 'Rate limit exceeded'}
    # ... search logic
```

**Trading endpoints (user-based):**
```python
@router.post("/trading/orders")
@ratelimit(key='user', rate='60/m')
def create_order(request, data: OrderSchema):
    if getattr(request, 'limited', False):
        return 429, {'error': 'Order rate limit exceeded'}
    # ... order logic
```

### Task 4: Custom Rate Limiting Logic (1h)

**Smart rate limiting for authenticated users:**
```python
from django_ratelimit.core import is_ratelimited

def get_rate_limit_key(request):
    """Return user ID if authenticated, else IP"""
    if request.user.is_authenticated:
        return f'user:{request.user.id}'
    return f'ip:{get_client_ip(request)}'

@router.post("/api/trading/orders")
def create_order(request, data: OrderSchema):
    """Rate limit: 60/m for users, 10/m for anonymous"""
    key = get_rate_limit_key(request)
    rate = '60/m' if request.user.is_authenticated else '10/m'

    if is_ratelimited(request, key=key, rate=rate, increment=True):
        return 429, {'error': 'Rate limit exceeded'}

    # ... order logic
```

**Burst allowance (allow short bursts):**
```python
@ratelimit(key='user', rate='100/m', block=True)
def endpoint(request):
    """Allow bursts up to 100, then block"""
    # ... logic
```

### Task 5: Add Rate Limit Headers (30m)

**Return rate limit info in response headers:**
```python
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import get_usage

@router.post("/api/search")
@ratelimit(key='user', rate='60/m')
def search(request, q: str):
    if getattr(request, 'limited', False):
        return 429, {'error': 'Rate limit exceeded'}

    usage = get_usage(request, key='user', rate='60/m')
    return 200, {
        'results': [...]
    }, headers={
        'X-RateLimit-Limit': '60',
        'X-RateLimit-Remaining': str(usage['limit'] - usage['count']),
        'X-RateLimit-Reset': str(usage['reset'])
    }
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] All public endpoints have rate limits
- [ ] All authenticated endpoints have rate limits
- [ ] Rate limits configured by endpoint type (public < auth < admin)
- [ ] Returns 429 status when limit exceeded
- [ ] Includes Retry-After header
- [ ] Uses cache backend for distributed systems
- [ ] Tests verify rate limiting works

---

## 🧪 TESTING

**Test rate limiting:**
```python
import pytest
from rest_framework.test import APIClient

def test_login_rate_limit():
    """Test that login is rate limited"""
    client = APIClient()

    # Make 5 successful requests
    for _ in range(5):
        response = client.post('/api/auth/login', {
            'email': 'test@example.com',
            'password': 'wrongpass'
        })
        assert response.status_code == 401  # Wrong password

    # 6th request should be rate limited
    response = client.post('/api/auth/login', {
        'email': 'test@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 429
    assert 'Rate limit' in response.json()['error']

def test_user_vs_anonymous_limits():
    """Test that users have higher limits"""
    # Anonymous: 10/m
    client = APIClient()
    for _ in range(10):
        response = client.get('/api/search?q=a')
        assert response.status_code == 200
    # 11th should fail
    response = client.get('/api/search?q=a')
    assert response.status_code == 429

    # Authenticated: 60/m
    user = User.objects.get(email='test@example.com')
    client.force_authenticate(user=user)
    for _ in range(60):
        response = client.get('/api/search?q=a')
        assert response.status_code == 200
```

---

## 📚 REFERENCES

**Django Ratelimit Docs:**
- https://django-ratelimit.readthedocs.io/

**Best Practices:**
- Rate limit public endpoints stricter than authenticated
- Use Redis for distributed systems
- Log rate limit violations (detect attacks)
- Return Retry-After header
- Different limits for different endpoint types

---

## 🚨 SECURITY NOTES

**Prevent:**
- **Brute force attacks:** Strict limits on login endpoints
- **DDoS attacks:** Moderate limits on public endpoints
- **API abuse:** User-based limits on expensive operations
- **Scraping:** Search endpoint limits

**Monitoring:**
- Log rate limit violations
- Alert on repeated violations (possible attack)
- Track which IPs/users hit limits most often

---

## 📊 DELIVERABLES

1. ✅ Django-ratelimit installed and configured
2. ✅ All public endpoints rate limited
3. ✅ All authenticated endpoints rate limited
4. ✅ Rate limit headers in responses
5. ✅ Tests verifying rate limits work
6. ✅ Documentation of rate limits for API users

---

## ✅ COMPLETION CHECKLIST

Before marking complete:
- [ ] django-ratelimit installed
- [ ] All public endpoints have decorators
- [ ] All authenticated endpoints have decorators
- [ ] Returns 429 on limit exceeded
- [ ] Includes Retry-After header
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed by Charo (Security)

---

**Next Task:** S-014 Request ID Tracking (assigned to Linus)

---

**Questions?** Ask in COMMUNICATION_HUB.md

**Status Updates:** Add to COMMUNICATION_HUB.md Agent Updates section

**When Complete:** Update TASK_TRACKER.md, notify GAUDÍ
