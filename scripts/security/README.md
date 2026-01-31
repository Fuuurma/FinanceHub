# Security Scripts

**Purpose:** Automated security scanning and monitoring scripts

**Author:** Charo (Security Engineer)
**Last Updated:** 2026-01-30

---

## Available Scripts

### scan.sh
Comprehensive security scanner for FinanceHub.

**Usage:**
```bash
./scripts/security/scan.sh
```

**What it scans:**
1. **Dependency Vulnerabilities**
   - Python packages (pip-audit)
   - Node.js packages (npm audit)

2. **Docker Images**
   - Backend image vulnerabilities (Trivy)
   - Critical/High severity issues

3. **Secret Detection**
   - Hardcoded API keys
   - Passwords in code
   - Tokens in git history

4. **File Permissions**
   - World-writable files
   - Executable scripts

5. **Git History**
   - Committed secrets
   - .gitignore configuration

**Output:**
- Reports saved to `docs/security/reports/`
- Summary report generated
- JSON outputs for detailed analysis

---

## Automated Security Checks

### Daily (CI/CD)
```bash
# Run dependency checks
cd apps/backend && pip-audit
cd apps/frontend && npm audit --audit-level=high
```

### Weekly (Full Scan)
```bash
# Run comprehensive security scan
./scripts/security/scan.sh
```

### Monthly (Manual Audit)
1. Review all security reports
2. Check git history for secrets
3. Update security documentation
4. Conduct penetration testing

---

## Security Monitoring

### Metrics to Track
- Vulnerability count by severity
- Time to remediation
- Dependency age
- Security scan coverage

### Alerts
- Critical vulnerabilities → Immediate alert
- High vulnerabilities → Within 24 hours
- Medium vulnerabilities → Within 1 week
- Low vulnerabilities → Next scan cycle

---

## Best Practices

1. **Run scans regularly**
   - Daily: Dependency checks
   - Weekly: Full scan
   - Monthly: Manual audit

2. **Fix vulnerabilities promptly**
   - Critical: 24 hours
   - High: 1 week
   - Medium: 1 month

3. **Keep dependencies updated**
   - Use Dependabot or Renovate
   - Review updates before merging

4. **Monitor git history**
   - No secrets in commits
   - Review PRs for security

---

## Troubleshooting

### pip-audit not found
```bash
pip install pip-audit
```

### npm audit fails
```bash
cd apps/frontend
npm install
npm audit
```

### Trivy not found
```bash
brew install trivy
```

---

## Related Documents

- [Security Testing Framework](../../docs/security/SECURITY_TESTING_FRAMEWORK.md)
- [Security Audit Checklist](../../docs/security/SECURITY_AUDIT_CHECKLIST.md)
- [Security Findings Report](../../docs/security/SECURITY_FINDINGS_REPORT.md)

---

**Document Version:** 1.0
**Next Review:** 2026-02-28
