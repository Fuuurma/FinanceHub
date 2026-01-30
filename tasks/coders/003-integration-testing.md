# Task C-003: Integration Testing

**Assigned To:** All Coders (2 backend + 1 frontend)
**Priority:** P0 (CRITICAL)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-02-02 5:00 PM
**Estimated Time:** 3 hours
**Dependencies:** C-001, C-002 (Path fixes complete)

---

## Overview
Perform comprehensive integration testing to verify backend and frontend work together correctly after the monorepo migration.

## Context
After fixing all path references, we need to verify the entire system still works. This includes backend-frontend communication, database connections, Docker integration, and end-to-end functionality.

## Acceptance Criteria
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] API calls succeed
- [ ] Database queries work
- [ ] Docker compose works
- [ ] E2E tests pass
- [ ] No console errors
- [ ] Websockets connect (if applicable)

## Prerequisites
- [ ] C-001 complete (Backend paths fixed)
- [ ] C-002 complete (Frontend paths fixed)
- [ ] All unit tests passing
- [ ] Database running

## Implementation Steps

### Step 1: Backend-Frontend Integration Test
```bash
# Terminal 1: Start Backend
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend
python manage.py runserver

# Expected output:
# Starting development server at http://127.0.0.1:8000/
```

```bash
# Terminal 2: Start Frontend (new terminal window)
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/frontend
npm run dev

# Expected output:
# Ready on http://localhost:3000
```

**Test Scenarios:**
1. Open browser: `http://localhost:3000`
2. Verify homepage loads
3. Check browser console for errors
4. Try logging in (if auth implemented)
5. Load data from API
6. Verify no CORS errors
7. Check Network tab in DevTools

**Expected Results:**
- ✅ Both servers start without errors
- ✅ Frontend can reach backend
- ✅ API responses are successful
- ✅ No CORS errors
- ✅ No console errors

### Step 2: Database Connection Test
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend

# Access database shell
python manage.py dbshell

# Run test queries
SHOW TABLES;
SELECT COUNT(*) FROM assets_country;
SELECT COUNT(*) FROM investments_currency;
SELECT COUNT(*) FROM assets_exchange;  # Verify correct table
SELECT COUNT(*) FROM assets_asset LIMIT 10;

# Exit
exit
```

**Expected Results:**
- ✅ Database connects successfully
- ✅ All tables accessible
- ✅ Data queries return results
- ✅ Exchange table exists (assets_exchanges)

### Step 3: Docker Integration Test
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Stop any running containers
docker-compose down

# Build and start all services
docker-compose up --build

# Expected:
# - Backend container builds and starts
# - Frontend container builds and starts
# - Database container starts
# - Services can communicate
```

**Test Scenarios:**
1. Check container status: `docker-compose ps`
2. View logs: `docker-compose logs backend`
3. View logs: `docker-compose logs frontend`
4. Access frontend: `http://localhost:3000`
5. Test API: `curl http://localhost:8000/api/`

**Expected Results:**
- ✅ All containers start
- ✅ No container crashes
- ✅ Logs show no errors
- ✅ Services accessible

### Step 4: API Endpoint Tests
```bash
# Test various API endpoints
curl http://localhost:8000/api/
curl http://localhost:8000/api/auth/login/
curl http://localhost:8000/api/assets/search/?q=AAPL
curl http://localhost:8000/api/markets/overview/
```

**Expected Results:**
- ✅ Endpoints respond
- ✅ JSON data returned
- ✅ No 404 errors
- ✅ No 500 errors

### Step 5: WebSocket Connection Test (if applicable)
```bash
# Check if WebSocket endpoints work
# Verify Daphne/ASGI server running

# Test from browser console
const ws = new WebSocket('ws://localhost:8000/ws/market/');
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

**Expected Results:**
- ✅ WebSocket connects
- ✅ No connection errors
- ✅ Messages received

### Step 6: End-to-End Tests
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/frontend

# Run E2E tests (if configured)
npm run test:e2e

# Or manually test:
# 1. User registration/login
# 2. Load market data
# 3. View stock details
# 4. Create watchlist
# 5. View portfolio
```

**Expected Results:**
- ✅ All E2E tests pass
- ✅ User flows work correctly
- ✅ Data displays properly

### Step 7: Performance Check
```bash
# Check page load times
# Check API response times
# Verify no memory leaks
# Check console for warnings

# In browser DevTools:
# - Network tab: Check response times
# - Performance tab: Check load times
# - Console: Check for warnings
```

**Expected Results:**
- ✅ Page loads in < 3 seconds
- ✅ API responses in < 1 second
- ✅ No memory leaks
- ✅ No performance warnings

### Step 8: Cross-Browser Test (if time permits)
```bash
# Test in multiple browsers:
# - Chrome/Edge (Chromium)
# - Firefox
# - Safari (if on Mac)

# Verify:
# - All browsers work correctly
# - No browser-specific issues
# - Consistent behavior
```

## Test Results Documentation

### Backend Tests:
- [ ] Server starts: ✅ / ❌
- [ ] Database connects: ✅ / ❌
- [ ] API endpoints work: ✅ / ❌
- [ ] No console errors: ✅ / ❌
- [ ] WebSocket connects: ✅ / ❌

### Frontend Tests:
- [ ] Server starts: ✅ / ❌
- [ ] Pages load: ✅ / ❌
- [ ] API calls succeed: ✅ / ❌
- [ ] No console errors: ✅ / ❌
- [ ] Build works: ✅ / ❌

### Integration Tests:
- [ ] Backend-Frontend communication: ✅ / ❌
- [ ] Docker compose works: ✅ / ❌
- [ ] E2E tests pass: ✅ / ❌
- [ ] No CORS errors: ✅ / ❌
- [ ] No 404/500 errors: ✅ / ❌

## Issues Found

### Issue #[N]: [Title]
- **Severity:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- **Location:** [Component/Page/API]
- **Description:** [What's wrong]
- **Steps to Reproduce:** [How to trigger]
- **Expected Behavior:** [What should happen]
- **Actual Behavior:** [What happens]
- **Screenshot/Log:** [Attach]

## Files Modified
- [ ] [If any fixes needed during testing]

## Code Quality Checklist
- [ ] All tests passing
- [ ] No console errors
- [ ] No network errors
- [ ] Pages load quickly
- [ ] Data displays correctly
- [ ] User flows work

## Rollback Plan
```bash
# If critical issues found:
1. Document issues
2. Report to Architect
3. Fix issues or rollback
4. Re-test

# Rollback command:
git reset --hard HEAD
```

## Tools to Use
- **MCP:** bash commands, docker operations
- **Manual:** Browser testing, DevTools
- **Testing:** Jest, Playwright (if configured)

## Dependencies
- ✅ C-001 (Backend paths fixed)
- ✅ C-002 (Frontend paths fixed)

## Feedback to Architect
[After completing, report using this format]

### What We Tested:
- ✅ Backend server startup
- ✅ Frontend server startup
- ✅ API endpoint connectivity
- ✅ Database queries
- ✅ Docker integration
- ✅ WebSocket connections
- ✅ End-to-end user flows

### Test Results:
**Backend Tests:**
- Server start: ✅ PASSED
- Database: ✅ PASSED
- API endpoints: ✅ PASSED ([N]/[N] successful)
- WebSocket: ✅ PASSED / ⚠️ PARTIAL / ❌ FAILED

**Frontend Tests:**
- Server start: ✅ PASSED
- Page loads: ✅ PASSED
- API calls: ✅ PASSED
- Build: ✅ PASSED

**Integration Tests:**
- Backend-Frontend: ✅ PASSED
- Docker compose: ✅ PASSED
- E2E tests: ✅ PASSED ([N]/[N])
- CORS: ✅ NO ERRORS
- Performance: ✅ GOOD

### Issues Found:
🔴 **[N] Critical Issues**
- [List if any]

🟠 **[N] High Issues**
- [List if any]

🟡 **[N] Medium Issues**
- [List if any]

### Assessment:
✅ **Integration is HEALTHY** - All systems working
OR
⚠️ **Integration has ISSUES** - [List blockers]

### Ready for Next Step:
Integration testing complete. Ready for Security validation (Task S-001) and final cleanup (Task D-005).

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when start testing]
- **[YYYY-MM-DD HH:MM]:** [Update with results]

---
**Last Updated:** 2026-01-30
**Note:** All 3 coders should participate in testing
**Next Step:** S-001 (Security Validation) - Charo's task
