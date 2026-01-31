# 📦 TASK: C-030 - Broker API Integration

**Task ID:** C-030
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Guido) or DevOps (Karen)
**Status:** ⏳ PENDING
**Priority:** P1 HIGH
**Estimated Time:** 14-18 hours
**Deadline:** February 15, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Integrate with broker APIs (Alpaca, Interactive Brokers, etc.) to enable:
- Account linking
- Automatic portfolio import
- Trade execution (future)
- Real-time account data sync

---

## 📋 REQUIREMENTS

### 1. Backend Integration
**Models:**
```python
# apps/backend/src/brokers/models.py
class BrokerConnection(models.Model):
    user = ForeignKey(User)
    broker_type = CharField()  # 'alpaca', 'interactive_brokers', etc.
    api_key = EncryptedCharField()
    api_secret = EncryptedCharField()
    is_active = BooleanField(default=True)
    last_sync = DateTimeField()
    created_at = DateTimeField(auto_now_add=True)

class BrokerPosition(models.Model):
    connection = ForeignKey(BrokerConnection)
    symbol = CharField()
    quantity = DecimalField()
    avg_cost = DecimalField()
    current_price = DecimalField()
    market_value = DecimalField()
    synced_at = DateTimeField()
```

**Service:**
```python
# apps/backend/src/brokers/services/broker_sync_service.py
class BrokerSyncService:
    def sync_positions(self, connection_id):
        """Fetch positions from broker API"""
        pass

    def sync_transactions(self, connection_id):
        """Fetch transaction history from broker API"""
        pass

    def sync_account_details(self, connection_id):
        """Fetch account details from broker API"""
        pass
```

**API Endpoints:**
```python
# apps/backend/src/brokers/api/
POST /api/brokers/connect - Connect new broker account
GET /api/brokers/connections - List user's broker connections
DELETE /api/brokers/connections/{id} - Disconnect broker
POST /api/brokers/sync/{id} - Manual sync trigger
GET /api/brokers/positions/{id} - Get synced positions
```

### 2. Broker Integrations

**Priority 1: Alpaca (easiest)**
- REST API integration
- OAuth authentication
- Position sync
- Transaction sync

**Priority 2: Interactive Brokers**
- IBKR API integration
- More complex authentication
- Wider asset coverage

**Priority 3: Coinbase (crypto)**
- Already exists in codebase
- Enhance integration

### 3. Security
- Encrypt API keys/secret in database
- OAuth flow where supported
- Rate limiting per broker
- Error handling for expired tokens
- Audit logging for all broker API calls

### 4. Data Mapping
- Map broker positions to internal Position model
- Map broker transactions to internal Transaction model
- Handle different asset classes
- Handle fractional shares
- Handle different currencies

---

## ✅ ACCEPTANCE CRITERIA

- [ ] User can connect Alpaca account via OAuth
- [ ] Positions sync automatically from broker
- [ ] Transactions sync automatically from broker
- [ ] API keys encrypted in database
- [ ] Sync happens every 5 minutes (background task)
- [ ] Error handling for expired/invalid credentials
- [ ] Manual sync trigger available
- [ ] Broker connection can be disconnected
- [ ] Audit logs for all broker API calls
- [ ] Rate limiting implemented
- [ ] Tests for sync service
- [ ] Tests for API endpoints
- [ ] Frontend UI for connecting broker accounts

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/brokers/models/broker_connection.py`
- `apps/backend/src/brokers/services/broker_sync_service.py`
- `apps/backend/src/brokers/api/broker_api.py`
- `apps/backend/src/brokers/tests/test_broker_sync.py`

### Modify:
- `apps/backend/src/brokers/models/__init__.py`
- `apps/frontend/src/components/portfolio/BrokerConnectionDialog.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- User authentication working
- Portfolio models exist
- Transaction models exist

**Related Tasks:**
- C-036: Paper Trading (can use broker API)
- C-025: CSV Import (alternative to broker import)

---

## 🚨 SECURITY CONSIDERATIONS

**Charo (Security) must review:**
- API key encryption (use `django-encrypted-fields`)
- OAuth token storage
- Rate limiting per user
- Audit logging
- Error messages don't leak credentials

---

## 📊 DELIVERABLES

1. **Backend Models:** BrokerConnection, BrokerPosition
2. **Service:** BrokerSyncService with sync methods
3. **API:** Connect/sync endpoints
4. **Frontend:** Broker connection dialog
5. **Tests:** Unit tests for sync service
6. **Documentation:** API integration guide

---

## 💬 NOTES

**Implementation Phases:**
1. Phase 1: Alpaca integration only (10-12h)
2. Phase 2: Add Interactive Brokers (4-6h additional)
3. Phase 3: Additional brokers (future)

**Third-Party Libraries:**
- `alpaca-trade-api` for Alpaca
- `ib-insync` for Interactive Brokers
- `django-encrypted-fields` for key storage

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Guido) or DevOps (Karen)
**Review:** Security review required before production

---

📦 *C-030: Broker API Integration*
*Connect real broker accounts, sync positions automatically*
