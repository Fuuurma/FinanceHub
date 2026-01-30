# Task D-001: Backup Obsolete src/ Directory

**Assigned To:** DevOps (Karen)
**Priority:** P0 (CRITICAL - MUST BE FIRST)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-01-30 10:00 AM
**Estimated Time:** 30 minutes

---

## Overview
Create a complete backup of the obsolete `src/` directory before any deletion. This is our safety net if the migration fails.

## Context
The root `src/` directory contains the OLD backend structure (pre-monorepo). Before we delete it, we MUST have a verified backup. This is critical for risk mitigation.

**Why:**
- If migration fails, we can restore
- If we discover needed code, we can retrieve it
- For compliance and audit trail

## Acceptance Criteria
- [ ] Backup created in `backups/src-backup-YYYYMMDD/`
- [ ] Backup manifest with MD5 checksums generated
- [ ] File count verified (backup matches original)
- [ ] Backup size recorded
- [ ] README.md created in backup directory
- [ ] Architect notified of backup location

## Prerequisites
- [ ] Sufficient disk space (check with `df -h`)
- [ ] Write permissions in project root
- [ ] Git repository clean (no uncommitted changes)

## Implementation Steps

### Step 1: Prepare Backup Directory
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Create backup directory with date
BACKUP_DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/src-backup-$BACKUP_DATE"
mkdir -p "$BACKUP_DIR"

echo "Backup directory created: $BACKUP_DIR"
```

### Step 2: Copy src/ Directory
```bash
# Copy entire src/ directory
cp -r src/ "$BACKUP_DIR/"

echo "Copy completed"
```

### Step 3: Generate Backup Manifest
```bash
cd "$BACKUP_DIR"

# Generate MD5 checksums for all files
find . -type f -exec md5sum {} \; > BACKUP_MANIFEST.txt

# Count files
FILE_COUNT=$(find . -type f | wc -l)
echo "Total files: $FILE_COUNT" >> BACKUP_MANIFEST.txt

# Get backup size
BACKUP_SIZE=$(du -sh . | cut -f1)
echo "Backup size: $BACKUP_SIZE" >> BACKUP_MANIFEST.txt

cd ../..
```

### Step 4: Create Backup README
```bash
cat > "$BACKUP_DIR/README.md" << 'EOF'
# src/ Directory Backup

**Date:** $(date +%Y-%m-%d)
**Reason:** Monorepo migration - obsolete backend structure
**Location:** FinanceHub/src/ (root)
**Backup ID:** src-backup-$(date +%Y%m%d)

## What's in This Backup
- Old Django apps (assets, core, data, investments, portfolios, users, utils)
- Old manage.py
- Old migrations
- All dependencies from original structure

## To Restore (if needed):
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub
rm -rf src/
cp -r backups/src-backup-$(date +%Y%m%d)/ src/
```

## Backup Contents
$(find "$BACKUP_DIR" -type d | head -20)

## Verification
- File count: $FILE_COUNT
- Backup size: $BACKUP_SIZE
- Manifest: BACKUP_MANIFEST.txt

## Status
⚠️ **DO NOT DELETE** until migration is complete and verified (after Day 5)
EOF
```

### Step 5: Verify Backup
```bash
# Verify backup exists
ls -la "$BACKUP_DIR"

# Verify file count matches original
ORIGINAL_COUNT=$(find src/ -type f | wc -l | tr -d ' ')
BACKUP_COUNT=$(find "$BACKUP_DIR" -type f | wc -l | tr -d ' ')

echo "Original files: $ORIGINAL_COUNT"
echo "Backup files: $BACKUP_COUNT"

if [ "$ORIGINAL_COUNT" -eq "$BACKUP_COUNT" ]; then
    echo "✅ Backup verified - file counts match"
else
    echo "❌ ERROR - File counts don't match!"
    exit 1
fi

# Show backup size
du -sh "$BACKUP_DIR"
```

## Verification Commands
```bash
# Check backup integrity
cd backups/src-backup-YYYYMMDD/
md5sum -c BACKUP_MANIFEST.txt | grep -v "OK"

# Verify README exists
cat README.md

# Check backup size
du -sh .
```

## Files Created
- [ ] `backups/src-backup-YYYYMMDD/` - Backup directory
- [ ] `backups/src-backup-YYYYMMDD/BACKUP_MANIFEST.txt` - MD5 checksums
- [ ] `backups/src-backup-YYYYMMDD/README.md` - Backup documentation

## Rollback Plan
Not applicable - this is the safety mechanism. If backup fails:
```bash
# Delete failed backup
rm -rf backups/src-backup-YYYYMMDD/

# Try again
# (Re-run steps above)
```

## Tools to Use
- **MCP:** bash commands for file operations
- **Manual:** None - fully automated
- **Verification:** MD5 checksums, file counts

## Dependencies
- None (this is the first task)

## Feedback to Architect
[After completing, report using this format]

### What I Did:
- Created backup directory: `backups/src-backup-[DATE]/`
- Copied all files from `src/`
- Generated MD5 manifest
- Created README with restore instructions
- Verified backup integrity

### What I Discovered:
- Original files: [NUMBER]
- Backup files: [NUMBER]
- Backup size: [SIZE]
- Backup location: [FULL PATH]

### Verification:
- ✅ File counts match
- ✅ MD5 checksums generated
- ✅ README created

### Ready for Next Step:
Backup complete. Ready to proceed with Task D-002 (Fix Git Repository).

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when you start working]
- **[YYYY-MM-DD HH:MM]:** [Update when complete]

---
**Last Updated:** 2026-01-30
**Next Task:** D-002 (Fix Git Repository Configuration)
