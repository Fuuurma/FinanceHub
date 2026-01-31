# WebSocket Security Requirements Documentation

**Date:** 2026-01-31
**Author:** Charo (Security Engineer)

---

## Overview

This document outlines the security requirements and implementation guidelines for WebSocket connections in the FinanceHub application.

---

## Current Security Issues (FAIL-005, FAIL-006)

### FAIL-005: Token in URL Query String

**Location:** `apps/backend/src/websocket_consumers/auth_middleware.py`

**Issue:** WebSocket tokens are passed in the URL query string:

```python
query_string = scope.get('query_string', b'').decode('utf-8')
token = dict(param.split('=') for param in query_string.split('&') if '=' in param).get('token')
```

**Problems:**
1. Tokens visible in browser history
2. Tokens visible in server access logs
3. Tokens visible in referer headers
4. Tokens can be leaked via referer header to third parties

**Severity:** HIGH

### FAIL-006: No Token Expiration Check

**Location:** `apps/backend/src/websocket_consumers/auth_middleware.py`

**Issue:** No validation of token expiration during WebSocket authentication:

```python
def decode_token(self, token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Error logged but not enforced
```

**Problems:**
1. Expired tokens can still authenticate
2. No enforcement of token expiration
3. Sessions can persist indefinitely

**Severity:** HIGH

---

## Security Requirements

### 1. Authentication

#### 1.1 Move Token from Query String to Authorization Header

**Current (Insecure):**
```
ws://localhost:8000/ws/market-data/?token=<jwt_token>
```

**Required (Secure):**
```
ws://localhost:8000/ws/market-data/
Headers:
  Authorization: Bearer <jwt_token>
```

**Implementation:**

```python
# In auth_middleware.py
async def authenticate_websocket(self, scope, receive, send):
    """Authenticate WebSocket connection using Authorization header"""
    
    # Get Authorization header from headers tuple
    headers_dict = dict(scope.get('headers', []))
    auth_header = headers_dict.get(b'authorization', b'').decode()
    
    if not auth_header:
        await self.send_error(send, "Missing Authorization header")
        return False
    
    if not auth_header.startswith('Bearer '):
        await self.send_error(send, "Invalid Authorization format")
        return False
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Validate token
    payload = self.validate_token(token)
    if not payload:
        await self.send_error(send, "Invalid or expired token")
        return False
    
    # Set user context
    scope['user'] = payload.get('user_id')
    return True
```

### 2. Token Validation

#### 2.1 Validate Token Expiration

```python
def validate_token(self, token: str) -> Optional[dict]:
    """Validate JWT token with full security checks"""
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["exp", "iat", "user_id"]
            }
        )
        
        # Additional validation
        if payload.get('type') != 'access':
            return None
        
        # Check token not revoked
        if TokenBlacklist.is_blacklisted(token):
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket connection rejected: expired token")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"WebSocket connection rejected: invalid token - {e}")
        return None
```

### 3. Rate Limiting

#### 3.1 Implement WebSocket Rate Limiting

```python
from django.core.cache import cache

class WebSocketRateLimitMiddleware:
    """Rate limiting for WebSocket connections"""
    
    RATE_LIMIT = 10  # messages per second
    BURST_LIMIT = 50  # maximum burst
    
    async def rate_limit_check(self, user_id: str) -> bool:
        """Check has if user exceeded rate limit"""
        
        key = f"ws_rate_limit:{user_id}"
        current = cache.get(key, 0)
        
        if current >= self.RATE_LIMIT:
            # Check if in burst mode
            burst_key = f"ws_burst:{user_id}"
            burst_count = cache.get(burst_key, 0)
            
            if burst_count >= self.BURST_LIMIT:
                return False  # Rate limit exceeded
            
            # Allow burst but track it
            cache.incr(burst_key)
            cache.expire(burst_key, 60)  # 1 minute burst window
            return True
        
        # Increment counter
        cache.incr(key)
        cache.expire(key, 1)  # 1 second window
        return True
```

### 4. Message Validation

#### 4.1 Validate Message Size

```python
MAX_MESSAGE_SIZE = 64 * 1024  # 64 KB

async def receive_message(self, message: dict) -> bool:
    """Validate incoming WebSocket message"""
    
    # Check message size
    message_size = len(message.get('bytes', b''))
    if message_size > MAX_MESSAGE_SIZE:
        logger.warning(f"WebSocket message too large: {message_size} bytes")
        await self.close(4009)  # Message too big
        return False
    
    # Validate message format
    if 'type' not in message:
        logger.warning("WebSocket message missing type")
        await self.close(4000)  # Protocol error
        return False
    
    # Validate message type against allowed types
    allowed_types = [
        'subscribe',
        'unsubscribe',
        'ping',
        'order',
        'position_update'
    ]
    
    if message['type'] not in allowed_types:
        logger.warning(f"Unknown WebSocket message type: {message['type']}")
        await self.close(4000)  # Protocol error
        return False
    
    return True
```

### 5. Connection Security

#### 5.1 Secure WebSocket Headers

```python
# In ASGI application or middleware
async def websocket_application(scope, receive, send):
    """Secure WebSocket application with proper headers"""
    
    # Verify connection is over SSL/WSS in production
    if not scope.get('secure') and settings.DEBUG is False:
        await send({
            'type': 'websocket.close',
            'code': 4003,  # Forbidden
        })
        return
    
    # Set secure headers
    await send({
        'type': 'websocket.accept',
        'subprotocol': None,
        'headers': [
            (b'X-Content-Type-Options', b'nosniff'),
            (b'X-Frame-Options', b'DENY'),
        ]
    })
```

### 6. Heartbeat/Ping-Pong

#### 6.1 Implement Heartbeat for Connection Health

```python
import asyncio

class WebSocketHeartbeat:
    """Heartbeat mechanism for WebSocket connections"""
    
    PING_INTERVAL = 30  # seconds
    PONG_TIMEOUT = 10   # seconds
    
    def __init__(self, consumer):
        self.consumer = consumer
        self.last_pong = None
    
    async def start_heartbeat(self):
        """Start heartbeat ping loop"""
        while True:
            await asyncio.sleep(self.PING_INTERVAL)
            
            if not self.consumer.connect:
                break
            
            # Send ping
            await self.consumer.send_json({
                'type': 'ping',
                'timestamp': time.time()
            })
    
    async def handle_pong(self, pong_data: dict):
        """Handle pong response"""
        self.last_pong = time.time()
        
        # Check for missed pongs
        if self.last_pong - self.last_pong > self.PONG_TIMEOUT * 2:
            await self.consumer.close(4001)  # Connection timed out
```

### 7. Session Management

#### 7.1 Track Active Connections

```python
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ConnectionManager:
    """Manage active WebSocket connections per user"""
    
    _connections = {}  # user_id -> set of channel names
    
    @classmethod
    def add_connection(cls, user_id: str, channel_name: str):
        """Add a new connection for user"""
        if user_id not in cls._connections:
            cls._connections[user_id] = set()
        cls._connections[user_id].add(channel_name)
    
    @classmethod
    def remove_connection(cls, user_id: str, channel_name: str):
        """Remove connection for user"""
        if user_id in cls._connections:
            cls._connections[user_id].discard(channel_name)
            
            if not cls._connections[user_id]:
                del cls._connections[user_id]
    
    @classmethod
    def get_connection_count(cls, user_id: str) -> int:
        """Get number of active connections for user"""
        return len(cls._connections.get(user_id, set()))
    
    @classmethod
    def disconnect_all(cls, user_id: str):
        """Disconnect all connections for user (security)"""
        if user_id in cls._connections:
            channel_layer = get_channel_layer()
            for channel_name in cls._connections[user_id]:
                async_to_sync(channel_layer.send)(
                    channel_name,
                    {'type': 'websocket.close', 'code': 4001}
                )
            del cls._connections[user_id]
```

### 8. Logging and Monitoring

#### 8.1 Log Security Events

```python
import logging

logger = logging.getLogger('websocket.security')

class WebSocketSecurityLogger:
    """Log WebSocket security events"""
    
    @classmethod
    def log_connection_attempt(cls, user_id: str, success: bool):
        level = logging.INFO if success else logging.WARNING
        logger.log(level, f"WebSocket connection attempt: user={user_id}, success={success}")
    
    @classmethod
    def log_rate_limit_exceeded(cls, user_id: str, message_count: int):
        logger.warning(f"WebSocket rate limit exceeded: user={user_id}, count={message_count}")
    
    @classmethod
    def log_auth_failure(cls, user_id: str, reason: str):
        logger.warning(f"WebSocket auth failure: user={user_id}, reason={reason}")
    
    @classmethod
    def log_message_violation(cls, user_id: str, violation: str):
        logger.warning(f"WebSocket message violation: user={user_id}, violation={violation}")
```

---

## Implementation Checklist

- [ ] Move token from query string to Authorization header (S-012)
- [ ] Implement token expiration validation
- [ ] Add rate limiting middleware
- [ ] Implement message size validation
- [ ] Add heartbeat mechanism
- [ ] Track active connections
- [ ] Add security event logging
- [ ] Set secure WebSocket headers
- [ ] Add connection timeout handling
- [ ] Implement connection revocation

---

## Testing Requirements

### Unit Tests
```python
def test_authorization_header_parsing():
    """Test that Authorization header is correctly parsed"""
    # Setup
    middleware = WebSocketAuthMiddleware()
    
    # Test valid Bearer token
    headers = [(b'authorization', b'Bearer test_token_123')]
    token = middleware.extract_token(headers)
    assert token == 'test_token_123'
    
    # Test missing header
    headers = []
    token = middleware.extract_token(headers)
    assert token is None

def test_rate_limiting():
    """Test that rate limiting works correctly"""
    # Setup
    rate_limiter = WebSocketRateLimitMiddleware()
    user_id = 'test_user'
    
    # Simulate messages
    for i in range(10):
        assert rate_limiter.rate_limit_check(user_id) is True
    
    # Should be rate limited
    assert rate_limiter.rate_limit_check(user_id) is False
```

### Integration Tests
```python
def test_websocket_auth_flow():
    """Test full WebSocket authentication flow"""
    # 1. Connect with valid token
    # 2. Verify connection established
    # 3. Send authenticated message
    # 4. Verify response
    pass

def test_websocket_rate_limiting():
    """Test WebSocket rate limiting under load"""
    # 1. Connect WebSocket
    # 2. Send messages rapidly
    # 3. Verify rate limiting kicks in
    pass
```

---

## Related Tasks

- S-007: WebSocket Security (Task)
- S-012: WebSocket Auth Header Migration (Task)
- S-008: Token Rotation Implementation (Related)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-31
