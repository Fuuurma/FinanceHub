# API Security Testing Guide

**Date:** 2026-01-31
**Author:** Charo (Security Engineer)
**Version:** 1.0

---

## Overview

This guide provides comprehensive API security testing procedures for FinanceHub endpoints. Use this document to verify API security during development and testing.

---

## Authentication Testing

### 1. JWT Token Testing

#### 1.1 Test Token Expiration

```bash
# Request with expired token
curl -X GET http://localhost:8000/api/portfolio/ \
  -H "Authorization: Bearer <expired_token>"

# Expected Response: 401 Unauthorized
# {"error": "Token has expired"}
```

#### 1.2 Test Token Validation

```bash
# Request with malformed token
curl -X GET http://localhost:8000/api/portfolio/ \
  -H "Authorization: Bearer invalid.token.here"

# Expected Response: 401 Unauthorized
```

#### 1.3 Test Missing Token

```bash
# Request without authorization header
curl -X GET http://localhost:8000/api/portfolio/

# Expected Response: 401 Unauthorized
# {"detail": "Authentication credentials were not provided."}
```

### 2. Token Rotation Testing

```python
import requests

def test_token_rotation():
    """Test that refresh tokens are properly rotated"""
    # Login to get tokens
    login_response = requests.post(
        'http://localhost:8000/api/auth/login/',
        json={'username': 'test', 'password': 'test'}
    )
    
    tokens = login_response.json()
    refresh_token = tokens['refresh']
    
    # Use refresh token
    refresh_response = requests.post(
        'http://localhost:8000/api/auth/token/refresh/',
        json={'refresh_token': refresh_token}
    )
    
    new_tokens = refresh_response.json()
    
    # Old refresh token should be invalid now
    reuse_response = requests.post(
        'http://localhost:8000/api/auth/token/refresh/',
        json={'refresh_token': refresh_token}
    )
    
    assert reuse_response.status_code == 401
    print("✅ Token rotation working correctly")
```

---

## Authorization Testing

### 1. IDOR (Insecure Direct Object Reference) Testing

#### 1.1 User Resource Access

```bash
# Create two users
USER1_TOKEN="<user1_token>"
USER2_TOKEN="<user2_token>"
USER1_PORTFOLIO_ID="<user1_portfolio_id>"

# User1 should access their own portfolio
curl -X GET http://localhost:8000/api/portfolios/$USER1_PORTFOLIO_ID/ \
  -H "Authorization: Bearer $USER1_TOKEN"
# Expected: 200 OK

# User2 should NOT access User1's portfolio
curl -X GET http://localhost:8000/api/portfolios/$USER1_PORTFOLIO_ID/ \
  -H "Authorization: Bearer $USER2_TOKEN"
# Expected: 403 Forbidden
```

#### 1.2 Bulk Data Access

```bash
# Try to access all portfolios (should be filtered)
curl -X GET http://localhost:8000/api/portfolios/ \
  -H "Authorization: Bearer $USER1_TOKEN"
# Expected: Only user's own portfolios returned
```

### 2. Role-Based Access Control

```python
def test_role_permissions():
    """Test role-based access control"""
    
    # Test free tier limits
    free_user = get_free_user()
    assert free_user.tier == 'free'
    
    # Free tier should have limited API calls
    for i in range(101):
        response = api.get('/api/market/quotes/', token=free_user.token)
    
    assert response.status_code == 429  # Rate limited
    
    # Premium user should have higher limits
    premium_user = get_premium_user()
    for i in range(1000):
        response = api.get('/api/market/quotes/', token=premium_user.token)
    
    assert response.status_code == 200  # Not rate limited
```

---

## Input Validation Testing

### 1. SQL Injection Testing

```bash
# Test for SQL injection in portfolio ID
curl -X GET "http://localhost:8000/api/portfolios/1' OR '1'='1/" \
  -H "Authorization: Bearer $TOKEN"
# Expected: 404 Not Found or 400 Bad Request (not 500 Internal Error)

# Test in search parameters
curl -X GET "http://localhost:8000/api/assets/search?q='; DROP TABLE assets;--" \
  -H "Authorization: Bearer $TOKEN"
# Expected: 400 Bad Request or sanitized response
```

```python
def test_sql_injection_prevention():
    """Verify SQL injection is prevented"""
    
    # Attempt SQL injection in various fields
    malicious_inputs = [
        "' OR '1'='1",
        "'; DROP TABLE users;--",
        "1; DELETE FROM portfolios WHERE 1=1",
        "admin'--",
        "UNION SELECT * FROM users--"
    ]
    
    for payload in malicious_inputs:
        response = requests.get(
            f'http://localhost:8000/api/portfolios/{payload}/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Should NOT return 500 Internal Server Error
        assert response.status_code != 500, f"SQLi possible: {payload}"
        
        # Should return 400 or 404
        assert response.status_code in [400, 404, 403]
    
    print("✅ SQL Injection prevention verified")
```

### 2. XSS Testing

```bash
# Test XSS in user profile
curl -X PUT http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bio": "<script>alert('XSS')</script>"}'

# Expected: 400 Bad Request or sanitized input
```

```python
def test_xss_prevention():
    """Verify XSS payloads are sanitized"""
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>"
    ]
    
    for payload in xss_payloads:
        response = requests.put(
            'http://localhost:8000/api/users/me/',
            json={'bio': payload},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Get the stored value
        get_response = requests.get(
            'http://localhost:8000/api/users/me/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Script tags should be escaped or stripped
        stored_bio = get_response.json().get('bio', '')
        assert '<script>' not in stored_bio
        assert 'onerror=' not in stored_bio
        assert 'javascript:' not in stored_bio
    
    print("✅ XSS prevention verified")
```

### 3. Mass Assignment Testing

```bash
# Try to modify read-only fields
curl -X POST http://localhost:8000/api/portfolios/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Portfolio",
    "is_admin": true,
    "id": 999999,
    "created_at": "2099-12-31T23:59:59Z"
  }'

# Expected: Fields should be ignored, not set
```

### 4. Parameter Pollution Testing

```bash
# Test duplicate parameters
curl -X GET "http://localhost:8000/api/portfolios/?id=1&id=2" \
  -H "Authorization: Bearer $TOKEN"

# Test type confusion
curl -X GET "http://localhost:8000/api/portfolios/abc" \
  -H "Authorization: Bearer $TOKEN"
# Expected: 400 or 404, not 500
```

---

## Rate Limiting Testing

### 1. Basic Rate Limit

```python
def test_rate_limiting():
    """Test API rate limiting"""
    
    # Make requests rapidly
    responses = []
    for i in range(110):  # Assuming limit is 100/hour
        response = requests.get(
            'http://localhost:8000/api/market/quotes/',
            headers={'Authorization': f'Bearer {token}'}
        )
        responses.append(response.status_code)
    
    # Check if rate limited
    rate_limited = sum(1 for r in responses if r == 429)
    
    assert rate_limited > 0, "Rate limiting not working"
    print(f"✅ Rate limiting active: {rate_limited} requests blocked")
```

### 2. Different Endpoints

```python
def test_endpoint_specific_limits():
    """Test different rate limits per endpoint"""
    
    # Some endpoints may have different limits
    endpoints = [
        ('/api/market/quotes/', 100),  # 100/hour
        ('/api/portfolios/', 50),      # 50/hour
        ('/api/orders/', 30),          # 30/hour
    ]
    
    for endpoint, limit in endpoints:
        blocked = 0
        for i in range(limit + 10):
            response = requests.get(
                f'http://localhost:8000{endpoint}',
                headers={'Authorization': f'Bearer {token}'}
            )
            if response.status_code == 429:
                blocked += 1
        
        assert blocked > 0, f"Rate limiting not working for {endpoint}"
        print(f"✅ {endpoint}: {blocked} requests blocked (limit: {limit}/hour)")
```

---

## Error Handling Testing

### 1. Verbose Error Messages

```bash
# Force an error to check error message content
curl -X GET http://localhost:8000/api/nonexistent/ \
  -H "Authorization: Bearer $TOKEN"

# Response should NOT contain:
# - Stack traces
# - Database queries
# - Internal paths
# - Server version info
```

```python
def test_error_message_security():
    """Verify errors don't leak sensitive information"""
    
    endpoints = [
        '/api/portfolios/999999/',
        '/api/users/999999/',
        '/api/orders/999999/',
    ]
    
    for endpoint in endpoints:
        response = requests.get(
            f'http://localhost:8000{endpoint}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code >= 400:
            error_text = response.text.lower()
            
            # Check for leaked information
            leaks = [
                'traceback' in error_text,
                'psycopg2' in error_text,
                'postgresql' in error_text,
                '/var/www' in error_text,
                'secret' in error_text,
                'password' in error_text,
            ]
            
            assert not any(leaks), f"Error leak in {endpoint}: {response.text[:200]}"
    
    print("✅ No sensitive information leaked in errors")
```

### 2. Timing Attacks

```python
import time

def test_timing_attack_resistance():
    """Verify timing attacks are mitigated"""
    
    # Test login timing for existing vs non-existing user
    existing_user = 'testuser@example.com'
    nonexistent = 'nonexistent@example.com'
    
    times = []
    for _ in range(10):
        start = time.time()
        requests.post(
            'http://localhost:8000/api/auth/login/',
            json={'email': existing_user, 'password': 'wrong'}
        )
        times.append(time.time() - start)
    
    existing_avg = sum(times) / len(times)
    
    times = []
    for _ in range(10):
        start = time.time()
        requests.post(
            'http://localhost:8000/api/auth/login/',
            json={'email': nonexistent, 'password': 'wrong'}
        )
        times.append(time.time() - start)
    
    nonexistent_avg = sum(times) / len(times)
    
    # Timing difference should be minimal
    timing_diff = abs(existing_avg - nonexistent_avg)
    assert timing_diff < 0.5, f"Possible timing attack: {timing_diff}s difference"
    
    print(f"✅ Timing attack resistance verified (diff: {timing_diff:.3f}s)")
```

---

## Data Exposure Testing

### 1. Field-Level Authorization

```python
def test_field_level_authorization():
    """Test that users can only see their own data"""
    
    # User1's portfolio
    user1_portfolio = get_portfolio(user1_token, user1_portfolio_id)
    
    # Should see their own data
    assert 'holdings' in user1_portfolio
    assert 'value' in user1_portfolio
    
    # User2 viewing User1's portfolio (should fail)
    user2_viewing_user1 = get_portfolio(user2_token, user1_portfolio_id)
    
    # Should not see detailed holdings
    assert user2_viewing_user1.status_code == 403
```

### 2. Pagination Security

```python
def test_pagination_limits():
    """Test pagination doesn't expose data"""
    
    # Get first page
    page1 = requests.get(
        'http://localhost:8000/api/portfolios/',
        headers={'Authorization': f'Bearer {token}'},
        params={'page': 1, 'limit': 100}
    )
    
    # Get second page
    page2 = requests.get(
        'http://localhost:8000/api/portfolios/',
        headers={'Authorization': f'Bearer {token}'},
        params={'page': 2, 'limit': 100}
    )
    
    # Verify total count doesn't exceed user's data
    assert len(page1.json()['results']) <= 100
    assert len(page2.json()['results']) <= 100
    
    # Verify no data from other users
    for item in page1.json()['results']:
        assert item['user_id'] == expected_user_id
```

---

## WebSocket Security Testing

### 1. Authentication

```python
def test_websocket_authentication():
    """Test WebSocket requires authentication"""
    
    # Without token - should be rejected
    with pytest.raises(WebSocketDisconnect):
        connect('ws://localhost:8000/ws/market-data/')
    
    # With invalid token - should be rejected
    with pytest.raises(WebSocketDisconnect):
        connect(
            'ws://localhost:8000/ws/market-data/',
            headers={'Authorization': 'Bearer invalid'}
        )
    
    # With valid token - should connect
    communication = connect(
        'ws://localhost:8000/ws/market-data/',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert communication.is_connected
```

### 2. Rate Limiting

```python
def test_websocket_rate_limiting():
    """Test WebSocket message rate limiting"""
    
    communication = connect(
        'ws://localhost:8000/ws/market-data/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    # Send many messages rapidly
    for i in range(100):
        communication.send_json({
            'type': 'subscribe',
            'symbol': 'AAPL'
        })
    
    # Should be disconnected or rate limited
    # Check for error response
    response = communication.receive_json()
    assert response.get('type') != 'error' or 'rate' in response.get('message', '').lower()
```

---

## Automated Security Test Suite

```python
import pytest

@pytest.mark.security
class TestAPISecurity:
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for tests"""
        response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json={'username': 'test', 'password': 'test'}
        )
        return response.json()['access']
    
    def test_unauthenticated_access(self, auth_token):
        """Test endpoints require authentication"""
        endpoints = [
            ('GET', '/api/portfolios/'),
            ('POST', '/api/orders/'),
            ('PUT', '/api/users/me/'),
        ]
        
        for method, endpoint in endpoints:
            response = requests.request(
                method,
                f'http://localhost:8000{endpoint}',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            # Should work with valid token
            assert response.status_code != 401
    
    def test_sql_injection_all_params(self, auth_token):
        """Test all parameters for SQL injection"""
        # Implementation from above
        pass
    
    def test_xss_all_input_fields(self, auth_token):
        """Test all input fields for XSS"""
        # Implementation from above
        pass
    
    def test_rate_limiting_headers(self, auth_token):
        """Test rate limiting headers present"""
        response = requests.get(
            'http://localhost:8000/api/market/quotes/',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # Should have rate limit headers
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
    
    def test_security_headers(self, auth_token):
        """Test security headers in responses"""
        response = requests.get(
            'http://localhost:8000/api/',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # Django should have security headers
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
```

---

## Test Execution

```bash
# Run all security tests
pytest tests/security/ -v

# Run specific test category
pytest tests/security/test_api_authentication.py -v
pytest tests/security/test_input_validation.py -v

# Run with coverage
pytest tests/security/ --cov=apps.backend.src --cov-report=html

# Generate security report
pytest tests/security/ --tb=short --junit-xml=security_report.xml
```

---

## Checklist

### Before Deployment
- [ ] All authentication tests pass
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Rate limiting is active
- [ ] Error messages don't leak info
- [ ] Authorization is enforced
- [ ] Rate limit headers present
- [ ] Security headers configured

### Regular Security Testing
- [ ] Weekly API security tests
- [ ] Monthly penetration testing
- [ ] Quarterly security audit
- [ ] Annual comprehensive review

---

**Document Version:** 1.0
**Last Updated:** 2026-01-31
