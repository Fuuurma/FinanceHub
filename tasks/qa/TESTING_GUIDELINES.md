# Testing Guidelines for FinanceHub

**Created:** Feb 1, 2026
**Author:** GRACE (QA/Testing Engineer)
**Version:** 1.0

---

## Introduction

This document provides testing guidelines for all developers working on FinanceHub. Following these standards ensures code quality and reliability.

---

## Golden Rules

1. **ALWAYS write tests first** - TDD approach when possible
2. **ALWAYS test edge cases** - Not just happy paths
3. **ALWAYS verify fixes** - Don't assume, run tests
4. **DOCUMENT test coverage** - What's tested, what's not
5. **COMMUNICATE gaps** - Missing tests, coverage issues

---

## Test Checklist

For each feature/fix:

- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Edge cases tested
- [ ] Error handling tested
- [ ] Performance tests (if applicable)
- [ ] Security tests (if applicable)
- [ ] Documentation updated

---

## Backend Testing (pytest)

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_portfolio_analytics.py

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test
pytest tests/test_portfolio_analytics.py::test_portfolio_value_calculation

# Run by marker
pytest -m "unit"
pytest -m "integration"
```

### Test Structure

```python
import pytest
from decimal import Decimal

class TestPortfolioCalculator:
    """Test class for portfolio calculations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.calculator = PortfolioCalculator()
    
    def test_calculate_portfolio_value(self):
        """Test basic portfolio value calculation"""
        # Arrange
        holdings = create_test_holdings()
        
        # Act
        result = self.calculator.calculate_portfolio_value(holdings)
        
        # Assert
        assert result['total_value'] > 0
        assert isinstance(result['total_value'], Decimal)
    
    def test_empty_portfolio(self):
        """Test empty portfolio handling"""
        # Act
        result = self.calculator.calculate_portfolio_value([])
        
        # Assert
        assert result['total_value'] == Decimal('0')
        assert result['holdings_count'] == 0
    
    def test_portfolio_with_fractional_shares(self):
        """Test fractional share handling"""
        # Given
        holdings = create_holdings_with_fractional_shares()
        
        # When
        result = self.calculator.calculate_portfolio_value(holdings)
        
        # Then
        assert result['total_value'] > 0
```

### Using Fixtures

```python
@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio for testing"""
    return {
        'holdings': [
            {'symbol': 'AAPL', 'shares': 10, 'price': 150.00},
            {'symbol': 'GOOGL', 'shares': 5, 'price': 2800.00},
        ],
        'total_value': 15500.00
    }

def test_portfolio_with_fixture(sample_portfolio):
    """Test using fixture"""
    calculator = PortfolioCalculator()
    result = calculator.calculate_portfolio_value(sample_portfolio['holdings'])
    assert result['total_value'] == Decimal('15500')
```

### Mocking External Services

```python
from unittest.mock import patch
import pytest

@patch('src.services.market_data.get_price')
def test_get_portfolio_value_with_mocked_price(mock_get_price):
    """Test with mocked external service"""
    # Arrange
    mock_get_price.side_effect = [Decimal('150.00'), Decimal('2800.00')]
    
    # Act
    result = get_portfolio_value('AAPL', 10)
    
    # Assert
    assert result == Decimal('15000.00')
    mock_get_price.assert_called_once_with('AAPL')
```

### Testing Edge Cases

```python
def test_division_by_zero():
    """Test safe division handling"""
    result = safe_divide(Decimal('100'), Decimal('0'))
    assert result == Decimal('0')

def test_none_handling():
    """Test None value handling"""
    result = to_decimal(None)
    assert result == Decimal('0')

def test_string_with_currency():
    """Test string with currency symbol"""
    result = to_decimal('$1,234.56')
    assert result == Decimal('1234.56')
```

---

## Frontend Testing (Jest)

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- PortfolioTable.test.tsx

# Run with coverage
npm run test:coverage

# Watch mode
npm test -- --watch
```

### Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('PortfolioTable', () => {
  it('renders portfolio data correctly', () => {
    // Arrange
    const mockPortfolio = {
      holdings: [{ symbol: 'AAPL', value: 15000 }]
    };
    
    // Act
    render(<PortfolioTable portfolio={mockPortfolio} />);
    
    // Assert
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('$15,000.00')).toBeInTheDocument();
  });

  it('handles empty portfolio', () => {
    // Act
    render(<PortfolioTable portfolio={{ holdings: [] }} />);
    
    // Assert
    expect(screen.getByText('No holdings')).toBeInTheDocument();
  });

  it('calls onRowClick when row is clicked', async () => {
    // Arrange
    const mockOnRowClick = jest.fn();
    const user = userEvent.setup();
    
    render(
      <PortfolioTable 
        portfolio={testPortfolio} 
        onRowClick={mockOnRowClick}
      />
    );
    
    // Act
    await user.click(screen.getByText('AAPL'));
    
    // Assert
    expect(mockOnRowClick).toHaveBeenCalledWith('AAPL');
  });
});
```

---

## Security Testing

### Testing Decimal Precision (S-009)

```python
def test_decimal_precision_eliminated():
    """Verify 0.1 + 0.2 = 0.3 exactly"""
    result = safe_add(0.1, 0.2)
    assert result == Decimal('0.3')

def test_financial_calculation_precision():
    """Test portfolio calculations maintain precision"""
    holdings = [
        {'shares': 0.1, 'price': 100.00},
        {'shares': 0.2, 'price': 200.00},
    ]
    result = calculate_portfolio_value(holdings)
    assert result['total_value'] == Decimal('50.00')  # 0.1*100 + 0.2*200 = 50

def test_no_float_in_financial_code():
    """Verify no float() usage in financial calculations"""
    # This should be a static analysis check
    assert not uses_float_in_calculations('src/utils/financial.py')
```

### Testing Token Security (S-010)

```python
@pytest.mark.asyncio
async def test_no_token_race_condition():
    """Test that concurrent token refreshes don't cause race conditions"""
    async def refresh_token():
        return await token_service.refresh()
    
    # Simulate 10 concurrent refresh requests
    tasks = [refresh_token() for _ in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # All should succeed or fail gracefully (no partial states)
    for result in results:
        assert isinstance(result, (Token, TokenRefreshError))
        assert not isinstance(result, Exception)
```

### Testing Logging (S-011)

```python
def test_no_print_statements_in_production():
    """Verify no print() in production code"""
    source_files = find_python_files('src/', exclude=['tests/'])
    
    for file in source_files:
        content = file.read()
        assert 'print(' not in content, f"print() found in {file}"

def test_logging_uses_proper_levels():
    """Verify logging uses appropriate levels"""
    # INFO for normal operations
    # WARNING for concerning conditions
    # ERROR for failures
    # DEBUG for detailed debugging
    
    logger = logging.getLogger('test_module')
    
    # Test that logger methods exist and work
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'debug')
```

---

## Common Patterns

### API Testing

```python
from django.test import APIClient

@pytest.mark.django_db
def test_api_endpoint():
    """Test API endpoint returns correct data"""
    client = APIClient()
    
    # Make request
    response = client.get('/api/portfolio/')
    
    # Assert response
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
```

### Database Testing

```python
@pytest.mark.django_db
def test_model_creation():
    """Test model creation and database storage"""
    portfolio = Portfolio.objects.create(
        name='Test Portfolio',
        user=test_user
    )
    
    assert portfolio.id is not None
    assert portfolio.created_at is not None
    
    # Verify in database
    db_portfolio = Portfolio.objects.get(id=portfolio.id)
    assert db_portfolio.name == 'Test Portfolio'
```

### Exception Testing

```python
def test_exception_handling():
    """Test that exceptions are handled properly"""
    with pytest.raises(ValueError):
        calculate_portfolio_value(None)
    
    # Test graceful degradation
    result = safe_divide(Decimal('100'), Decimal('0'))
    assert result == Decimal('0')
```

---

## Best Practices

### DO
- Write tests before fixing bugs
- Use descriptive test names
- Test edge cases and error conditions
- Keep tests fast and independent
- Use fixtures for common setup
- Mock external dependencies
- Aim for meaningful coverage

### DON'T
- Skip tests for "obvious" fixes
- Write tests that only pass by coincidence
- Make tests dependent on each other
- Test multiple things in one test
- Leave commented-out test code
- Ignore test failures

---

## Coverage Requirements

| Type | Minimum | Recommended |
|------|---------|-------------|
| Unit Tests | 60% | 80% |
| Integration Tests | 20% | 30% |
| Critical Paths | 100% | 100% |

---

## Reporting Issues

If you find issues during testing:

1. **Document clearly:** What failed, how to reproduce
2. **Include context:** Test case, environment, data
3. **Tag appropriately:** Bug, Feature, Security
4. **Report to:** GRACE + GAUDÍ

---

**GRACE - QA/Testing Engineer**
**Quality is not an act, it's a habit.**
