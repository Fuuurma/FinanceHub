# Task C-001: Fix Backend Path References

**Assigned To:** Coder(s) - Backend focus (2 coders recommended)
**Priority:** P0 (CRITICAL)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-01-31 5:00 PM
**Estimated Time:** 4 hours
**Dependencies:** D-003 (Directory reorganization complete)

---

## Overview
Update all backend code to use new monorepo paths (`apps/backend/` instead of `Backend/`).

## Context
After moving `Backend/` to `apps/backend/`, all internal path references need updating. This includes Django settings, imports, Docker configs, and management commands.

**Path Changes:**
- `Backend/` → `apps/backend/`
- `Backend/src/` → `apps/backend/src/`

## Acceptance Criteria
- [ ] All imports updated to new paths
- [ ] Django settings paths corrected
- [ ] Management commands work
- [ ] Docker configurations updated
- [ ] Django check passes with no errors
- [ ] All tests pass
- [ ] Backend server starts successfully
- [ ] No "Module not found" errors

## Prerequisites
- [ ] D-003 complete (directories moved)
- [ ] Python environment activated
- [ ] Access to `apps/backend/` directory

## Implementation Steps

### Step 1: Find All Path References
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend

# Search for old paths in Python files
grep -r "Backend" --include="*.py" . 2>/dev/null

# Search for old paths in config files
grep -r "Backend" --include="*.yml" --include="*.yaml" --include="*.json" . 2>/dev/null

# Document all findings
grep -r "Backend" . > backend-paths-to-fix.txt
```

### Step 2: Update Django Settings
```bash
# Edit settings.py
nano src/core/settings.py

# Update these paths if they reference Backend:
"""
# STATIC_ROOT
# STATICFILES_DIRS
# MEDIA_ROOT
# MEDIA_URL
# TEMPLATES
# DATABASE (if using SQLite for testing)

# Example changes:
STATIC_ROOT = BASE_DIR / 'static'  # was Backend/static
MEDIA_ROOT = BASE_DIR / 'media'     # was Backend/media
"""
```

### Step 3: Fix Import Statements
```bash
# Find all imports referencing old paths
grep -rn "from Backend" src/
grep -rn "import Backend" src/

# Replace imports (automated where safe)
# BE CAREFUL: Review each replacement

# Common patterns:
# from Backend.src.apps.X → from apps.X
# from Backend.src.core → from core
# (Most imports should be relative now)
```

### Step 4: Update Management Commands
```bash
# Find management commands
find src/ -name "management/commands/*.py"

# Check for hardcoded paths
grep -n "Backend" src/**/management/commands/*.py

# Update working directory references if any
```

### Step 5: Update Docker Configuration
```bash
# Update Dockerfile (if using WORKDIR)
nano Dockerfile

# Change:
# WORKDIR /app/Backend → WORKDIR /app
# (or adjust based on new structure)

# Update docker-compose.yml (if backend-specific)
# Should be handled by DevOps, but verify
```

### Step 6: Update ASGI/Daphne Config
```bash
# Check ASGI configuration
cat src/daphne_config.py

# Update paths if hardcoded
# Most should be relative to BASE_DIR
```

### Step 7: Update Environment Variables
```bash
# Check .env.example
cat .env.example

# Update any Backend/ references
# PYTHONPATH if needed
```

### Step 8: Test Backend
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend

# Run Django system check
python manage.py check

# Expected: No errors
# If errors: Fix and re-run

# Run migrations check
python manage.py makemigrations --check

# Run tests
python manage.py test

# Start server manually to verify
python manage.py runserver

# Expected: Server starts without errors
```

### Step 9: Fix Remaining Issues
```bash
# For any remaining issues:
1. Read the error message carefully
2. Find the file with the issue
3. Update the path reference
4. Re-test

# Common issues:
# - Import errors: Fix imports
# - Template not found: Fix TEMPLATES setting
# - Static file not found: Fix STATIC_ROOT
# - Migration issues: Fix database path (if SQLite)
```

### Step 10: Commit Changes
```bash
git add .
git status  # Review changes

git commit -m "refactor: update backend paths for monorepo structure

- Update Django settings paths
- Fix import statements
- Update management commands
- Fix Docker configurations
- All tests passing

Part of monorepo migration."

git push
```

## Testing

### Automated Tests:
```bash
cd apps/backend

# 1. Django check
python manage.py check
# Expected: 0 errors

# 2. Migrations check
python manage.py makemigrations --check
# Expected: No new migrations needed

# 3. Run tests
python manage.py test
# Expected: All tests pass

# 4. Start server
python manage.py runserver
# Expected: Server starts, no import errors
```

### Manual Verification:
```bash
# Test in browser
# http://localhost:8000/admin
# http://localhost:8000/api/

# Verify:
# - Admin panel loads
# - API endpoints respond
# - No console errors
```

## Files Modified
- [ ] `apps/backend/src/core/settings.py` - Path updates
- [ ] `apps/backend/src/daphne_config.py` - Path updates
- [ ] `apps/backend/Dockerfile` - WORKDIR updates
- [ ] `apps/backend/.env.example` - Path references
- [ ] Various import statements - Path fixes

## Code Quality Checklist
- [ ] Django check passes (0 errors)
- [ ] All tests pass
- [ ] Server starts successfully
- [ ] No import errors
- [ ] No "Module not found" errors
- [ ] Admin panel accessible
- [ ] API endpoints work

## Rollback Plan
```bash
# If changes break everything:
git reset --hard HEAD
git checkout [previous-commit]

# Start over with careful review of each change
```

## Tools to Use
- **MCP:** File operations, grep for searching, bash commands
- **Skills:** python-helpers (if available)
- **Reference:** Django documentation for path settings

## Dependencies
- ✅ D-003 (Directory reorganization)

## Feedback to Architect
[After completing, report using this format]

### What I Did:
- Updated Django settings (STATIC_ROOT, MEDIA_ROOT, etc.)
- Fixed import statements ([N] files)
- Updated management commands
- Fixed Docker configurations
- Tested all changes

### Testing:
- ✅ Django check: PASSED (0 errors)
- ✅ Migrations check: PASSED
- ✅ Tests: PASSED ([N] passing)
- ✅ Server start: PASSED
- ✅ Admin panel: ACCESSIBLE
- ✅ API endpoints: WORKING

### What I Discovered:
- [N] files needed path updates
- No unexpected issues
- All imports resolved correctly

### Files Modified:
- `src/core/settings.py` - Updated paths
- [List all modified files]

### Ready for Next Step:
Backend paths fixed. Ready for Task C-002 (Frontend paths) or C-003 (Integration testing).

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when start working]
- **[YYYY-MM-DD HH:MM]:** [Update when complete]

---
**Last Updated:** 2026-01-30
**Next Task:** C-002 (Fix Frontend Path References)
