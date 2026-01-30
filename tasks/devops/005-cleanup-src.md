# Task D-005: Delete Obsolete src/ Directory

**Assigned To:** DevOps (Karen)
**Priority:** P1 (HIGH)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-02-03 5:00 PM
**Estimated Time:** 15 minutes
**Dependencies:** D-003, C-001, C-002, C-003 (All migration work complete)

---

## Overview
Remove the obsolete `src/` directory from the repository after all migration work is complete and verified.

## Context
The root `src/` directory contains the OLD backend structure that is no longer needed. All functionality has been moved to `apps/backend/`. This is the final cleanup step.

**⚠️ CRITICAL:** This is IRREVERSIBLE (except from backup). Get explicit approval from Architect before proceeding.

## Acceptance Criteria
- [ ] Explicit approval from Architect received
- [ ] All coders confirm their apps work
- [ ] All tests passing (backend, frontend, integration)
- [ ] `src/` removed from git (git rm)
- [ ] `src/` removed from filesystem
- [ ] Git clean (no untracked src/ files)
- [ ] Changes committed and pushed
- [ ] Backup verified and accessible

## Prerequisites
- [ ] ✅ D-001 (Backup exists and verified)
- [ ] ✅ D-003 (Directory reorganization complete)
- [ ] ✅ C-001 (Backend path fixes complete)
- [ ] ✅ C-002 (Frontend path fixes complete)
- [ ] ✅ C-003 (Integration tests passing)
- [ ] ✅ Architect approval obtained

## Implementation Steps

### Step 1: Final Verification
```bash
# Ask Architect for approval:
# "Are we absolutely sure we don't need anything in src/?"

# Verify backup exists
ls -la backups/src-backup-*/

# Verify all tests pass
cd apps/backend && python manage.py test && cd ../..
cd apps/frontend && npm test && cd ../..

# Verify integration tests pass
# (from C-003)
```

### Step 2: Get Architect Approval
**Send this message to Architect:**
```markdown
## Final Verification Complete - Ready to Delete src/

**Task:** D-005
**Status:** Ready for deletion

### Verification Complete:
- ✅ Backup exists: backups/src-backup-[DATE]/
- ✅ Backend tests passing
- ✅ Frontend tests passing
- ✅ Integration tests passing
- ✅ All path fixes complete
- ✅ No references to src/ in code

### Ready to Delete:
- Directory: /Users/sergi/Desktop/Projects/FinanceHub/src/
- Files: [NUMBER] files
- Backup: [BACKUP_LOCATION]

### Architect Approval Needed:
Please confirm: "Proceed with deletion" or "Stop, I need something"

### Safety:
If deletion fails, can restore with:
```bash
cp -r backups/src-backup-[DATE]/ src/
```
```

### Step 3: Remove from Git
```bash
# Only after Architect approval!

# Remove from git tracking
git rm -r src/

# Verify removal
git status
# Should show: deleted: src/...
```

### Step 4: Remove from Filesystem
```bash
# Remove from filesystem
rm -rf src/

# Verify removal
ls -la | grep src
# Should return nothing

# Verify git clean
git status
# Should show no untracked src/ files
```

### Step 5: Final Commit
```bash
# Commit deletion
git commit -m "refactor: remove obsolete src/ directory

- Old backend structure (pre-monorepo)
- All functionality now in apps/backend/
- Backup stored in backups/src-backup-[DATE]/
- All migration work complete and verified

Safety: Can restore from backup if needed"

# Push to GitHub
git push
```

### Step 6: Update Backup README
```bash
# Mark backup as "keep for 30 days"
cat >> backups/src-backup-[DATE]/README.md << 'EOF'

## Deletion Date: [CURRENT DATE]
## Keep Until: [DATE + 30 days]

After 30 days with no issues, this backup can be deleted.
EOF
```

## Verification
```bash
# Verify src/ is gone
ls -la | grep src
# Expected: (no output)

# Verify git status clean
git status
# Expected: nothing to commit

# Verify apps work
cd apps/backend && python manage.py check && cd ../..
cd apps/frontend && npm run build && cd ../..

# Verify on GitHub
# - No src/ directory visible
# - Only apps/backend and apps/frontend
```

## Files Deleted
- [ ] `src/` - Entire directory and contents

## Rollback Plan
⚠️ **IRREVERSIBLE** except from backup

If catastrophic failure:
```bash
# Emergency restore
cd /Users/sergi/Desktop/Projects/FinanceHub
cp -r backups/src-backup-[DATE]/ src/

# Verify restored
ls -la src/

# Report to Architect immediately
```

## Tools to Use
- **MCP:** bash commands, git operations
- **Manual:** Architect approval (conversation)

## Dependencies
- ✅ D-001 (Backup verified)
- ✅ D-003 (Reorganization complete)
- ✅ C-001 (Backend fixes)
- ✅ C-002 (Frontend fixes)
- ✅ C-003 (Integration tests passing)
- ✅ Architect approval

## Feedback to Architect
[After completion, report final status]

### What I Did:
- Received explicit approval: [APPROVAL MESSAGE]
- Removed src/ from git tracking
- Removed src/ from filesystem
- Committed deletion with detailed message
- Updated backup README with keep-until date

### Final Status:
- ✅ src/ directory deleted
- ✅ Git status clean
- ✅ All apps still working
- ✅ Backup preserved

### Migration Complete:
Monorepo migration successfully completed! All tasks D-001 through D-005 finished.

### Next Steps:
- Monitor for 30 days
- Delete backup after [DATE + 30 days] if no issues

## Updates
- **2026-01-30 09:00:** Task created, status PENDING (waiting on all dependencies)
- **[YYYY-MM-DD HH:MM]:** [Update when ready for deletion]
- **[YYYY-MM-DD HH:MM]:** [Update after deletion complete]

---
**Last Updated:** 2026-01-30
**Note:** This is the FINAL task of the monorepo migration
