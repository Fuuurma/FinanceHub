# FinanceHub Database Schema Documentation

**Last Updated:** 2026-01-30
**Status:** ANALYSIS COMPLETE - Improvements identified

---

## Overview

FinanceHub uses **Django ORM** with **PostgreSQL** as the primary database.

**Total Models Found:** 50+ models across 10 modules

### Core Modules
- `users` - Authentication & Authorization
- `assets` - Asset management & reference data
- `portfolios` - Holdings, Transactions, Performance
- `investments` - Watchlists, Alerts, Market data
- `fundamentals` - Financial statements, earnings
- `ai_advisor` - AI templates & reports
- `charts` - User chart drawings
- `trading` - Orders & positions

---

## Database Schema Analysis

### ✅ STRENGTHS

1. **UUID Primary Keys**
   - All models use UUIDs (via `UUIDModel`)
   - No sequential ID enumeration attacks
   - Obfuscated URLs

2. **Timestamped Models**
   - All models have `created_at` and `updated_at`
   - Consistent audit trail

3. **Soft Delete**
   - Most models inherit from `SoftDeleteModel`
   - `is_deleted` flag prevents data loss

4. **Comprehensive Indexing**
   - Foreign keys indexed
   - Date fields indexed
   - Composite indexes for common queries

5. **JSON Fields**
   - `metadata` field on User, Asset for extensibility
   - `preferences` on User
   - `related_symbols` on NewsArticle

6. **Asset Classification**
   - AssetClass (Equities, Crypto, etc.)
   - AssetType (Common Stock, ETF, Bitcoin)
   - Sector/Industry classification
   - Country reference
   - Exchange tracking

7. **User Security**
   - 2FA support
   - Login tracking (IP, timestamp)
   - Account lockout
   - Role-based access control

8. **Portfolio Tracking**
   - Holdings with average buy price
   - Transactions with fees
   - Performance metrics (Sharpe, drawdown)
   - Paper trading support

9. **Alert System**
   - Multiple alert types (price, RSI, MACD)
   - Delivery channels (websocket, email, push)
   - Alert history for auditing
   - Cooldown periods

10. **Market Data**
    - News with sentiment analysis
    - Economic indicators
    - Dividends & corporate actions
    - Technical indicators

---

## ❌ ISSUES & IMPROVEMENTS NEEDED

### CRITICAL (P0)

#### 1. Duplicate Exchange Tables
**Issue:** Two `exchange` models (root-level and backend)
- Root: `src/assets/models/exchange.py` (OLD schema)
- Backend: `apps/backend/src/assets/models/exchange.py` (NEW schema)

**Impact:** Schema mismatch between projects

**Fix:** Already migrated - root now uses same schema

---

#### 2. Deprecated Columns in Asset Model

**Issue:** CharField columns still exist but marked deprecated:

```python
sector = models.CharField(max_length=150, blank=True, null=True)
industry = models.CharField(max_length=150, blank=True, null=True)
```

**Impact:** Data inconsistency, migration debt

**Fix:**
```sql
-- Create migration to remove deprecated columns
ALTER TABLE assets DROP COLUMN sector;
ALTER TABLE assets DROP COLUMN industry;
```

---

#### 3. Missing Database Constraints

**Issue:** No uniqueness constraint on (ticker, exchange)

**Impact:** Same ticker from different exchanges could conflict

**Fix:**
```sql
-- Add constraint
ALTER TABLE assets ADD CONSTRAINT assets_ticker_exchange_unique 
UNIQUE (ticker, exchange);
```

---

#### 4. No Soft Delete on All Models

**Issue:** Some models missing soft delete:
- `Country`
- `Sector`
- `Industry`
- `Currency`
- `Benchmark`
- `NewsArticle`
- `Alert` (uses standard Model, not UUIDModel)

**Impact:** Permanent data deletion risk

**Fix:** Add `SoftDeleteModel` inheritance to these models

---

### HIGH (P1)

#### 5. Missing Indexes

**Issue:** High-cardinality fields not indexed:
- `assets.last_price` (partially indexed)
- `assets.ticker` (indexed but no composite)
- `transactions.asset_id`
- `news_articles.related_symbols` (JSON, can't index easily)

**Impact:** Slow queries on large datasets

**Fix:**
```sql
CREATE INDEX assets_ticker_exchange_idx ON assets(ticker, exchange);
CREATE INDEX transactions_asset_date_idx ON transactions(asset_id, date DESC);
```

---

#### 6. No Table Partitioning

**Issue:** Time-series data not partitioned:
- `news_articles` (grows continuously)
- `price_history` (high volume)
- `transactions` (grows with user activity)

**Impact:** Performance degradation over time

**Fix:**
```sql
-- Partition news by month
CREATE TABLE news_articles_partitioned (...) PARTITION BY RANGE (published_at);
```

---

#### 7. Decimal Precision Too High

**Issue:** Excessive decimal precision:
```python
last_price = models.DecimalField(max_digits=30, decimal_places=10)
market_cap = models.DecimalField(max_digits=30, decimal_places=2)
```

**Impact:** Wasted storage, slower calculations

**Fix:** Reduce to reasonable values:
```python
last_price = models.DecimalField(max_digits=18, decimal_places=8)
market_cap = models.DecimalField(max_digits=15, decimal_places=2)
```

---

#### 8. Missing Audit Trail

**Issue:** No change tracking on sensitive fields:
- `users.password_changed_at` exists but no history
- `users.email` changes not logged
- `users.account_type` changes not logged

**Impact:** Security blind spots

**Fix:** Add `UserAuditLog` model:
```python
class UserAuditLog(UUIDModel):
    user_id = models.ForeignKey(User)
    action = models.CharField(max_length=50)
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()
    changed_by = models.ForeignKey(User, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
```

---

### MEDIUM (P2)

#### 9. No Cascade Delete Configuration

**Issue:** Some FKs use `PROTECT` when they should cascade:
- `Asset.asset_type` uses PROTECT
- `Asset.asset_class` uses PROTECT

**Impact:** Orphaned data can't be cleaned up

**Fix:** Review PROTECT usage, use SET_NULL where appropriate

---

#### 10. Session Table Missing Fields

**Issue:** `user_sessions` table missing:
- `last_activity_at` (exists on User but not Session)
- `device_info`
- `location` (geolocation)

**Impact:** Limited security analysis

**Fix:** Add columns to `UserSession` model

---

#### 11. Alert Model Not Using UUIDModel

**Issue:** `Alert` model uses standard `models.Model`:
```python
class Alert(models.Model):  # Not UUIDModel
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
```

**Impact:** Inconsistent with other models

**Fix:** Inherit from `UUIDModel`

---

#### 12. No Database Views

**Issue:** Complex queries computed in Python:
- Portfolio performance calculations
- Asset correlations
- Sector allocations

**Impact:** Slow performance, code duplication

**Fix:** Create SQL views:
```sql
CREATE VIEW portfolio_summary AS
SELECT p.id, p.name, SUM(h.quantity * a.last_price) as value
FROM portfolios p
JOIN holdings h ON h.portfolio_id = p.id
JOIN assets a ON a.id = h.asset_id
GROUP BY p.id;
```

---

#### 13. Missing Constraints

**Issue:** No CHECK constraints:
- `transaction.fees >= 0`
- `holding.quantity > 0`
- `user.failed_login_attempts >= 0`

**Impact:** Data integrity issues

**Fix:** Add CHECK constraints in migrations

---

#### 14. No Full-Text Search

**Issue:** News articles searched via LIKE:
```python
NewsArticle.objects.filter(title__icontains=query)
```

**Impact:** Slow text search

**Fix:** Use PostgreSQL full-text search:
```python
from django.contrib.postgres.search import SearchVectorField

class NewsArticle(models.Model):
    search_vector = SearchVectorField(null=True)
```

---

### LOW (P3)

#### 15. Inconsistent Naming

**Issue:** Mixed naming conventions:
- `users` table vs `investments_alert` table
- `is_deleted` vs `is_active`

**Impact:** Confusion

**Fix:** Standardize naming (low priority)

---

#### 16. No Data Retention Policy

**Issue:** No TTL on old data:
- Old alert history
- Expired sessions
- Old news articles

**Impact:** Storage growth

**Fix:** Add automated cleanup jobs

---

#### 17. Missing Foreign Key Constraints

**Issue:** Some models missing FK constraints:
- `NewsArticle` has no FK to Asset (uses JSON)
- `BenchmarkPriceHistory` may have missing FKs

**Impact:** Orphaned data

**Fix:** Add FK constraints where appropriate

---

#### 18. Currency Table Missing Decimal Places

**Issue:** `Currency.decimals` not used consistently:
```python
decimals = models.PositiveSmallIntegerField(default=2)
```

**Impact:** Incorrect rounding on crypto

**Fix:** Use `decimals` field in calculations

---

## RECOMMENDED IMPROVEMENTS

### Phase 1: Data Integrity (Week 1)
1. Remove deprecated columns from Asset
2. Add CHECK constraints
3. Fix Alert model inheritance
4. Add missing soft deletes

### Phase 2: Performance (Week 2)
1. Add composite indexes
2. Reduce decimal precision
3. Add database views
4. Implement table partitioning

### Phase 3: Security (Week 3)
1. Add audit logging
2. Enhance session tracking
3. Add password history
4. Implement data retention

### Phase 4: Features (Week 4)
1. Full-text search
2. Geolocation tracking
3. Correlation data
4. Time-series optimizations

---

## SUMMARY

| Category | Count | Priority |
|----------|-------|----------|
| Critical Issues | 4 | P0 |
| High Priority | 5 | P1 |
| Medium Priority | 4 | P2 |
| Low Priority | 5 | P3 |

**Overall Assessment:** The schema is well-designed with good separation of concerns, proper indexing, and comprehensive models. Main issues are technical debt (deprecated columns), missing constraints, and performance optimizations.

---

**Next Steps:**
1. Review and prioritize fixes
2. Create migration tasks
3. Implement Phase 1 (Data Integrity)
4. Test thoroughly

---

**Document Status:** COMPLETE
**Last Updated:** 2026-01-30
**Author:** Architect (Karen)
