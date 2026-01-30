# Task D-004: Update CI/CD Pipelines

**Assigned To:** DevOps (Karen)
**Priority:** P1 (HIGH)
**Status:** ✅ COMPLETED
**Created:** 2026-01-30
**Deadline:** 2026-02-02 5:00 PM
**Estimated Time:** 2 hours
**Dependencies:** D-003 (Directory reorganization complete)

---

## Overview
Update all CI/CD workflow files and deployment scripts to use new monorepo paths (`apps/backend/`, `apps/frontend/`).

## Context
After moving directories, all automated pipelines need path updates. This ensures CI/CD continues to work seamlessly.

**Files to Update:**
- `.github/workflows/*.yml` - GitHub Actions workflows
- Deployment scripts (if any)
- Environment configurations
- Docker build contexts

## Acceptance Criteria
- [ ] All GitHub Actions workflows updated
- [ ] Backend workflow tests successfully
- [ ] Frontend workflow tests successfully
- [ ] Docker build paths correct
- [ ] Environment variables updated
- [ ] Workflows committed and tested

## Prerequisites
- [ ] D-003 complete (directories reorganized)
- [ ] Access to GitHub repository settings

## Implementation Steps

### Step 1: Identify All CI/CD Files
```bash
# Find workflow files
find .github/workflows -name "*.yml" -o -name "*.yaml"

# Find deployment scripts
find . -name "*deploy*.sh" -o -name "*deploy*.yml"

# Find Docker-related configs
find . -name "docker-compose*.yml" -o -name "Dockerfile*"
```

### Step 2: Update GitHub Actions Workflows
```bash
# List all workflows
ls -la .github/workflows/

# For each workflow file, update paths:
# Backend workflows:
# - ./Backend/src → ./apps/backend/src
# - ./Backend → ./apps/backend

# Frontend workflows:
# - ./Frontend/src → ./apps/frontend/src
# - ./Frontend → ./apps/frontend

# Example workflow update:
# jobs:
#   backend-test:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v3
#       - name: Test Backend
#         run: |
#           cd apps/backend
#           python manage.py test
```

### Step 3: Update Docker Build Contexts
```bash
# Update docker-compose.yml
# Check build contexts and volumes

# Example changes:
# services:
#   backend:
#     build:
#       context: ./apps/backend  # was ./Backend
#       dockerfile: Dockerfile
#     volumes:
#       - ./apps/backend:/app    # was ./Backend
#
#   frontend:
#     build:
#       context: ./apps/frontend  # was ./Frontend
#       dockerfile: Dockerfile
#     volumes:
#       - ./apps/frontend:/app    # was ./Frontend
```

### Step 4: Test Workflows Locally
```bash
# Test Docker compose builds
docker-compose build backend
docker-compose build frontend

# Verify build succeeds
docker-compose ps
```

### Step 5: Commit Updates
```bash
# Stage workflow changes
git add .github/workflows/
git add docker-compose.yml
git add Dockerfile*

# Review changes
git diff --cached

# Commit
git commit -m "ci: update CI/CD pipelines for monorepo structure

- Update GitHub Actions workflow paths
- Update Docker build contexts
- Update volume mount paths
- Test builds successfully"

# Push
git push
```

### Step 6: Verify on GitHub
```bash
# Visit GitHub Actions tab
# Trigger a workflow run manually
# Verify it completes successfully
```

## Verification
```bash
# Verify workflow syntax
yamllint .github/workflows/*.yml

# Verify Docker compose
docker-compose config

# Check for any remaining old paths
grep -r "Backend/\|Frontend/" .github/workflows/
grep -r "Backend/\|Frontend/" docker-compose.yml
# Should return nothing
```

## Files Modified
- [ ] `.github/workflows/*.yml` - Path updates
- [ ] `docker-compose.yml` - Build context updates
- [ ] Any deployment scripts - Path updates

## Rollback Plan
```bash
# If workflows fail:
git reset --hard HEAD~1

# Fix issues and try again
```

## Tools to Use
- **MCP:** File operations, bash commands
- **GitHub:** Manual workflow testing on GitHub

## Dependencies
- ✅ D-003 (Directories reorganized)

## Feedback to Architect
[Report completion with workflow run links]

---
**Last Updated:** 2026-01-30
