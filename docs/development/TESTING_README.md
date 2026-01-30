# Testing Infrastructure for FinanceHub

## Overview

Complete testing infrastructure with CI/CD pipelines, automated testing, security scanning, and comprehensive documentation.

## Quick Start

### Run Backend Tests
```bash
cd Backend/src
pytest --cov=. --cov-report=html -v
```

### Run Frontend Tests
```bash
cd Frontend
npm test
```

### Run E2E Tests
```bash
cd Frontend
npx playwright test
```

### Run Security Scans
```bash
# Backend
cd Backend
pip-audit --desc
bandit -r src/

# Frontend
cd Frontend
npm audit
```

### Run Smoke Tests (After Deployment)
```bash
./scripts/smoke-test.sh staging
./scripts/health-check.sh production
```

## Test Structure

### Backend Tests
```
Backend/src/tests/
├── conftest.py                    # Pytest fixtures
├── test_ai_advisor.py            # AI features
├── test_analytics.py             # Analytics endpoints
├── test_fundamentals.py          # Market data
├── test_optimization.py          # Portfolio optimization
├── test_options_pricing.py       # Options calculations
├── test_quantitative_models.py   # Financial models
├── test_websocket_consumer.py    # WebSocket connections
└── test_tasks.py                 # Background jobs
```

### Frontend Tests
```
Frontend/src/tests/
├── components/                   # Component tests
│   ├── realtime/                # Real-time data components
│   └── ai/templates/            # AI template components
└── pages/                       # Page integration tests
    ├── alerts.test.tsx
    ├── analytics.test.tsx
    └── sentiment.test.tsx
```

### E2E Tests
```
Frontend/tests/e2e/
├── smoke.spec.ts               # Basic smoke tests
└── auth-portfolio.spec.ts      # Auth & portfolio flows
```

## CI/CD Pipeline

### GitHub Actions Workflows
```
.github/workflows/
├── ci.yml           # Continuous Integration
├── deploy.yml       # Deployment to staging/production
└── security.yml     # Security scanning (daily)
```

### CI Pipeline Stages
1. **Backend Lint** - Black, isort, Flake8, MyPy (~3 min)
2. **Backend Tests** - Pytest with coverage (~8 min)
3. **Frontend Lint** - ESLint, TypeScript (~2 min)
4. **Frontend Tests** - Jest with coverage (~5 min)
5. **Security Scan** - Trivy, pip-audit, npm audit (~4 min)
6. **Build Verification** - Production build (~3 min)

**Total Time**: ~25 minutes

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Backend | 70% | 65% |
| Frontend | 60% | 55% |

## Security Scanning

### Automated Scans
- **Dependency vulnerabilities** (pip-audit, npm audit)
- **Code security** (bandit, semgrep)
- **Container scanning** (trivy)
- **Secret detection** (trufflehog)
- **License compliance** (pip-licenses)

### Scan Schedule
- **Pre-commit**: Fast security checks
- **PR validation**: Full security scan suite
- **Nightly**: Deep security analysis (3 AM UTC)

## Deployment Scripts

### Smoke Tests
```bash
./scripts/smoke-test.sh [staging|production]
```
Tests critical endpoints after deployment.

### Health Check
```bash
./scripts/health-check.sh [staging|production]
```
Checks system health status.

### Rollback
```bash
./scripts/rollback.sh [staging|production]
```
Reverts to previous Docker image.

## Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - CI/CD pipeline details
- [MONITORING.md](./MONITORING.md) - Monitoring & alerting
- [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) - System architecture
- [SECURITY_SCANNING.md](./SECURITY_SCANNING.md) - Security procedures

## Testing Best Practices

### Backend (Python)
- Use descriptive test names
- One assertion per test (when possible)
- Mock external dependencies
- Use fixtures for common setup
- Test both success and failure cases

### Frontend (TypeScript)
- Test user behavior, not implementation
- Use testing-library queries (getByRole, getByText)
- Mock API calls
- Test loading/error states
- Avoid testing implementation details

### E2E (Playwright)
- Test critical user flows
- Use page objects for complex pages
- Wait for elements, don't use fixed timeouts
- Test across browsers (Chrome, Firefox, Safari)
- Keep tests independent

## Troubleshooting

### Tests Failing Locally
```bash
# Backend
cd Backend/src
python -m pytest -xvs tests/test_failing.py

# Frontend
cd Frontend
npm test -- --testNamePattern="failing test"
```

### Coverage Dropped
```bash
# Check what changed
git diff HEAD~1 coverage.xml

# Run specific test with coverage
pytest --cov=module tests/test_module.py
```

### Security Scan Found Vulnerability
```bash
# Check details
pip-audit --desc

# Update package
pip install --upgrade package-name

# Verify fix
pip-audit
```

## Configuration Files

- **Backend**: `Backend/src/setup.cfg`
- **Frontend**: `Frontend/jest.config.js`, `Frontend/playwright.config.ts`
- **CI/CD**: `.github/workflows/*.yml`

## Next Steps

1. Install test dependencies
   ```bash
   cd Backend && pip install -r requirements-testing.txt
   cd Frontend && npm install
   ```

2. Run tests locally to verify
   ```bash
   cd Backend/src && pytest
   cd Frontend && npm test
   ```

3. Set up GitHub Actions
   - Configure AWS credentials
   - Set up Slack webhook
   - Enable required actions

4. Configure monitoring
   - Set up CloudWatch dashboards
   - Configure alerts
   - Test incident response

---

**For questions or issues**, contact the DevOps team.
