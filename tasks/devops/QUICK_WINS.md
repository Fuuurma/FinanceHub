# Quick DevOps Wins (5-30 min each)

**Date:** January 31, 2026

---

## 1. ✅ PostgreSQL Charset Fix (DONE - 10 min)
- Removed wrong `charset: utf8mb4` from settings.py
- This was MySQL syntax, not PostgreSQL

---

## 2. Add Prometheus Metrics (30 min)

**File:** `apps/backend/src/core/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from django.http import HttpResponse

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP latency', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Active users')
DB_CONNECTIONS = Gauge('db_connections', 'Database connections')

def metrics_view(request):
    return HttpResponse(generate_latest(), content_type='text/plain')
```

**Add to urls.py:**
```python
path('metrics/', metrics_view, name='metrics'),
```

---

## 3. Uptime Monitor GitHub Action (20 min)

**File:** `.github/workflows/uptime-monitor.yml`

```yaml
name: Uptime Monitor
on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Check API health
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://api.financehub.com/health/)
          if [ "$response" != "200" ]; then
            echo "API DOWN: $response"
            exit 1
          fi
      
      - name: Check frontend
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://financehub.com/)
          if [ "$response" != "200" ]; then
            echo "Frontend DOWN: $response"
            exit 1
          fi
      
      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: 'error'
          text: "Uptime check failed!"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 4. Slow Query Logging (15 min)

**File:** `apps/backend/src/core/settings.py`

Add LOGGING configuration:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```

---

## 5. Bundle Size Check (10 min)

**File:** `.github/workflows/ci.yml`

Add to `build-verification` job:

```yaml
- name: Check bundle size
  run: |
    cd apps/frontend
    SIZE=$(du -sh .next | cut -f1)
    echo "Bundle size: $SIZE"
    if [ $(echo "$SIZE > 200M" | bc -l) -eq 1 ]; then
      echo "Bundle size exceeds 200M threshold"
      exit 1
    fi
```

---

## 6. Health Check Retry (15 min)

**File:** `.github/workflows/deploy.yml`

Replace single curl with retry:

```yaml
- name: Run smoke tests with retry
  run: |
    for i in {1..3}; do
      if curl -f https://staging.financehub.com/health; then
        exit 0
      fi
      echo "Retry $i/3..."
      sleep 10
    done
    echo "Health check failed after 3 retries"
    exit 1
```

---

## Summary

| Task | Time | Effort |
|------|------|--------|
| PostgreSQL charset fix | 10 min | ✅ DONE |
| Prometheus metrics | 30 min | ⏳ |
| Uptime monitor | 20 min | ⏳ |
| Slow query logging | 15 min | ⏳ |
| Bundle size check | 10 min | ⏳ |
| Health check retry | 15 min | ⏳ |

**Total: ~100 minutes (under 2 hours)**

---

**Taking accountability. Quick wins add up.**

---

## 7. Django Cache TTL Configuration (15 min)

**File:** `apps/backend/src/core/settings.py`

Current:
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
```

Improved:
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "financehub",
        "TIMEOUT": 300,  # Default 5 minutes
    }
}
```

---

## 8. GitHub Actions Cache Update (10 min)

**File:** `.github/workflows/ci.yml`

Update outdated actions:
- `codecov/codecov-action@v3` → `@v4`
- `actions/upload-artifact@v3` → `@v4`
- `github/codeql-action/upload-sarif@v2` → `@v3`

---

## 9. Non-root User in Frontend (20 min)

**File:** `apps/frontend/Dockerfile`

```dockerfile
# Add non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs

# Change ownership
RUN chown -R nextjs:nodejs /app

USER nextjs
```

---

## 10. Database Connection Settings (10 min)

**File:** `apps/backend/src/core/settings.py`

Current:
```python
"CONN_MAX_AGE": 600,
```

Improved:
```python
"CONN_MAX_AGE": 600,
"OPTIONS": {
    "connect_timeout": 10,
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 5,
    "keepalives_count": 5,
},
```

---

## Updated Summary

| Task | Time | Status |
|------|------|--------|
| PostgreSQL charset fix | 10 min | ✅ DONE |
| Prometheus metrics | 30 min | ⏳ |
| Uptime monitor | 20 min | ⏳ |
| Slow query logging | 15 min | ⏳ |
| Bundle size check | 10 min | ⏳ |
| Health check retry | 15 min | ⏳ |
| Cache TTL config | 15 min | ⏳ |
| GitHub Actions update | 10 min | ⏳ |
| Non-root frontend user | 20 min | ⏳ |
| DB connection settings | 10 min | ⏳ |

**Total: ~165 minutes (under 3 hours)**

All tasks can be done in parallel by multiple people!
