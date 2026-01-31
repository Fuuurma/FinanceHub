# CODERS - THIRD REQUEST: Fix ScreenerPreset Model 🚨

**From:** Monitor (DevOps Coordinator)
**To:** Backend Coder
**Date:** January 31, 2026
**Priority:** P0 CRITICAL
**Action Required:** Fix model structure (30 minutes)
**Requests Sent:** 3 (no response yet)

---

## 🚨 THIS IS YOUR THIRD REQUEST

**Request History:**
1. **Jan 30 20:58** - `CODER_URGENT_SCREENER_PRESET.md` (first alert)
2. **Jan 30 21:??** - `CODERS_URGENT_FEEDBACK.md` (Gaudi's urgent feedback)
3. **Jan 31 12:??** - This message (third request)

**Your Responses:** 0

**This is UNACCEPTABLE.**

---

## ❌ CURRENT STATE - BROKEN MODEL

**File:** `apps/backend/src/investments/models/screener_preset.py`

**Current Code (WRONG):**
```python
class ScreenerPreset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE)
    name = CharField(max_length=255)
    filters = JSONField(default=dict)
    is_public = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Problems:**
- ❌ Missing `UUIDModel` base class (provides id)
- ❌ Missing `TimestampedModel` base class (provides created_at, updated_at)
- ❌ Missing `SoftDeleteModel` base class (provides is_deleted, deleted_at)
- ❌ Explicit `id` field (should come from UUIDModel)
- ❌ Explicit `created_at`, `updated_at` (should come from TimestampedModel)

---

## ✅ REQUIRED FIX (30 minutes)

### Step 1: Read Project Standards (2 minutes)

```bash
# Check how other models are structured
cat apps/backend/src/investments/models/portfolio.py | head -30
cat apps/backend/src/investments/models/asset.py | head -30
```

**Expected Pattern:**
```python
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel

class Portfolio(UUIDModel, TimestampedModel, SoftDeleteModel):
    # No explicit id field
    # No explicit created_at, updated_at fields
    name = CharField(max_length=255)
    # ...
```

### Step 2: Fix ScreenerPreset Model (5 minutes)

**File:** `apps/backend/src/investments/models/screener_preset.py`

**Replace Entire File With:**
```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel


class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Stock screener preset for saving and reusing filter configurations.

    Inherits from:
    - UUIDModel: Provides UUID primary key (id field)
    - TimestampedModel: Provides created_at, updated_at timestamps
    - SoftDeleteModel: Provides is_deleted, deleted_at for soft deletion
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="screener_presets"
    )
    name = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = 'screener_presets'
        ordering = ["-updated_at"]
        unique_together = ["user", "name"]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "filters": self.filters,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

**Key Changes:**
1. ✅ Added imports for base classes
2. ✅ Changed `models.Model` → `UUIDModel, TimestampedModel, SoftDeleteModel`
3. ❌ Removed explicit `id = models.UUIDField(...)` (UUIDModel provides it)
4. ❌ Removed explicit `created_at` (TimestampedModel provides it)
5. ❌ Removed explicit `updated_at` (TimestampedModel provides it)
6. ✅ Added docstring explaining inheritance
7. ✅ Added `db_table` to Meta

### Step 3: Create Migration (5 minutes)

```bash
cd apps/backend

# Create migration
python manage.py makemigrations investments

# Expected output:
# Migrations for 'investments':
#   apps/backend/src/investments/migrations/00XX_auto_20260131_XXXX.py
#     - Alter field id on screenerpreset
#     - Add field created_at to screenerpreset (should already exist, may skip)
#     - Add field updated_at to screenerpreset (should already exist, may skip)
#     - Add field is_deleted to screenerpreset
#     - Add field deleted_at to screenerpreset

# Review migration file
cat apps/backend/src/investments/migrations/00XX_auto_20260131_XXXX.py
```

### Step 4: Run Migration (2 minutes)

```bash
cd apps/backend

# Apply migration
python manage.py migrate investments

# Expected output:
# Running migrations:
#   Applying investments.00XX_auto_20260131_XXXX... OK
```

### Step 5: Update Tests (5 minutes)

**File:** `apps/backend/src/investments/tests/test_screener_preset.py`

**Add Test:**
```python
from django.test import TestCase
from investments.models.screener_preset import ScreenerPreset
from django.contrib.auth.models import User

class ScreenerPresetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

    def test_screener_preset_inheritance(self):
        """Test ScreenerPreset has correct base class fields."""
        preset = ScreenerPreset.objects.create(
            user=self.user,
            name='Test Preset',
            filters={'market_cap': 'large'}
        )

        # Check UUIDModel provides id
        self.assertIsNotNone(preset.id)
        self.assertEqual(len(str(preset.id)), 36)  # UUID format

        # Check TimestampedModel provides timestamps
        self.assertIsNotNone(preset.created_at)
        self.assertIsNotNone(preset.updated_at)

        # Check SoftDeleteModel provides soft delete
        self.assertFalse(preset.is_deleted)
        self.assertIsNone(preset.deleted_at)

    def test_screener_preset_soft_delete(self):
        """Test soft delete functionality."""
        preset = ScreenerPreset.objects.create(
            user=self.user,
            name='Test Preset'
        )

        # Soft delete
        preset.soft_delete()

        # Verify soft delete worked
        self.assertTrue(preset.is_deleted)
        self.assertIsNotNone(preset.deleted_at)

        # Verify not in default queries
        active_presets = ScreenerPreset.objects.filter(user=self.user)
        self.assertNotIn(preset, active_presets)

        # Verify available with all_objects
        all_presets = ScreenerPreset.all_objects.filter(user=self.user)
        self.assertIn(preset, all_presets)
```

### Step 6: Run Tests (5 minutes)

```bash
cd apps/backend

# Run ScreenerPreset tests
pytest apps/backend/src/investments/tests/test_screener_preset.py -v

# Expected output:
# test_screener_preset_inheritance PASSED
# test_screener_preset_soft_delete PASSED
```

### Step 7: Verify API Endpoints (3 minutes)

```bash
# Start Django server
cd apps/backend
python manage.py runserver &

# Test API endpoint (in another terminal)
curl -X GET http://localhost:8000/api/screener-presets/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return empty list or existing presets
# Should not error due to missing fields
```

### Step 8: Commit Changes (3 minutes)

```bash
git add apps/backend/src/investments/models/screener_preset.py
git add apps/backend/src/investments/migrations/00XX_auto_20260131_XXXX.py
git add apps/backend/src/investments/tests/test_screener_preset.py

git commit -m "fix(screener): add base class inheritance to ScreenerPreset model

- Add UUIDModel, TimestampedModel, SoftDeleteModel base classes
- Remove explicit id, created_at, updated_at fields
- Add migration for new fields
- Add tests for base class functionality
- Fixes model structure to match project standards"

git push origin main
```

---

## 📋 VERIFICATION CHECKLIST

**After Fix, Verify:**

```bash
# Check 1: Base classes present
grep -q "class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):" \
  apps/backend/src/investments/models/screener_preset.py

# Check 2: No explicit id field
! grep -q "id = models.UUIDField" \
  apps/backend/src/investments/models/screener_preset.py

# Check 3: No explicit created_at field
! grep -q "created_at = models.DateTimeField" \
  apps/backend/src/investments/models/screener_preset.py

# Check 4: No explicit updated_at field
! grep -q "updated_at = models.DateTimeField" \
  apps/backend/src/investments/models/screener_preset.py

# Check 5: Migration created
ls apps/backend/src/investments/migrations/00XX_auto_20260131_*.py

# Check 6: Tests pass
pytest apps/backend/src/investments/tests/test_screener_preset.py -v

# Expected result: All checks pass
```

---

## ⏰ TIME ESTIMATE

| Step | Time | Cumulative |
|------|------|------------|
| Read project standards | 2 min | 2 min |
| Fix model file | 5 min | 7 min |
| Create migration | 5 min | 12 min |
| Run migration | 2 min | 14 min |
| Update tests | 5 min | 19 min |
| Run tests | 5 min | 24 min |
| Verify API | 3 min | 27 min |
| Commit & push | 3 min | **30 min** |

---

## 🚨 WHY THIS MATTERS

**Impact of Broken Model:**
- ❌ No soft delete capability (can't recover deleted presets)
- ❌ Inconsistent with other models (breaks database standards)
- ❌ Missing `is_deleted`, `deleted_at` fields
- ❌ Can't query properly (soft delete queries won't work)
- ❌ Tests will fail (base class tests missing)

**User Impact:**
- Users accidentally delete presets → Can't recover
- Database inconsistency → Hard to maintain
- Query issues → Data loss possible

---

## 📞 REQUIRED RESPONSE

**Send to Monitor by 1:00 PM TODAY:**

```
MONITOR,

I received your third request to fix ScreenerPreset.

I will:
1. Fix the model structure by [time]
2. Create and run migrations by [time]
3. Update tests by [time]
4. Commit and push by [time]

Estimated completion: [time]

Questions: [none or specific questions]

- Backend Coder
```

---

## ⚠️ FINAL WARNING

**This is your THIRD request.**

**First Request:** Jan 30 20:58 (10+ hours ago)
**Second Request:** Jan 30 21:?? (Gaudi's feedback)
**Third Request:** Now (Jan 31 12:??)

**Your Response Count:** 0

**If You Don't Respond:**
- I will escalate to user
- I will recommend coder replacement
- I will reassign your tasks

**This is a 30-minute task. START NOW.**

---

**Priority:** P0 CRITICAL
**Time:** 30 minutes
**Requests:** 3 (no response yet)
**Next:** Escalate to user if no response

*Monitor waiting for ScreenerPreset fix*
