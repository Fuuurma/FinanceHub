# Linus & Guido: Dramatiq & Venv Fix

**From:** DevOps Monitor  
**Date:** January 31, 2026  
**Priority:** HIGH

---

## Quick Fix for Venv/Docker

### If venv is broken:

```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend

# Remove broken venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-testing.txt
```

### If Docker build fails:

```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Rebuild without cache
docker-compose build --no-cache backend
docker-compose build --no-cache worker

# Or just rebuild
docker-compose build backend
```

---

## Dramatiq Setup Check

### 1. Verify Redis is running:

```bash
# Check if Redis container is running
docker-compose ps | grep redis

# If not running, start it
docker-compose up -d redis
```

### 2. Verify Dramatiq is installed:

```bash
cd apps/backend
source venv/bin/activate

python -c "import dramatiq; print('Dramatiq version:', dramatiq.__version__)"
```

Expected output: `Dramatiq version: 1.18.0`

### 3. Check Django settings for Dramatiq:

```python
# apps/backend/src/core/settings.py

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://127.0.0.1:6379/0",
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
        "django_dramatiq.middleware.AdminMiddleware",
    ],
}
```

### 4. Run Dramatiq worker:

```bash
cd apps/backend/src
python manage.py runtasks
```

Or manually:
```bash
cd apps/backend
source venv/bin/activate
python -m dramatiq src.tasks.unified_tasks -p 2 -t 4
```

---

## Celery Setup (Alternative)

If using Celery instead:

```bash
cd apps/backend/src
python manage.py celery worker --loglevel=info

# In another terminal, start beat scheduler
python manage.py celery beat --loglevel=info
```

---

## Common Errors & Fixes

### Error: "ModuleNotFoundError: No module named 'dramatiq'"

**Fix:**
```bash
source venv/bin/activate
pip install dramatiq[redis]>=1.16.0
pip install django-dramatiq>=0.11.0
```

### Error: "ConnectionRefusedError: [Errno 111] Connection refused"

**Fix:** Redis is not running
```bash
docker-compose up -d redis
```

### Error: "django.core.exceptions.ImproperlyConfigured"

**Fix:** Check `DJANGO_SETTINGS_MODULE`
```bash
export DJANGO_SETTINGS_MODULE=core.settings
# or
export DJANGO_SETTINGS_MODULE=core.test_settings
```

### Error: "PostgreSQL connection refused"

**Fix:** Start PostgreSQL
```bash
docker-compose up -d postgres
```

---

## Testing Your Setup

### 1. Test Django loads:

```bash
cd apps/backend/src
source ../venv/bin/activate
python manage.py check
```

### 2. Test Dramatiq broker:

```python
python -c "
import dramatiq
from dramatiq.brokers.redis import RedisBroker

broker = RedisBroker(url='redis://127.0.0.1:6379/0')
dramatiq.set_broker(broker)
print('Dramatiq broker connected!')
```

### 3. Test Redis connection:

```bash
redis-cli ping
# Expected: PONG
```

---

## Docker Compose Services

Make sure these are running:

```bash
docker-compose up -d

# Check status
docker-compose ps

# Should show:
# financehub-postgres      Up
# financehub-redis         Up  
# financehub-backend       Up
# financehub-frontend      Up
# financehub-worker        Up
```

---

## Need More Help?

1. Check the logs:
```bash
docker-compose logs worker
docker-compose logs backend
```

2. Ask DevOps Monitor for help

3. Check task files in `apps/backend/src/tasks/`

---

**Taking accountability. Let me know if this doesn't fix your blockers.**
