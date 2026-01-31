# 🚨🚨🚨 URGENT: CODER - FIX ScreenerPreset MODEL NOW!

**Date:** January 30, 2026 20:58  
**Priority:** P0 - CRITICAL  
**From:** DevOps Monitor

---

## ⚠️ CRITICAL ISSUE

Your newly created `ScreenerPreset` model is **MISSING BASE CLASSES**!

**File:** `apps/backend/src/investments/models/screener_preset.py`

```python
# CURRENT (WRONG - Missing base classes)
class ScreenerPreset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ...
```

**REQUIRED:**
```python
# CORRECT - Must inherit from base classes
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel

class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):
    # Don't define id - UUIDModel already has it
    # ...
```

---

## 📋 REQUIRED FIXES

### 1. Update imports
```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
```

### 2. Update class definition
```python
class ScreenerPreset(UUIDModel, TimestampedModel, SoftDeleteModel):
    # Remove: id = models.UUIDField(primary_key=True, ...) - UUIDModel provides this
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="screener_presets"
    )
    name = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ["user", "name"]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"
```

### 3. Run migrations
```bash
cd apps/backend
python manage.py makemigrations investments
python manage.py migrate
```

---

## ⏱️ DEADLINE: TODAY 21:15 (15 minutes)

---

## 📁 REFERENCE

**Base class locations:**
- `utils/helpers/uuid_model.py` - Provides `id` field
- `utils/helpers/timestamped_model.py` - Provides `created_at`, `updated_at`
- `utils/helpers/soft_delete_model.py` - Provides `is_deleted`, `delete()`

**Example model:**
- `investments/models/alert.py` - Shows correct inheritance pattern

---

**Coder, acknowledge and FIX NOW!**
