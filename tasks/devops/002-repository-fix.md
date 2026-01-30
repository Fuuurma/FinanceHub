# Task D-002: Fix Git Repository Configuration

**Assigned To:** DevOps (Karen)
**Priority:** P0 (CRITICAL)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-01-30 2:00 PM
**Estimated Time:** 1 hour
**Dependencies:** D-001 (Backup must be complete)

---

## Overview
Create a new monorepo GitHub repository and migrate from `FinanceHub-Backend` to `FinanceHub`. This establishes the correct repository structure for our monorepo.

## Context
Current repository still points to `FinanceHub-Backend` (the old backend-only repo). We need a new `FinanceHub` repository that reflects the monorepo structure with both backend and frontend.

**Why:**
- Current repo name doesn't match monorepo structure
- Need clean slate for monorepo migration
- Old repo should be archived (not deleted)

## Acceptance Criteria
- [ ] New repository `FinanceHub` created on GitHub
- [ ] Git remote updated to point to new repo
- [ ] All code pushed to new repository
- [ ] Old repository `FinanceHub-Backend` archived
- [ ] `README.md` updated with new repo URL
- [ ] All branches verified

## Prerequisites
- [ ] Task D-001 complete (backup verified)
- [ ] GitHub account access
- [ ] Current repo is clean (committed changes)

## Implementation Steps

### Step 1: Check Current Git Configuration
```bash
# View current remote
git remote -v
# Expected: https://github.com/Fuuurma/FinanceHub-Backend.git

# View current branches
git branch -a

# Check for uncommitted changes
git status
```

### Step 2: Create New GitHub Repository (MANUAL)
**Do this in your browser:**

1. Go to: https://github.com/new
2. Repository name: `FinanceHub`
3. Description: "Financial platform (Bloomberg Terminal-inspired) - Monorepo with Django backend and Next.js frontend"
4. Visibility: [Choose Private/Public based on your preference]
5. ⚠️ **DO NOT** initialize with README (we have one)
6. ⚠️ **DO NOT** add .gitignore (we have one)
7. ⚠️ **DO NOT** add license (we have one)
8. Click "Create repository"
9. Copy the new repository URL: `https://github.com/Fuuurma/FinanceHub.git`

### Step 3: Update Git Remote
```bash
# Update remote URL
git remote set-url origin https://github.com/Fuuurma/FinanceHub.git

# Verify change
git remote -v
# Expected: https://github.com/Fuuurma/FinanceHub.git
```

### Step 4: Push to New Repository
```bash
# Ensure we're on main branch
git branch -M main

# Push all branches and tags
git push -u origin main
git push --all
git push --tags

# Verify push
git log --oneline -5
```

### Step 5: Verify Repository
```bash
# Check GitHub to verify:
# - All files present
# - All branches present
# - README.md visible
# - Git history intact

# Locally verify
git fetch --all
git branch -a
```

### Step 6: Archive Old Repository (MANUAL)
**Do this on GitHub:**

1. Go to: https://github.com/Fuuurma/FinanceHub-Backend/settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility"
4. Change to "Archive" or make private
5. ⚠️ **DO NOT DELETE** - Keep for historical reference

### Step 7: Update README.md
```bash
# Edit README.md
nano README.md

# Update repository URL section:
# Old: https://github.com/Fuuurma/FinanceHub-Backend.git
# New: https://github.com/Fuuurma/FinanceHub.git

# Add monorepo note:
"""
## Repository Structure

This is a **monorepo** containing:
- **Backend:** Django/Python REST API (`apps/backend/`)
- **Frontend:** Next.js TypeScript UI (`apps/frontend/`)
"""
```

## Verification
```bash
# Verify remote updated
git remote -v
# Should show: https://github.com/Fuuurma/FinanceHub.git

# Verify push worked
git log --oneline -3

# Verify all branches
git branch -a

# Visit GitHub and verify:
# - All files present
# - History intact
# - README displays correctly
```

## Files Modified
- [ ] `.git/config` - Git remote URL
- [ ] `README.md` - Repository URLs and structure

## Rollback Plan
If something goes wrong:
```bash
# Revert to old remote
git remote set-url origin https://github.com/Fuuurma/FinanceHub-Backend.git

# Verify
git remote -v
```

## Tools to Use
- **MCP:** None - this is manual GitHub work
- **GitHub Skill:** Use github skill if available for repo management
- **Manual:** GitHub web interface

## Dependencies
- ✅ D-001 (Backup complete) - Must be complete first

## Feedback to Architect
[After completing, report using this format]

### What I Did:
- Created new GitHub repository: `FinanceHub`
- Updated git remote to new repo
- Pushed all branches and tags
- Archived old `FinanceHub-Backend` repository
- Updated README.md with new URLs

### What I Discovered:
- New repo URL: https://github.com/Fuuurma/FinanceHub.git
- Old repo archived (not deleted)
- All [N] branches migrated successfully
- Git history intact (commits preserved)

### Evidence:
- Git remote output: [PASTE]
- GitHub screenshot: [ATTACH]
- Branch list: [PASTE]

### Ready for Next Step:
Git repository fixed. Ready for Task D-003 (Rename Directories).

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when you start working]
- **[YYYY-MM-DD HH:MM]:** [Update when complete]

---
**Last Updated:** 2026-01-30
**Next Task:** D-003 (Rename Directories to Monorepo Structure)
