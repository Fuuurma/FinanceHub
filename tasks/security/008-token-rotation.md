# Task S-008: Token Rotation Implementation

**Task ID:** S-008
**Assigned To:** Backend Coder (1 Coder)
**Priority:** P0 (CRITICAL)
**Status:** ✅ APPROVED - Ready for Coder Assignment
**Created:** 2026-01-30
**Estimated Time:** 2-3 hours

---

## Overview

Implement token rotation on refresh to prevent token replay attacks and improve session security.

## Why This Matters

### Current Vulnerability
**Location:** `apps/backend/src/api/websocket_auth.py:120-123`

**Issue:** Refresh tokens can be reused indefinitely:

```python
new_access_token = auth_service.refresh_access_token(refresh_data.refresh_token, user)
if not new_access_token:
    return {"error": "Token refresh failed"}, 401
```

**Risk Assessment:**
| Factor | Score | Impact |
|--------|-------|--------|
| Exploitability | 🔴 HIGH | Token replay possible |
| Impact | 🔴 HIGH | Session hijacking |
| Likelihood | 🔴 HIGH | Common attack vector |
| **Overall** | 🔴 **CRITICAL** | **Immediate action required** |

### Attack Vector
1. Attacker steals refresh token (via XSS, network interception)
2. Attacker uses refresh token to get new access token
3. Refresh token still valid, can be reused
4. Session remains compromised

### Real-World Impact
- Persistent session compromise
- Unauthorized trading
- Financial loss
- Data theft

---

## Task Requirements

### Phase 1: Token Blacklisting (1 hour)

#### 1.1 Create Token Blacklist Model
**File:** `apps/backend/src/users/models/token_blacklist.py`

```python
from django.db import models
from django.utils import timezone
from datetime import timedelta

class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    user_id = models.CharField(max_length=36)  # UUID
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user_id']),
            models.Index(fields=['expires_at']),
        ]

    @classmethod
    def blacklist_token(cls, token: str, user_id: str, expires_in: int = 86400):
        """Blacklist a token until its expiration"""
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        cls.objects.get_or_create(
            token=token,
            defaults={
                'user_id': user_id,
                'expires_at': expires_at
            }
        )

    @classmethod
    def is_blacklisted(cls, token: str) -> bool:
        """Check if a token is blacklisted"""
        return cls.objects.filter(
            token=token,
            expires_at__gt=timezone.now()
        ).exists()

    @classmethod
    def cleanup_expired(cls):
        """Remove expired blacklisted tokens"""
        cls.objects.filter(expires_at__lte=timezone.now()).delete()
```

#### 1.2 Update Auth Service
**File:** `apps/backend/src/users/services/auth_service.py`

```python
class AuthService:
    def refresh_access_token(self, refresh_token: str, user) -> Optional[str]:
        """Refresh access token with rotation - invalidates old refresh token"""
        
        # Check if token is blacklisted
        if TokenBlacklist.is_blacklisted(refresh_token):
            return None
        
        # Verify refresh token
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
        
        # Blacklist the old refresh token
        TokenBlacklist.blacklist_token(
            token=refresh_token,
            user_id=str(user.id),
            expires_in=7 * 24 * 3600  # 7 days
        )
        
        # Generate new access token (no new refresh token)
        access_token = self.generate_access_token(user)
        return access_token
```

---

### Phase 2: Update Refresh Endpoint (30 min)

#### 2.1 Modify Refresh Token Handler
**File:** `apps/backend/src/api/websocket_auth.py`

```python
@router.post("/auth/token/refresh", response=TokenResponse)
def refresh_token(request, refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    IMPORTANT: Old refresh token is blacklisted after use.
    """
    from django.contrib.auth import get_user_model
    from users.models.token_blacklist import TokenBlacklist

    User = get_user_model()
    
    # Check if token is already blacklisted
    if TokenBlacklist.is_blacklisted(refresh_data.refresh_token):
        return {"error": "Token has been invalidated"}, 401
    
    payload = auth_service.verify_token(refresh_data.refresh_token)

    if not payload or payload.get('type') != 'refresh':
        return {"error": "Invalid refresh token"}, 401

    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return {"error": "User not found"}, 401

    # Blacklist old refresh token
    TokenBlacklist.blacklist_token(
        token=refresh_data.refresh_token,
        user_id=str(user.id)
    )

    # Generate new tokens
    new_access_token = auth_service.generate_access_token(user)
    new_refresh_token = auth_service.generate_refresh_token(user)

    tier = getattr(user, 'tier', 'free')
    expiry_hours = getattr(request, 'JWT_EXPIRY_HOURS', 24)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="Bearer",
        expires_in=expiry_hours * 3600,
        user_id=str(user.id),
        username=user.username,
        tier=tier
    )
```

---

### Phase 3: Add Cleanup Task (30 min)

#### 3.1 Create Cleanup Management Command
**File:** `apps/backend/src/management/commands/cleanup_blacklisted_tokens.py`

```python
from django.core.management.base import BaseCommand
from users.models.token_blacklist import TokenBlacklist

class Command(BaseCommand):
    help = 'Clean up expired blacklisted tokens'

    def handle(self, *args, **options):
        deleted = TokenBlacklist.cleanup_expired()
        self.stdout.write(f'Deleted {deleted} expired blacklisted tokens')
```

#### 3.2 Schedule in Celery Beat
```python
# tasks.py or celery.py
from celery import shared_task
from users.models.token_blacklist import TokenBlacklist

@shared_task
def cleanup_blacklisted_tokens():
    """Run daily to clean up expired tokens"""
    TokenBlacklist.cleanup_expired()
```

---

### Phase 4: Testing (30 min)

#### 4.1 Unit Tests
```python
def test_token_rotation():
    """Test that refresh token is blacklisted after use"""
    user = create_test_user()
    refresh_token = auth_service.generate_refresh_token(user)
    
    # Use refresh token
    new_access = auth_service.refresh_access_token(refresh_token, user)
    
    # Old token should be blacklisted
    assert TokenBlacklist.is_blacklisted(refresh_token) is True
    
    # New token should work
    assert new_access is not None
    
    # Old token should not work
    payload = auth_service.verify_token(refresh_token)
    assert payload is None

def test_blacklisted_token_rejected():
    """Test that blacklisted tokens are rejected"""
    user = create_test_user()
    refresh_token = auth_service.generate_refresh_token(user)
    
    # Blacklist token
    TokenBlacklist.blacklist_token(refresh_token, str(user.id))
    
    # Should be rejected
    result = auth_service.refresh_access_token(refresh_token, user)
    assert result is None
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `apps/backend/src/users/models/token_blacklist.py` | Token blacklist model |
| `apps/backend/src/management/commands/cleanup_blacklisted_tokens.py` | Cleanup command |

## Files to Modify

| File | Changes |
|------|---------|
| `apps/backend/src/users/services/auth_service.py` | Add blacklist check |
| `apps/backend/src/api/websocket_auth.py` | Update refresh endpoint |
| `tasks.py` or `celery.py` | Add cleanup task |

## Acceptance Criteria

- [ ] Refresh tokens are blacklisted after use
- [ ] Blacklisted tokens are rejected
- [ ] Cleanup task removes expired blacklisted tokens
- [ ] All tests pass
- [ ] Documentation updated

---

## Rollback Plan

If issues occur:
1. Disable token blacklisting in settings
2. Run: `DELETE FROM users_tokenblacklist;`
3. Revert auth service changes

---

## Dependencies

- None (uses existing Django models)

---

## Questions for Gaudí

1. Should I proceed with implementing S-008?
2. Should refresh tokens be single-use (current approach) or allow limited reuse?
3. Should we implement refresh token rotation (new refresh token each time)?

---

**Task S-008 Created: Ready for Approval**

**Status:** ⏳ Waiting for Gaudí's decision
**Priority:** P0 (CRITICAL) - Addresses active token replay vulnerability
