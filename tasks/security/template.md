# Task Template - Security (Charo)

**Copy this file to create new tasks:**
```bash
cp tasks/security/template.md tasks/security/[ID]-[short-name].md
```

---

# Task #[ID]: [Title]

**Assigned To:** Security (Charo)
**Priority:** [P0 | P1 | P2 | P3]
**Status:** [PENDING | IN_PROGRESS | SECURITY_ISSUE | COMPLETED]
**Created:** [YYYY-MM-DD]
**Deadline:** [YYYY-MM-DD]
**Estimated Time:** [X hours]

---

## Overview
[What security check/validation needs to be done]

## Context
[Why this security check is important]
[Related to: Migration, New Dependency, etc.]

## Security Focus Areas
- [ ] [Area 1 - e.g., Dependency vulnerabilities]
- [ ] [Area 2 - e.g., Secrets exposure]
- [ ] [Area 3 - e.g., Access control]

## Acceptance Criteria
- [ ] [Security check completed]
- [ ] [No new vulnerabilities introduced]
- [ ] [All findings documented]
- [ ] [Recommendations provided]
- [ ] [Security report generated]

## Prerequisites
- [ ] [What must be in place first]
- [ ] [Access needed]
- [ ] [Tools required]

## Security Checks

### Check 1: [Title]
```bash
# Commands to run
# What to look for
# Severity levels

# Example:
npm audit
pip-audit
```

### Check 2: [Title]
```bash
# Commands to run
# What to look for
# Severity levels
```

### Check 3: [Title]
```bash
# Commands to run
# What to look for
# Severity levels
```

## Severity Levels
- 🔴 **CRITICAL:** Immediate action, block deployment
- 🟠 **HIGH:** Fix within 24 hours
- 🟡 **MEDIUM:** Fix within 48 hours
- 🟢 **LOW:** Fix in next sprint
- 🔵 **INFO:** Best practice suggestion

## Findings Template
### Issue #[N]: [Title]
- **Severity:** [CRITICAL/HIGH/MEDIUM/LOW/INFO]
- **Location:** [File/Line/Dependency]
- **Description:** [What's wrong]
- **Impact:** [What could happen]
- **Recommendation:** [How to fix]
- **Evidence:** [Commands/output]

## Tools to Use
- **MCP:** grep, bash commands, git operations
- **Skills:** web search (for CVE lookup), github (for secret scanning)
- **Manual:** [What needs manual review]

## Dependencies
- [Task_ID] - [Must complete first]
- [Resource] - [Link]

## Feedback to Architect
[Report findings using this format]

### What I Checked:
- [Check 1]
- [Check 2]
- [Check 3]

### What I Found:
🔴 **[N] Critical Issues**
- [Issue 1]
- [Issue 2]

🟠 **[N] High Issues**
- [Issue 3]
- [Issue 4]

🟡 **[N] Medium Issues**
- [Issue 5]

🟢 **[N] Low Issues**
- [Issue 6]

### Recommendations:
1. [Immediate action for critical]
2. [Follow-up for high]
3. [Backlog for medium/low]

### Security Report:
[Attached or link to report]

## Updates
- **[YYYY-MM-DD HH:MM]:** [Status update]
- **[YYYY-MM-DD HH:MM]:** [Status update]

---
**Last Updated:** [YYYY-MM-DD]
