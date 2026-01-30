# Task B-001: Backend Model & Code Improvements

**Assigned To:** Coder (Backend Developer)
**Priority:** P1 (HIGH)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-02-10 5:00 PM
**Estimated Time:** 3 days
**Dependencies:** None (standalone improvements)

---

## Overview

Implement prioritized improvements for the FinanceHub backend based on two analysis documents:
- `BACKEND_IMPROVEMENTS.md` (15 issues)
- `BACKEND_IMPROVEMENTS_SUPPLEMENT.md` (16 additional issues)

**Total Issues:** 31 (3 P0, 10 P1, 12 P2, 6 P3)

## Context

The backend analysis identified several areas needing improvement:
- Performance (N+1 queries, missing caching)
- Security (no rate limiting, input validation)
- Code quality (inconsistent models, empty files)
- API design (no versioning, duplicate code)

## Acceptance Criteria

### P0 Critical (Must Do)
- [ ] Fix Alert model inheritance (add UUIDModel, TimestampedModel, SoftDeleteModel)
- [ ] Add rate limiting to public endpoints
- [ ] Fix N+1 query in portfolio_service.py

### P1 High Priority
- [ ] Add select_related/prefetch_related to unoptimized endpoints
- [ ] Fix Watchlist asset_symbols N+1 query
- [ ] Add related_name to FKs missing it
- [ ] Remove empty service files (asset.py)
- [ ] Add abstract = True to Mixin classes

### P2 Medium Priority
- [ ] Add type hints and docstrings to services
- [ ] Standardize error response format
- [ ] Add pagination to un-paginated endpoints
- [ ] Remove hardcoded USD references
- [ ] Create shared filter utilities

### P3 Low Priority
- [ ] Add API versioning
- [ ] Fix inconsistent naming conventions
- [ ] Document API contracts

## Implementation Steps

### Phase 1: Critical Fixes (Day 1)

#### 1.1 Fix Alert Model Inheritance
```python
# File: apps/backend/src/investments/models/alert.py

# BEFORE
class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

# AFTER
class Alert(UUIDModel, TimestampedModel, SoftDeleteModel):
    # Remove id field - UUIDModel provides it
```

**Also fix:** AlertHistory, AlertNotification, AlertTemplate

#### 1.2 Fix N+1 Query in PortfolioService
```python
# File: apps/backend/src/utils/services/portfolio_service.py

# BEFORE (O(n²))
for holding in portfolio.holdings.all():
    latest_price = holding.asset.prices.order_by("-date").first()

# AFTER (O(1))
holdings = portfolio.holdings.select_related('asset').filter(is_deleted=False)
asset_ids = [h.asset_id for h in holdings]
prices = AssetPricesHistoric.objects.filter(
    asset_id__in=asset_ids
).distinct('asset_id').order_by('asset_id', '-date')
```

#### 1.3 Add Rate Limiting
```python
# Install: pip install django-ratelimit

# In settings.py
MIDDLEWARE = [
    ...
    'django_ratelimit.middleware.RatelimitMiddleware',
    ...
]

# In api/ endpoint
from django_ratelimit.decorators import ratelimit

@router.get("/public-data")
@ratelimit(key='ip', rate='100/h')
def public_data(request):
    ...
```

### Phase 2: Performance Fixes (Day 2)

#### 2.1 Fix Watchlist asset_symbols
```python
# File: apps/backend/src/investments/models/watchlist.py

# BEFORE
@property
def asset_symbols(self):
    return [asset.symbol for asset in self.assets.all()]

# AFTER
@property
def asset_symbols(self):
    return list(self.assets.values_list('symbol', flat=True))
```

#### 2.2 Add select_related to Endpoints
```python
# In apps/backend/src/api/alerts.py
queryset = Alert.objects.filter(
    user=request.user
).select_related('user', 'transaction_type')  # Add these
```

#### 2.3 Add Pagination to Endpoints
```python
@router.get("/", response=List[AlertOut])
def list_alerts(request, filters: AlertFilter = Query(...)):
    qs = Alert.objects.filter(user=request.user)
    offset = int(request.query_params.get('offset', 0))
    limit = int(request.query_params.get('limit', 20))
    return list(qs[offset:offset + limit])
```

### Phase 3: Code Quality (Day 3)

#### 3.1 Remove Empty Files
```bash
rm apps/backend/src/utils/services/asset.py
```

#### 3.2 Add Abstract to Mixins
```python
# In apps/backend/src/fundamentals/base.py
class MarketCapMixin(models.Model):
    class Meta:
        abstract = True
    ...
```

#### 3.3 Create Shared Filter Utilities
```python
# Create: utils/api/filters.py
class AssetFilterMixin:
    def apply_asset_filters(self, qs, filters):
        ...
```

## Files Modified

### Models
- `apps/backend/src/investments/models/alert.py`
- `apps/backend/src/investments/models/alert_history.py`
- `apps/backend/src/investments/models/alert_notification.py`
- `apps/backend/src/investments/models/watchlist.py`
- `apps/backend/src/fundamentals/base.py`

### Services
- `apps/backend/src/utils/services/portfolio_service.py`
- `apps/backend/src/utils/services/asset.py` (delete)

### API
- `apps/backend/src/api/alerts.py`
- `apps/backend/src/api/economic.py`
- Various other endpoints

### Utilities
- `utils/api/filters.py` (new file)

## Verification

```bash
# Run tests
cd apps/backend
python manage.py test

# Check for N+1 queries
python manage.py shell
>>> from portfolios.models import Portfolio
>>> p = Portfolio.objects.first()
>>> # Should not trigger additional queries

# Verify rate limiting works
curl -X GET http://localhost:8000/api/public-data
# Should return 429 after 100 requests/hour

# Check empty files removed
ls apps/backend/src/utils/services/asset.py
# Should return: No such file
```

## Rollback Plan

```bash
# If issues arise:
git checkout HEAD~1 -- apps/backend/src/investments/models/alert.py
git checkout HEAD~1 -- apps/backend/src/utils/services/portfolio_service.py
```

## Dependencies

None - this is a standalone improvement task

## Feedback to Architect

[After completing, report using this format]

### What I Did:
- Fixed Alert model inheritance
- Added rate limiting
- Fixed N+1 queries
- [Other fixes completed]

### What I Discovered:
- Total N+1 queries fixed: [NUMBER]
- Endpoints with select_related added: [NUMBER]
- Empty files removed: [NUMBER]

### Verification:
- ✅ All tests passing
- ✅ No new N+1 queries introduced
- ✅ Rate limiting working

### Ready for Next Step:
Backend improvements complete.

## Updates

- **2026-01-30 20:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when starting]
- **[YYYY-MM-DD HH:MM]:** [Update when complete]

---

**Last Updated:** 2026-01-30
**Next Task:** B-002 (Security hardening based on findings)
