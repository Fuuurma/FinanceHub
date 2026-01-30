# CI/CD Pipeline for FinanceHub

## Overview

FinanceHub uses GitHub Actions for continuous integration and deployment. The pipeline ensures code quality, security, and reliable deployments.

## Pipeline Structure

```
.github/workflows/
├── ci.yml              # Continuous Integration (lint, test, security)
├── deploy.yml          # Deployment to staging/production
├── security.yml        # Scheduled security scans
└── performance.yml     # Performance tests (nightly)
```

## CI Pipeline (ci.yml)

### Triggers
- Pull requests to `main`
- Pushes to `main`
- Manual workflow dispatch

### Jobs

#### 1. Backend Lint
**Purpose**: Ensure code quality and style consistency

**Tools**: Black, isort, Flake8, MyPy

**Duration**: ~3 minutes

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run Black format check
5. Run isort import check
6. Run Flake8 lint
7. Run MyPy type check

**Failure Conditions**:
- Code not properly formatted
- Import order violations
- Linting errors
- Type checking failures

#### 2. Backend Tests
**Purpose**: Verify backend functionality

**Tools**: Pytest, pytest-django, pytest-cov

**Duration**: ~8 minutes

**Services**:
- PostgreSQL 15 (test database)

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run database migrations
5. Run pytest with coverage
6. Upload coverage to Codecov
7. Upload test results as artifacts

**Coverage Requirements**:
- Minimum 70% line coverage
- All critical paths covered

**Test Categories**:
- Unit tests (fast)
- Integration tests (medium)
- API tests (comprehensive)

#### 3. Frontend Lint
**Purpose**: Ensure frontend code quality

**Tools**: ESLint, TypeScript

**Duration**: ~2 minutes

**Steps**:
1. Checkout code
2. Set up Node 20
3. Install dependencies
4. Run ESLint
5. Run TypeScript type check

**Failure Conditions**:
- Linting errors
- Type errors

#### 4. Frontend Tests
**Purpose**: Verify frontend functionality

**Tools**: Jest, React Testing Library

**Duration**: ~5 minutes

**Steps**:
1. Checkout code
2. Set up Node 20
3. Install dependencies
4. Run Jest with coverage
5. Upload coverage to Codecov

**Test Categories**:
- Component tests
- Hook tests
- Utility function tests
- Page integration tests

#### 5. Security Scans
**Purpose**: Detect vulnerabilities and security issues

**Tools**: Trivy, pip-audit, npm audit

**Duration**: ~4 minutes

**Steps**:
1. Checkout code
2. Run Trivy vulnerability scanner
3. Upload results to GitHub Security
4. Run pip-audit (Python)
5. Run npm audit (Node)

**Scanning**:
- Dependency vulnerabilities
- Code security issues
- Container security
- Secret detection

**Failure Conditions**:
- High severity vulnerabilities
- Critical security issues

#### 6. Build Verification
**Purpose**: Ensure production build works

**Duration**: ~3 minutes

**Steps**:
1. Build frontend production bundle
2. Verify build output
3. Check bundle size

**Total CI Duration**: ~25 minutes

## Deploy Pipeline (deploy.yml)

### Triggers
- Push to `main` (after CI passes)
- Manual workflow dispatch

### Environments

#### Staging
**URL**: https://staging.financehub.com

**Deployment Process**:
1. Build Docker image
2. Push to ECR
3. Deploy to ECS staging
4. Run smoke tests
5. Notify team

**Prerequisites**:
- All CI checks pass
- Security review approved
- No blocking issues

#### Production
**URL**: https://financehub.com

**Deployment Process**:
1. Verify staging is healthy
2. Build Docker image
3. Push to ECR
4. Deploy to ECS production
5. Run smoke tests
6. Monitor for 10 minutes
7. Create GitHub release
8. Notify team

**Prerequisites**:
- Staging deployment successful
- Smoke tests pass
- Rollback plan ready
- Maintenance window scheduled (if needed)

## Performance Pipeline (performance.yml)

### Schedule
- Nightly at 2 AM UTC

### Tests
- Load testing (Locust)
- API response times
- Database query performance
- Frontend bundle size
- Lighthouse scores

### Alerts
- Performance degradation > 20%
- API P95 > 2 seconds
- Bundle size increase > 100KB

## Security Pipeline (security.yml)

### Schedule
- Nightly at 3 AM UTC
- On-demand manual trigger

### Scans
- Full dependency audit
- Static code analysis
- Container image scanning
- Secret scanning
- License compliance check

### Reports
- Generated daily
- Stored in `reports/` directory
- Reviewed weekly

## Pre-Commit Hooks (Optional)

### Backend
```bash
# .git/hooks/pre-commit
#!/bin/bash
cd Backend/src
black --check .
isort --check-only .
flake8 .
mypy .
```

### Frontend
```bash
# .git/hooks/pre-commit
#!/bin/bash
cd Frontend
npm run lint
npm run typecheck
```

## Environment Variables

### Required Secrets
Configure in GitHub repository settings:

```
AWS_ACCESS_KEY_ID              # AWS credentials
AWS_SECRET_ACCESS_KEY          # AWS secret key
AWS_REGION                     # AWS region (us-east-1)
ECR_REPOSITORY                 # ECR repo name (finance-hub)
SLACK_WEBHOOK                  # Slack notifications
CODECOV_TOKEN                  # Codecov coverage token
```

### Environment-Specific Variables

#### Staging
```
ENVIRONMENT=staging
DATABASE_URL=postgres://...
DJANGO_SECRET_KEY=***
```

#### Production
```
ENVIRONMENT=production
DATABASE_URL=postgres://...
DJANGO_SECRET_KEY=***
```

## Rollback Procedures

### Automatic Rollback
Triggered if:
- Smoke tests fail
- Health check fails
- Error rate > 5%

### Manual Rollback
```bash
# Via GitHub CLI
gh workflow run deploy.yml --raw-field environment=production --raw-field rollback=true

# Via AWS CLI
aws ecs update-service \
  --cluster finance-hub-production \
  --service finance-hub-api \
  --task-definition finance-hub:OLD_VERSION
```

## Monitoring and Alerts

### Deployment Metrics
- Deployment frequency
- Lead time for changes
- Change failure rate
- Mean time to recovery

### Alerts
- Deployment failures
- Health check failures
- Performance degradation
- Security vulnerabilities

## Best Practices

1. **Keep pipelines fast**
   - Run tests in parallel
   - Cache dependencies
   - Use incremental builds

2. **Fail fast**
   - Run quick checks first
   - Expensive tests later
   - Stop on first failure

3. **Provide clear feedback**
   - Descriptive job names
   - Detailed error messages
   - Test result summaries

4. **Maintain reliability**
   - Pin dependency versions
   - Regular pipeline updates
   - Monitor execution times

## Troubleshooting

### CI Failures

#### Lint Failures
```bash
# Run locally
cd Backend/src && black . && isort . && flake8 .
cd Frontend && npm run lint
```

#### Test Failures
```bash
# Run locally
cd Backend/src && pytest -v
cd Frontend && npm test
```

#### Build Failures
```bash
# Check build logs
gh run view [run-id] --log

# Rebuild locally
cd Frontend && npm run build
```

### Deployment Failures

#### Health Check Failures
```bash
# Check application logs
kubectl logs -f deployment/finance-hub-api

# Check database connection
curl https://api.financehub.com/health
```

#### Performance Issues
```bash
# Check metrics
kubectl top pods -n finance-hub

# Check database performance
# Use AWS CloudWatch metrics
```

## Continuous Improvement

### Metrics to Track
- Pipeline execution time
- Test pass rate
- Deployment success rate
- Mean time to recovery

### Optimization Goals
- CI pipeline < 10 minutes
- Deployment < 5 minutes
- 99%+ deployment success rate
- < 5 minutes MTTR

---

**Last Updated**: 2026-01-30
**Maintained By**: DevOps Team
