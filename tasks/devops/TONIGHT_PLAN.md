# Tonight's DevOps Plan

**Date:** January 31, 2026  
**Time:** Evening

---

## 🎯 Goal

Complete as many quick wins as possible while waiting for Gaudi and coders.

---

## Order of Operations

### Phase 1: Quick Fixes (30 min)
1. ✅ PostgreSQL charset fix - DONE
2. ⏳ Update GitHub Actions (3 actions)
3. ⏳ Add bundle size check to CI

### Phase 2: Monitoring (1 hour)
4. ⏳ Create Prometheus metrics endpoint
5. ⏳ Create Uptime monitor workflow
6. ⏳ Add slow query logging

### Phase 3: Docker & Cache (45 min)
7. ⏳ Add non-root user to frontend
8. ⏳ Configure cache TTL
9. ⏳ Tune DB connection settings

---

## Files to Modify

| File | Changes |
|------|---------|
| `apps/backend/src/core/settings.py` | Charset fix, cache, DB settings |
| `apps/backend/src/core/metrics.py` | NEW - Prometheus metrics |
| `.github/workflows/ci.yml` | Actions update, bundle check |
| `.github/workflows/uptime-monitor.yml` | NEW - Uptime monitoring |
| `apps/frontend/Dockerfile` | Non-root user |
| `apps/backend/src/core/settings.py` | Slow query logging |

---

## Commands Ready

```bash
# Apply changes
git add -A
git commit -m "devops: Apply quick fixes and monitoring"
git push

# Verify
docker-compose build --no-cache
docker-compose up -d
```

---

## Waiting On

1. **Gaudi:** Task creation (D-009-015)
2. **Coders:** Unblock on Dramatiq/venv

---

## Deliverables by Morning

- [ ] 10 quick wins completed
- [ ] D-004 ~80% complete
- [ ] D-005 ~90% complete
- [ ] Ready for D-009-015 creation

---

**Taking accountability. Making progress.**
