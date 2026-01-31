# Task S-012: WebSocket Auth Header Migration

**Task ID:** S-012
**Priority:** P1 (HIGH)
**Status:** ✅ APPROVED - Ready for Coder Assignment
**Estimated Time:** 1-2 hours
**Action:** Move WebSocket token from query string to Authorization header

---

## Overview
Move WebSocket authentication from URL query string to Authorization header to prevent token leakage in logs and browser history.

## File to Modify
`apps/backend/src/websocket_consumers/auth_middleware.py`

## Key Changes
```python
# Before - Token in URL query string
query_string = scope.get('query_string', b'').decode('utf-8')
token = dict(param.split('=') for param in query_string.split('&') if '=' in param).get('token')

# After - Token in Authorization header
auth_header = dict(scope.get('headers', [])).get(b'authorization', b'').decode()
if auth_header.startswith('Bearer '):
    token = auth_header[7:]
```

## Acceptance Criteria
- [ ] Tokens not visible in URLs
- [ ] No token in query strings
- [ ] Authorization header used
- [ ] Tests verify header-based auth
