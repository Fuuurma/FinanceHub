# Task S-008: Docker Base Image Security Update

**Task ID:** S-008
**Assigned To:** Karen (DevOps) + Charo (Security)
**Priority:** 🔴 P0 CRITICAL
**Status:** ⏳ PENDING
**Created:** January 31, 2026
**Estimated Time:** 2-3 hours
**Deadline:** February 2, 2026 (48 hours)

---

## 🚨 CRITICAL SECURITY ISSUE

### Vulnerability Summary
**Source:** Trivy Docker Scan (January 30, 2026)
**Scan Results:** `docs/security/DOCKER_SCAN_RESULTS_20260130.md`

| Severity | Count | Status |
|----------|-------|--------|
| **CRITICAL** | 4 | 🔴 FIX IMMEDIATELY |
| **HIGH** | 7 | 🟠 URGENT |
| **MEDIUM** | 12 | 🟡 SCHEDULED |
| **LOW** | 28 | 🟢 MONITOR |

**Root Cause:** Outdated Python base image (`python:3.11-slim-bullseye`)

---

## Current State

### Backend Dockerfile
**File:** `apps/backend/Dockerfile`

**Current (VULNERABLE):**
```dockerfile
FROM python:3.11-slim-bullseye
# OpenSSL 3.0.2 (CRITICAL-4, HIGH-7 vulnerabilities)
# Other outdated system packages
```

**Issues:**
- OpenSSL 3.0.2 has 4 CRITICAL, 7 HIGH vulnerabilities
- bullseye (Debian 11) packages outdated
- Security patches not backported

---

## Target State

### Updated Dockerfile
**File:** `apps/backend/Dockerfile`

**Target (SECURE):**
```dockerfile
FROM python:3.11-slim-bookworm
# Debian 12 (bookworm) with latest security patches
# OpenSSL 3.0.x (latest version)
# All security fixes applied
```

---

## Implementation Steps

### Step 1: Update Backend Dockerfile (30 min)

**File:** `apps/backend/Dockerfile`

**Change:**
```diff
- FROM python:3.11-slim-bullseye
+ FROM python:3.11-slim-bookworm
```

**Full updated Dockerfile:**
```dockerfile
# Build stage
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

### Step 2: Update docker-compose.yml (15 min)

**File:** `docker-compose.yml`

**No changes needed** - Docker Compose will pull new image automatically.

**Optional: Add explicit version:**
```yaml
services:
  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: "3.11-slim-bookworm"
```

---

### Step 3: Build and Test (30 min)

```bash
# Build new image
docker-compose build backend

# Check build output for vulnerabilities (should see reduction)
docker images | grep financehub-backend

# Test locally
docker-compose up -d backend

# Check logs
docker-compose logs backend

# Verify application works
curl http://localhost:8000/health/
```

---

### Step 4: Run Security Scan (30 min)

```bash
# Run Trivy scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  --severity CRITICAL,HIGH \
  financehub-backend:latest

# Expected results:
# - CRITICAL: 0 (down from 4)
# - HIGH: 0-2 (down from 7)
# - All OpenSSL vulnerabilities FIXED
```

---

### Step 5: Update CI/CD Pipeline (30 min)

**File:** `.github/workflows/deploy.yml`

**Add Docker image scanning:**
```yaml
- name: Build Docker image
  run: docker-compose build backend

- name: Scan for vulnerabilities
  run: |
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy image \
      --exit-code 1 \
      --severity CRITICAL,HIGH \
      financehub-backend:latest

- name: Deploy if scan passes
  if: success()
  run: echo "Deploying..."
```

---

### Step 6: Deploy and Monitor (30 min)

```bash
# Deploy to production
git add .
git commit -m "fix(security): update Docker base to bookworm (S-008)"
git push origin main

# Monitor deployment
docker-compose ps
docker-compose logs -f backend

# Verify health check
curl https://api.financehub.app/health/
```

---

### Step 7: Verify Fix (30 min)

**Run full security scan:**
```bash
./scripts/security/scan.sh

# Expected improvements:
# - Backend CRITICAL: 0 (was 4)
# - Backend HIGH: 0-2 (was 7)
# - Overall security score: B+ (was C)
```

---

## Acceptance Criteria

- [ ] Backend Dockerfile updated to `python:3.11-slim-bookworm`
- [ ] Image builds successfully
- [ ] All tests pass locally
- [ ] Trivy scan shows 0 CRITICAL vulnerabilities
- [ ] Trivy scan shows < 2 HIGH vulnerabilities
- [ ] Health check passes
- [ ] CI/CD pipeline includes vulnerability scan
- [ ] Deployment successful
- [ ] Application stable for 24 hours

---

## Rollback Plan

If deployment fails:

```bash
# Quick rollback (5 min)
git revert HEAD
git push origin main

# Rebuild with old image
docker-compose build backend
docker-compose up -d backend
```

**Alternative: Tag specific working version:**
```dockerfile
FROM python:3.11-slim-bullseye@sha256:<working-hash>
```

---

## Testing Checklist

### Pre-Deployment
- [ ] Build image locally
- [ ] Run `docker-compose up`
- [ ] Check health endpoint
- [ ] Run integration tests
- [ ] Run Trivy scan

### Post-Deployment
- [ ] Monitor error logs (should not increase)
- [ ] Check response times (should not change)
- [ ] Verify database connections
- [ ] Check Redis connectivity
- [ ] Monitor memory usage (should be similar)

---

## Impact Analysis

### Expected Benefits
- ✅ **Security:** Eliminate 4 CRITICAL, 7 HIGH vulnerabilities
- ✅ **Compliance:** Meet security standards
- ✅ **Stability:** Latest Debian patches
- ✅ **Performance:** Same or better (bookworm optimized)

### Potential Risks
- ⚠️ **Compatibility:** Unlikely (Python 3.11 compatible)
- ⚠️ **Downtime:** < 5 minutes (rolling deploy)
- ⚠️ **Dependencies:** All tested with bookworm

**Mitigation:** Test in staging first, rolling deployment

---

## Communication

### Before Deployment
- [ ] Notify team of planned security update
- [ ] Schedule maintenance window (if needed)
- [ ] Prepare rollback plan

### During Deployment
- [ ] Monitor deployment logs
- [ ] Check health endpoint continuously
- [ ] Be ready to rollback

### After Deployment
- [ ] Confirm all services healthy
- [ ] Run full security scan
- [ ] Update documentation
- [ ] Notify team of success

---

## Success Metrics

| Metric | Before | Target | After |
|--------|--------|--------|-------|
| CRITICAL vulnerabilities | 4 | 0 | _ |
| HIGH vulnerabilities | 7 | < 2 | _ |
| Security score | C (74) | B+ (80+) | _ |
| Build time | ~5 min | ~5 min | _ |
| Image size | ~500MB | ~500MB | _ |

---

## References

- **Scan Results:** `docs/security/DOCKER_SCAN_RESULTS_20260130.md`
- **Docker Hub:** https://hub.docker.com/_/python
- **Debian Bookworm:** https://wiki.debian.org/DebianBookworm
- **OpenSSL 3.0:** https://www.openssl.org/

---

## Questions for GAUDÍ

1. **Approval:** Should I proceed with S-008 (Docker base image update)?
2. **Timing:** Deploy immediately or schedule maintenance window?
3. **Scope:** Update frontend Dockerfile too (Node base image)?

---

**Task S-008 Created: Awaiting Approval**

**Priority:** 🔴 P0 CRITICAL - 4 CRITICAL, 7 HIGH vulnerabilities
**Deadline:** February 2, 2026 (48 hours)
**Impact:** Security score C (74) → B+ (80+)

---

**Recommended Action:** APPROVE and DEPLOY IMMEDIATELY
