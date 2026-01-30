# Task S-001: Validate Security After Migration

**Assigned To:** Security (Charo)
**Priority:** P0 (CRITICAL)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-02-02 5:00 PM
**Estimated Time:** 3 hours
**Dependencies:** D-003, C-001, C-002 (Path fixes complete)

---

## Overview
Perform comprehensive security validation after monorepo migration to ensure no new vulnerabilities were introduced and no security controls were broken.

## Context
After structural changes (directory moves, path updates, repository changes), we need to verify:
- No new dependency vulnerabilities
- No exposed secrets in git history
- File permissions remain secure
- Docker images are clean
- Access controls intact

## Security Focus Areas
- [ ] Dependency vulnerability scans (backend & frontend)
- [ ] Secret detection (git history scan)
- [ ] File permission review
- [ ] Docker image scanning
- [ ] .gitignore validation
- [ ] Environment variable checks

## Acceptance Criteria
- [ ] All dependency scans run successfully
- [ ] No new vulnerabilities introduced (same baseline as before)
- [ ] No secrets exposed in git history
- [ ] All sensitive files in .gitignore
- [ ] File permissions are secure
- [ ] Docker images pass security scan
- [ ] Security report generated

## Prerequisites
- [ ] D-003 complete (directories reorganized)
- [ ] C-001, C-002 complete (path fixes)
- [ ] All apps build successfully
- [ ] Access to security scanning tools

## Security Checks

### Check 1: Backend Dependency Scan
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend

# Run pip-audit
pip-audit

# Run safety check
safety check

# Document results
pip-audit > ../backups/security-scan-backend-$(date +%Y%m%d).txt
safety check > ../backups/safety-check-backend-$(date +%Y%m%d).txt
```

**What to look for:**
- Known CVEs in Python packages
- Outdated dependencies with vulnerabilities
- Severity levels

### Check 2: Frontend Dependency Scan
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/frontend

# Run npm audit
npm audit

# Fix if possible (manual review first)
# npm audit fix

# Document results
npm audit > ../backups/security-scan-frontend-$(date +%Y%m%d).txt
```

**What to look for:**
- Known CVEs in npm packages
- Vulnerability counts by severity
- Compare to baseline (should be same or better)

### Check 3: Git History Secret Scan
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Scan for sensitive keywords in git history
git log --all --full-history --source --grep="password\|secret\|key\|token" | head -50

# Scan for file additions with sensitive names
git log --all --name-only --format="" | grep -iE "password|secret|key|credential|\.env$|\.pem$|\.p12$" | sort -u

# Document findings
git log --all --full-history --source -- "*password*" "*secret*" "*key*" > backups/secret-scan-$(date +%Y%m%d).txt
```

**What to look for:**
- API keys, passwords in commits
- Configuration files with secrets
- Certificate files
- Environment files

### Check 4: .gitignore Validation
```bash
# Check what's actually tracked in git
git ls-files | grep -E "\.(env|key|pem|p12|credential|password)$"

# Verify .gitignore covers sensitive files
cat .gitignore | grep -E "env|key|pem|p12"

# Check for unintended tracked files
git ls-files | grep -v "node_modules" | grep -v ".pyc"
```

**What to look for:**
- .env files tracked
- Certificate files tracked
- Key files tracked
- Missing patterns in .gitignore

### Check 5: File Permissions Review
```bash
# Find overly permissive files
find /Users/sergi/Desktop/Projects/FinanceHub -type f -perm -o+w -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/venv/*"

# Check for world-writable files
find . -type f -perm -o=w

# Document findings
find . -type f -perm -o+w > backups/permissions-scan-$(date +%Y%m%d).txt
```

**What to look for:**
- World-writable files
- Overly permissive permissions
- Sensitive files with wrong permissions

### Check 6: Docker Image Scanning
```bash
# Build images first
cd /Users/sergi/Desktop/Projects/FinanceHub
docker-compose build

# Scan backend image
docker scan financehub-backend:latest

# Scan frontend image
docker scan financehub-frontend:latest

# Document results
docker scan financehub-backend:latest > backups/docker-scan-backend-$(date +%Y%m%d).txt
docker scan financehub-frontend:latest > backups/docker-scan-frontend-$(date +%Y%m%d).txt
```

**What to look for:**
- Known vulnerabilities in base images
- CVE counts
- High/critical severity issues

## Findings Template

### Issue #[N]: [Vulnerability Title]
- **Severity:** 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW / 🔵 INFO
- **Location:** [File/Package/Line]
- **CVE:** [CVE-XXXX-XXXX]
- **Description:** [What's wrong]
- **Impact:** [What could happen]
- **Recommendation:** [How to fix]
- **Evidence:** [Command output]

## Tools to Use
- **MCP:** bash commands, grep, git operations, file operations
- **Skills:** web search (for CVE details), github (for secret scanning)
- **Manual:** Review of scan results

## Dependencies
- ✅ D-003 (Directory reorganization)
- ✅ C-001 (Backend path fixes)
- ✅ C-002 (Frontend path fixes)

## Feedback to Architect
[Report findings after all checks complete]

### What I Checked:
- ✅ Backend dependencies (pip-audit, safety)
- ✅ Frontend dependencies (npm audit)
- ✅ Git history for secrets
- ✅ File permissions
- ✅ Docker images
- ✅ .gitignore validation

### What I Found:
🔴 **[N] Critical Issues**
- [List if any]

🟠 **[N] High Issues**
- [List if any]

🟡 **[N] Medium Issues**
- [List if any]

🟢 **[N] Low Issues**
- [List if any]

🔵 **[N] Info (Best Practices)**
- [List if any]

### Comparison to Baseline:
- **Before Migration:**
  - Backend: [N] vulnerabilities
  - Frontend: [N] vulnerabilities
  - Secrets: [N] exposed

- **After Migration:**
  - Backend: [N] vulnerabilities (change: +N/-N)
  - Frontend: [N] vulnerabilities (change: +N/-N)
  - Secrets: [N] exposed (change: +N/-N)

### Assessment:
✅ **Migration is SAFE** - No new security issues introduced
OR
⚠️ **Migration has ISSUES** - [List concerns]

### Recommendations:
1. [Immediate action for critical]
2. [Follow-up for high]
3. [Monitor for medium/low]

### Security Report:
Generated: `backups/security-validation-report-$(date +%Y%m%d).md`

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when start scanning]
- **[YYYY-MM-DD HH:MM]:** [Update with findings]

---
**Last Updated:** 2026-01-30
**Note:** This validation MUST pass before D-005 (Delete src/) can proceed
