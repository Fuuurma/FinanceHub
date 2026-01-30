# Docker Security Scan Procedure

**Document Version:** 1.0  
**Created:** 2026-01-30  
**Author:** Security (Charo)  
**Task Reference:** S-002

---

## Overview

This document defines the Docker security scan procedures for the FinanceHub monorepo. Security scanning is critical for identifying vulnerabilities in Docker images before deployment to production.

## Scan Objectives

1. Identify known vulnerabilities in base images and dependencies
2. Ensure compliance with security policies
3. Establish baseline security posture
4. Enable continuous security monitoring

## Docker Images in Project

| Image | Location | Base Image | Purpose |
|-------|----------|------------|---------|
| Backend | `apps/backend/Dockerfile` | `python:3.11-slim` | Django/Ninja API server |
| Frontend | `apps/frontend/Dockerfile` | `node:20-alpine` | Next.js application |

## Vulnerability Severity Levels

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| CRITICAL | Immediate threat, exploitable vulnerability | Fix within 24 hours |
| HIGH | Significant vulnerability, likely exploitable | Fix within 1 week |
| MEDIUM | Moderate risk, harder to exploit | Fix within 1 month |
| LOW | Minimal risk, informational | Review quarterly |

## Scan Procedure

### Step 1: Build Images

```bash
cd /Users/sergi/Desktop/Projects/FinanceHub

# Build backend image
docker build -t financehub-backend -f apps/backend/Dockerfile .

# Build frontend image
docker build -t financehub-frontend -f apps/frontend/Dockerfile .
```

### Step 2: Execute Scans

```bash
# Scan backend image
docker scan financehub-backend --json > backend-scan-results.json

# Scan frontend image
docker scan financehub-frontend --json > frontend-scan-results.json
```

### Step 3: Review Results

```bash
# View scan summary
docker scan financehub-backend
docker scan financehub-frontend
```

## Remediation Procedures

### Critical/High Vulnerabilities

1. **Update Base Image**
2. **Update Dependencies**
3. **Rebuild and Rescan**

### Medium/Low Vulnerabilities

1. Add to allowlist if acceptable risk
2. Monitor for fixes in upstream
3. Schedule remediation in backlog

## Scan Schedule

| Environment | Frequency | Trigger |
|-------------|-----------|---------|
| Development | Weekly | Manual or scheduled CI |
| Staging | Every build | Auto on merge to staging |
| Production | Every push | Auto on tag/release |

---

**Next Review:** 2026-02-28  
**Owner:** Security Team
