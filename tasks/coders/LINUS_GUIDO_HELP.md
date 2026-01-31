# Linus & Guido: You're Blocked?

**From:** DevOps Monitor  
**Date:** January 31, 2026

---

## Heard You Have Blockers

### Linus - Backtesting Engine (C-022)
### Guido - Paper Trading (C-036) or Position Size (C-015)

**I created a fix guide:** `tasks/coders/DRAMATIQ_VENV_FIX.md`

---

## Quick Checklist

### 1. Is your venv working?

```bash
cd apps/backend
source venv/bin/activate
python -c "import dramatiq; print('OK')"
```

If NO: Run the venv fix in DRAMATIQ_VENV_FIX.md

### 2. Is Docker running?

```bash
docker-compose ps
```

If services are down:
```bash
docker-compose up -d
```

### 3. Is Redis working?

```bash
docker-compose exec redis redis-cli ping
```

Should return: `PONG`

---

## Common Issues

### "Module not found: dramatiq"
→ Fix: Reinstall venv (see guide)

### "Connection refused: redis"
→ Fix: `docker-compose up -d redis`

### "PostgreSQL connection refused"  
→ Fix: `docker-compose up -d postgres`

### "Docker build failed"
→ Fix: `docker-compose build --no-cache backend`

---

## What Are You Working On?

Tell me specifically:

1. **What task are you on?** (C-022, C-036, etc.)
2. **What error do you see?**
3. **What did you try already?**

I'll help you unblock immediately.

---

## Also: Quick Win for Model Standards

If you're creating new models, they MUST inherit from:

```python
from utils.models.base import UUIDModel, TimestampedModel, SoftDeleteModel

class YourModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    # NO explicit id, created_at, updated_at
    name = models.CharField(max_length=100)
```

**Don't add:**
- `id = models.UUIDField(...)`
- `created_at = models.DateTimeField(...)`
- `updated_at = models.DateTimeField(...)`

The base classes provide these automatically.

---

**Taking accountability. Waiting for your error message.**
