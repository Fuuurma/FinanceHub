# Task S-007: WebSocket Security Implementation

**Task ID:** S-007
**Assigned To:** Security (Charo) - task creation
**Priority:** P2 (MEDIUM)
**Status:** ⏳ PENDING APPROVAL
**Created:** 2026-01-30
**Estimated Time:** 2-3 hours

---

## Overview

Implement comprehensive security measures for WebSocket connections used for real-time data.

## Why This Matters

### Current State
**Location:** `apps/backend/src/websocket_consumers/`

**Risk Assessment:**
| Factor | Score | Impact |
|--------|-------|--------|
| Authentication | ⚠️ MEDIUM | Token validation needed |
| Rate Limiting | ⚠️ MEDIUM | Flood protection needed |
| Message Validation | ⚠️ MEDIUM | Injection prevention needed |
| Connection Security | ⚠️ MEDIUM | WSS encryption needed |
| **Overall** | 🟠 **MEDIUM** | **Action recommended** |

### Attack Vectors
1. **WebSocket Hijacking**
   - Cross-site WebSocket hijacking (CSWSH)
   - Token theft via WebSocket

2. **Denial of Service**
   - Connection flooding
   - Message flooding
   - Memory exhaustion

3. **Message Injection**
   - Malicious payloads
   - Protocol violation
   - SQL/NoSQL injection via messages

---

## Task Requirements

### Phase 1: Authentication & Authorization (1 hour)

#### 1.1 Token Validation
**File:** `apps/backend/src/websocket_consumers.py`

```python
import jwt
from channels.middleware import BaseMiddleware
from django.conf import settings

class WebSocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract token from query string or headers
        query_string = scope.get('query_string', b'').decode()
        token = self.extract_token(query_string)
        
        if not token:
            # Close connection if no token
            await send({
                'type': 'websocket.close',
                'code': 4001,  # Unauthorized
            })
            return
        
        # Validate token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            scope['user'] = payload['user_id']
        except jwt.ExpiredSignatureError:
            await send({
                'type': 'websocket.close',
                'code': 4002,  # Token expired
            })
            return
        except jwt.InvalidTokenError:
            await send({
                'type': 'websocket.close',
                'code': 4003,  # Invalid token
            })
            return
        
        await super().__call__(scope, receive, send)
    
    def extract_token(self, query_string):
        params = dict(p.split('=') for p in query_string.split('&') if '=' in p)
        return params.get('token')
```

#### 1.2 Origin Validation
```python
# Prevent cross-site WebSocket hijacking
ALLOWED_ORIGINS = [
    'https://financehub.app',
    'https://www.financehub.app',
    'http://localhost:3000',
]

class WebSocketOriginMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        origin = scope.get('headers', {}).get(b'origin', b'').decode()
        
        if origin and origin not in ALLOWED_ORIGINS:
            await send({
                'type': 'websocket.close',
                'code': 4004,  # Forbidden origin
            })
            return
        
        await super().__call__(scope, receive, send)
```

---

### Phase 2: Rate Limiting (30 min)

#### 2.1 Connection Rate Limiting
```python
from django.core.cache import cache

class ConnectionRateLimitMiddleware:
    RATE_LIMIT = 10  # connections per minute
    RATE_WINDOW = 60  # seconds
    
    async def __call__(self, scope, receive, send):
        client_ip = scope['client'][0]
        cache_key = f'ws_connections:{client_ip}'
        
        connections = cache.get(cache_key, 0)
        if connections >= self.RATE_LIMIT:
            await send({
                'type': 'websocket.close',
                'code': 4029,  # Too many requests
            })
            return
        
        cache.set(cache_key, connections + 1, self.RATE_WINDOW)
        
        await super().__call__(scope, receive, send)
```

#### 2.2 Message Rate Limiting
```python
class MessageRateLimitMiddleware:
    MAX_MESSAGES_PER_SECOND = 100
    MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB
    
    async def __call__(self, scope, receive, send):
        message_count = 0
        start_time = time.time()
        
        async def rate_limited_receive():
            nonlocal message_count
            
            # Check rate limit
            if time.time() - start_time < 1:
                message_count += 1
                if message_count > self.MAX_MESSAGES_PER_SECOND:
                    await send({
                        'type': 'websocket.close',
                        'code': 4029,
                    })
                    return
            
            return await receive()
        
        await super().__call__(scope, rate_limited_receive, send)
```

---

### Phase 3: Message Validation (30 min)

#### 3.1 Schema Validation
```python
from pydantic import BaseModel, ValidationError
from typing import Optional

class WebSocketMessage(BaseModel):
    type: str
    payload: Optional[dict] = None
    timestamp: float

# Validate incoming messages
async def validate_message(message):
    try:
        validated = WebSocketMessage(**message)
        return validated
    except ValidationError as e:
        await send({
            'type': 'websocket.close',
            'code': 4000,  # Bad request
        })
        return None
```

#### 3.2 Message Size Limits
```python
MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB

async def receive_message(receive):
    message = await receive()
    
    if message.get('bytes', b''):
        if len(message['bytes']) > MAX_MESSAGE_SIZE:
            await send({
                'type': 'websocket.close',
                'code': 4008,  # Message too large
            })
            return None
    
    return message
```

---

### Phase 4: Security Headers & Encryption (30 min)

#### 4.1 WebSocket Security Headers
```python
# Configure WebSocket consumer
class SecureWebSocketConsumer(JsonWebsocketConsumer):
    def http_request(self, message):
        # Add security headers
        message.reply_headers.update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
        })
```

#### 4.2 WSS Enforcement
```javascript
// Frontend WebSocket connection
const socket = new WebSocket(
  process.env.NEXT_PUBLIC_WS_URL  // Must be wss://
)

// Verify SSL certificate
const socket = new WebSocket('wss://api.financehub.app/ws', {
  rejectUnauthorized: true,
})
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `apps/backend/src/websocket_security.py` | Security middleware |
| `apps/backend/src/api/websocket.py` | WebSocket API endpoints |
| `tests/security/test_websocket.py` | WebSocket security tests |

## Files to Modify

| File | Changes |
|------|---------|
| `apps/backend/src/core/asgi.py` | Add WebSocket middleware |
| `apps/backend/src/websocket_consumers.py` | Add authentication |
| `apps/frontend/src/lib/api/websocket.ts` | Secure connection |

---

## Acceptance Criteria

- [ ] WebSocket connections require authentication
- [ ] Cross-origin connections blocked
- [ ] Connection rate limiting enabled
- [ ] Message rate limiting enabled
- [ ] Message schema validation implemented
- [ ] Message size limits enforced
- [ ] WSS encryption required
- [ ] Tests pass

---

## Rollback Plan

If WebSocket security causes issues:
1. Relax rate limits temporarily
2. Add more origins to allowlist
3. Disable message validation for debugging

---

## References

| Resource | URL |
|----------|-----|
| WebSocket Security | https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html |
| Django Channels Security | https://channels.readthedocs.io/en/stable/topics/security.html |

---

## Questions for Gaudí

1. Should I proceed with implementing S-007 (WebSocket Security)?
2. Should we implement real-time monitoring for WebSocket attacks?
3. Should we add WebSocket metrics to observability?

---

**Task S-007 Created: Ready for Approval**

**Status:** ⏳ Waiting for Gaudí's decision
**Priority:** P2 (MEDIUM) - Important but not critical
