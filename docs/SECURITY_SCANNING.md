# Security Scanning Configuration for FinanceHub

## Tools Used

### Backend (Python)
- **pip-audit**: Vulnerability scanner for Python dependencies
- **bandit**: Security linter for Python code
- **safety**: Security vulnerability checker
- **semgrep**: Static analysis for security patterns

### Frontend (JavaScript/TypeScript)
- **npm audit**: Built-in Node.js vulnerability scanner
- **trivy**: Container and filesystem vulnerability scanner

### Infrastructure
- **trivy**: Container image scanning
- **git-secrets**: Secret detection in git history

## Scanning Commands

### Backend Security Scan
```bash
# Dependency vulnerability scan
pip-audit --desc --format json > reports/backend-pip-audit.json

# Code security analysis
bandit -r Backend/src -f json -o reports/backend-bandit.json

# Safety check
safety check --json > reports/backend-safety.json

# Semgrep security scan
semgrep --config=auto --json --output=reports/backend-semgrep.json Backend/src/
```

### Frontend Security Scan
```bash
# npm audit
cd Frontend
npm audit --json > ../reports/frontend-npm-audit.json

# Trivy filesystem scan
trivy fs --format json --output ../reports/frontend-trivy.json Frontend/
```

### Container Scan
```bash
# Scan Docker image
trivy image --format json --output reports/image-trivy.json finance-hub:latest
```

## CI/CD Integration

All security scans run automatically in CI pipeline. Build will fail if:
- High severity vulnerabilities found
- Known security issues detected in code
- Secrets detected in committed files

## Remediation

### Vulnerability Found
1. Check severity level
2. Review affected package
3. Update to patched version
4. Re-run scan to verify fix

### Code Security Issue
1. Review flagged code
2. Understand security implication
3. Refactor to secure pattern
4. Add test case if needed

## Reporting

All security reports generated in `reports/` directory:
- `backend-pip-audit.json` - Python dependency vulnerabilities
- `backend-bandit.json` - Python code security issues
- `frontend-npm-audit.json` - Node.js dependency vulnerabilities
- `frontend-trivy.json` - Frontend filesystem scan
- `image-trivy.json` - Docker image vulnerabilities

## False Positives

To mark false positives:

### pip-audit
```bash
pip-audit --skip VULN-ID-1,VULN-ID-2
```

### bandit
```bash
# noqa: B101
assert True  # Intentional for testing
```

### npm audit
```json
// .npmrc
audit-level=high
```

## Regular Scanning Schedule

- **Pre-commit**: Fast security checks
- **PR Validation**: Full security scan suite
- **Nightly**: Deep security analysis
- **Pre-release**: Complete security audit

## Security Best Practices

1. **Keep dependencies updated**
   ```bash
   pip list --outdated
   npm outdated
   ```

2. **Pin dependency versions**
   ```bash
   pip freeze > requirements.txt
   ```

3. **Use lockfiles**
   - package-lock.json (frontend)
   - requirements.txt (backend)

4. **Regular security reviews**
   - Monthly dependency audits
   - Quarterly code security reviews
   - Annual penetration testing

## Incident Response

If critical vulnerability found:

1. **Immediate Action**
   - Notify team
   - Create security issue
   - Assess impact

2. **Investigation**
   - Determine affected systems
   - Check exploit availability
   - Review mitigation options

3. **Remediation**
   - Apply patch or workaround
   - Test thoroughly
   - Deploy to production

4. **Post-Incident**
   - Document lessons learned
   - Update processes
   - Share with team
