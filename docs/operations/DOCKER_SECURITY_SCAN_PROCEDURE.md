# Docker Security Scan Procedure

**Document Version:** 1.0
**Created:** 2026-01-30
**Author:** Charo (Security Engineer)
**Last Updated:** 2026-01-30

---

## Purpose

This document outlines the standard operating procedure for scanning Docker images for security vulnerabilities in the FinanceHub project.

---

## Scope

- All Docker images built for FinanceHub
- Backend and Frontend applications
- CI/CD pipeline integration
- Local development scanning

---

## Prerequisites

### Tools Required
```bash
# Install Trivy (recommended scanner)
brew install trivy  # macOS
# OR
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Alternative scanners (optional)
brew install snyk   # Snyk CLI
brew install grype  # Grype CLI
```

### Access Required
- Docker daemon running
- Access to project root directory
- Permission to build images

---

## Scan Workflow

### Step 1: Prepare Environment

```bash
# Verify Docker is running
docker info

# Verify Trivy is installed
trivy --version

# Navigate to project root
cd /Users/sergi/Desktop/Projects/FinanceHub
```

### Step 2: Build Docker Images

#### Backend Image
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub
docker build -t financehub-backend -f apps/backend/Dockerfile .
```

#### Frontend Image
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/frontend
docker build -t financehub-frontend -f Dockerfile .
```

**Note:** Frontend build may fail due to missing dependencies. This is not a security issue.

### Step 3: Execute Scans

#### Quick Scan (Critical/High only)
```bash
# Scan backend for critical and high vulnerabilities
trivy image --severity CRITICAL,HIGH financehub-backend

# Scan frontend
trivy image --severity CRITICAL,HIGH financehub-frontend
```

#### Full Scan (All severities)
```bash
# Comprehensive backend scan
trivy image financehub-backend

# Export results to JSON
trivy image -f json -o backend-scan-results.json financehub-backend
```

#### Scan with Specific Options
```bash
# Skip dependency scanning (faster)
trivy image --scanners vuln financehub-backend

# Include security checks
trivy image --security-checks financehub-backend

# Output in table format
trivy image -f table financehub-backend
```

### Step 4: Analyze Results

#### Vulnerability Severity Levels

| Severity | CVSS Score | Action Required |
|----------|------------|-----------------|
| 🔴 CRITICAL | 9.0-10.0 | Fix immediately (24h) |
| 🟠 HIGH | 7.0-8.9 | Fix within 1 week |
| 🟡 MEDIUM | 4.0-6.9 | Fix within 1 month |
| 🟢 LOW | 0.1-3.9 | Monitor, fix when convenient |

#### Common Vulnerability Types

1. **OS Package Vulnerabilities**
   - Base image outdated
   - Missing security patches
   - Solution: Update base image

2. **Application Dependencies**
   - Python/Node packages with CVEs
   - Solution: Update requirements/package.json

3. **Configuration Issues**
   - Running as root
   - Missing health checks
   - Solution: Fix Dockerfile

4. **Secrets Exposure**
   - API keys in image
   - Solution: Use secrets management

### Step 5: Document Findings

#### Create Scan Report
```bash
# Generate detailed report
trivy image -f json -o scan-results.json financehub-backend

# Create markdown summary
trivy image -f template -o scan-report.md \
  --template "@contrib/markdown.tpl" financehub-backend
```

#### Required Documentation
1. Scan date and time
2. Image version/tag
3. Scanner version
4. Vulnerabilities found (by severity)
5. Remediation actions required
6. Risk assessment

### Step 6: Remediate Vulnerabilities

#### For Base Image Issues
```dockerfile
# Update base image in Dockerfile
FROM python:3.11-slim-bookworm  # Use specific version

# OR use security-updated variant
FROM python:3.11-slim@sha256:abc123...
```

#### For Dependency Issues
```bash
# Update Python packages
cd apps/backend
pip install --upgrade package-with-cve

# Update frontend packages
cd apps/frontend
npm update package-with-cve
```

#### For Configuration Issues
```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Add health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Step 7: Verify Fixes

```bash
# Rebuild image
docker build -t financehub-backend:fixed -f apps/backend/Dockerfile .

# Re-scan
trivy image --severity CRITICAL,HIGH financehub-backend:fixed

# Verify no critical/high vulnerabilities remain
# Expected: 0 Critical, 0 High
```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/docker-security.yml`:

```yaml
name: Docker Security Scan

on:
  push:
    paths:
      - 'apps/backend/Dockerfile'
      - 'apps/frontend/Dockerfile'
      - 'apps/backend/requirements.txt'
      - 'apps/frontend/package.json'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Backend Image
        uses: docker/build-push-action@v5
        with:
          context: ./apps/backend
          load: true
          tags: financehub-backend

      - name: Run Trivy Vulnerability Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'financehub-backend'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
          timeout: '10m'
```

### GitLab CI Example

```yaml
docker_scan:
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH financehub-backend
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - changes:
        - apps/backend/Dockerfile
        - apps/backend/requirements.txt
```

---

## Threshold Definitions

### Block Deployment (Fail Build)
- **Critical:** >= 1
- **High:** >= 5
- **Medium:** >= 50

### Warn Only (Don't Block)
- **Critical:** 0
- **High:** 1-4
- **Medium:** 10-49

### Pass
- **Critical:** 0
- **High:** 0
- **Medium:** < 10

---

## Scheduled Scanning

### Daily
- Scan all deployed images
- Report new vulnerabilities
- Alert on critical/high findings

### Weekly
- Full scan of all images
- Review vulnerability trends
- Plan remediation

### Monthly
- Base image updates
- Dependency updates
- Security policy review

---

## Troubleshooting

### Trivy Database Update Fails
```bash
# Update database manually
trivy db update --download-db-only

# Use mirror
TRIVY_DB_REPOSITORY=ghcr.io/aquasec/trivy-db:2 trivy image financehub-backend
```

### Scan Times Out
```bash
# Skip slow scans
trivy image --scanners vuln --skip-dirs node_modules financehub-backend
```

### False Positives
```bash
# Ignore specific vulnerabilities
trivy image --ignore-unfixed \
  --ignorefile .trivyignore.yaml \
  financehub-backend
```

Create `.trivyignore.yaml`:
```yaml
# Ignore CVE-2025-1234 (false positive)
CVE-2025-1234
```

---

## Related Documents

- [Docker Scan Results 2026-01-30](../security/DOCKER_SCAN_RESULTS_20260130.md)
- [Security Policy](../security/SECURITY.md)
- [Vulnerability Remediation Plan](../security/VULNERABILITY_REMEDIATION_PLAN.md)

---

## Quick Reference

### Common Commands
```bash
# Quick scan (critical/high only)
trivy image --severity CRITICAL,HIGH financehub-backend

# Full scan with JSON output
trivy image -f json -o results.json financehub-backend

# Scan with detailed report
trivy image -f template -o report.md \
  --template "@contrib/markdown.tpl" financehub-backend

# Ignore fixed vulnerabilities
trivy image --ignore-unfixed financehub-backend
```

### Severity Thresholds
| Level | CVSS | Response Time |
|-------|------|---------------|
| CRITICAL | 9.0+ | 24 hours |
| HIGH | 7.0-8.9 | 1 week |
| MEDIUM | 4.0-6.9 | 1 month |
| LOW | 0.1-3.9 | Next cycle |

---

## Approval

| Role | Name | Date |
|------|------|------|
| Security Engineer | Charo | 2026-01-30 |
| Architect | Gaudí | [Pending] |

---

**Document Version:** 1.0
**Next Review:** 2026-02-28
