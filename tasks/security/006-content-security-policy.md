# Task S-006: Content Security Policy (CSP) Implementation

**Task ID:** S-006
**Assigned To:** Security (Charo) - task creation
**Priority:** P1 (HIGH)
**Status:** ⏳ PENDING APPROVAL
**Created:** 2026-01-30
**Estimated Time:** 1-2 hours

---

## Overview

Implement Content Security Policy (CSP) headers to prevent XSS attacks and data injection.

## Why This Matters

### Current Vulnerability
**Status:** No CSP headers configured

**Risk Assessment:**
| Factor | Score | Impact |
|--------|-------|--------|
| Exploitability | 🔴 HIGH | XSS attacks possible |
| Impact | 🔴 HIGH | Code injection, data theft |
| Likelihood | 🔴 HIGH | Common attack vector |
| **Overall** | 🔴 **HIGH** | **Immediate action recommended** |

### Attack Vectors Prevented by CSP
1. **Cross-Site Scripting (XSS)**
   - Inline script execution blocked
   - Event handlers blocked
   - `javascript:` URLs blocked

2. **Data Injection**
   - Inline styles blocked
   - Object/embed tags blocked
   - Form submissions controlled

3. **Clickjacking**
   - Frame ancestors controlled
   - X-Frame-Options enhanced

4. **Mixed Content**
   - HTTP resources blocked on HTTPS

---

## Task Requirements

### Phase 1: CSP Policy Design (30 min)

#### 1.1 Define CSP Directives
```javascript
// next.config.js CSP configuration
const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  img-src 'self' data: https: blob:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.financehub.app wss://ws.financehub.app;
  frame-src 'self';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  upgrade-insecure-requests;
`
```

#### 1.2 Identify Required Sources

| Resource Type | Allowed Sources | Justification |
|--------------|-----------------|---------------|
| Scripts | `self`, `unsafe-inline`, `unsafe-eval` | React hydration, third-party APIs |
| Styles | `self`, `unsafe-inline` | Tailwind CSS, dynamic styles |
| Images | `self`, `data:`, `https:`, `blob:` | User uploads, charts |
| Fonts | `self`, `fonts.gstatic.com` | Google Fonts |
| API | `self`, `api.financehub.app` | Backend API |
| WebSocket | `self`, `ws.financehub.app` | Real-time data |
| Frames | `self` | No external iframes |

---

### Phase 2: Implementation (30 min)

#### 2.1 Next.js Middleware for CSP Headers
**File:** `apps/frontend/src/middleware.ts`

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  // Content Security Policy
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https: blob:",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://api.financehub.app wss://ws.financehub.app",
    "frame-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "upgrade-insecure-requests",
  ].join('; ')

  response.headers.set('Content-Security-Policy', csp)

  // Additional Security Headers
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

  return response
}

export const config = {
  matcher: [
    '/:path*',
  ],
}
```

#### 2.2 Update Next.js Config
**File:** `apps/frontend/src/next.config.js`

```javascript
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: process.env.NODE_ENV === 'production'
              ? "default-src 'self'; script-src 'self' ..."
              : undefined,
          },
        ],
      },
    ]
  },
}
```

---

### Phase 3: Testing (30 min)

#### 3.1 Test CSP Headers
```bash
# Check CSP headers
curl -I https://localhost:3000 | grep -i content-security-policy

# Verify CSP is applied
curl -s -I https://localhost:3000 | grep -i "X-Content-Type-Options"
```

#### 3.2 Test XSS Prevention
```javascript
// Test that inline scripts are blocked
const testXSS = async () => {
  const response = await fetch('https://localhost:3000', {
    method: 'POST',
    body: '<script>alert("xss")</script>',
  })
  // Should be blocked or sanitized
}
```

#### 3.3 Report-URI Endpoint
```python
# Django endpoint for CSP violations
@router.post('/csp-report')
def csp_report(request):
    report = json.loads(request.body)
    # Log violation for monitoring
    logger.warning(f'CSP Violation: {report}')
    return {'status': 'ok'}
```

---

### Phase 4: Refinement (Optional)

#### 4.1 Nonce-Based CSP (Advanced)
```typescript
// Generate nonce for each request
export function middleware(request: NextRequest) {
  const nonce = generateNonce()
  request.headers.set('x-nonce', nonce)

  const response = NextResponse.next()
  response.headers.set('Content-Security-Policy', `
    script-src 'self' 'nonce-${nonce}'
    ...
  `)
  return response
}
```

#### 4.2 CSP Reporting
```javascript
// Add report-to directive
const csp = `
  default-src 'self';
  report-uri https://api.financehub.app/csp-report;
  report-to csp-endpoint;
`

// Django endpoint
@router.post('/csp-report')
def csp_report(request):
    report = request.json()
    # Analyze and alert on violations
    return {'status': 'received'}
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `apps/frontend/src/middleware.ts` | CSP middleware |
| `apps/backend/src/api/csp.py` | CSP violation reporting |
| `tests/security/test_csp.py` | CSP security tests |

## Files to Modify

| File | Changes |
|------|---------|
| `apps/frontend/src/next.config.js` | Add CSP headers |
| `apps/frontend/src/middleware.ts` | Create CSP middleware |

---

## Acceptance Criteria

- [ ] CSP headers present on all responses
- [ ] XSS attacks blocked by CSP
- [ ] No inline scripts allowed (except React)
- [ ] Third-party domains whitelisted
- [ ] CSP violation reporting configured
- [ ] Tests pass
- [ ] Documentation updated

---

## Rollback Plan

If CSP blocks legitimate functionality:
1. Adjust `script-src` directive
2. Add specific domains to allowlist
3. Use `report-only` mode for testing

```javascript
// Test with report-only
response.headers.set('Content-Security-Policy-Report-Only', csp)
```

---

## References

| Resource | URL |
|----------|-----|
| CSP Specification | https://content-security-policy.com/ |
| Next.js Security Headers | https://nextjs.org/docs/advanced-features/security-headers |
| OWASP CSP Guide | https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html |

---

## Questions for Gaudí

1. Should I proceed with implementing S-006 (CSP)?
2. Should we use strict CSP or relaxed for development?
3. Should we implement CSP reporting for monitoring?

---

**Task S-006 Created: Ready for Approval**

**Status:** ⏳ Waiting for Gaudí's decision
**Priority:** P1 (HIGH) - Addresses active XSS vulnerability
