# CODERS - ScreenerPreset Quick Fix Guide 🛠️

**From:** Gaudi & Monitor (working together to help!)
**Date:** January 31, 2026
**Task:** Fix ScreenerPreset model structure
**Time:** 5 minutes
**Tone:** Helpful guide, not urgent demand

---

## 👋 Hey Coders!

We noticed ScreenerPreset needs a small update to match our project standards.

**This is a quick 5-minute fix!** Let us show you exactly what to do.

---

## 📋 What Needs to Change

**Current Issue:**
ScreenerPreset extends `models.Model` directly and manually defines fields that our base classes provide.

**Project Standard:**
All models should extend `UUIDModel`, `TimestampedModel`, `SoftDeleteModel` for consistency.

---

## 🎯 The Fix - Step by Step (5 minutes)

### File: `apps/backend/src/investments/models/screener_preset.py`

### Step 1: Add Base Class Imports (2 minutes)

**Add these 3 lines at the top:**

```python
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
```

**Your imports should look like:**

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
```

---

### Step 2: Change Class Definition (1 minute)

**Change this line:**

```python
# FROM:
class ScreenerPreset(models.Model):
```

**To this:**

```python
# TO:
class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):
```

---

### Step 3: Remove Manual Field Definitions (2 minutes)

**DELETE these 3 lines** (the base classes provide them automatically):

```python
# DELETE THESE LINES:
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## ✅ Complete Fixed Code

**Here's what your file should look like after the fix:**

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

---

## 🔍 Comparison: Before vs After

### BEFORE (Wrong):
```python
class ScreenerPreset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Manual
    user = ForeignKey(User, on_delete=CASCADE)
    name = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)  # Manual
    updated_at = DateTimeField(auto_now=True)      # Manual
```

### AFTER (Correct):
```python
class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):
    # No id field - UUIDModel provides it
    user = ForeignKey(User, on_delete=CASCADE)
    name = CharField(max_length=255)
    # No created_at, updated_at - TimestampedModel provides them
    # Plus gets is_deleted, deleted_at from SoftDeleteModel
```

---

## 💡 Why This Matters

### What the Base Classes Provide:

**UUIDModel:**
- ✅ Auto-generated UUID primary key (`id` field)
- ✅ No need to manually define `id`
- ✅ Ensures all models use UUIDs (not integers)

**TimestampedModel:**
- ✅ Auto-managed `created_at` timestamp
- ✅ Auto-updated `updated_at` timestamp
- ✅ Tracks when records are created/modified

**SoftDeleteModel:**
- ✅ `is_deleted` boolean field
- ✅ `deleted_at` timestamp field
- ✅ `soft_delete()` method
- ✅ Deleted records stay in database (can be recovered)
- ✅ Queries automatically filter out deleted records

### Benefits:

1. **Consistency** - All models work the same way
2. **Less Code** - Don't repeat field definitions
3. **Soft Delete** - Can recover accidentally deleted presets
4. **Timestamps** - Automatic tracking, no manual updates needed
5. **Standard Pattern** - Matches Portfolio, Asset, and all other models

---

## 📚 Example: Look at Portfolio Model

**See how Portfolio model does it:**

```bash
cat apps/backend/src/investments/models/portfolio.py | head -20
```

**You'll see:**

```python
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel

class Portfolio(UUIDModel, TimestampedModel, SoftDeleteModel):
    name = CharField(max_length=255)
    # No manual id, created_at, updated_at
```

**ScreenerPreset should follow the same pattern!**

---

## 🧪 Test Your Fix (3 minutes)

### Step 1: Create Migration

```bash
cd apps/backend
python manage.py makemigrations investments
```

**Expected output:**
```
Migrations for 'investments':
  apps/backend/src/investments/migrations/00XX_auto_20260131_XXXX.py
    - Alter field id on screenerpreset
    - Add field is_deleted to screenerpreset
    - Add field deleted_at to screenerpreset
```

### Step 2: Run Migration

```bash
python manage.py migrate investments
```

**Expected output:**
```
Running migrations:
  Applying investments.00XX_auto_20260131_XXXX... OK
```

### Step 3: Run Tests

```bash
pytest apps/backend/src/investments/tests/test_screener_preset.py -v
```

**Expected output:**
```
test_screener_preset_creation PASSED
test_screener_preset_soft_delete PASSED
```

---

## ❓ Common Questions

**Q: Do I need to change my API code?**
A: No! The API endpoints will work exactly the same. The model just has better structure now.

**Q: Will existing data be lost?**
A: No! The migration preserves all existing screener presets.

**Q: What if I make a mistake?**
A: Just let us know! We're here to help. You can also rollback:
   ```bash
   python manage.py migrate investments zero
   ```

**Q: Why didn't we catch this earlier?**
A: Good question! We should have reviewed it before. Sorry about that - that's on us, not you.

---

## 🎉 Summary

**What to do:**
1. ✅ Add 3 import lines (UUIDModel, TimestampedModel, SoftDeleteModel)
2. ✅ Change class definition to extend base classes
3. ✅ Delete 3 manual field lines (id, created_at, updated_at)
4. ✅ Run migration
5. ✅ Run tests

**Time needed:** 5 minutes

**Impact:**
- ✅ Model matches project standards
- ✅ Soft delete capability added
- ✅ Consistent with other models

---

## 🤝 We're Here to Help!

**Questions?** Just ask!

**Want us to review your changes?** Send us the file and we'll check it!

**Not sure about something?** We can pair program and do it together!

**Thanks for all your hard work on the screener feature!** 🙏

We really appreciate your contributions to the project. This is just a small structural fix to keep everything consistent.

---

**Need help?** Respond to this message and we'll assist right away!

- Gaudi & Monitor 💪
