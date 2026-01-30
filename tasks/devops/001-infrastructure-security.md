---
title: "DevOps Infrastructure Security & Configuration"
status: pending
priority: p0
estimate: "2 days"
created: "2026-01-30"
assigned_to: gaudi
---

## Summary

Fix critical infrastructure security issues identified in INFRASTRUCTURE_ANALYSIS.md. These are P0 issues that must be fixed immediately.

## Issues to Fix

### P0 - Critical Security

#### 1. Remove Hardcoded Development Secrets

**File:** `docker-compose.yml:11`

```yaml
# CURRENT (BROKEN)
POSTGRES_PASSWORD: financehub_dev_password
```

**Fix:**
```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}
```

**Also create `.env.example`:**
```bash
POSTGRES_PASSWORD=your_complex_password_here
REDIS_PASSWORD=your_redis_password
DJANGO_SECRET_KEY=your_django_secret_key_min_50_chars
ALPHA_VANTAGE_API_KEY=your_api_key
# ... other secrets
```

**Verification:**
```bash
# Test that docker-compose fails without .env
rm .env
docker-compose config  # Should fail
```

#### 2. Fix Django Secret Key Fallback

**File:** `docker-compose.yml`

```yaml
# CURRENT (BROKEN)
DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-django-insecure-dev-key-change-in-production}
```

**Fix:**
```yaml
DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:?DJANGO_SECRET_KEY must be set}
```

**Impact:** The old fallback allowed production deployment with weak development key.

#### 3. Create .dockerignore File

**File:** `.dockerignore` (create at project root)

**Content:**
```
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

# Testing
.pytest_cache
.coverage
htmlcov/
.coverage

# IDE
.vscode
.idea
*.swp
*.swo

# Django
db.sqlite3
media/

# Node
node_modules/

# Next.js
.next/
out/

# Secrets
.env
.env.local
*.pem
*.key

# Docs
*.md
!README.md

# OS
.DS_Store
Thumbs.db
```

**Impact:** Reduces Docker build context size significantly.

#### 4. Add Resource Limits to Docker Compose

**File:** `docker-compose.yml`

**Add to each service:**
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

  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

## Files to Modify

1. `docker-compose.yml` - Secrets and resource limits
2. `.env.example` - Create new file
3. `.dockerignore` - Create new file

## Files to Create

1. `.env.example` - Template for environment variables
2. `.dockerignore` - Build context exclusion

## Testing

```bash
# Verify secrets are not hardcoded
grep -r "financehub_dev_password" . --include="*.yml" --include="*.yaml"
# Should return nothing after fix

# Verify .dockerignore works
docker build -t test . --progress=plain
# Check build context size

# Verify resource limits
docker-compose config | grep -A 10 "resources:"
```

## Success Criteria

1. ✅ No hardcoded passwords in docker-compose.yml
2. ✅ Docker Compose fails without required env vars
3. ✅ .dockerignore reduces build context
4. ✅ All services have resource limits

## Related Issues

- Part of INFRASTRUCTURE_ANALYSIS.md (Issues 1, 2, 14)
