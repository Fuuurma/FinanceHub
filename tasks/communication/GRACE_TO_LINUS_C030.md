## TEST COORDINATION REQUEST - C-030 Broker Integration

**From:** GRACE (QA Engineer)
**To:** Linus (Backend) + Turing (Frontend)
**Date:** February 1, 2026

---

### Test File Created

**Backend:** `apps/backend/src/brokers/tests/test_broker_integration.py`
- 9 test scenarios (TC-BI-001 through TC-BI-009)
- Tests: Account connection, order execution, cancellation, position sync, security

### What I Need From You

1. **Linus:**
   - BrokerService at `src/brokers/services/broker_service.py`
   - AlpacaService at `src/brokers/services/alpaca_service.py`
   - BrokerConnectionError at `src/brokers/exceptions.py`
   - InvalidCredentialsError at `src/brokers/exceptions.py`
   - PermissionDeniedError at `src/brokers/exceptions.py`
   - Test Alpaca API credentials (paper trading account)

2. **Turing:**
   - Broker connection UI components (if any)

### Test Status
- ✅ Test file created
- ⏳ Pending execution (need dev builds + test credentials)
- ⏳ Security validation (need Charo review)

### Performance Targets
- Order execution: < 1 second
- API keys: Encrypted at rest
- User isolation: Verified

### Security Requirements (per Charo)
- API keys must be encrypted before storage
- User A cannot access User B's broker accounts
- All tests use paper trading accounts only (no real money)

**Ready to execute tests when builds and test credentials are available.**

- GRACE
