# Gaudi: Create DevOps Tasks for Coders

**From:** DevOps Monitor  
**Date:** January 31, 2026  
**Priority:** High

---

## Summary

Completed comprehensive DevOps audit. Found **14 new improvements** but also **2 existing pending tasks** that need completion.

---

## Existing Tasks to COMPLETE First

### D-004: Monitoring & Logging
**File:** `tasks/devops/004-monitoring-logging.md`
- Status: pending
- Estimate: 2 days
- Assigned to: gaudi
- **What's done:** Health checks, Django health endpoint, logging, nginx endpoints
- **What's missing:** Prometheus metrics, uptime monitoring, alerting, CloudWatch export

### D-005: Backup, DR & Performance
**File:** `tasks/devops/005-backup-recovery.md`
- Status: pending
- Estimate: 2 days
- Assigned to: gaudi
- **What's done:** Backup scripts (backup.sh, restore.sh), connection pooling config, cache manager
- **What's missing:** Docker multi-stage builds, pgbouncer production config

**Action:** Complete D-004 and D-005 before creating new tasks.

---

## New Tasks to Create

### D-009: CI/CD Pipeline Enhancement (8h)
**File:** `.github/workflows/ci.yml`

1. Update GitHub Actions to latest versions (v3 -> v4)
2. Add migration check job (`makemigrations --check --dry-run`)
3. Add integration tests job (requires writing tests)
4. Add performance tests job (requires writing tests)
5. Fix mypy to fail on errors (remove `|| true`)
6. Add pip caching to backend-test job
7. Add bundle size threshold check

---

### D-010: Deployment Rollback & Safety (12h)
**File:** `.github/workflows/deploy.yml`

1. Add rollback job (auto-revert on failure)
2. Add database migration step using ECS run-task
3. Replace hardcoded sleep with health check polling
4. Update deprecated `actions/create-release` to `softprops/action-gh-release`
5. Add health check retry logic (3 attempts)
6. Add pre-deploy RDS snapshot backup

---

### D-011: Docker Security Hardening (4h)

**Backend:** `apps/backend/Dockerfile`
- Audit builder stage for sensitive data

**Frontend:** `apps/frontend/Dockerfile`
- Add non-root user (nextjs user)
- Add security context

---

### D-012: Database Performance Optimization (6h)
**File:** `apps/backend/src/core/settings.py`

1. Add connection pool settings (max_connections, connect_timeout)
2. Add prepared statements (statement_timeout)
3. Configure slow query logging
4. Fix wrong charset option (utf8mb4 -> remove for PostgreSQL)

**Note:** D-005 already has connection pooling config - merge implementations.

---

### D-013: Security Scan Improvements (4h)
**File:** `.github/workflows/security.yml`

1. Update all actions to latest versions
2. Add automated vulnerability reporting
3. Configure severity thresholds

---

### D-014: Monitoring & Alerting Setup (8h)
**Reference:** `tasks/devops/004-monitoring-logging.md`

**Missing from D-004:**
1. Prometheus metrics endpoint
2. Uptime monitoring GitHub Actions
3. Alerting integration (Slack/PagerDuty)
4. CloudWatch metrics export

---

### D-015: Caching Strategy Implementation (4h)
**Reference:** `tasks/devops/005-backup-recovery.md` (has cache_manager.py)

**Missing:**
1. Add TTL configuration to Redis cache
2. Add cache key prefixing
3. Implement cache invalidation strategy
4. Configure L1/L2/L3 cache levels

---

## Priority Order

### Week 1: Complete Existing
1. **D-004:** Finish monitoring (1 day remaining)
2. **D-005:** Finish backup/DR (1 day remaining)

### Week 2: New Critical Tasks
3. **D-009:** CI/CD Pipeline (1 day)
4. **D-010:** Deployment Safety (1.5 days)

### Week 3: Performance & Security
5. **D-011:** Docker Security (0.5 day)
6. **D-012:** Database Performance (0.5 day)
7. **D-013:** Security Scans (0.5 day)
8. **D-014:** Alerting (1 day)
9. **D-015:** Caching (0.5 day)

---

## Effort Summary

| Task | Hours | Priority | Status |
|------|-------|----------|--------|
| D-004 | 8h | High | Exists (partial) |
| D-005 | 8h | High | Exists (partial) |
| D-009 | 8h | High | New |
| D-010 | 12h | High | New |
| D-011 | 4h | Medium | New |
| D-012 | 6h | Medium | New |
| D-013 | 4h | Medium | New |
| D-014 | 8h | High | New |
| D-015 | 4h | Medium | New |
| **Total** | **62h** | 2-3 weeks | |

---

## What I Need From You

1. **Check D-004 and D-005 status** - Are they being worked on?
2. **If blocked:** Create new tasks D-009 through D-015
3. **If unblocked:** Focus on completing D-004/D-005 first
4. **Assign coders** with clear ownership
5. **Set dependencies:** D-002 → D-006/7/8 → D-004/5 → D-009-015

---

## Context for Coders

Full audit details in: `tasks/devops/DEVOPS_IMPROVEMENTS_AUDIT.md`

Each task has:
- Specific files to modify
- Current state vs desired state
- Code examples for fixes
- Effort estimates

---

## Quick Win: Fix Wrong Charset (10 min)

**File:** `apps/backend/src/core/settings.py:161`

**Current (wrong):**
```python
"OPTIONS": {
    "charset": "utf8mb4",  # MySQL only!
    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
},
```

**Fix:**
```python
"OPTIONS": {
    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
},
```

This is PostgreSQL, not MySQL. The charset option is ignored but causes confusion.

---

**Taking accountability. Completing D-004 and D-005 first, then creating new tasks.**
