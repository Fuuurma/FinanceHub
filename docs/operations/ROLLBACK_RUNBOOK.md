# Deployment Rollback Runbook

**Purpose:** Emergency procedures for rolling back failed deployments

**Last Updated:** February 1, 2026

**Owner:** DevOps (Karen)

---

## 🚨 Emergency Rollback Procedures

### When to Rollback

Rollback is necessary when:
- Critical errors detected after deployment
- Health checks failing
- Performance degradation > 50%
- Data corruption or loss
- Security vulnerabilities introduced

---

## Quick Rollback (Database Only)

### Scenario: Migration failed

```bash
# 1. Stop backend
docker-compose stop backend

# 2. Restore from latest backup
cd /Users/sergi/Desktop/Projects/FinanceHub
./scripts/rollback_migration.sh

# 3. Verify rollback
curl http://localhost:8000/health/v2/simple

# 4. Check logs
docker-compose logs backend --tail 50
```

**Time to rollback:** 2-5 minutes

---

## Full Deployment Rollback

### Scenario: Complete deployment failure

```bash
# 1. Full rollback script
cd /Users/sergi/Desktop/Projects/FinanceHub
./scripts/rollback_deployment.sh

# 2. If script fails, manual rollback:
docker-compose stop backend frontend
git checkout <previous-commit>
docker-compose build --no-cache backend
docker-compose up -d backend

# 3. Verify
./scripts/post_deployment_validate.sh
```

**Time to rollback:** 10-15 minutes

---

## Health Check Rollback Decisions

### Use Health Endpoint to Decide

```bash
# Check detailed health
curl http://localhost:8000/health/v2/detailed | jq .

# If checks.can_deploy == false, consider rollback
# If components.database.status == "unhealthy", immediate rollback
# If components.migrations.critical_pending > 0, investigate first
```

### Decision Matrix

| Component Status | Action |
|-----------------|---------|
| Database unhealthy | 🚨 Immediate rollback |
| Redis unhealthy | ⚠️ Investigate, may need rollback |
| Migrations not applied | ⚠️ Investigate, manual fix may work |
| High error rate | 🚨 Rollback if errors > 10/min |

---

## Manual Rollback Steps

### If Automated Scripts Fail

#### 1. Database Rollback

```bash
# List available backups
ls -lt ./backups/migrations/

# Restore specific backup
gunzip -c ./backups/migrations/finance_hub_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose exec -T postgres psql -U financehub -d finance_hub
```

#### 2. Code Rollback

```bash
# View recent commits
git log --oneline -10

# Checkout previous commit
git checkout <commit-hash>

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Environment Variables Rollback

```bash
# If .env was changed
git checkout .env

# Restart services
docker-compose restart backend
```

---

## Post-Rollback Verification

### Checklist

- [ ] All containers healthy: `docker-compose ps`
- [ ] Health endpoint responding: `curl http://localhost:8000/health/v2/simple`
- [ ] No errors in logs: `docker-compose logs backend --tail 100`
- [ ] API endpoints working: Test critical endpoints
- [ ] Database queries working: Connect and run test query
- [ ] Frontend accessible: Load web application

### Automated Verification

```bash
./scripts/post_deployment_validate.sh
```

---

## Communication

### Who to Notify

**Immediate:**
- GAUDÍ (Architect)
- ARIA (Architect Assistant)

**If database issue:**
- Database team (if exists)

**If security issue:**
- Charo (Security Engineer)

### What to Report

1. What went wrong
2. What was rolled back
3. Current system status
4. Next steps / timeline
5. Any data impact

---

## Prevention

### How to Avoid Rollbacks

1. **Pre-deployment checks**
   ```bash
   ./scripts/pre_deployment_check.sh
   ```

2. **Migration safety**
   ```bash
   ./scripts/safe_migrate.sh --dry-run
   ```

3. **Staging environment testing**
   - Test in staging first
   - Validate all changes
   - Get approval before production

4. **Incremental deployments**
   - Deploy to subset of servers
   - Monitor for 15 minutes
   - Roll out to rest if stable

---

## Common Scenarios

### Scenario 1: Migration Lock Timeout

**Symptom:** Migration hangs, locks database

**Solution:**
```bash
# 1. Check active locks
docker-compose exec postgres psql -U financehub -d finance_hub -c "
  SELECT * FROM pg_locks WHERE NOT granted;
"

# 2. Cancel problematic queries
docker-compose exec postgres psql -U financehub -d finance_hub -c "
  SELECT pg_cancel_backend(<pid>);
"

# 3. If still stuck, rollback migration
./scripts/rollback_migration.sh
```

### Scenario 2: Out of Memory During Migration

**Symptom:** Container killed during migration

**Solution:**
```bash
# 1. Increase memory limits
# Edit docker-compose.yml
# services.backend.deploy.resources.limits.memory

# 2. Restart and try again
docker-compose restart backend
./scripts/safe_migrate.sh
```

### Scenario 3: Missing Dependencies

**Symptom:** Import errors after deployment

**Solution:**
```bash
# 1. Check requirements
cat apps/backend/requirements.txt

# 2. Rebuild with no cache
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## Recovery Time Objectives (RTO)

| Severity | Target RTO | Actual RTO |
|----------|-----------|-----------|
| Critical (database down) | 5 min | ____ |
| High (API errors) | 15 min | ____ |
| Medium (degraded performance) | 30 min | ____ |
| Low (minor issues) | 2 hours | ____ |

---

## Lessons Learned

After each rollback, document:

1. What caused the failure
2. What worked in the rollback
3. What didn't work
4. How to prevent this in the future

Update this runbook with findings.

---

## Contact

**Primary:** Karen (DevOps)
**Escalation:** GAUDÍ (Architect)

**Emergency Contact:** [Add contact details]

---

**Remember:** It's better to rollback quickly than to leave a broken deployment in production. Users prefer temporary downtime over persistent errors.
