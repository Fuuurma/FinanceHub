# Task D-003: Rename Directories to Monorepo Structure

**Assigned To:** DevOps (Karen)
**Priority:** P0 (CRITICAL)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-01-31 12:00 PM
**Estimated Time:** 2 hours
**Dependencies:** D-002 (Git repository must be updated)

---

## Overview
Reorganize the repository structure to match monorepo best practices. Move `Backend/` and `Frontend/` into `apps/` directory.

## Context
To establish a clear monorepo structure, we need to organize our applications under an `apps/` directory. This makes it explicit that we have multiple applications in one repository.

**Current Structure:**
```
FinanceHub/
├── Backend/        ← Django backend
├── Frontend/       ← Next.js frontend
├── src/            ← Old backend (to be deleted later)
└── [root files]
```

**Target Structure:**
```
FinanceHub/
├── apps/
│   ├── backend/    ← Move Backend/ here
│   └── frontend/   ← Move Frontend/ here
├── [root files]
```

## Acceptance Criteria
- [ ] `apps/` directory created
- [ ] `Backend/` moved to `apps/backend/` via git mv
- [ ] `Frontend/` moved to `apps/frontend/` via git mv
- [ ] No `Backend/` or `Frontend/` directories at root
- [ ] Docker configuration files updated
- [ ] `.gitignore` updated if needed
- [ ] Changes committed and pushed
- [ ] Architect notified

## Prerequisites
- [ ] D-002 complete (git repo updated)
- [ ] Clean working directory (git status clean)
- [ ] All changes committed

## Implementation Steps

### Step 1: Create apps/ Directory
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Create apps directory
mkdir -p apps

# Verify creation
ls -la | grep apps
```

### Step 2: Move Backend Using Git MV
```bash
# Use git mv to preserve history
git mv Backend apps/backend

# Verify move
ls -la apps/
ls -la | grep Backend  # Should show nothing

# Check git status
git status
# Should show: renamed: Backend -> apps/backend
```

### Step 3: Move Frontend Using Git MV
```bash
# Use git mv to preserve history
git mv Frontend apps/frontend

# Verify move
ls -la apps/
ls -la | grep Frontend  # Should show nothing

# Check git status
git status
```

### Step 4: Update Docker Configuration
```bash
# Update docker-compose.yml paths
nano docker-compose.yml

# Change:
# - ./Backend -> ./apps/backend
# - ./Frontend -> ./apps/frontend

# Example changes:
# services:
#   backend:
#     build: ./apps/backend
#     volumes:
#       - ./apps/backend:/app
#
#   frontend:
#     build: ./apps/frontend
#     volumes:
#       - ./apps/frontend:/app
```

### Step 5: Move/Update Dockerfiles
```bash
# Option A: Move Dockerfiles into app directories
git mv Dockerfile.backend apps/backend/Dockerfile
git mv Dockerfile.frontend apps/frontend/Dockerfile

# Update WORKDIR in Dockerfiles:
# backend/Dockerfile: WORKDIR /app
# frontend/Dockerfile: WORKDIR /app

# Option B: Keep in config/ directory
mkdir -p config/docker
git mv Dockerfile.backend config/docker/Dockerfile.backend
git mv Dockerfile.frontend config/docker/Dockerfile.frontend

# [Choose Option A or B based on your preference]
```

### Step 6: Update .gitignore
```bash
# Check if any Backend/ or Frontend/ specific ignores exist
nano .gitignore

# Update paths if needed:
# Old:
# Backend/venv/
# Frontend/.next/

# New:
# apps/backend/venv/
# apps/frontend/.next/
```

### Step 7: Update Makefile (if exists)
```bash
# Check if Makefile has Backend/Frontend paths
grep -n "Backend\|Frontend" Makefile

# Update paths:
# Backend -> apps/backend
# Frontend -> apps/frontend
```

### Step 8: Commit the Reorganization
```bash
# Stage all changes
git add .

# Review what will be committed
git status

# Commit with detailed message
git commit -m "refactor: reorganize to monorepo structure

- Move Backend/ → apps/backend/
- Move Frontend/ → apps/frontend/
- Update Docker paths in docker-compose.yml
- Update Dockerfile locations
- Prepare for path reference updates by coders

This establishes clear monorepo structure with apps/ directory."

# Push to GitHub
git push origin main
```

### Step 9: Verify on GitHub
```bash
# Visit GitHub to verify:
# - apps/backend/ directory exists
# - apps/frontend/ directory exists
# - No Backend/ or Frontend/ at root
# - Commit history preserved
```

## Verification
```bash
# Verify new structure
ls -la apps/
# Expected: backend/ frontend/

# Verify old directories gone
ls -la | grep -E "Backend|Frontend"
# Expected: (no output)

# Verify git history
git log --oneline --follow apps/backend/README.md | head -5

# Verify commit
git log -1 --stat
```

## Files Modified
- [ ] `apps/` - Created new directory
- [ ] `apps/backend/` - Moved from Backend/
- [ ] `apps/frontend/` - Moved from Frontend/
- [ ] `docker-compose.yml` - Updated paths
- [ ] `Dockerfile.*` - Moved or updated references
- [ ] `.gitignore` - Updated paths
- [ ] `Makefile` - Updated paths (if exists)

## Rollback Plan
If something goes wrong:
```bash
# Reset to before the move
git reset --hard HEAD~1

# Verify directories restored
ls -la | grep -E "Backend|Frontend"
# Should see Backend/ and Frontend/ back

# Try again after fixing issue
```

## Tools to Use
- **MCP:** bash commands, git operations
- **Manual:** None - fully automated via git mv

## Dependencies
- ✅ D-002 (Git repository updated) - Must be complete first

## Feedback to Architect
[After completing, report using this format]

### What I Did:
- Created `apps/` directory
- Moved `Backend/` to `apps/backend/` (git mv)
- Moved `Frontend/` to `apps/frontend/` (git mv)
- Updated docker-compose.yml paths
- Updated Dockerfile locations
- Updated .gitignore paths
- Committed and pushed changes

### What I Discovered:
- [N] directories moved successfully
- Git history preserved
- Docker configs updated
- No Backend/ or Frontend/ at root

### Verification:
- ✅ apps/backend/ exists
- ✅ apps/frontend/ exists
- ✅ Old directories removed
- ✅ Commit pushed to GitHub

### Ready for Next Step:
Directory reorganization complete. Coders can now update path references (Tasks C-001, C-002).

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when you start working]
- **[YYYY-MM-DD HH:MM]:** [Update when complete]

---
**Last Updated:** 2026-01-30
**Next Task:** D-004 (Update CI/CD Pipelines)
**Dependencies Complete:** Coders need to finish path fixes before D-005 (Delete src/)
