# Security Testing Framework

**Document Version:** 1.0
**Created:** 2026-01-30
**Author:** Charo (Security Engineer)
**Last Updated:** 2026-01-30

---

## Overview

This document outlines the security testing framework for FinanceHub, including test categories, methodologies, and automation strategies.

---

## Test Categories

### 1. Authentication & Authorization Tests

#### 1.1 JWT Token Security
```python
def test_jwt_token_not_accessible_via_xss():
    """Verify tokens are not accessible via XSS attacks"""
    # Attempt to access localStorage via XSS simulation
    # Verify tokens are protected
    assert get_token_from_localstorage() is None

def test_jwt_token_expiration():
    """Verify JWT tokens expire correctly"""
    token = create_token(expiration=timedelta(minutes=15))
    assert token.expired after 16 minutes
    assert not token.expired after 14 minutes

def test_refresh_token_rotation():
    """Verify refresh tokens are rotated on use"""
    old_token = get_refresh_token()
    refresh_access_token()
    new_token = get_refresh_token()
    assert old_token != new_token
```

#### 1.2 Session Management
```python
def test_concurrent_sessions_limited():
    """Verify maximum concurrent sessions enforced"""
    for i in range(MAX_SESSIONS + 1):
        login()
    assert oldest_session_kicked()

def test_session_timeout():
    """Verify inactive sessions timeout"""
    # Simulate inactivity
    advance_time(SESSION_TIMEOUT + 1 minute)
    assert session_expired()
```

---

### 2. Input Validation Tests

#### 2.1 SQL Injection Prevention
```python
def test_sql_injection_prevention():
    """Verify SQL injection attempts are blocked"""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1; DELETE FROM portfolios WHERE 1=1",
        "' OR '1'='1",
    ]
    
    for input in malicious_inputs:
        response = api.get(f'/api/users?name={input}')
        assert response.status_code == 400
        assert 'error' in response.json()

def test_no_sql_injection_via_orm():
    """Verify ORM properly sanitizes queries"""
    # Attempt SQL injection through ORM
    user = User.objects.filter(name="' OR '1'='1").first()
    assert user is None
```

#### 2.2 XSS Prevention
```python
def test_xss_in_user_input():
    """Verify XSS payloads are sanitized"""
    xss_payloads = [
        '<script>alert("xss")</script>',
        '<img src=x onerror=alert("xss")>',
        'javascript:alert("xss")',
        '<svg onload=alert("xss")>',
    ]
    
    for payload in xss_payloads:
        response = api.post('/api/comments', data={'text': payload})
        # Verify payload is sanitized or rejected
        stored = get_comment_text()
        assert payload not in stored
        assert '<script>' not in stored

def test_dom_xss_prevention():
    """Verify DOM XSS is prevented"""
    # Test user input rendered in templates
    user_input = '<img src=x onerror=alert("xss")>'
    rendered = render_template(user_input)
    assert 'onerror' not in rendered
```

---

### 3. API Security Tests

#### 3.1 Rate Limiting
```python
def test_rate_limiting_enforced():
    """Verify API rate limiting works"""
    for i in range(RATE_LIMIT + 1):
        response = api.get('/api/data')
    
    assert response.status_code == 429
    assert 'Retry-After' in response.headers

def test_rate_limiting_resets():
    """Verify rate limit resets after window"""
    # Make requests up to limit
    for i in range(RATE_LIMIT):
        api.get('/api/data')
    
    # Wait for reset
    advance_time(RATE_WINDOW + 1 second)
    
    response = api.get('/api/data')
    assert response.status_code == 200
```

#### 3.2 Authentication Bypass
```python
def test_protected_endpoints_require_auth():
    """Verify protected endpoints reject unauthenticated requests"""
    protected_endpoints = [
        '/api/portfolios',
        '/api/users/me',
        '/api/trades',
        '/api/alerts',
    ]
    
    for endpoint in protected_endpoints:
        response = api.get(endpoint)
        assert response.status_code == 401

def test_authorization_enforced():
    """Verify users can only access their own resources"""
    # User A creates resource
    resource = create_resource(user=user_a)
    
    # User B attempts to access
    response = api.get(f'/api/resources/{resource.id}')
    assert response.status_code == 403
```

---

### 4. WebSocket Security Tests

#### 4.1 Connection Security
```python
def test_websocket_requires_authentication():
    """Verify WebSocket connections require authentication"""
    socket = WebSocketClient(url='ws://localhost:8001/ws')
    await socket.connect()
    
    # Should be disconnected or rejected
    assert socket.connection_rejected

def test_websocket_rate_limiting():
    """Verify WebSocket message rate limiting"""
    socket = await connect_websocket()
    
    # Send messages faster than allowed
    for i in range(MAX_WS_MESSAGES + 1):
        await socket.send_message({'test': 'data'})
    
    assert socket.connection_closed
```

---

### 5. File Upload Security

#### 5.1 Malicious File Detection
```python
def test_malicious_file_upload_blocked():
    """Verify malicious file uploads are blocked"""
    malicious_files = [
        ('shell.php', b'<?php system($_GET["cmd"]; ?>'),
        ('script.jpg', b'<script>alert("xss")</script>'),
        ('exe.pdf', b'%PDF-1.4\n...'),
    ]
    
    for filename, content in malicious_files:
        response = api.upload('/api/upload', 
                            files={'file': (filename, content)})
        assert response.status_code == 400

def test_file_size_limit():
    """Verify file size limits are enforced"""
    large_file = b'x' * (MAX_FILE_SIZE + 1)
    response = api.upload('/api/upload',
                         files={'file': ('large.csv', large_file)})
    assert response.status_code == 413
```

---

## Test Execution

### Run All Security Tests
```bash
# Backend
cd apps/backend
pytest tests/security/ -v

# Frontend
cd apps/frontend
npm test -- --testPathPattern=security
```

### Run Specific Test Categories
```bash
# Authentication tests only
pytest tests/security/test_authentication.py -v

# API security tests only
pytest tests/security/test_api_security.py -v

# XSS tests only
pytest tests/security/test_xss.py -v
```

---

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Security Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd apps/backend
          pip install -r requirements-testing.txt
      
      - name: Run security tests
        run: |
          pytest tests/security/ -v --tb=short
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-test-results
          path: apps/backend/test-results/
```

---

## Test Coverage Goals

| Category | Current Coverage | Target Coverage |
|----------|------------------|-----------------|
| Authentication | 50% | 90% |
| Input Validation | 40% | 85% |
| API Security | 60% | 90% |
| WebSocket Security | 20% | 80% |
| File Upload | 30% | 85% |

---

## Reporting

### Test Results Format
```json
{
  "summary": {
    "total_tests": 150,
    "passed": 145,
    "failed": 5,
    "skipped": 0,
    "pass_rate": "96.7%"
  },
  "vulnerabilities": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 10
  },
  "recommendations": [
    "Add rate limiting to /api/data endpoint",
    "Fix XSS vulnerability in comment rendering",
    "Implement CSRF protection on forms"
  ]
}
```

---

## References

| Resource | URL |
|----------|-----|
| OWASP Testing Guide | https://owasp.org/www-project-web-security-testing-guide/ |
| Django Security Tests | https://docs.djangoproject.com/en/stable/topics/testing/ |
| React Testing Library | https://testing-library.com/docs/react-testing-library/intro/ |

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-30 | Charo | Initial document |

---

**Document Version:** 1.0
**Next Review:** 2026-02-28
