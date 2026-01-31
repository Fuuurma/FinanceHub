# Authentication Security Patterns

**Date:** 2026-01-31
**Author:** Charo (Security Engineer)
**Version:** 1.0

## Overview

Secure authentication patterns for FinanceHub covering JWT, sessions, passwords, and MFA.

## JWT Token Security

### Token Structure

```python
TOKEN_PAYLOAD = {
    "user_id": "uuid-string",
    "username": "string",
    "tier": "free|premium|enterprise",
    "type": "access|refresh",
    "iat": 1234567890,
    "exp": 1234567890,
    "jti": "unique-id"
}
```

### Token Configuration

```python
# settings.py
JWT_CONFIG = {
    'ALGORITHM': 'HS256',
    'SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'BLACKLIST_ENABLED': True,
}
```

### Token Generation

```python
import jwt
import secrets
from datetime import datetime, timedelta

class TokenService:
    def generate_access_token(self, user) -> str:
        now = datetime.utcnow()
        payload = {
            'user_id': str(user.id),
            'username': user.username,
            'tier': getattr(user, 'tier', 'free'),
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=24),
            'jti': secrets.token_urlsafe(16),
            'iss': 'financehub',
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    
    def generate_refresh_token(self, user) -> str:
        now = datetime.utcnow()
        payload = {
            'user_id': str(user.id),
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=7),
            'jti': secrets.token_urlsafe(16),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
```

### Token Storage (Frontend)

```typescript
// See: apps/frontend/src/contexts/AuthContext.tsx.secure

interface TokenStorage {
  setAccessToken(token: string, expiresIn: number): void;
  getAccessToken(): string | null;
  clearTokens(): void;
}

class CookieTokenStorage implements TokenStorage {
  private options = {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict' as const,
    path: '/',
  };

  setAccessToken(token: string, expiresIn: number): void {
    const expires = new Date(Date.now() + expiresIn * 1000);
    document.cookie = `access_token=${token};expires=${expires.toUTCString()};SameSite=Strict;Secure;HttpOnly;path=/`;
  }

  getAccessToken(): string | null {
    const match = document.cookie.match(/access_token=([^;]+)/);
    return match ? match[1] : null;
  }

  clearTokens(): void {
    document.cookie = 'access_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT';
  }
}
```

## Session Management

### Session Configuration

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

### Session Security

```python
class SecureSessionStore:
    def validate_session(self) -> bool:
        last_activity = self.get('last_activity')
        if last_activity:
            last = datetime.fromisoformat(last_activity)
            if datetime.utcnow() - last > timedelta(hours=1):
                return False
        return True
```

## Password Security

### Password Requirements

```python
PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### Login Attempt Tracking

```python
class LoginAttemptTracker:
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 15 * 60

    @classmethod
    def is_locked_out(cls, identifier: str) -> bool:
        key = f"login_attempts:{identifier}"
        attempts = cache.get(key, [])
        now = datetime.utcnow()
        recent = [t for t in attempts if now - t < timedelta(minutes=1)]
        return len(recent) >= cls.MAX_ATTEMPTS
```

## Multi-Factor Authentication

### TOTP Setup

```python
import pyotp

class MFAService:
    def generate_secret(self) -> str:
        return pyotp.random_base32()
    
    def verify_code(self, secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
```

## Checklist

- [ ] JWT tokens use httpOnly cookies
- [ ] Access token lifetime <= 24 hours
- [ ] Refresh token rotation enabled
- [ ] Password minimum 12 characters
- [ ] Login rate limiting active
- [ ] Session timeout configured
- [ ] MFA available for users

**Document Version:** 1.0
**Last Updated:** 2026-01-31
