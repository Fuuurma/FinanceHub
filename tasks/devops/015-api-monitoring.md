# Task D-015: Comprehensive API Monitoring

**Task ID:** D-015
**Assigned To:** Karen (DevOps)
**Priority:** 🟢 PROACTIVE
**Status:** 🔄 IN PROGRESS
**Created:** February 1, 2026
**Estimated Time:** 3 hours
**Deadline:** February 8, 2026

---

## 📋 OVERVIEW

**Objective:** Implement comprehensive monitoring for all 45+ backend API endpoints

**Current State:**
- Basic health check exists (`/health/`)
- Enhanced health check exists (`/health/v2/`)
- Prometheus metrics partially implemented
- No per-endpoint monitoring

**Target State:**
- All endpoints monitored
- Response time tracking per endpoint
- Error rate tracking per endpoint
- Request volume tracking per endpoint
- Automatic alerting on anomalies

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Enhance Prometheus Metrics (1 hour)

**Current:** `apps/backend/src/core/metrics.py` exists but limited

**Add to metrics.py:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Per-endpoint metrics
endpoint_requests = Counter(
    'api_endpoint_requests_total',
    'Total API requests by endpoint',
    ['method', 'endpoint', 'status']
)

endpoint_duration = Histogram(
    'api_endpoint_duration_seconds',
    'API endpoint duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

endpoint_errors = Counter(
    'api_endpoint_errors_total',
    'Total API errors by endpoint',
    ['method', 'endpoint', 'error_type']
)

active_connections = Gauge(
    'api_active_connections',
    'Active API connections',
    ['endpoint']
)
```

### Phase 2: Create API Middleware (1 hour)

**File:** `apps/backend/src/core/api_monitoring.py` (NEW)

```python
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from .metrics import endpoint_requests, endpoint_duration, endpoint_errors

logger = logging.getLogger(__name__)

class APIMonitoringMiddleware(MiddlewareMixin):
    """Monitor all API endpoint calls"""

    def process_request(self, request):
        """Record start time"""
        request.start_time = time.time()

    def process_response(self, request, response):
        """Record metrics"""
        if not hasattr(request, 'start_time'):
            return response

        # Calculate duration
        duration = time.time() - request.start_time

        # Extract endpoint path
        endpoint = self._get_endpoint_path(request.path)

        # Record metrics
        endpoint_requests.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        endpoint_duration.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)

        # Log slow requests
        if duration > 1.0:
            logger.warning(
                f"Slow API call: {request.method} {endpoint} "
                f"took {duration:.2f}s"
            )

        # Log errors
        if response.status_code >= 400:
            endpoint_errors.labels(
                method=request.method,
                endpoint=endpoint,
                error_type=str(response.status_code)
            ).inc()

        return response

    def _get_endpoint_path(self, path):
        """Normalize path for metrics"""
        # Remove IDs for grouping
        parts = path.split('/')
        normalized_parts = []

        for i, part in enumerate(parts):
            # Replace numeric IDs with :id
            if part.isdigit():
                normalized_parts.append(':id')
            # Replace UUIDs with :uuid
            elif len(part) == 36 and part.count('-') == 4:
                normalized_parts.append(':uuid')
            else:
                normalized_parts.append(part)

        return '/'.join(normalized_parts)
```

### Phase 3: Add to Django Settings (5 min)

**File:** `apps/backend/src/core/settings.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.api_monitoring.APIMonitoringMiddleware',  # ADD THIS
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Phase 4: Create Grafana Dashboard (30 min)

**File:** `docs/operations/GRAFANA_DASHBOARD.json` (NEW)

```json
{
  "dashboard": {
    "title": "FinanceHub API Monitoring",
    "panels": [
      {
        "title": "Request Rate by Endpoint",
        "targets": [
          {
            "expr": "rate(api_endpoint_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time P95",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, api_endpoint_duration_seconds_bucket)",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(api_endpoint_errors_total[5m])",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Active Connections",
        "targets": [
          {
            "expr": "api_active_connections",
            "legendFormat": "{{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

### Phase 5: Alerting Rules (30 min)

**File:** `docs/operations/PROMETHEUS_ALERTS.yml` (NEW)

```yaml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighAPIErrorRate
        expr: rate(api_endpoint_errors_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High API error rate on {{endpoint}}"
          description: "{{endpoint}} has error rate > 5% for 2 minutes"

      # Slow endpoint
      - alert: SlowAPIEndpoint
        expr: histogram_quantile(0.95, api_endpoint_duration_seconds_bucket) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API endpoint: {{endpoint}}"
          description: "P95 latency > 2s for 5 minutes on {{endpoint}}"

      # Endpoint down
      - alert: APIEndpointDown
        expr: rate(api_endpoint_requests_total{status="503"}[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API endpoint returning 503: {{endpoint}}"
          description: "Endpoint {{endpoint}} is unavailable"
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Prometheus metrics enhanced with per-endpoint tracking
- [ ] API monitoring middleware created
- [ ] Middleware added to Django settings
- [ ] Grafana dashboard JSON created
- [ ] Prometheus alerting rules created
- [ ] Documentation updated
- [ ] Metrics visible at `/metrics/` endpoint

---

## 📊 EXPECTED RESULTS

**Before:**
- Basic health check only
- No per-endpoint visibility
- No performance tracking
- Reactive debugging

**After:**
- All 45+ endpoints monitored
- Response time tracking (P50, P95, P99)
- Error rate tracking by endpoint
- Request volume tracking
- Proactive alerting

---

## 🧪 TESTING

### Test Metrics Collection
```bash
# Make some API calls
curl http://localhost:8000/api/v1/portfolios/
curl http://localhost:8000/api/v1/assets/
curl http://localhost:8000/api/v1/orders/

# Check metrics
curl http://localhost:8000/metrics/ | grep api_endpoint

# Should see:
# api_endpoint_requests_total{endpoint="/api/v1/portfolios",method="GET",status="200"} 1.0
# api_endpoint_duration_seconds_bucket{endpoint="/api/v1/portfolios",method="GET",le="0.1"} 1.0
```

### Test Middleware Integration
```bash
# Restart backend
docker-compose restart backend

# Check logs for slow request warnings
docker-compose logs backend --tail 20

# Make a slow request (if any exist)
curl http://localhost:8000/api/v1/analytics/  # This might be slow
```

---

## 📁 FILES TO CREATE/MODIFY

**Files to Create:**
1. `apps/backend/src/core/api_monitoring.py` - API monitoring middleware
2. `docs/operations/GRAFANA_DASHBOARD.json` - Grafana dashboard config
3. `docs/operations/PROMETHEUS_ALERTS.yml` - Alerting rules
4. `tasks/devops/015-api-monitoring.md` - This task file

**Files to Modify:**
1. `apps/backend/src/core/metrics.py` - Add per-endpoint metrics
2. `apps/backend/src/core/settings.py` - Add middleware

---

## 🔗 REFERENCES

- Prometheus Best Practices: https://prometheus.io/docs/practices/naming/
- Django Middleware: https://docs.djangoproject.com/en/5.0/topics/http/middleware/
- RED Method: https://weave.works/blog/the-red-method-key-metrics-for-monitoring/

---

**Task D-015 Status:** 🔄 IN PROGRESS

**Karen - DevOps Engineer**
*Building Financial Excellence* 🎨
