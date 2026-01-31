# Gaudi: Model Relationships Need Fixing

**From:** DevOps Monitor  
**Date:** February 1, 2026  
**Priority:** High - BLOCKING MIGRATIONS

---

## Problem

Database is configured and PostgreSQL is running, but **migrations are blocked** by Django system check errors.

### Errors Found

| Model | Field | Issue |
|-------|-------|-------|
| investments.Alert | asset | References `investments.Asset` which doesn't exist |
| investments.Alert | portfolio | References `investments.Portfolio` which doesn't exist |
| investments.Notification | related_asset | References `investments.Asset` which doesn't exist |
| investments.DashboardLayout | user | Uses `auth.User` instead of `AUTH_USER_MODEL` |
| investments.ScreenerPreset | user | Uses `auth.User` instead of `AUTH_USER_MODEL` |

---

## What Needs to Be Fixed

### 1. Alert Model (`investments/models/alert.py`)

**Current (wrong):**
```python
asset = models.ForeignKey('investments.Asset', ...)
portfolio = models.ForeignKey('investments.Portfolio', ...)
```

**Should be:**
```python
from assets.models import Asset
from portfolios.models import Portfolio

asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
```

### 2. Notification Model

**Current (wrong):**
```python
related_asset = models.ForeignKey('investments.Asset', ...)
```

**Should be:**
```python
from assets.models import Asset

related_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True)
```

### 3. User References

**Current (wrong):**
```python
user = models.ForeignKey(User, ...)
```

**Should be:**
```python
from django.conf import settings

user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

---

## Files to Modify

1. `apps/backend/src/investments/models/alert.py`
2. `apps/backend/src/investments/models/notification.py`
3. Any other model with `ForeignKey(User)`

---

## After Fixes

Run migrations:
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend/src
source ../venv/bin/activate
python manage.py migrate
```

---

**Taking accountability. Please assign to coders to fix these relationships.**
