# 📋 Task Assignment: S-014 Request ID Tracking

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Linus (Backend Coder)
**Priority:** HIGH - Observability Critical
**Estimated Effort:** 2-3 hours
**Timeline:** Start immediately, no deadline (quality-driven)

---

## 🎯 OVERVIEW

Add unique request ID tracking to all API requests for debugging, monitoring, and tracing request flows through the system.

**Context:**
- Security audit approved this task as P1 HIGH priority
- Critical for debugging production issues
- Enables tracing requests across services
- Required for logging and monitoring

---

## 📋 YOUR TASKS

### Task 1: Create Request ID Middleware (1h)

**File:** `apps/backend/src/middleware/request_id.py`

```python
import uuid
from django.utils.deprecation import MiddlewareMixin

class RequestIDMiddleware(MiddlewareMixin):
    """Add unique X-Request-ID header to all requests"""

    def process_request(self, request):
        """Generate or retrieve request ID"""
        # Check if request ID already exists (from client)
        request_id = request.META.get('HTTP_X_REQUEST_ID')

        if not request_id:
            # Generate new UUID
            request_id = str(uuid.uuid4())

        # Store on request object
        request.id = request_id

        # Add to META for access in views
        request.META['HTTP_X_REQUEST_ID'] = request_id

        return None

    def process_response(self, request, response):
        """Add request ID to response headers"""
        if hasattr(request, 'id'):
            response['X-Request-ID'] = request.id

        return response
```

**Register middleware in settings:**
```python
# apps/backend/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
    'src.middleware.request_id.RequestIDMiddleware',  # Add this
    'django.middleware.common.CommonMiddleware',
    ...
]
```

**Middleware order is important:**
- RequestIDMiddleware should be FIRST (after SecurityMiddleware)
- This ensures all subsequent middleware/views have access to request.id

### Task 2: Update Logging to Include Request ID (1h)

**Configure logging formatter:**
```python
# apps/backend/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} [req-{request_id}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message} [req-{request_id}]',
            'style': '{',
        },
    },
    'filters': {
        'request_id': {
            '()': 'src.middleware.request_id.RequestIDFilter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['request_id'],
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'verbose',
            'filters': ['request_id'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'src': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

**Create request ID filter:**
```python
# apps/backend/src/middleware/request_id.py
import logging

class RequestIDFilter(logging.Filter):
    """Logging filter to add request ID to log records"""

    def filter(self, record):
        """Add request_id to log record if available"""
        from threading import local

        # Get current request from thread local
        request = getattr(local(), 'request', None)

        if request and hasattr(request, 'id'):
            record.request_id = request.id
        else:
            record.request_id = 'N/A'

        return True

# Store request in thread local in middleware
from threading import local
_thread_locals = local()

class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request_id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        request.id = request_id
        request.META['HTTP_X_REQUEST_ID'] = request_id

        # Store in thread local for logging
        _thread_locals.request = request

        return None
```

**Example log output:**
```
INFO 2026-02-01 14:30:15 trading.views [req-550e8400-e29b-41d4-a716-446655440000] Creating order for AAPL
INFO 2026-02-01 14:30:15 trading.services [req-550e8400-e29b-41d4-a716-446655440000] Order executed: price 150.25
ERROR 2026-02-01 14:30:16 trading.views [req-550e8400-e29b-41d4-a716-446655440000] Insufficient balance
```

### Task 3: Update Django Ninja Endpoints (30m)

**Pass request ID to services:**
```python
from ninja import Router
from .services import TradingService

router = Router()

@router.post("/orders")
def create_order(request, data: CreateOrderSchema):
    """Create order with request ID tracking"""
    # Request ID available as request.id
    result = TradingService.create_order(
        user=request.user,
        symbol=data.symbol,
        quantity=data.quantity,
        request_id=request.id  # Pass to service
    )
    return result
```

**Update services to accept request_id:**
```python
# apps/backend/src/trading/services.py
import logging

logger = logging.getLogger(__name__)

class TradingService:
    @staticmethod
    def create_order(user, symbol, quantity, request_id=None):
        """Create order with request ID for tracing"""
        logger.info(
            f"Creating order: {symbol} x{quantity}",
            extra={'request_id': request_id}
        )

        # ... order logic

        logger.info(
            f"Order created: {order.id}",
            extra={'request_id': request_id}
        )

        return order
```

### Task 4: Add Request ID to Error Responses (30m)

**Create error handler with request ID:**
```python
# apps/backend/src/api/exceptions.py
from ninja import errors
import logging

logger = logging.getLogger(__name__)

@router.exception_handler(Exception)
def generic_error(request, exc):
    """Handle errors with request ID"""
    request_id = getattr(request, 'id', 'N/A')

    logger.exception(
        f"Unhandled error: {str(exc)}",
        extra={'request_id': request_id}
    )

    return {
        'error': 'Internal Server Error',
        'request_id': request_id,
        'message': str(exc) if settings.DEBUG else 'An error occurred'
    }, 500
```

**Error response format:**
```json
{
  "error": "Validation Error",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "details": [...]
}
```

### Task 5: WebSocket Request ID (Optional, 1h)

**Pass request ID to WebSocket consumers:**
```python
# apps/backend/src/trading/consumers.py
from channels.consumer import SyncConsumer

class TradingConsumer(SyncConsumer):
    def websocket_connect(self, event):
        """Extract request ID from connection"""
        # Get request ID from connection params or headers
        request_id = self.scope.get('request_id', 'N/A')

        # Store for logging
        self.request_id = request_id

        logger.info(
            f"WebSocket connected: {self.channel_name}",
            extra={'request_id': request_id}
        )
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] RequestIDMiddleware created and registered
- [ ] All requests get unique X-Request-ID header
- [ ] Request ID included in all log messages
- [ ] Request ID returned in all API responses
- [ ] Request ID included in error responses
- [ ] Clients can provide their own request ID
- [ ] Thread-safe (works with async/threading)

---

## 🧪 TESTING

**Test request ID middleware:**
```python
from django.test import RequestFactory
from src.middleware.request_id import RequestIDMiddleware

def test_request_id_generated():
    """Test that request ID is generated"""
    factory = RequestFactory()
    request = factory.get('/api/test')

    middleware = RequestIDMiddleware(get_response=lambda r: r)
    middleware.process_request(request)

    assert hasattr(request, 'id')
    assert len(request.id) == 36  # UUID format

def test_request_id_from_header():
    """Test that client-provided request ID is used"""
    factory = RequestFactory()
    custom_id = 'my-custom-request-id'
    request = factory.get('/api/test', HTTP_X_REQUEST_ID=custom_id)

    middleware = RequestIDMiddleware(get_response=lambda r: r)
    middleware.process_request(request)

    assert request.id == custom_id

def test_request_id_in_response():
    """Test that request ID is in response headers"""
    factory = RequestFactory()
    request = factory.get('/api/test')

    middleware = RequestIDMiddleware(get_response=lambda r: HttpResponse())
    response = middleware.process_response(request, HttpResponse())

    assert 'X-Request-ID' in response
```

**Test logging:**
```python
def test_request_id_in_logs(caplog):
    """Test that logs include request ID"""
    factory = RequestFactory()
    request = factory.get('/api/test')
    request.id = 'test-request-id'

    # Log something
    logger.info("Test message", extra={'request_id': request.id})

    # Check log contains request ID
    assert 'test-request-id' in caplog.text
```

---

## 📚 REFERENCES

**Django Middleware:**
- https://docs.djangoproject.com/en/4.2/topics/http/middleware/

**Request ID Best Practices:**
- https://cloud.google.com/architecture/distributed-tracing
- https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html

**Logging Documentation:**
- https://docs.djangoproject.com/en/4.2/topics/logging/

---

## 🚨 PRODUCTION NOTES

**Benefits:**
- **Debugging:** Find all logs for a specific request
- **Tracing:** Track request flow across services
- **Support:** Share request ID with users for support
- **Monitoring:** Group errors by request ID
- **Performance:** Track request latency by ID

**Integration with monitoring:**
- Send request ID to Sentry, DataDog, New Relic
- Use request ID to correlate logs across services
- Track request ID in APM tools

**Client usage:**
```javascript
// Client can provide their own request ID
fetch('/api/test', {
  headers: {
    'X-Request-ID': 'my-custom-id'
  }
})

// Or get request ID from response
fetch('/api/test')
  .then(res => {
    const requestId = res.headers.get('X-Request-ID')
    console.log('Request ID:', requestId)
  })
```

---

## 📊 DELIVERABLES

1. ✅ RequestIDMiddleware created and registered
2. ✅ Logging updated with request ID filter
3. ✅ All endpoints return X-Request-ID header
4. ✅ Error responses include request ID
5. ✅ Tests for middleware
6. ✅ Documentation of request ID usage

---

## ✅ COMPLETION CHECKLIST

Before marking complete:
- [ ] RequestIDMiddleware registered first in MIDDLEWARE list
- [ ] All log messages include request ID
- [ ] Response headers include X-Request-ID
- [ ] Error responses include request ID
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Logging format verified in production

---

**Next Task:** S-015 Database Connection Pooling (assigned to Karen)

---

**Questions?** Ask in COMMUNICATION_HUB.md

**Status Updates:** Add to COMMUNICATION_HUB.md Agent Updates section

**When Complete:** Update TASK_TRACKER.md, notify GAUDÍ
