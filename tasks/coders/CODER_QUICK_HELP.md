# Coders: Quick Help & Resources

**From:** DevOps Monitor  
**Date:** January 31, 2026

---

## ✅ Quick Fix Applied

**PostgreSQL Charset Fix** (10 min task)

**File:** `apps/backend/src/core/settings.py:161`

The charset `utf8mb4` is MySQL-only. Removed it.

---

## 📚 Model Standards (IMPORTANT)

All models MUST follow this pattern:

```python
from utils.models.base import UUIDModel, TimestampedModel, SoftDeleteModel

class YourModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    """Your model description."""
    
    name = models.CharField(max_length=100)
    # NO explicit id, created_at, updated_at fields
    # UUIDModel provides id (UUID primary key)
    # TimestampedModel provides created_at, updated_at
    # SoftDeleteModel provides is_deleted, deleted_at
    
    class Meta:
        verbose_name = "Your Model"
        verbose_name_plural = "Your Models"
    
    def __str__(self):
        return self.name
```

**Why?** Consistent with ScreenerPreset fix (commit 8f11a20)

---

## 📁 Key Files for Reference

| Task | File | Status |
|------|------|--------|
| C-015 | Position Size Calculator | ✅ Complete |
| C-022 | Backtesting Engine | 🔄 In Progress |
| C-036 | Paper Trading | ⏳ Pending |
| C-040 | Robo-Advisor | ⏳ Pending |

---

## 🆘 Common Blockers & Solutions

### 1. "Module not found" errors
```bash
# Run from project root
source venv/bin/activate
pip install -r apps/backend/requirements.txt
```

### 2. Database migrations
```bash
cd apps/backend/src
python manage.py makemigrations
python manage.py migrate
```

### 3. Running tests
```bash
cd apps/backend/src
pytest --cov=. -v
```

---

## 📞 Need Help?

1. Check `tasks/coders/` for detailed guides
2. Check `tasks/devops/` for DevOps tasks
3. Ask DevOps Monitor for quick fixes

---

**Taking accountability. Here to help.**
