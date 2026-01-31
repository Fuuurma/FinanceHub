# GAUDI - Quick Guide: D-001 Implementation 🚀

**From:** Monitor (DevOps Coordinator)
**To:** GAUDÍ (Architect/DevOps)
**Date:** January 31, 2026
**Task:** Complete D-001 (Infrastructure Security)
**Time:** 35 minutes
**Tone:** Let's do this together!

---

## 💡 You're Almost There!

**Status:** D-001 is 50% complete
- ✅ Task file created (excellent!)
- ✅ Specifications documented
- ⏳ Implementation needed (35 minutes)

**Let's finish this together and unblock the project!**

---

## 🎯 What Needs to Be Done (3 files to edit)

### File 1: `.env.example` (5 minutes)

**Current Issue:** Hardcoded password on lines 10, 15

**Line 10 - Change:**
```bash
# FROM:
DATABASE_URL=postgres://financehub:financehub_dev_password@localhost:5432/finance_hub

# TO:
DATABASE_URL=postgres://financehub:${POSTGRES_PASSWORD}@localhost:5432/finance_hub
```

**Lines 13-16 - Replace:**
```bash
# FROM:
# Database
DB_PASSWORD=financehub_dev_password

# TO:
# Database Password - REQUIRED
# Generate with: openssl rand -base64 32
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}
```

**Why:**
- No hardcoded passwords in version control
- Environment variable enforcement (deployment fails if not set)
- Clear guidance on how to generate secure password

---

### File 2: `docker-compose.yml` (15 minutes)

**Issue 1 - Line 11 - Hardcoded password:**

```yaml
# FROM:
POSTGRES_PASSWORD: financehub_dev_password

# TO:
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}
```

**Issue 2 - Lines 50, 115 - Weak secret key fallback:**

```yaml
# FROM:
DJANGO_SECRET_KEY:
  ${DJANGO_SECRET_KEY:-django-insecure-dev-key-change-in-production}

# TO:
DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:?DJANGO_SECRET_KEY must be set}
```

**Issue 3 - Add resource limits to all services (10 minutes):**

**Add to backend service:**
```yaml
  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
      cache_from:
        - financehub-backend:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Add to frontend service:**
```yaml
  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

**Add to postgres service:**
```yaml
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Add to redis service:**
```yaml
  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

**Add to worker service:**
```yaml
  worker:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

---

### File 3: Update D-001 Task File (5 minutes)

**Add completion checklist:**

```markdown
## ✅ COMPLETION CHECKLIST

### Implemented Changes:
- [x] Task file created
- [x] Specifications documented
- [x] Urgent alerts sent
- [ ] .env.example updated (remove hardcoded passwords)
- [ ] docker-compose.yml updated (use env vars for secrets)
- [ ] Resource limits added to all services
- [ ] Documentation updated
- [ ] Tested with docker-compose config

### Security Verification:
```bash
# Verify no hardcoded passwords
! grep -r "financehub_dev_password" .env.example docker-compose.yml

# Verify environment variable enforcement
grep -q ":?.*must be set" docker-compose.yml

# Verify resource limits
grep -q "resources:" docker-compose.yml
```
```

---

## 🧪 Test Your Changes (5 minutes)

### Step 1: Verify docker-compose config

```bash
docker-compose config
```

**Expected:** Configuration loads without errors

### Step 2: Check for hardcoded passwords

```bash
grep -r "financehub_dev_password" .env.example docker-compose.yml
```

**Expected:** No results (exit code 1)

### Step 3: Check environment variable enforcement

```bash
grep -c ":?" docker-compose.yml
```

**Expected:** 2 or more (POSTGRES_PASSWORD, DJANGO_SECRET_KEY)

### Step 4: Check resource limits

```bash
grep -c "deploy:" docker-compose.yml
grep -c "resources:" docker-compose.yml
grep -c "limits:" docker-compose.yml
```

**Expected:** All show 5 (one for each service)

---

## 📝 Commit Your Changes (5 minutes)

```bash
git add .env.example docker-compose.yml tasks/devops/001-infrastructure-security.md

git commit -m "fix(security): remove hardcoded passwords, add resource limits (D-001 complete)

- Remove hardcoded financehub_dev_password from .env.example
- Use ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set} pattern
- Remove weak DJANGO_SECRET_KEY fallback
- Add resource limits (cpu, memory) to all services
- Enforce environment variables at deployment time
- Update D-001 task completion checklist

Security improvements:
- No hardcoded credentials in version control
- Deployment fails if secrets not provided
- Resource limits prevent runaway containers
- Clear guidance on password generation

Fixes #D-001"

git push origin main
```

---

## ✅ Verification Checklist

**Before pushing, verify:**

- [ ] `.env.example` does NOT contain `financehub_dev_password`
- [ ] `.env.example` uses `${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}`
- [ ] `docker-compose.yml` does NOT contain `financehub_dev_password`
- [ ] `docker-compose.yml` uses `${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}`
- [ ] `docker-compose.yml` uses `${DJANGO_SECRET_KEY:?DJANGO_SECRET_KEY must be set}`
- [ ] All 5 services have `deploy.resources.limits` defined
- [ ] `docker-compose config` runs successfully
- [ ] Changes committed and pushed

---

## 🎉 Summary

**What to do:**
1. ✅ Edit `.env.example` (remove hardcoded passwords)
2. ✅ Edit `docker-compose.yml` (use env vars, add resource limits)
3. ✅ Update D-001 task file (mark complete)
4. ✅ Test configuration
5. ✅ Commit and push

**Time:** 35 minutes
**Impact:** Unblocks D-002, D-006, D-007, D-008

---

## 🤝 Need Help?

**Stuck on something?** Let me know!

**Want me to review before you commit?** Send me the files!

**Not sure about resource limits?** We can decide together what values make sense!

**You got this!** 🚀

Once D-001 is done, we can start D-002 (database migrations) and then implement those awesome new models (D-006, D-007, D-008)!

---

**Ready when you are, Gaudi!** 💪

*Let's unblock this project together!*
