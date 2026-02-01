# Backend Improvements Supplement

**Date:** 2026-01-30  
**Scope:** Additional model and code issues found  
**Based on:** BACKEND_IMPROVEMENTS.md (completed earlier)

---

## Additional Issues Found

### MODEL INCONSISTENCIES (P0)

#### 1. Alert Model Missing Standard Inheritance

**File:** `apps/backend/src/investments/models/alert.py:34`

**Issue:** Alert model uses `models.Model` instead of `UUIDModel, TimestampedModel, SoftDeleteModel`

```python
class Alert(models.Model):  # ❌ Should inherit from UUIDModel
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ...
```

**Impact:**
- Inconsistent with other models
- No soft delete support
- No timestamps (uses auto_now_add but inconsistent)

**Fix:**
```python
class Alert(UUIDModel, TimestampedModel, SoftDeleteModel):
    ...
```

**Also Affects:**
- `AlertHistory` (line 131)
- `AlertNotification` (line 158)
- `AlertTemplate` (line 191)

---

#### 2. Reference Models Missing Soft Delete

**Files:**
- `apps/backend/src/assets/models/asset_type.py:7`
- `apps/backend/src/assets/models/asset_class.py:7`
- `apps/backend/src/investments/models/transaction_type.py:7`
- `apps/backend/src/users/models/user_status.py`
- `apps/backend/src/users/models/account_type.py`

**Issue:** These models use `models.Model` directly

```python
class AssetType(models.Model):  # Missing SoftDeleteModel
    name = models.CharField(max_length=100)
    ...
```

**Impact:** Cannot soft delete reference data

**Fix:** Add `SoftDeleteModel` if deletion tracking needed, or document as intentional

---

### FOREIGN KEY ISSUES (P1)

#### 3. Missing related_name on Several FKs

**Files:**
- `apps/backend/src/fundamentals/bonds/metrics.py` - sector_fk missing related_name
- `apps/backend/src/fundamentals/base.py` - asset FK missing related_name
- `apps/backend/src/charts/models/chart_drawing.py` - multiple FKs missing related_name

**Issue:** Cannot easily traverse relationships backwards

```python
# Current
asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

# Should be
asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='financial_metrics')
```

**Impact:** Cannot query like `asset.financial_metrics.all()`

---

#### 4. Inconsistent on_delete Behavior

**Files:**
- `apps/backend/src/portfolios/models/holdings.py` - Uses CASCADE
- `apps/backend/src/portfolios/models/transaction.py` - Uses PROTECT for asset

**Issue:** Different strategies for similar relationships

**Fix:** Standardize:
- `PROTECT` for reference data (AssetType, AssetClass, Country)
- `CASCADE` for ownership (Portfolio → Holdings → Transactions)
- `SET_NULL` for optional relationships

---

### CODE QUALITY ISSUES (P2)

#### 5. Empty Service Files

**Files:**
- `apps/backend/src/utils/services/asset.py` (1 line - empty)
- `apps/backend/src/utils/services/portfolio.py` (directory, not file)

**Fix:** Either remove or populate with appropriate methods

---

#### 6. 64 Hardcoded USD References

**Files:** Throughout codebase

**Issue:**
```python
currency = models.CharField(max_length=3, default="USD")
```

**Fix:** Use `settings.DEFAULT_CURRENCY` or constant

---

#### 7. Mixin Classes Missing Meta

**Files:**
- `apps/backend/src/fundamentals/base.py`

**Issue:**
```python
class MarketCapMixin(models.Model):  # No abstract = True
    ...
```

**Fix:**
```python
class MarketCapMixin(models.Model):
    class Meta:
        abstract = True
    ...
```

---

#### 8. Inconsistent Naming Conventions

**Files:** Various

**Issue:**
- Some use `snake_case` for methods
- Some use `camelCase` for fields
- Some use `kebab-case` for choices

**Examples:**
```python
price_change_24h  # snake_case - good
triggered_count   # snake_case - good
delivery_channels # snake_case - good

# But some APIs use:
get_market_overview  # snake_case
getPortfolioData     # mixed - bad
```

**Fix:** Enforce snake_case throughout

---

### PERFORMANCE ISSUES (P1)

#### 9. No Bulk Operations in Watchlist

**File:** `apps/backend/src/investments/models/watchlist.py:28-30`

**Issue:**
```python
@property
def asset_symbols(self):
    return [asset.symbol for asset in self.assets.all()]  # N queries
```

**Fix:**
```python
@property
def asset_symbols(self):
    return list(self.assets.values_list('symbol', flat=True))  # 1 query
```

---

#### 10. Duplicate Filter Logic

**Files:**
- `apps/backend/src/api/market_overview.py`
- `apps/backend/src/api/asset.py`
- `apps/backend/src/api/unified_market_data.py`

**Issue:** Same filter patterns repeated

**Fix:** Create shared filter utilities in `utils/api/filters.py`

---

### SECURITY ISSUES (P0)

#### 11. No Rate Limiting on Public Endpoints

**Files:** All endpoints in `apps/backend/src/api/`

**Issue:** No rate limiting configured

**Fix:** Add django-ratelimit:
```python
from django_ratelimit.decorators import ratelimit

@router.get("/public-data")
@ratelimit(key='ip', rate='100/h')
def public_data(request):
    ...
```

---

#### 12. String-based Status Choices

**File:** `apps/backend/src/investments/models/alert.py:46`

**Issue:**
```python
status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.ACTIVE)
```

**Fix:** Use TextChoices properly or FK to UserStatus model for consistency

---

### API DESIGN ISSUES (P2)

#### 13. 212 Endpoints - No Versioning

**Files:** All in `apps/backend/src/api/`

**Issue:** All endpoints at `/api/` without versioning

**Fix:** Use Ninja versioning:
```python
api_v1 = NinjaAPI(urls_namespace='v1', version='1.0')
api_v2 = NinjaAPI(urls_namespace='v2', version='2.0')
```

---

#### 14. Inconsistent Response Formats

**Issue:** Different endpoints return different error formats

**Examples:**
```python
# Some return dict
return {"error": "message"}

# Some raise exceptions
raise Http400BadRequest(message=str(e))

# Some return plain text
return HttpResponse("error")
```

**Fix:** Standardize using Ninja's error handling:
```python
from ninja.errors import HttpError

@router.get("/")
def endpoint(request):
    try:
        ...
    except ValidationError as e:
        raise HttpError(400, str(e))
```

---

### MIGRATION ISSUES (P1)

#### 15. Duplicate Migration 0012

**Files:**
- `src/assets/migrations/0012_exchange_mic_exchange_operating_hours_and_more.py` (DELETED - was in old src/)
- `apps/backend/src/assets/migrations/0012_exchange_mic_exchange_operating_hours_and_more.py` (exists)

**Issue:** Migration file exists in both locations (old and new)

**Fix:** Migration already cleaned up during monorepo migration

---

#### 16. Inconsistent Migration Naming

**Files:** Various

**Issue:** Some migrations use `camelCase`, some use `snake_case`

**Fix:** Follow Django convention: `####_description.py`

---

## Quick Fixes (Can Do Today)

### Fix 1: Add related_name to ChartDrawing FKs
```python
# In apps/backend/src/charts/models/chart_drawing.py
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chart_drawings')
asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='chart_drawings')
```

### Fix 2: Fix Watchlist asset_symbols
```python
@property
def asset_symbols(self):
    return list(self.assets.values_list('symbol', flat=True))
```

### Fix 3: Remove empty asset.py
```bash
rm apps/backend/src/utils/services/asset.py
```

### Fix 4: Add abstract = True to Mixins
```python
class MarketCapMixin(models.Model):
    class Meta:
        abstract = True
    ...
```

---

## Summary of Additional Issues

| Category | Issues | Priority |
|----------|--------|----------|
| Model Inheritance | 2 | P0 |
| Foreign Keys | 2 | P1 |
| Code Quality | 4 | P2 |
| Performance | 2 | P1 |
| Security | 2 | P0 |
| API Design | 2 | P2 |
| Migrations | 2 | P1 |

**Total New Issues:** 16

**Combined with Previous Analysis:** 31 total improvement areas

---

## Next Steps

1. Create task file for backend improvements (B-001)
2. Prioritize fixes by impact
3. Start with P0 issues (Alert model inheritance, rate limiting)
4. Proceed through phases

---

**Document Status:** SUPPLEMENT COMPLETE  
**Total Issues Now:** 31 (15 + 16 new)
**Quick Fixes Available:** 7
