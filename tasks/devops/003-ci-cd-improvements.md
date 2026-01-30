---
title: "CI/CD Pipeline Improvements"
status: pending
priority: p1
estimate: "2 days"
created: "2026-01-30"
assigned_to: gaudi
depends_on:
  - d-001
---

## Summary

Enhance GitHub Actions CI/CD pipelines for better security, reliability, and automation. Based on INFRASTRUCTURE_ANALYSIS.md and best practices.

## Issues to Fix

### P1 - High Priority CI/CD

#### 1. Add Database Migration Checks to CI

**File:** `.github/workflows/ci.yml`

**Add migration check step:**
```yaml
- name: Check for pending migrations
  run: |
    cd apps/backend
    python manage.py makemigrations --check --dry-run
  env:
    DJANGO_SECRET_KEY: test-secret-key
    DATABASE_URL: postgres://test:test@localhost:5432/test

- name: Detect unapplied migrations
  run: |
    cd apps/backend
    python manage.py showmigrations --list
    # Fail if any migrations are unapplied
```

#### 2. Run Security Scans on Every PR

**File:** `.github/workflows/security.yml`

**Currently:** Runs on schedule, not on PR

**Fix:** Add `pull_request` trigger:
```yaml
on:
  pull_request:
    paths:
      - '**/requirements*.txt'
      - '**/package*.json'
      - '**/Pipfile'
      - '**/pyproject.toml'
  schedule:
    - cron: '0 0 * * 0'  # Weekly
```

#### 3. Add Dependency Review Action

**File:** `.github/workflows/ci.yml`

**Add GitHub Dependency Review:**
```yaml
- name: Dependency Review
  uses: actions/dependency-review-action@v4
  with:
    # Fail on known vulnerabilities
    fail-on-severity: critical
    # License review
    license-check: true
    # Allow certain licenses
    allow-licenses: MIT, Apache-2.0, BSD-3-Clause
```

#### 4. Add Container Security Scanning

**File:** `.github/workflows/ci.yml`

**Add Trivy scan for containers:**
```yaml
- name: Build container image
  run: |
    docker build -t ${{ github.repository }}:${{ github.sha }} -f apps/backend/Dockerfile apps/backend

- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: '${{ github.repository }}:${{ github.sha }}'
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
    vuln-type: 'os,library'
```

#### 5. Fix Deployment Path in deploy.yml

**File:** `.github/workflows/deploy.yml`

**Already fixed in D-004, verify it's correct:**
```yaml
# Should be
docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -f apps/backend/Dockerfile apps/backend
```

**Verify no old paths exist:**
```bash
grep -r "docker build" .github/workflows/
```

#### 6. Add Automatic Version Bumping

**File:** `.github/workflows/`

**Add release workflow:**
```yaml
# .github/workflows/release.yml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref_name }}
          release_name: Release ${{ github.ref_name }}
          draft: false
          prerelease: false
```

#### 7. Add Linting to CI

**File:** `.github/workflows/ci.yml`

**Add Python linting:**
```yaml
- name: Lint Python
  run: |
    cd apps/backend
    pip install ruff
    ruff check .
    ruff format --check .

- name: Lint Frontend
  run: |
    cd apps/frontend
    npm run lint
```

**Add ESLint/Prettier for frontend:**
```yaml
- name: Check frontend formatting
  run: |
    cd apps/frontend
    npm run format:check
```

#### 8. Add Django System Checks in CI

**File:** `.github/workflows/ci.yml`

**Add deployment checks:**
```yaml
- name: Run Django system checks
  run: |
    cd apps/backend
    python manage.py check --deploy
    python manage.py check --fail-level WARNING
```

#### 9. Add Test Coverage Gates

**File:** `.github/workflows/ci.yml`

**Add coverage threshold:**
```yaml
- name: Check coverage
  run: |
    cd apps/backend
    pip install coverage
    coverage run --source='.' manage.py test
    coverage report --fail-under=80
```

**Or use coverage-badge:**
```yaml
- name: Generate coverage badge
  uses: schneegans/gh-actions@coverage-badge@v2
  with:
    output: coverage.svg
```

#### 10. Add Parallel Job Optimization

**File:** `.github/workflows/ci.yml`

**Optimize for faster execution:**
```yaml
jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run backend tests
        run: |
          cd apps/backend
          pip install -r requirements.txt
          pytest --cov=.

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Run frontend tests
        run: |
          cd apps/frontend
          npm install
          npm test -- --coverage

  # Run in parallel, fail fast
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... lint steps
```

## Files to Modify

1. `.github/workflows/ci.yml` - Add migration checks, security scans, linting
2. `.github/workflows/security.yml` - Add PR trigger
3. `.github/workflows/deploy.yml` - Verify paths (already done)

## Files to Create

1. `.github/workflows/release.yml` - Auto-release on tag

## Testing

```bash
# Test locally
act pull_request -j lint  # With act CLI
# Or manually verify workflow syntax:
npm install -g @githubnext/github-linter
github-linter --workflow .github/workflows/

# Verify no syntax errors
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

## Success Criteria

1. ✅ CI fails if migrations are missing
2. ✅ Security scans run on every PR
3. ✅ Dependency review catches vulnerabilities
4. ✅ Container scans on every build
5. ✅ Linting passes before merge
6. ✅ Coverage threshold enforced
7. ✅ Parallel jobs for faster execution

## Related Issues

- INFRASTRUCTURE_ANALYSIS.md Issues 6, 12, 13
