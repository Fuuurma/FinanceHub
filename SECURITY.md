# Security Policy

## Vulnerability Scanning

We scan for vulnerabilities automatically:
- **Docker images:** On every PR and push (via `security-scan.yml`)
- **Python dependencies:** On every PR and push
- **Node dependencies:** On every PR and push
- **Daily scans:** Run automatically at 2 AM UTC

## Severity Thresholds

Our security policy:

- **CRITICAL:** 🔴 Blocks deployment - Fix within 24 hours
- **HIGH:** 🟠 Blocks deployment - Fix within 72 hours
- **MEDIUM:** 🟡 Warning only - Fix within 1 week
- **LOW:** 🟢 Informational only - Fix within next sprint

## Current Security Posture

As of February 1, 2026:

- **Docker Backend:** 2 CRITICAL, 6 HIGH vulnerabilities (S-008 in progress)
- **Docker Frontend:** TBD (needs scanning)
- **Python Dependencies:** TBD (needs scanning)
- **Node Dependencies:** TBD (needs scanning)

## Reporting

Vulnerabilities are reported to:

1. **GitHub Security Tab** - SARIF results from automated scans
2. **Pull Request Comments** - Summary of scan results
3. **Slack Notifications** - On CRITICAL findings
4. **Security Team** - Charo (Security Lead)

## Remediation Process

### When Vulnerabilities Are Found

1. **CRITICAL (24 hours):**
   - Stop deployment
   - Notify Security Lead (Charo)
   - Create security issue
   - Fix immediately
   - Re-scan before merge

2. **HIGH (72 hours):**
   - Notify team
   - Schedule fix
   - Create task if needed
   - Update in next sprint

3. **MEDIUM (1 week):**
   - Add to backlog
   - Schedule for next release
   - Track in project board

4. **LOW (next sprint):**
   - Technical debt item
   - Fix when convenient

## Prevention

To prevent vulnerabilities:

1. **Keep dependencies updated:**
   - Review dependency updates weekly
   - Test updates in staging first
   - Update in coordinated releases

2. **Security scanning:**
   - Run `docker scan` locally before pushing
   - Check GitHub Security tab regularly
   - Review scan results in PRs

3. **Code reviews:**
   - Check for new dependencies
   - Verify security implications
   - Ask for security review if unsure

## Contact

For security issues or questions:

- **Security Lead:** Charo
- **DevOps:** Karen
- **GitHub Security:** https://github.com/Fuuurma/FinanceHub/security

## Resources

- [S-008: Docker Base Image Update](../tasks/security/008-docker-base-image-update.md)
- [D-009: CI/CD Pipeline Enhancement](../tasks/devops/009-ci-cd-pipeline-enhancement.md)
- [D-014: Security Scanning Integration](../tasks/devops/014-security-scanning-integration.md)

---

**Last Updated:** February 1, 2026
**Maintained By:** Karen (DevOps) + Charo (Security)
