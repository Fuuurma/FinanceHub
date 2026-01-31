# Task S-009: Decimal Financial Calculations

**Task ID:** S-009
**Assigned To:** Backend Coder (1 Coder)
**Priority:** P0 (CRITICAL)
**Status:** ✅ APPROVED - Ready for Coder Assignment
**Created:** 2026-01-30
**Estimated Time:** 3-4 hours

---

## Overview

Replace all `float()` usage in financial calculations with `Decimal()` to prevent precision errors that could lead to incorrect trading decisions.

## Why This Matters

### Current Vulnerability
**Location:** Multiple files
- `apps/backend/src/investments/tasks/finnhub_tasks.py`
- `apps/backend/src/investments/models/alert.py`
- `apps/backend/src/investments/tasks/news_tasks.py`

**Issue:** Using `float()` for financial values:

```python
"signal": float(signal_value) if signal_value else None,
"upper": float(upper_band),
"histogram": float(macd_value - signal_value)
```

**Risk Assessment:**
| Factor | Score | Impact |
|--------|-------|--------|
| Exploitability | 🟡 MEDIUM | Requires specific conditions |
| Impact | 🔴 CRITICAL | Financial loss possible |
| Likelihood | 🟡 MEDIUM | Precision errors common |
| **Overall** | 🔴 **CRITICAL** | **Immediate action required** |

### The Float Problem
```python
>>> 0.1 + 0.2
0.30000000000000004  # NOT 0.3!

>>> float(1.0) + float(2.0)
3.0  # Works for integers

>>> format(0.1 + 0.2, '.20f')
'0.30000000000000004441'  # Precision loss!
```

### Impact on Financial Systems
- Incorrect portfolio values
- Wrong trading signals
- Incorrect stop-loss calculations
- Regulatory compliance issues
- Financial loss

---

## Task Requirements

### Phase 1: Create Decimal Utility (30 min)

#### 1.1 Create Financial Utility Module
**File:** `apps/backend/src/utils/financial.py`

```python
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional, Union

Number = Union[int, float, str, Decimal]

def to_decimal(value: Optional[Number], default: Decimal = Decimal('0')) -> Decimal:
    """Convert value to Decimal, handling all types safely"""
    if value is None:
        return default
    
    if isinstance(value, Decimal):
        return value
    
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    
    if isinstance(value, str):
        try:
            # Handle currency formatting
            cleaned = value.replace('$', '').replace(',', '').strip()
            return Decimal(cleaned)
        except InvalidOperation:
            return default
    
    return default

def safe_add(a: Optional[Number], b: Optional[Number]) -> Decimal:
    """Safely add two numbers"""
    return to_decimal(a) + to_decimal(b)

def safe_subtract(a: Optional[Number], b: Optional[Number]) -> Decimal:
    """Safely subtract two numbers"""
    return to_decimal(a) - to_decimal(b)

def safe_multiply(a: Optional[Number], b: Optional[Number]) -> Decimal:
    """Safely multiply two numbers"""
    return to_decimal(a) * to_decimal(b)

def safe_divide(a: Optional[Number], b: Optional[Number], 
               default: Decimal = Decimal('0')) -> Decimal:
    """Safely divide, avoiding division by zero"""
    divisor = to_decimal(b)
    if divisor == 0:
        return default
    return to_decimal(a) / divisor

def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """Round Decimal to specified decimal places"""
    quantizer = Decimal(10) ** -places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)

def format_currency(value: Decimal, currency: str = '$') -> str:
    """Format Decimal as currency string"""
    return f"{currency}{value:,.2f}"

def format_percentage(value: Decimal, places: int = 2) -> str:
    """Format Decimal as percentage"""
    return f"{round_decimal(value * 100, places)}%"
```

---

### Phase 2: Update Finnhub Tasks (1 hour)

#### 2.1 Update Technical Indicators
**File:** `apps/backend/src/investments/tasks/finnhub_tasks.py`

```python
from utils.financial import to_decimal, round_decimal

def calculate_bollinger_bands(prices: list, period: int = 20, std_dev: float = 2.0):
    """Calculate Bollinger Bands with Decimal precision"""
    # Convert to Decimal
    price_decimals = [to_decimal(p) for p in prices]
    
    # Calculate middle band (SMA)
    sma = sum(price_decimals[-period:]) / period
    
    # Calculate standard deviation
    variance = sum((p - sma) ** 2 for p in price_decimals[-period:]) / period
    std = variance.sqrt()  # Decimal sqrt
    
    # Calculate bands
    upper_band = round_decimal(sma + (std * to_decimal(std_dev)))
    lower_band = round_decimal(sma - (std * to_decimal(std_dev)))
    middle_band = round_decimal(sma)
    
    return {
        "upper": upper_band,
        "middle": middle_band,
        "lower": lower_band,
        "bandwidth": upper_band - lower_band,
        "percent_b": round_decimal(
            (last_price - lower_band) / (upper_band - lower_band) 
            if upper_band != lower_band else Decimal('0.5')
        )
    }

def calculate_macd(prices: list, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD with Decimal precision"""
    price_decimals = [to_decimal(p) for p in prices]
    
    # Calculate EMAs using Decimal
    def calc_ema(prices_list, period):
        multiplier = Decimal('2') / (period + 1)
        ema = prices_list[0]
        for price in prices_list[1:]:
            ema = (price * multiplier) + (ema * (Decimal('1') - multiplier))
        return ema
    
    fast_ema = calc_ema(price_decimals[-fast:], fast)
    slow_ema = calc_ema(price_decimals[-slow:], slow)
    
    macd_line = fast_ema - slow_ema
    signal_line = calc_ema([macd_line], signal)  # Simplified
    
    histogram = macd_line - signal_line
    
    return {
        "macd": round_decimal(macd_line),
        "signal": round_decimal(signal_line),
        "histogram": round_decimal(histogram),
        "crossover": "bullish" if macd_line > signal_line else "bearish"
    }
```

---

### Phase 3: Update Alert Model (1 hour)

#### 3.1 Update Alert Evaluation
**File:** `apps/backend/src/investments/models/alert.py`

```python
from utils.financial import to_decimal, round_decimal

class PriceAlert(UUIDModel, TimestampedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)  # 'above', 'below'
    condition_value = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        help_text="Price level to trigger alert"
    )
    is_active = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    triggered_value = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        null=True,
        blank=True
    )

    def should_trigger(self, current_value: float) -> bool:
        """Check if alert should trigger with Decimal precision"""
        current = to_decimal(current_value)
        trigger_value = to_decimal(self.condition_value)
        
        if self.alert_type == 'above':
            return current >= trigger_value
        elif self.alert_type == 'below':
            return current <= trigger_value
        return False

    def get_triggered_value_formatted(self) -> str:
        """Format triggered value as currency"""
        if self.triggered_value:
            return f"${round_decimal(self.triggered_value):,.2f}"
        return "N/A"
```

---

### Phase 4: Update News Tasks (30 min)

#### 4.1 Update Sentiment Scores
**File:** `apps/backend/src/investments/tasks/news_tasks.py`

```python
from utils.financial import to_decimal, round_decimal

def calculate_sentiment_score(sentiment_data: dict) -> dict:
    """Calculate sentiment score with Decimal precision"""
    # Convert all values to Decimal
    compound = to_decimal(sentiment_data.get('compound', 0))
    positive = to_decimal(sentiment_data.get('positive', 0))
    negative = to_decimal(sentiment_data.get('negative', 0))
    neutral = to_decimal(sentiment_data.get('neutral', 0))
    
    # Normalize scores
    total = positive + negative + neutral
    if total > 0:
        positive_pct = round_decimal(positive / total * 100)
        negative_pct = round_decimal(negative / total * 100)
        neutral_pct = round_decimal(neutral / total * 100)
    else:
        positive_pct = negative_pct = neutral_pct = Decimal('0')
    
    # Sentiment classification
    if compound >= Decimal('0.05'):
        sentiment = 'positive'
    elif compound <= Decimal('-0.05'):
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'sentiment': sentiment,
        'score': round_decimal(compound, 4),
        'positive_pct': positive_pct,
        'negative_pct': negative_pct,
        'neutral_pct': neutral_pct
    }
```

---

### Phase 5: Update Portfolio Calculations (30 min)

#### 5.1 Update Portfolio Value Calculations
**File:** `apps/backend/src/portfolios/services/calculator.py`

```python
from utils.financial import (
    to_decimal, safe_add, safe_subtract, 
    safe_multiply, safe_divide, round_decimal
)

class PortfolioCalculator:
    def calculate_portfolio_value(self, holdings: list) -> dict:
        """Calculate total portfolio value with Decimal precision"""
        total_value = Decimal('0')
        total_cost = Decimal('0')
        
        for holding in holdings:
            shares = to_decimal(holding.shares)
            price = to_decimal(holding.current_price)
            cost_basis = to_decimal(holding.cost_basis)
            
            value = safe_multiply(shares, price)
            total_value = safe_add(total_value, value)
            total_cost = safe_add(total_cost, cost_basis)
        
        total_pnl = safe_subtract(total_value, total_cost)
        total_pnl_pct = safe_divide(
            total_pnl, 
            total_cost, 
            Decimal('0')
        ) * 100 if total_cost > 0 else Decimal('0')
        
        return {
            'total_value': round_decimal(total_value),
            'total_cost': round_decimal(total_cost),
            'total_pnl': round_decimal(total_pnl),
            'total_pnl_percent': round_decimal(total_pnl_pct, 2),
            'holdings_count': len(holdings)
        }
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `apps/backend/src/utils/financial.py` | Decimal financial utilities |

## Files to Modify

| File | Changes |
|------|---------|
| `apps/backend/src/investments/tasks/finnhub_tasks.py` | Replace float() with Decimal() |
| `apps/backend/src/investments/models/alert.py` | Use Decimal in calculations |
| `apps/backend/src/investments/tasks/news_tasks.py` | Use Decimal in sentiment |
| `apps/backend/src/portfolios/services/calculator.py` | Use Decimal in portfolio |

## Acceptance Criteria

- [ ] All financial calculations use Decimal
- [ ] No float() in financial code paths
- [ ] Precision errors eliminated
- [ ] Tests verify precision
- [ ] Documentation updated

---

## Testing Requirements

### Unit Tests
```python
def test_decimal_precision():
    """Test that Decimal precision is maintained"""
    result = safe_add(0.1, 0.2)
    assert result == Decimal('0.3')

def test_currency_calculation():
    """Test portfolio value calculation"""
    calculator = PortfolioCalculator()
    result = calculator.calculate_portfolio_value(holdings)
    
    assert isinstance(result['total_value'], Decimal)
    assert result['total_pnl'] == result['total_value'] - result['total_cost']

def test_division_by_zero():
    """Test safe division handling"""
    result = safe_divide(100, 0)
    assert result == Decimal('0')
```

---

## Rollback Plan

If issues occur:
1. Revert to float() temporarily
2. Add fallback: `try: Decimal() except: float()`
3. Gradual migration with feature flag

---

## Questions for Gaudí

1. Should I proceed with implementing S-009?
2. Should we migrate all financial fields to DecimalField in models?
3. Should we add precision validation in serializers?

---

**Task S-009 Created: Ready for Approval**

**Status:** ⏳ Waiting for Gaudí's decision
**Priority:** P0 (CRITICAL) - Prevents financial precision errors
