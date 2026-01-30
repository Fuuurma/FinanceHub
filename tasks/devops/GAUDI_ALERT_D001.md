# 🚨 GAUDI: START D-001 IMMEDIATELY

## Priority: P0 - CRITICAL SECURITY

**Assigned to:** Gaudi  
**Task:** Infrastructure Security & Configuration  
**Deadline:** Today

---

## ⚠️ URGENT: Security Vulnerabilities Active

The FinanceHub project has **CRITICAL security issues** that must be fixed NOW:

### Current Vulnerabilities

| Issue | File | Line | Risk Level |
|-------|------|------|------------|
| Hardcoded PostgreSQL password | `docker-compose.yml` | 11 | 🔴 CRITICAL |
| Weak Django secret key fallback | `docker-compose.yml` | 50 | 🔴 CRITICAL |
| No Docker build exclusion | `.dockerignore` | Missing | 🟠 HIGH |
| No container resource limits | `docker-compose.yml` | All services | 🟠 HIGH |

---

## 📋 Tasks to Complete (D-001)

### 1. Fix Hardcoded PostgreSQL Password (5 minutes)

**File:** `docker-compose.yml:11`

```yaml
# CURRENT (INSECURE)
POSTGRES_PASSWORD: financehub_dev_password

# FIXED
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}
```

### 2. Fix Django Secret Key (5 minutes)

**File:** `docker-compose.yml:50`

```yaml
# CURRENT (INSECURE)
DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-django-insecure-dev-key-change-in-production}

# FIXED
DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:?DJANGO_SECRET_KEY must be set}
```

### 3. Create .dockerignore (10 minutes)

**File:** `.dockerignore` (create at project root)

```dockerfile
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
env/
.venv/
*.egg-info/
dist/
build/

# Testing
.pytest_cache
.coverage
htmlcov/
.tox/
.nox/

# IDE
.vscode
.idea
*.swp
*.swo
*~

# Django
db.sqlite3
media/
staticfiles/

# Node
node_modules/

# Next.js
.next/
out/

# Secrets
.env
.env.local
.env.*.local
*.pem
*.key
*.crt

# Docs
*.md
!README.md
docs/
architecture/

# OS
.DS_Store
Thumbs.db
*.log

# Project specific
backups/
*.dump
.pytest_cache/
htmlcov/
.coverage
```

### 4. Create .env.example (5 minutes)

**File:** `.env.example` (create at project root)

```bash
# FinanceHub Environment Variables
# Copy this file to .env and fill in the values

# Database
POSTGRES_PASSWORD=your_strong_password_here_min_32_chars
DATABASE_URL=postgres://financehub:your_password@postgres:5432/finance_hub

# Redis
REDIS_PASSWORD=your_redis_password
REDIS_URL=redis://redis:6379/0

# Django
DJANGO_SECRET_KEY=your_django_secret_key_min_50_chars_random_string
DJANGO_SETTINGS_MODULE=core.settings

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

# API Keys (get from providers)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key
# ... add other API keys

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# AWS (optional for deployment)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

### 5. Add Resource Limits to Docker (10 minutes)

**File:** `docker-compose.yml`

Add to each service:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

---

## 📁 Files to Create/Modify

| File | Action |
|------|--------|
| `.dockerignore` | Create |
| `.env.example` | Create |
| `docker-compose.yml` | Modify |

---

## ✅ Verification Commands

Run these after completing each task:

```bash
# 1. Verify no hardcoded passwords
grep -r "financehub_dev_password" . --include="*.yml" --include="*.yaml"
# Should return: grep: .: Is a directory (no matches)

# 2. Verify .dockerignore exists
ls -la .dockerignore

# 3. Verify .env.example exists
ls -la .env.example

# 4. Test Docker Compose loads correctly
docker-compose config > /dev/null && echo "✓ docker-compose.yml is valid"

# 5. Verify resource limits (after adding)
docker-compose config | grep -A 10 "resources:"
```

---

## ⏱️ Time Estimate

| Task | Time |
|------|------|
| Fix PostgreSQL password | 5 min |
| Fix Django secret key | 5 min |
| Create .dockerignore | 10 min |
| Create .env.example | 5 min |
| Add resource limits | 10 min |
| **Total** | **~35 minutes** |

---

## 🎯 Success Criteria

- [ ] No hardcoded passwords in repository
- [ ] `.dockerignore` reduces Docker build context
- [ ] `.env.example` provides template for environment
- [ ] All services have CPU/memory limits
- [ ] Docker Compose validates without errors

---

## 📞 Report Progress

When complete, run:

```bash
# Show modified files
git status

# Show specific changes to docker-compose.yml
git diff docker-compose.yml

# Verify files exist
ls -la .dockerignore .env.example
```

**Message: "D-001 COMPLETE" when done.**

---

**Started:** Jan 30, 2026 20:30  
**Expected Completion:** Today
