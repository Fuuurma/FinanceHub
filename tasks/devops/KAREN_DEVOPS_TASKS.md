# 🔧 DEVOPS TASKS - IMPROVEMENTS AUDIT

**From:** Karen (DevOps) Research
**Date:** January 31, 2026
**Priority:** 🟠 P1 HIGH
**Total Issues:** 14 improvements across 4 categories

---

## 📊 Summary of Findings

| Category | Issues | Priority | Est. Time |
|----------|--------|----------|-----------|
| CI/CD Pipeline | 8 | High | 8 hours |
| Deployment | 6 | High | 12 hours |
| Docker Security | 2 | Medium | 4 hours |
| Database Performance | 4 | Medium | 6 hours |

**Total Estimated Time:** 30 hours (3-5 days)

---

## 🚨 HIGH PRIORITY - CRITICAL DEPLOYMENT ISSUES

### D-009: CI/CD Pipeline Enhancement
**Priority:** 🟠 HIGH
**Assigned To:** Karen (DevOps)
**Estimated:** 8 hours
**Deadline:** February 5, 2026

**Issues Found (8):**
1. Outdated GitHub Actions (v3 → v4)
2. No database migration checks
3. No integration tests
4. No performance tests
5. Type checking fails silently
6. No pip caching
7. No bundle size checks
8. Trivy not in CI

**File:** `.github/workflows/ci.yml`

**Fixes Required:**

#### 1. Update Actions to v4
```yaml
# BEFORE:
- uses: codecov/codecov-action@v3
- uses: actions/upload-artifact@v3

# AFTER:
- uses: codecov/codecov-action@v4
- uses: actions/upload-artifact@v4
```

#### 2. Add Migration Check Job
```yaml
  migrations-check:
    name: Check Migrations
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: finance_hub_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: |
          cd apps/backend
          pip install -r requirements.txt
      - name: Check for unapplied migrations
        run: |
          cd apps/backend
          python manage.py makemigrations --check --dry-run
```

#### 3. Add pip Caching
```yaml
      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

#### 4. Fix Type Checking
```yaml
# BEFORE:
- name: Type check (Backend)
  run: mypy . || true  # <-- FAILS SILENTLY

# AFTER:
- name: Type check (Backend)
  run: mypy .  # <-- FAILS ON ERROR
```

#### 5. Add Security Scanning
```yaml
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

**Acceptance Criteria:**
- [ ] All actions updated to latest versions
- [ ] Migration check job passes
- [ ] Type checking fails on errors
- [ ] Pip caching configured
- [ ] Security scanning in CI
- [ ] All tests passing

---

### D-010: Deployment Rollback & Safety
**Priority:** 🔴 CRITICAL
**Assigned To:** Karen (DevOps)
**Estimated:** 12 hours
**Deadline:** February 3, 2026

**Issues Found (6):**
1. **No rollback mechanism** (CRITICAL)
2. **No database migration handling** (CRITICAL)
3. Hardcoded sleep times
4. Deprecated GitHub action
5. No health check retries
6. No pre-deploy backup

**File:** `.github/workflows/deploy.yml`

**Fixes Required:**

#### 1. Add Rollback Job
```yaml
  rollback:
    name: Rollback on Failure
    if: failure()
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Revert deploy
        run: |
          echo "Deployment failed, initiating rollback..."
          # Add rollback logic here
          gh api \
            --method POST \
            /repos/Fuuurma/FinanceHub/deployments \
            -f environment=production \
            -f state=inactive
```

#### 2. Add Database Migration Step
```yaml
      - name: Run Database Migrations
        run: |
          aws ecs run-task \
            --cluster financehub-production \
            --task-definition financehub-migrate \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[${{ env.PRIVATE_SUBNET }}],securityGroups=[${{ env.SECURITY_GROUP }}],assignPublicIp=DISABLED}"
```

#### 3. Replace Sleep with Health Check
```yaml
# BEFORE:
- name: Wait for deployment
  run: sleep 60  # <-- HARDCODED

# AFTER:
- name: Wait for healthy deployment
  run: |
        for i in {1..30}; do
          if curl -f https://api.financehub.app/health/; then
            echo "Deployment is healthy"
            exit 0
          fi
          echo "Waiting for health... ($i/30)"
          sleep 2
        done
        echo "Deployment failed health check"
        exit 1
```

#### 4. Add Pre-deploy Backup
```yaml
      - name: Create RDS Snapshot
        run: |
          SNAPSHOT_ID=$(aws rds create-db-snapshot \
            --db-instance-identifier financehub-prod \
            --db-snapshot-identifier pre-deploy-$(date +%Y%m%d-%H%M%S) \
            --query 'DBSnapshot.DBSnapshotIdentifier' \
            --output text)
          echo "Snapshot created: $SNAPSHOT_ID"
          echo "SNAPSHOT_ID=$SNAPSHOT_ID" >> $GITHUB_ENV
```

#### 5. Update Deprecated Action
```yaml
# BEFORE:
- uses: actions/create-release@v1  # DEPRECATED

# AFTER:
- uses: softprops/action-gh-release@v2  # CURRENT
```

#### 6. Add Health Check Retries
```yaml
      - name: Health Check with Retries
        run: |
          MAX_RETRIES=3
          RETRY_COUNT=0
          while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
            if curl -f https://api.financehub.app/health/; then
              echo "Health check passed"
              exit 0
            fi
            RETRY_COUNT=$((RETRY_COUNT + 1))
            echo "Retry $RETRY_COUNT/$MAX_RETRIES"
            sleep 10
          done
          echo "Health check failed after $MAX_RETRIES attempts"
          exit 1
```

**Acceptance Criteria:**
- [ ] Rollback mechanism tested
- [ ] Migrations run before deploy
- [ ] Health checks replace sleep
- [ ] Pre-deploy snapshots created
- [ ] Health check retries configured
- [ ] All actions updated

---

## 🟡 MEDIUM PRIORITY

### D-011: Docker Security Hardening
**Priority:** 🟡 MEDIUM
**Assigned To:** Karen (DevOps)
**Estimated:** 4 hours
**Deadline:** February 8, 2026

**Issues Found (2):**
1. Frontend runs as root
2. Backend builder stage audit needed

**Files:**
- `apps/frontend/Dockerfile`
- `apps/backend/Dockerfile`

**Fixes Required:**

#### 1. Frontend: Add Non-Root User
```dockerfile
# apps/frontend/Dockerfile

# Add this after dependencies are installed
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Switch to non-root user
USER nextjs
```

#### 2. Backend: Audit Builder Stage
```dockerfile
# apps/backend/Dockerfile

# Builder stage - ensure no secrets
FROM python:3.11-slim-bookworm AS builder

# Don't copy:
# - .env files
# - SSH keys
# - API keys

# Only copy what's needed for building
COPY requirements.txt .
COPY apps/backend/ .

# Multi-stage build ensures secrets don't leak
FROM python:3.11-slim-bookworm

# Copy only artifacts, not source
COPY --from=builder /app /app
```

**Acceptance Criteria:**
- [ ] Frontend runs as non-root user
- [ ] Backend builder stage audited
- [ ] No secrets in final image
- [ ] Security scan passes

---

### D-012: Database Performance Optimization
**Priority:** 🟡 MEDIUM
**Assigned To:** Karen (DevOps)
**Estimated:** 6 hours
**Deadline:** February 8, 2026

**Issues Found (4):**
1. No connection pooling
2. No slow query logging
3. Wrong charset (utf8mb4 for PostgreSQL)
4. No prepared statements

**File:** `apps/backend/src/core/settings.py`

**Fixes Required:**

#### 1. Add Connection Pooling
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 seconds
        },
        'POOL': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}
```

#### 2. Fix Wrong Charset
```python
# BEFORE (WRONG):
"OPTIONS": {
    "charset": "utf8mb4",  # This is MySQL only!
}

# AFTER (CORRECT):
"OPTIONS": {
    # PostgreSQL uses UTF-8 by default
    # No charset option needed
}
```

#### 3. Add Slow Query Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',  # Log slow queries
            'handlers': ['console'],
        },
    },
}
```

#### 4. Enable Prepared Statements
```python
DATABASES = {
    'default': {
        'OPTIONS': {
            'sslmode': 'require',
            'prepare_threshold': 100,  # Use prepared statements
        },
    }
}
```

**Acceptance Criteria:**
- [ ] Connection pooling configured
- [ ] Slow queries logged
- [ ] Charset option removed
- [ ] Prepared statements enabled
- [ ] Performance tests pass

---

## 📋 Existing Tasks to Complete

### D-004: Monitoring & Logging
**Status:** ⏳ Partially Complete
**Remaining Work:**
- [ ] Prometheus metrics endpoint
- [ ] Uptime monitoring
- [ ] Alerting integration
- [ ] CloudWatch metrics export

### D-005: Backup & Disaster Recovery
**Status:** ⏳ Partially Complete
**Remaining Work:**
- [ ] Docker multi-stage builds
- [ ] Production pgbouncer config
- [ ] Backup automation
- [ ] Restore testing

---

## 📊 Implementation Timeline

### Week 1 (Feb 1-3): CRITICAL
1. **D-010:** Deployment Rollback (Karen) - 12 hours
   - Add rollback mechanism
   - Add migration handling
   - Replace sleeps with health checks
   - Add pre-deploy backups

### Week 2 (Feb 4-5): HIGH
2. **D-009:** CI/CD Enhancement (Karen) - 8 hours
   - Update actions to v4
   - Add migration checks
   - Add security scanning
   - Fix type checking

### Week 3 (Feb 6-8): MEDIUM
3. **D-011:** Docker Security (Karen) - 4 hours
4. **D-012:** Database Performance (Karen) - 6 hours
5. **Complete D-004:** Monitoring (Karen)
6. **Complete D-005:** Backup/DR (Karen)

---

## 🎯 Success Metrics

**CI/CD Pipeline:**
- [ ] All actions updated to latest
- [ ] Migration checks in place
- [ ] Security scanning automated
- [ ] Type checking enforced

**Deployment:**
- [ ] Rollback tested and working
- [ ] Zero-downtime deployments
- [ ] Health checks reliable
- [ ] Pre-deploy backups automated

**Database:**
- [ ] Connection pooling active
- [ ] Slow queries visible
- [ ] Performance improved 20%+
- [ ] No wrong charset

**Docker:**
- [ ] No root user in frontend
- [ ] Builder stage audited
- [ ] Security scan passing

---

## 🚨 Immediate Actions

**TODAY (January 31):**
1. GAUDÍ approves tasks D-009 through D-012
2. Update TASK_TRACKER.md
3. Assign to Karen
4. Send communication to Karen

**TOMORROW (February 1):**
1. Karen starts D-010 (Deployment Rollback)
2. Safety mechanisms prioritized

**This Week:**
1. Complete D-010 (critical)
2. Start D-009 (CI/CD)

---

## 📞 Coordination

**D-010 depends on:**
- S-008 (Docker base image) complete
- D-008 (Docker optimization) complete

**Can work in parallel with:**
- S-009 through S-016 (Security tasks)

---

**All tasks based on Karen's comprehensive audit.**

**Full Report:** `tasks/devops/DEVOPS_IMPROVEMENTS_AUDIT.md`

---

🔧 *Karen - DevOps Engineer*

🎨 *GAUDÍ - Approval Required*
