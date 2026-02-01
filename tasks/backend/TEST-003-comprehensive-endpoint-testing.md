# Task: Comprehensive Backend Endpoint Testing

**Priority:** HIGH
**Status:** OPEN
**Assigned To:** Backend Testing Team
**Created:** February 1, 2026
**Estimated Time:** 4-6 hours

## Overview

The frontend has been successfully built! Now we need comprehensive testing of all backend API endpoints to ensure they work correctly before production deployment.

## ✅ Build Status - COMPLETE

**Frontend:** ✅ Built Successfully (Next.js 16.1.6)
**Backend:** ✅ Running & Healthy (localhost:8000)
**Database:** ✅ PostgreSQL 15 (healthy)
**Cache:** ✅ Redis 7 (healthy)

**Frontend Build Output:**
- ✓ Compiled successfully in 8.7s
- ✓ TypeScript passed
- ✓ 35 routes generated
- ✓ Static pages generated
- ✓ Production build complete

## 🧪 Endpoint Testing Requirements

### Phase 1: User Authentication (1-2 hours)

#### 1.1 Registration ✅ (FIXED - Pydantic V2)
- **Endpoint:** `POST /users/register`
- **Status:** ✅ Working (tested)
- **Tests:**
  - [x] Valid registration - WORKS
  - [ ] Weak password validation - FIX NEEDED (returns 500)
  - [ ] Password mismatch validation - FIX NEEDED (returns 500)
  - [ ] Duplicate email detection - FIX NEEDED (returns 500)
  - [ ] Missing required fields - FIX NEEDED (returns 500)

#### 1.2 Login/Authentication
- **Endpoint:** `POST /users/login`
- **Tests:**
  - [ ] Valid login
  - [ ] Invalid username
  - [ ] Invalid password
  - [ ] Token structure validation
  - [ ] Token refresh flow

#### 1.3 Token Management
- **Endpoints:**
  - `POST /users/token/refresh`
  - `POST /users/token/verify`
  - `POST /users/token/blacklist`
- **Tests:**
  - [ ] Token refresh works
  - [ ] Token verification works
  - [ ] Token blacklist works
  - [ ] Expired token handling

#### 1.4 Protected Endpoints
- **Endpoints:**
  - `GET /users/me`
  - `PATCH /users/me`
  - `POST /users/me/change-password`
- **Tests:**
  - [ ] Access with valid token
  - [ ] Access without token (401)
  - [ ] Access with expired token (401)
  - [ ] Access with invalid token (401)

### Phase 2: Portfolio Management (1-2 hours)

#### 2.1 Portfolio CRUD
- **Endpoints:**
  - `GET /portfolios/portfolios` - List portfolios
  - `POST /portfolios/portfolios` - Create portfolio
  - `GET /portfolios/portfolios/{id}` - Get portfolio
  - `PATCH /portfolios/portfolios/{id}` - Update portfolio
  - `DELETE /portfolios/portfolios/{id}` - Delete portfolio
- **Tests:**
  - [ ] Create portfolio with valid data
  - [ ] Create portfolio with invalid data
  - [ ] List all portfolios (empty, one, multiple)
  - [ ] Get specific portfolio (own, others')
  - [ ] Update portfolio (own, others')
  - [ ] Delete portfolio (own, others')
  - [ ] Permission checks

#### 2.2 Holdings Management
- **Endpoints:**
  - `GET /portfolios/portfolios/{id}/holdings`
  - `POST /portfolios/portfolios/{id}/holdings`
  - `PATCH /portfolios/portfolios/{id}/holdings/{holding_id}`
  - `DELETE /portfolios/portfolios/{id}/holdings/{holding_id}`
- **Tests:**
  - [ ] Add holding to portfolio
  - [ ] List holdings
  - [ ] Update holding
  - [ ] Delete holding
  - [ ] Portfolio ownership checks
  - [ ] Invalid asset IDs

#### 2.3 Transactions
- **Endpoints:**
  - `GET /portfolios/portfolios/{id}/transactions`
  - `POST /portfolios/portfolios/{id}/transactions`
- **Tests:**
  - [ ] Add transaction
  - [ ] List transactions
  - [ ] Transaction types (buy, sell, dividend)
  - [ ] Invalid transaction data

### Phase 3: Market Data (1 hour)

#### 3.1 Asset Endpoints
- **Endpoints:**
  - `GET /assets/` - List assets
  - `GET /assets/{symbol}` - Get asset details
  - `GET /assets/{symbol}/price` - Get current price
  - `GET /assets/{symbol}/historical` - Get historical data
  - `GET /assets/{symbol}/fundamentals` - Get fundamentals
  - `GET /assets/{symbol}/news` - Get news
- **Tests:**
  - [ ] Valid symbols (AAPL, GOOGL, etc.)
  - [ ] Invalid symbols
  - [ ] Historical data date ranges
  - [ ] Pagination (if applicable)

#### 3.2 Market Overview
- **Endpoints:**
  - `GET /market/market-data`
  - `POST /market/market-data/batch`
  - `GET /market/price/{symbol}`
  - `GET /market/historical/{symbol}`
  - `GET /market/news`
  - `GET /market/technical/{symbol}`
  - `GET /market/fundamentals/{symbol}`
- **Tests:**
  - [ ] Market overview data
  - [ ] Batch data requests
  - [ ] Technical analysis data
  - [ ] News data
  - [ ] Error handling for invalid symbols

### Phase 4: Edge Cases & Error Handling (1 hour)

#### 4.1 Input Validation
- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] Malformed JSON
- [ ] Missing required fields
- [ ] Invalid data types
- [ ] Out of range values

#### 4.2 Rate Limiting
- [ ] Verify rate limits are enforced
- [ ] Check rate limit headers
- [ ] Test rate limit recovery

#### 4.3 Authentication Edge Cases
- [ ] Concurrent logins
- [ ] Token reuse after blacklist
- [ ] Password change during active session
- [ ] Session expiration

## Test Execution Plan

### Automated Tests
Create test scripts for each endpoint category:

```bash
#!/bin/bash
# test-endpoints.sh

BASE_URL="http://localhost:8000"

echo "=== Testing User Registration ==="
# Valid registration
curl -X POST "${BASE_URL}/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test'$(date +%s)'@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }' | jq .

# Login
echo "=== Testing Login ==="
TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access')
echo "Access Token: ${ACCESS_TOKEN:0:20}..."

# Protected endpoint
echo "=== Testing Protected Endpoint ==="
curl -X GET "${BASE_URL}/users/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .

# Test without token
echo "=== Testing Without Token ==="
curl -X GET "${BASE_URL}/users/me" | jq .
```

### Manual Testing Checklist

Use Postman/Insomnia or frontend for:
- [ ] All authentication flows work in UI
- [ ] Portfolio creation/management works
- [ ] Charts load with real data
- [ ] Real-time updates work
- [ ] Error messages are user-friendly

## Success Criteria

✅ All public endpoints return valid responses
✅ All protected endpoints enforce authentication
✅ Validation returns proper 422 errors (not 500)
✅ Error messages are clear and actionable
✅ No 500 errors for expected failures
✅ Rate limiting works
✅ Performance is acceptable (< 2s for most endpoints)

## Deliverables

1. Test results spreadsheet (pass/fail for each endpoint)
2. Collection of curl test scripts
3. Bug reports for any issues found
4. Fixed code for validation errors
5. Updated API documentation if needed

## Known Issues to Fix

### 1. Registration Validation Errors (HIGH PRIORITY)
**Issue:** Validation failures return 500 instead of 422
**Related Task:** FIX-002-registration-validation-errors.md
**Status:** Task created, awaiting fix

**Tests to Run:**
```bash
# Test weak password
curl -X POST 'http://localhost:8000/users/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "weakuser",
    "email": "weak@example.com",
    "password": "weak",
    "password_confirm": "weak"
  }'

# Expected: 422 with validation errors
# Current: 500 database error
```

## Next Steps

1. **Immediate:** Run authentication endpoint tests
2. **Today:** Complete Phase 1 & 2 (Auth + Portfolios)
3. **Tomorrow:** Complete Phase 3 & 4 (Market + Edge Cases)
4. **This Week:** Fix any issues found
5. **Ongoing:** Add tests to CI/CD pipeline

## Tools

- **curl** - For API testing
- **jq** - For JSON parsing
- **Postman/Insomnia** - For manual testing
- **pytest** - For automated tests (setup in TEST-002)
- **Frontend** - http://localhost:3000 (built and ready)

## Related Tasks

- **TEST-002:** Backend Testing Infrastructure Setup (pytest, fixtures)
- **FIX-002:** Registration Validation Errors (validation returns 500)
- **D-014:** Security Scanning Integration (already complete)
- **Frontend Build:** ✅ COMPLETE

## Resources

- API Documentation: http://localhost:8000/docs
- Backend Health: http://localhost:8000/health/
- Frontend: http://localhost:3000
- Test Scripts: `/scripts/test-endpoints.sh`

---

**APP IS READY FOR TESTING! 🚀**

Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
