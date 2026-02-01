# Task: Test All Backend API Endpoints

**Priority:** HIGH
**Status:** OPEN
**Assigned To:** Backend Team (Cassandra + Testing Specialist)
**Created:** February 1, 2026
**Estimated Time:** 6-8 hours

## Overview

After fixing the user registration endpoint, we need comprehensive testing of all backend API endpoints to ensure they work correctly. The registration endpoint had Pydantic V2 compatibility issues that may affect other endpoints.

## Critical Endpoints to Test

### 1. User Authentication Endpoints ✅ (PARTIALLY DONE)
- [x] **POST /users/register** - FIXED (Pydantic V2 compatibility)
- [ ] **POST /users/login** - Needs testing
- [ ] **POST /users/token/refresh** - Needs testing
- [ ] **POST /users/token/verify** - Needs testing
- [ ] **POST /users/token/blacklist** - Needs testing
- [ ] **GET /users/me** - Needs testing (requires auth)
- [ ] **PATCH /users/me** - Needs testing (requires auth)
- [ ] **POST /users/me/change-password** - Needs testing (requires auth)

### 2. Asset Endpoints
- [ ] **GET /assets/** - List all assets
- [ ] **GET /assets/<symbol>** - Get asset details
- [ ] **GET /assets/<symbol>/price** - Get current price
- [ ] **GET /assets/<symbol>/historical** - Get historical data
- [ ] **GET /assets/<symbol>/fundamentals** - Get fundamentals
- [ ] **GET /assets/<symbol>/news** - Get news for asset

### 3. Portfolio Endpoints
- [ ] **GET /portfolios/portfolios** - List portfolios (requires auth)
- [ ] **POST /portfolios/portfolios** - Create portfolio (requires auth)
- [ ] **GET /portfolios/portfolios/<id>** - Get portfolio (requires auth)
- [ ] **PATCH /portfolios/portfolios/<id>** - Update portfolio (requires auth)
- [ ] **DELETE /portfolios/portfolios/<id>** - Delete portfolio (requires auth)
- [ ] **GET /portfolios/portfolios/<id>/holdings** - List holdings (requires auth)
- [ ] **POST /portfolios/portfolios/<id>/holdings** - Add holding (requires auth)
- [ ] **PATCH /portfolios/portfolios/<id>/holdings/<holding_id>** - Update holding (requires auth)
- [ ] **DELETE /portfolios/portfolios/<id>/holdings/<holding_id>** - Delete holding (requires auth)
- [ ] **GET /portfolios/portfolios/<id>/transactions** - List transactions (requires auth)
- [ ] **POST /portfolios/portfolios/<id>/transactions** - Add transaction (requires auth)
- [ ] **GET /portfolios/assets** - List available assets
- [ ] **GET /portfolios/assets/<id>/prices** - Get asset prices

### 4. Market Data Endpoints
- [ ] **GET /market/market-data** - Get market overview
- [ ] **POST /market/market-data/batch** - Batch market data request
- [ ] **GET /market/price/<symbol>** - Get price for symbol
- [ ] **GET /market/historical/<symbol>** - Get historical data
- [ ] **GET /market/news** - Get market news
- [ ] **GET /market/technical/<symbol>** - Get technical analysis
- [ ] **GET /market/fundamentals/<symbol>** - Get fundamentals

### 5. Health & Status
- [x] **GET /health/** - Working (confirmed)

## Known Issues to Check

### Pydantic V2 Compatibility
The user registration endpoint failed because:
1. Used deprecated `from_orm()` method
2. Missing `from_attributes = True` in Config
3. Used old `schema_extra` instead of `json_schema_extra`

**Check all schemas for:**
- [ ] Any usage of `from_orm()` → replace with direct instantiation or `model_validate()`
- [ ] All `Config` classes have `from_attributes = True` if using Django models
- [ ] All `schema_extra` → `json_schema_extra`

### Response Schemas
Check all output schemas:
- [ ] User schemas (user.py, register.py, token.py, login.py)
- [ ] Portfolio schemas
- [ ] Asset schemas
- [ ] Market data schemas
- [ ] Transaction schemas

## Test Plan

### Phase 1: Authentication Flow (1-2 hours)
1. Register new user
2. Login to get tokens
3. Access protected endpoint with token
4. Refresh token
5. Logout/blacklist token

### Phase 2: Public Endpoints (1-2 hours)
1. Test all GET endpoints that don't require auth
2. Verify response schemas
3. Check error handling (invalid symbols, etc.)

### Phase 3: Protected Endpoints (2-3 hours)
1. Create portfolio
2. Add holdings
3. Add transactions
4. Update holdings
5. Get analytics
6. Delete data

### Phase 4: Edge Cases (1 hour)
1. Invalid data
2. Missing fields
3. Duplicate entries
4. Rate limiting
5. Permission checks

## Test Script Template

```bash
# 1. Register user
curl -X POST 'http://localhost:8000/users/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# 2. Login
TOKEN_RESPONSE=$(curl -s -X POST 'http://localhost:8000/users/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access')

# 3. Access protected endpoint
curl -X GET 'http://localhost:8000/users/me' \
  -H 'Authorization: Bearer $ACCESS_TOKEN'
```

## Files to Check

### Schemas (Pydantic V2 Compatibility)
- `/apps/backend/src/users/schemas/*.py` (user.py, register.py, login.py, token.py)
- `/apps/backend/src/portfolios/schemas/*.py`
- `/apps/backend/src/market/schemas/*.py`
- `/apps/backend/src/assets/schemas/*.py`

### API Endpoints
- `/apps/backend/src/users/api/auth/`
- `/apps/backend/src/portfolios/api/`
- `/apps/backend/src/market/api/`
- `/apps/backend/src/assets/api/`

## Success Criteria

✅ All public endpoints return valid responses
✅ All protected endpoints properly enforce authentication
✅ Pydantic V2 compatibility issues resolved
✅ Response schemas match API documentation
✅ Error handling works correctly
✅ No 500 errors (proper 4xx errors for bad requests)
✅ Rate limiting works where configured

## Deliverables

1. Test results document (pass/fail for each endpoint)
2. Fixed code for any broken endpoints
3. Updated schemas for Pydantic V2 compatibility
4. Test scripts for regression testing
5. Updated API documentation if needed

## Notes

- Use Django test framework: `python manage.py test <app>`
- Or create integration tests in `tests/` directory
- Check logs: `docker-compose logs backend`
- API docs available at: http://localhost:8000/docs
- Some endpoints may require external API keys (IEX, Alpha Vantage, etc.)

## Related Tasks

- D-014: Security Scanning Integration (already complete)
- Task: Fix Shadcn Sidebar Provider Issue (frontend)
- Previous fix: User Registration Pydantic V2 compatibility

## References

- Django Ninja Docs: https://django-ninja.rest-framework.com/
- Pydantic V2 Migration: https://docs.pydantic.dev/latest/migration/
- API Documentation: http://localhost:8000/docs
