# Token Storage Security Migration Guide

**Date:** 2026-01-30
**Author:** Charo (Security Engineer)
**Purpose:** Migrate JWT tokens from localStorage to httpOnly cookies

---

## Overview

This guide documents the migration from vulnerable localStorage token storage to secure httpOnly cookies.

## Why This Migration is Necessary

### Current Vulnerability
JWT tokens are stored in localStorage, which is accessible to JavaScript:

```typescript
// VULNERABLE - Tokens accessible via XSS
localStorage.setItem(TOKEN_KEY, data.access)
localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
```

### Risk Assessment

| Attack Vector | Impact | Likelihood |
|---------------|--------|------------|
| XSS Token Theft | Account takeover | HIGH |
| Malicious Scripts | Session hijacking | HIGH |
| Third-party Scripts | Data exfiltration | MEDIUM |

### Security Impact
- **Account Takeover:** Attackers can steal tokens and access user accounts
- **Financial Loss:** Unauthorized trades, portfolio access
- **Data Breach:** Personal and financial data exposure

---

## Migration Plan

### Phase 1: Backend Changes

#### 1.1 Update Django Settings
**File:** `apps/backend/src/core/settings.py`

```python
# Cookie settings for token storage
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CORS_ALLOW_CREDENTIALS = True
```

#### 1.2 Update Login Endpoint
**File:** `apps/backend/src/users/api/auth/login.py`

```python
from django.http import HttpResponse

@router.post("/login")
def login(request, response: Response):
    # ... existing validation ...
    
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    response = HttpResponse()
    
    # Set tokens as httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not DEBUG,
        samesite="lax",
        max_age=15 * 60,  # 15 minutes
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not DEBUG,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
    )
    
    response.status_code = 200
    return response
```

#### 1.3 Update Logout Endpoint
**File:** `apps/backend/src/users/api/auth/logout.py`

```python
@router.post("/logout")
def logout(request):
    response = HttpResponse()
    
    # Clear tokens
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("user_data")
    
    # Blacklist refresh token if using token blacklisting
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        blacklist_token(refresh_token)
    
    return response
```

---

### Phase 2: Frontend Changes

#### 2.1 Auth Context (SECURE VERSION)
**File:** `apps/frontend/src/contexts/AuthContext.tsx`

```typescript
// SECURE - Tokens in httpOnly cookies (not accessible to JavaScript)
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null
  return null
}

function setCookie(name: string, value: string, maxAgeSeconds: number): void {
  const isProduction = window.location.protocol === 'https:'
  document.cookie = `${name}=${value}; max-age=${maxAgeSeconds}; path=/; SameSite=Lax${isProduction ? '; Secure' : ''}`
}

function deleteCookie(name: string): void {
  document.cookie = `${name}=; max-age=0; path=/;`
}
```

#### 2.2 API Client (SECURE VERSION)
**File:** `apps/frontend/src/lib/api/client.ts`

```typescript
// SECURE - Read token from cookie (not localStorage)
private getAuthHeaders(): Record<string, string> {
  const token = getCookie('access_token')
  if (token) {
    return { Authorization: `Bearer ${token}` }
  }
  return {}
}
```

---

### Phase 3: Testing

#### 3.1 Security Tests
```python
def test_tokens_not_accessible_via_xss():
    """Verify tokens cannot be stolen via XSS"""
    # Attempt to access localStorage
    localStorage_tokens = execute_js("localStorage.getItem('access_token')")
    assert localStorage_tokens is None
    
    # Verify cookies are httpOnly
    cookies = get_all_cookies()
    assert 'access_token' in cookies
    assert cookies['access_token'].httponly == True

def test_session_hijacking_prevented():
    """Verify session hijacking is prevented"""
    # Attempt to steal cookie via JavaScript
    stolen = execute_js("document.cookie")
    assert 'access_token' not in stolen
```

#### 3.2 Functional Tests
```typescript
test('login sets httpOnly cookies', async () => {
  await login('user', 'password')
  
  const cookies = await getAllCookies()
  expect(cookies).toContain('access_token')
  expect(cookies).toContain('refresh_token')
  
  const accessTokenCookie = cookies.find(c => c.name === 'access_token')
  expect(accessTokenCookie.httponly).toBe(true)
  expect(accessTokenCookie.secure).toBe(true)
})

test('logout clears cookies', async () => {
  await logout()
  
  const cookies = await getAllCookies()
  expect(cookies).not.toContain('access_token')
  expect(cookies).not.toContain('refresh_token')
})
```

---

## Rollback Plan

If issues occur during migration:

### Quick Rollback
```bash
# Revert to localStorage version
git checkout AuthContext.tsx.localStorage
git checkout client.ts.localStorage
```

### Feature Flag (Recommended)
```typescript
const USE_HTTP_ONLY_COOKIES = process.env.NEXT_PUBLIC_USE_HTTP_ONLY_COOKIES === 'true'

if (USE_HTTP_ONLY_COOKIES) {
  // Use cookie-based storage
} else {
  // Use localStorage (for gradual rollout)
}
```

---

## Monitoring

### Metrics to Track
1. **Login Success Rate** - Should not decrease
2. **Session Timeout** - Should work correctly
3. **Cookie Issues** - Monitor for cookie errors
4. **XSS Attempts** - Monitor CSP reports

### Alerts
- Failed login rate > 10%
- Session timeout errors > 5%
- Cookie parse errors

---

## Compatibility

### Supported Browsers
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Limitations
- Some older browsers may not support SameSite=Lax
- Third-party cookies may be blocked in some scenarios

---

## Verification Steps

### 1. Verify Cookies Are httpOnly
```bash
# In browser console
document.cookie
// Should NOT show access_token or refresh_token

// Check in DevTools > Application > Cookies
// Should show httponly: true
```

### 2. Verify Tokens Not in localStorage
```javascript
// In browser console
localStorage.getItem('access_token')
// Should return null
```

### 3. Test Authentication Flow
1. Login → Verify cookies set
2. Refresh page → Verify session persists
3. Navigate → Verify authenticated state
4. Logout → Verify cookies cleared

---

## Files Modified

| File | Changes |
|------|---------|
| `apps/backend/src/core/settings.py` | Cookie settings |
| `apps/backend/src/users/api/auth/login.py` | Set httpOnly cookies |
| `apps/backend/src/users/api/auth/logout.py` | Clear cookies |
| `apps/frontend/src/contexts/AuthContext.tsx` | Read from cookies |
| `apps/frontend/src/lib/api/client.ts` | Read token from cookie |

---

## Testing Checklist

- [ ] Login sets httpOnly cookies
- [ ] Logout clears cookies
- [ ] Token refresh works
- [ ] Protected routes require authentication
- [ ] XSS cannot steal tokens
- [ ] Works across browser refresh
- [ ] Logout on all tabs (optional)
- [ ] CSRF protection active

---

## References

| Resource | URL |
|----------|-----|
| httpOnly Cookies | https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies |
| SameSite Cookies | https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite |
| OWASP Session Management | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html |

---

## Migration Timeline

| Phase | Duration | Actions |
|-------|----------|---------|
| Phase 1 | 1 hour | Backend changes |
| Phase 2 | 1 hour | Frontend changes |
| Phase 3 | 30 min | Testing |
| Phase 4 | 30 min | Monitoring |

**Total Time:** 3 hours

---

**Document Version:** 1.0
**Created:** 2026-01-30
**Author:** Charo (Security Engineer)
