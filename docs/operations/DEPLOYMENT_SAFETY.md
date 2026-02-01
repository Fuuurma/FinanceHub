# Deployment Safety Documentation

**Purpose:** Guidelines and best practices for safe deployments

**Last Updated:** February 1, 2026

**Owner:** DevOps (Karen)

---

## 🛡️ Deployment Safety Principles

### 1. Never Deploy Without Testing

```
Development → Staging → Production
```

Always test in:
- Development environment (local)
- Staging environment (pre-production)
- Production (canary deployment)

### 2. Always Have a Rollback Plan

Before any deployment:
- ✅ Verify recent database backup exists
- ✅ Know rollback procedure
- ✅ Have team on standby
- ✅ Set monitoring alerts

### 3. Deploy During Low-Traffic Hours

Best times:
- Weekday evenings (after 6 PM)
- Weekends
- Avoid: Monday mornings, Friday afternoons

### 4. Use Incremental Deployments

```
Canary (5%) → Partial (25%) → Full (100%)
```

Monitor at each step before proceeding.

---

## 📋 Pre-Deployment Checklist

### Automation (Required)

Run automated pre-deployment check:

```bash
cd /Users/sergi/Desktop/Projects/FinanceHub
./scripts/pre_deployment_check.sh
```

**All checks must pass before proceeding.**

### Manual (Required)

- [ ] Code reviewed and approved
- [ ] Tests passing locally
- [ ] Staging environment tested
- [ ] Migration plan reviewed
- [ ] Rollback plan documented
- [ ] Team notified of deployment
- [ ] Monitoring configured
- [ ] Backup verified (< 24 hours old)

### For Database Migrations

- [ ] Migration SQL reviewed
- [ ] Dry-run completed
- [ ] Reversibility confirmed
- [ ] Impact analysis done
- [ ] Testing on staging data
- [ ] Rollback SQL prepared

---

## 🚀 Deployment Process

### Standard Deployment

```bash
# 1. Pre-deployment checks
./scripts/pre_deployment_check.sh

# 2. Pull latest code
git pull origin main

# 3. Run migrations (if any)
./scripts/safe_migrate.sh

# 4. Build and deploy
docker-compose build backend
docker-compose up -d backend

# 5. Post-deployment validation
./scripts/post_deployment_validate.sh
```

### Database Migration Deployment

```bash
# 1. Backup database
./scripts/backup.sh

# 2. Test migration (dry-run)
./scripts/safe_migrate.sh --dry-run

# 3. Review migration plan
# Check what SQL will be executed

# 4. Run migration
./scripts/safe_migrate.sh

# 5. Verify application
curl http://localhost:8000/health/v2/detailed
```

### Emergency Hotfix

```bash
# 1. Create hotfix branch
git checkout -b hotfix/<issue>

# 2. Apply fix
# Make changes

# 3. Quick test
docker-compose build backend
docker-compose up -d backend

# 4. Validate
./scripts/post_deployment_validate.sh

# 5. Deploy to production
# (Follow standard deployment if validation passes)
```

---

## 🛠️ Deployment Safety Tools

### Health Checks

**Simple health check:**
```bash
curl http://localhost:8000/health/v2/simple
```

**Detailed health check:**
```bash
curl http://localhost:8000/health/v2/detailed | jq .
```

**Readiness probe:**
```bash
curl http://localhost:8000/health/v2/ready
```

**Liveness probe:**
```bash
curl http://localhost:8000/health/v2/live
```

### Monitoring

**Real-time logs:**
```bash
docker-compose logs -f backend
```

**Error monitoring:**
```bash
docker-compose logs backend | grep ERROR
```

**Performance monitoring:**
```bash
docker stats financehub-backend
```

### Database Safety

**Before migration:**
```bash
# Check active connections
docker-compose exec postgres psql -U financehub -d finance_hub -c "
  SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
"

# Check database size
docker-compose exec postgres psql -U financehub -d finance_hub -c "
  SELECT pg_size_pretty(pg_database_size('finance_hub'));
"
```

**After migration:**
```bash
# Verify schema
docker-compose exec backend python src/manage.py showmigrations

# Check for errors
docker-compose logs backend | tail -100
```

---

## 🚨 Rollback Triggers

### Automatic Rollback Triggers

Rollback immediately if:
- Health check fails > 3 consecutive times
- Error rate > 10% for > 5 minutes
- Database connection lost
- Response time > 5 seconds for > 2 minutes
- Container restarts > 3 times in 10 minutes

### Manual Rollback Decision

Consider rollback if:
- Critical functionality broken
- Data corruption detected
- Security vulnerability exposed
- User complaints > threshold
- Performance degradation > 50%

### Rollback Process

```bash
# Quick rollback (database)
./scripts/rollback_migration.sh

# Full rollback
./scripts/rollback_deployment.sh

# Verify
./scripts/post_deployment_validate.sh
```

---

## 📊 Deployment Metrics

### Track These Metrics

- **Deployment frequency**: How often you deploy
- **Lead time**: Time from commit to deploy
- **Change failure rate**: % of deployments that fail
- **MTTR**: Mean time to restore (rollback time)
- **Deployment time**: How long deployment takes

### Targets

| Metric | Target | Current |
|--------|--------|---------|
| Deployment frequency | 1-2 per week | ____ |
| Lead time | < 1 day | ____ |
| Change failure rate | < 15% | ____ |
| MTTR | < 15 min | ____ |
| Deployment time | < 10 min | ____ |

---

## 🎯 Best Practices

### Code Quality

- Write tests for new features
- Run linters and formatters
- Review all code changes
- Document complex changes

### Testing

- Unit tests: Cover critical paths
- Integration tests: Test API endpoints
- End-to-end tests: Test user flows
- Load tests: For performance changes

### Monitoring

- Set up alerts before deploying
- Monitor key metrics during deployment
- Have dashboard ready
- Log everything

### Communication

- Notify team before deploying
- Update status during deployment
- Announce completion or issues
- Document any problems

---

## 🔒 Safety Checks

### Never Deploy When

- ⛔ No recent backup exists
- ⛔ Tests are failing
- ⛔ Staging not validated
- ⛔ Team unavailable
- ⛔ Before weekend/holiday (unless critical)
- ⛔ During high-traffic events
- ⛔ When already debugging issues

### Always Stop Deployment If

- 🛑 Health checks failing
- 🛑 Errors spiking in logs
- 🛑 Performance degraded
- 🛑 Users reporting issues
- 🛑 Unexpected behavior observed

---

## 📚 Related Documentation

- [ROLLBACK_RUNBOOK.md](./ROLLBACK_RUNBOOK.md) - Rollback procedures
- [../development/DEPLOYMENT.md](../development/DEPLOYMENT.md) - Deployment guide
- [tasks/devops/010-deployment-rollback.md](../../tasks/devops/010-deployment-rollback.md) - Task details

---

## 📞 Support

**Questions?** Ask Karen (DevOps)

**Issues?** Escalate to GAUDÍ (Architect)

**Emergency?** Follow ROLLBACK_RUNBOOK.md immediately

---

**Remember:** A safe, slow deployment is better than a fast, broken one.

**Team safety depends on following these guidelines.**
