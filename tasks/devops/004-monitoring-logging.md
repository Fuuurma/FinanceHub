---
title: "Monitoring, Logging & Health Checks"
status: pending
priority: p1
estimate: "2 days"
created: "2026-01-30"
assigned_to: gaudi
depends_on:
  - d-001
---

## Summary

Implement comprehensive monitoring, logging, and health checks for production reliability. Based on INFRASTRUCTURE_ANALYSIS.md and CELERY_ANALYSIS.md findings.

## Issues to Fix

### P1 - High Priority Monitoring

#### 1. Add Health Checks to All Docker Services

**File:** `docker-compose.yml`

**Add health checks:**
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  frontend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  nginx:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "financehub", "-d", "finance_hub"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### 2. Add Health Endpoint to Django

**File:** `apps/backend/src/core/urls.py` or create new

**Add health check views:**
```python
# apps/backend/src/core/health.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from redis import RedisError
import os

def health_check(request):
    """Comprehensive health check endpoint"""
    status = {
        'status': 'healthy',
        'version': os.environ.get('APP_VERSION', 'unknown'),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        status['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}
        status['status'] = 'unhealthy'
    
    # Redis check
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['checks']['redis'] = {'status': 'healthy'}
        else:
            status['checks']['redis'] = {'status': 'unhealthy', 'error': 'Cache mismatch'}
            status['status'] = 'degraded'
    except RedisError as e:
        status['checks']['redis'] = {'status': 'unhealthy', 'error': str(e)}
        status['status'] = 'degraded'
    
    # Celery check
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        active = inspect.active()
        if active:
            status['checks']['celery'] = {'status': 'healthy', 'workers': len(active)}
        else:
            status['checks']['celery'] = {'status': 'unhealthy', 'error': 'No workers active'}
            status['status'] = 'degraded'
    except Exception as e:
        status['checks']['celery'] = {'status': 'unhealthy', 'error': str(e)}
        status['status'] = 'degraded'
    
    # Disk space check
    try:
        import shutil
        disk = shutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        status['checks']['disk'] = {
            'status': 'healthy' if free_gb > 1 else 'unhealthy',
            'free_gb': round(free_gb, 2)
        }
    except Exception as e:
        status['checks']['disk'] = {'status': 'unknown', 'error': str(e)}
    
    return JsonResponse(status, status=200 if status['status'] == 'healthy' else 503)

# Add to urls.py
from django.urls import path
urlpatterns = [
    path('health/', health_check, name='health_check'),
]
```

#### 3. Configure Docker Logging

**File:** `docker-compose.yml`

**Add logging configuration:**
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
        tag: "{{.ImageName}}/{{.Name}}"

  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  postgres:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### 4. Add Structured Logging to Django

**File:** `apps/backend/src/utils/helpers/logger/`

**Enhance logger for production:**
```python
# utils/helpers/logger/production.py
import json
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

class ProductionLogger(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['environment'] = os.environ.get('ENVIRONMENT', 'development')
        log_record['service'] = 'financehub-backend'

def setup_production_logging():
    """Configure JSON logging for production"""
    handler = logging.StreamHandler()
    formatter = ProductionLogger(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
```

#### 5. Add Nginx Health Check Endpoint

**File:** `nginx.conf`

**Add health endpoint:**
```nginx
server {
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    location /ready {
        access_log off;
        # Check backend is responding
        proxy_pass http://backend:8000/health/;
        proxy_connect_timeout 5s;
        proxy_read_timeout 10s;
        
        error_page 502 503 504 = @fallback;
    }

    location @fallback {
        return 503 "not ready";
        add_header Content-Type text/plain;
    }
}
```

#### 6. Add Prometheus Metrics (Optional)

**File:** `apps/backend/src/core/metrics.py`

**Add Prometheus metrics endpoint:**
```python
# Install: pip install prometheus_client
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from django.http import HttpResponse

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_USERS = Gauge('active_users', 'Number of active users')

def metrics_view(request):
    """Prometheus metrics endpoint"""
    return HttpResponse(generate_latest(), content_type='text/plain')

# Add middleware to track requests
class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        return response
```

#### 7. Add Uptime Monitoring (GitHub Actions)

**File:** `.github/workflows/uptime-monitor.yml`

```yaml
name: Uptime Monitor

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Check API health
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://api.financehub.com/health/)
          if [ "$response" != "200" ]; then
            echo "Health check failed with status $response"
            # Send alert (Slack, email, etc.)
            exit 1
          fi

      - name: Check frontend
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://financehub.com/)
          if [ "$response" != "200" ]; then
            echo "Frontend check failed with status $response"
            exit 1
          fi
```

## Files to Modify

1. `docker-compose.yml` - Health checks and logging
2. `apps/backend/src/core/urls.py` - Add health endpoint
3. `nginx.conf` - Add nginx health endpoints

## Files to Create

1. `apps/backend/src/core/health.py` - Health check views
2. `apps/backend/src/core/metrics.py` - Prometheus metrics
3. `apps/backend/src/utils/helpers/logger/production.py` - JSON logging
4. `.github/workflows/uptime-monitor.yml` - Uptime monitoring

## Testing

```bash
# Test health endpoint locally
curl http://localhost:8000/health/

# Check all services are healthy
docker-compose ps

# Verify logging configuration
docker-compose logs --tail 100 backend

# Test nginx health
curl http://localhost/health
```

## Success Criteria

1. ✅ All Docker services have health checks
2. ✅ Health endpoint returns comprehensive status
3. ✅ Structured JSON logging in production
4. ✅ Nginx health endpoints working
5. ✅ Uptime monitoring active
6. ✅ Logs are rotated and sized properly

## Related Issues

- INFRASTRUCTURE_ANALYSIS.md Issues 5, 7
- CELERY_ANALYSIS.md (monitoring gaps)
