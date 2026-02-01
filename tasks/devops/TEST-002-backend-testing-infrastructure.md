# Task: Backend Testing Infrastructure Setup

**Priority:** HIGH
**Status:** OPEN
**Assigned To:** Karen (DevOps) + Testing Team
**Created:** February 1, 2026
**Estimated Time:** 3-4 hours

## Overview

We need to set up proper testing infrastructure for the backend API. Currently:
- No pytest installed
- Tests exist but not organized
- No automated test runner
- No test coverage reports

## Current State

### Existing Tests
```bash
# Found 50+ test files:
- src/users/ (no tests found)
- src/brokers/tests/test_broker_integration.py
- src/social_sentiment/tests/test_sentiment.py
- src/tests/test_*.py (20+ general tests)
- src/trading/tests/test_paper_trading.py
- src/investments/management/commands/test_*.py (8+ command tests)
```

### Test Runners
- ✅ Django test framework available (`python manage.py test`)
- ❌ pytest not installed
- ❌ No coverage tool configured
- ❌ No automated CI tests (D-014 added security scanning but not unit tests)

## Required Setup

### Phase 1: Install Testing Tools (30 minutes)

1. **Install pytest and plugins**
```bash
# Add to requirements.txt or pyproject.toml
pytest==7.4.3
pytest-django==4.5.2
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0
```

2. **Configure pytest**
Create `apps/backend/pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = src
addopts =
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

### Phase 2: Create Test Structure (1 hour)

Organize tests by app/module:

```
apps/backend/src/
├── users/
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_registration.py
│       ├── test_login.py
│       └── test_user_api.py
├── portfolios/
│   └── tests/
│       ├── __init__.py
│       ├── test_portfolios.py
│       ├── test_holdings.py
│       └── test_transactions.py
├── market/
│   └── tests/
│       ├── __init__.py
│       ├── test_market_data.py
│       └── test_technical_analysis.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_fixtures.py
    └── test_integration.py
```

### Phase 3: Create Test Fixtures (1 hour)

Create `src/tests/conftest.py`:
```python
import pytest
from django.contrib.auth import get_user_model
from users.models.role import Role

@pytest.fixture
def db():
    """Setup database for tests"""
    pytest_setup = True

@pytest.fixture
def test_user(db):
    """Create a test user"""
    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!"
    )
    return user

@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post('/users/login', {
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    return response.json()['access']

@pytest.fixture
def investor_role(db):
    """Create investor role"""
    role, _ = Role.objects.get_or_create(
        name="Investor",
        defaults={'description': 'Standard investor role'}
    )
    return role
```

### Phase 4: Create Endpoint Tests (2 hours)

#### User Registration Tests
`src/users/tests/test_registration.py`:
```python
import pytest
from django.test import Client

@pytest.mark.django_db
class TestUserRegistration:
    
    def test_valid_registration(self, client):
        """Test successful user registration"""
        response = client.post('/users/register', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }, content_type='application/json')
        
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert data['username'] == 'newuser'
        assert data['email'] == 'newuser@example.com'
    
    def test_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/users/register', {
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': 'weak',
            'password_confirm': 'weak'
        }, content_type='application/json')
        
        assert response.status_code == 422
        # Should have validation errors
    
    def test_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/users/register', {
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!'
        }, content_type='application/json')
        
        assert response.status_code == 422
```

### Phase 5: Integration with CI (30 minutes)

Update `.github/workflows/ci.yml` to run tests:

```yaml
- name: Run tests
  run: |
    docker-compose exec -T backend pytest src/ -v --cov

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./htmlcov/
```

## Test Commands

```bash
# Run all tests
docker-compose exec backend pytest src/ -v

# Run specific app tests
docker-compose exec backend pytest src/users/ -v

# Run with coverage
docker-compose exec backend pytest src/ --cov=src --cov-report=html

# Run specific test file
docker-compose exec backend pytest src/users/tests/test_registration.py -v

# Run with markers
docker-compose exec backend pytest -m "not slow" -v
```

## Coverage Goals

- **Overall:** 70% minimum
- **User Authentication:** 90% (critical)
- **Portfolios:** 80%
- **Market Data:** 60%
- **Assets:** 75%

## Success Criteria

✅ pytest installed and configured
✅ Can run tests with `pytest src/`
✅ Test fixtures working (db, user, auth_token)
✅ Coverage reporting works
✅ CI pipeline runs tests
✅ Minimum 70% code coverage
✅ All critical endpoints tested

## Deliverables

1. pytest configuration files
2. Test fixtures in conftest.py
3. Test files for each major endpoint
4. Coverage report (HTML)
5. Updated CI workflow with tests
6. Test documentation

## Files to Create

1. `/apps/backend/pytest.ini`
2. `/apps/backend/src/tests/conftest.py`
3. `/apps/backend/src/users/tests/test_registration.py`
4. `/apps/backend/src/users/tests/test_login.py`
5. `/apps/backend/src/portfolios/tests/test_portfolios.py`
6. Any additional test files needed

## Related Tasks

- TEST-001: Test All Backend API Endpoints (manual testing task)
- FIX-002: Improve User Registration Error Handling
- D-014: Security Scanning Integration (CI/CD already set up)

## Notes

- Use pytest-django for Django integration
- Database transactions should be rolled back after each test
- Use `@pytest.mark.django_db` for tests needing database
- Use factory_boy for test data if needed
- Consider pytest-mock for mocking external APIs
