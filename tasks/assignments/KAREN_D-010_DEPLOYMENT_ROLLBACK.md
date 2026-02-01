# 📋 Task Assignment: D-010 Deployment Rollback & Safety

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Karen (DevOps Engineer)
**Priority:** P0 CRITICAL - Infrastructure
**Estimated Effort:** 6-8 hours
**Timeline:** Due Feb 3, 2026 (CRITICAL)

---

## 🎯 OVERVIEW

Implement robust deployment rollback mechanisms, migration safety checks, and health monitoring to prevent failed deployments from breaking production.

**Context:**
- Security audit approved this task as P0 CRITICAL
- Current deployment has no rollback mechanism
- No migration safety checks
- No health checks before/after deployment
- **Due: Feb 3, 2026** (strict deadline)

---

## 📋 YOUR TASKS

### Task 1: Add Pre-Deployment Health Checks (2h)

**Create health check script:**
```bash
#!/bin/bash
# scripts/pre-deploy-health-check.sh

set -e

echo "🔍 Running pre-deployment health checks..."

# Check if current deployment is healthy
echo "Checking backend health..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health/ || echo "000")
if [ "$BACKEND_HEALTH" != "200" ]; then
  echo "❌ Backend health check failed: $BACKEND_HEALTH"
  exit 1
fi
echo "✅ Backend healthy"

# Check database connection
echo "Checking database connection..."
python manage.py dbshell --command "SELECT 1" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ Database connection failed"
  exit 1
fi
echo "✅ Database connected"

# Check Redis
echo "Checking Redis connection..."
redis-cli -h $REDIS_HOST ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ Redis connection failed"
  exit 1
fi
echo "✅ Redis connected"

# Check disk space (need at least 10GB free)
echo "Checking disk space..."
FREE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$FREE_SPACE" -lt 10 ]; then
  echo "❌ Insufficient disk space: ${FREE_SPACE}GB free"
  exit 1
fi
echo "✅ Disk space OK (${FREE_SPACE}GB free)"

echo "✅ All pre-deployment checks passed!"
```

**Integrate into GitHub Actions:**
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Pre-deployment health check
        run: |
          chmod +x scripts/pre-deploy-health-check.sh
          ./scripts/pre-deploy-health-check.sh

      - name: Deploy backend
        run: |
          # ... deployment steps

      - name: Post-deployment health check
        run: |
          chmod +x scripts/post-deploy-health-check.sh
          ./scripts/post-deploy-health-check.sh
```

### Task 2: Add Post-Deployment Health Checks (1h)

**Create post-deployment health check:**
```bash
#!/bin/bash
# scripts/post-deploy-health-check.sh

set -e

echo "🔍 Running post-deployment health checks..."
MAX_RETRIES=30
RETRY_DELAY=5

# Wait for deployment to stabilize
echo "Waiting for deployment to stabilize..."
sleep 10

# Health check with retries
for i in $(seq 1 $MAX_RETRIES); do
  echo "Health check attempt $i/$MAX_RETRIES..."

  HEALTH_STATUS=$(curl -s $BACKEND_URL/health/ | jq -r '.status' 2>/dev/null || echo "unhealthy")

  if [ "$HEALTH_STATUS" == "healthy" ]; then
    echo "✅ Deployment is healthy!"
    break
  fi

  if [ $i -eq $MAX_RETRIES ]; then
    echo "❌ Health check failed after $MAX_RETRIES attempts"
    echo "🔄 Initiating automatic rollback..."
    ./scripts/rollback-last-deployment.sh
    exit 1
  fi

  echo "⏳ Waiting for deployment to be healthy... ($i/$MAX_RETRIES)"
  sleep $RETRY_DELAY
done

# Run smoke tests
echo "Running smoke tests..."
python scripts/smoke_tests.py
if [ $? -ne 0 ]; then
  echo "❌ Smoke tests failed"
  ./scripts/rollback-last-deployment.sh
  exit 1
fi

echo "✅ All post-deployment checks passed!"
```

**Health check endpoint:**
```python
# apps/backend/api/health.py
from ninja import Router
from django.db import connections
from django.core.cache import cache

router = Router(tags=["health"])

@router.get("/health")
def health_check(request):
    """Health check endpoint for monitoring"""
    checks = {
        "status": "healthy",
        "checks": {}
    }

    # Database check
    try:
        db_conn = connections["default"]
        db_conn.cursor().execute("SELECT 1")
        checks["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["database"] = {"status": "unhealthy", "error": str(e)}

    # Redis check
    try:
        cache.set("health_check", "ok", 10)
        cache.get("health_check") == "ok"
        checks["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}

    status_code = 200 if checks["status"] == "healthy" else 503
    return checks, status_code
```

### Task 3: Implement Automatic Rollback (2-3h)

**Create rollback script:**
```bash
#!/bin/bash
# scripts/rollback-last-deployment.sh

set -e

echo "🔄 Initiating deployment rollback..."

# Get previous deployment info
PREVIOUS_DEPLOYMENT=$(git log -2 --pretty=format:"%H" | tail -1)
CURRENT_DEPLOYMENT=$(git rev-parse HEAD)

echo "Current deployment: $CURRENT_DEPLOYMENT"
echo "Rolling back to: $PREVIOUS_DEPLOYMENT"

# Backup current database schema (in case of migration)
echo "Backing up database schema..."
pg_dump $DATABASE_URL -s > /tmp/schema_before_rollback.sql

# Revert migrations to previous version
echo "Reverting database migrations..."
python manage.py migrate apps zero --noinput
python manage.py migrate $(git show $PREVIOUS_DEPLOYMENT:apps/backend/migrations/ | head -1) --noinput

# Revert code
echo "Reverting code..."
git reset --hard $PREVIOUS_DEPLOYMENT

# Restart services
echo "Restarting services..."
systemctl restart financehub-backend
systemctl restart financehub-frontend

# Wait for services to start
sleep 15

# Verify rollback health
echo "Verifying rollback health..."
HEALTH_STATUS=$(curl -s $BACKEND_URL/health/ | jq -r '.status')
if [ "$HEALTH_STATUS" != "healthy" ]; then
  echo "❌ Rollback verification failed!"
  echo "⚠️ Manual intervention required!"
  exit 1
fi

echo "✅ Rollback completed successfully!"
echo "📧 Alerting team..."
# Send alert to team (Slack, email, etc.)
```

**GitHub Actions rollback:**
```yaml
# .github/workflows/deploy-backend.yml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3

    - name: Deploy
      id: deploy
      run: |
        ./scripts/deploy.sh

    - name: Health check
      id: health_check
      run: |
        ./scripts/post-deploy-health-check.sh

    - name: Rollback on failure
      if: failure()
      run: |
        echo "❌ Deployment failed, initiating rollback..."
        ./scripts/rollback-last-deployment.sh
```

### Task 4: Migration Safety Checks (2h)

**Create migration safety script:**
```bash
#!/bin/bash
# scripts/check-migration-safety.sh

set -e

echo "🔍 Checking migration safety..."

# Get pending migrations
PENDING_MIGRATIONS=$(python manage.py showmigrations | grep "\[ \]" | wc -l)

if [ "$PENDING_MIGRATIONS" -eq 0 ]; then
  echo "✅ No pending migrations"
  exit 0
fi

echo "⚠️ Found $PENDING_MIGRATIONS pending migrations"

# Check if migrations are reversible
echo "Checking if migrations are reversible..."
python manage.py migrate --plan | grep "Un reversible" && {
  echo "❌ Irreversible migration detected!"
  echo "Please review migrations manually"
  exit 1
}

# Dry-run migration
echo "Dry-running migrations..."
python manage.py migrate --fake 2>&1 | tee /tmp/migration_dryrun.log

# Check for data loss operations
if grep -i "DROP\|DELETE\|TRUNCATE" /tmp/migration_dryrun.log; then
  echo "❌ Potential data loss detected in migrations!"
  echo "⚠️ Manual review required"
  exit 1
fi

# Backup database before real migration
echo "Creating database backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > /tmp/db_backup_$TIMESTAMP.sql

echo "✅ Migration safety checks passed"
```

**Integrate into deployment:**
```yaml
# GitHub Actions deployment
- name: Check migration safety
  run: |
    chmod +x scripts/check-migration-safety.sh
    ./scripts/check-migration-safety.sh

- name: Run migrations
  run: |
    python manage.py migrate --noinput

- name: Migration rollback on failure
  if: failure()
  run: |
    echo "❌ Migrations failed, rolling back..."
    LATEST_BACKUP=$(ls -t /tmp/db_backup_*.sql | head -1)
    psql $DATABASE_URL < $LATEST_BACKUP
```

### Task 5: Monitoring & Alerting (1h)

**Create deployment monitoring dashboard:**
```yaml
# prometheus/alerts.yml
groups:
  - name: deployment
    rules:
      - alert: DeploymentUnhealthy
        expr: up{job="financehub-backend"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Deployment is unhealthy"
          description: "Backend has been down for 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
```

**Slack alert integration:**
```python
# scripts/alert.py
import requests
import os

def send_alert(message: str, severity: str = "info"):
  """Send alert to Slack"""
  webhook_url = os.environ["SLACK_WEBHOOK_URL"]

  color = {
    "critical": "#FF0000",
    "warning": "#FFA500",
    "info": "#36A64F"
  }

  payload = {
    "attachments": [{
      "color": color.get(severity, "#36A64F"),
      "title": f"Deployment Alert [{severity.upper()}]",
      "text": message,
      "footer": "FinanceHub Deployment Bot"
    }]
  }

  requests.post(webhook_url, json=payload)
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Pre-deployment health checks pass before deploy
- [ ] Post-deployment health checks verify deployment
- [ ] Automatic rollback triggers on health check failure
- [ ] Migration safety checks prevent data loss
- [ ] Database backups created before migrations
- [ ] Monitoring alerts configured
- [ ] Team notified on rollback
- [ ] Rollback verified with health checks

---

## 🧪 TESTING

**Test rollback mechanism:**
1. Deploy a broken version
2. Verify automatic rollback triggers
3. Verify previous version is restored
4. Verify health checks pass after rollback

**Test migration safety:**
1. Create irreversible migration
2. Verify safety check catches it
3. Verify deployment is blocked

**Test health checks:**
1. Stop backend service
2. Verify health check fails
3. Verify deployment is blocked

---

## 📚 REFERENCES

**Django Deployment:**
- https://docs.djangoproject.com/en/4.2/howto/deployment/

**GitHub Actions Deployment:**
- https://docs.github.com/en/actions/deployment

**PostgreSQL Backups:**
- https://www.postgresql.org/docs/current/backup.html

---

## 🚨 PRODUCTION NOTES

**Rollback Strategy:**
- Blue-green deployment (switch traffic to previous version)
- Database migrations reversible or with data backups
- Automatic rollback on health check failure
- Manual rollback trigger available

**Monitoring:**
- Prometheus + Grafana dashboards
- Slack alerts for failures
- Error rate monitoring
- Response time tracking

---

## 📊 DELIVERABLES

1. ✅ Pre-deployment health check script
2. ✅ Post-deployment health check script
3. ✅ Automatic rollback script
4. ✅ Migration safety checks
5. ✅ Database backup automation
6. ✅ Monitoring & alerting setup
7. ✅ GitHub Actions integration
8. ✅ Documentation

---

## ✅ COMPLETION CHECKLIST

Before marking complete:
- [ ] Health check endpoints created
- [ ] Pre-deployment checks pass
- [ ] Post-deployment checks pass
- [ ] Rollback tested and works
- [ ] Migration safety checks tested
- [ ] Monitoring configured
- [ ] Alerts tested
- [ ] Documentation complete

---

**Next Task:** D-011 Docker Security Hardening

---

**Questions?** Ask in COMMUNICATION_HUB.md

**Status Updates:** Add to COMMUNICATION_HUB.md Agent Updates section

**When Complete:** Update TASK_TRACKER.md, notify GAUDÍ
