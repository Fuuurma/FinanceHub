# 📋 Task Assignment: S-012 Input Validation

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Guido (Backend Coder)
**Priority:** HIGH - Security Critical
**Estimated Effort:** 4-6 hours
**Timeline:** Start after C-037 completion, no deadline (quality-driven)

---

## 🎯 OVERVIEW

Add comprehensive Pydantic validation to all API endpoints to prevent injection attacks and ensure data integrity.

**Context:**
- Security audit identified missing input validation
- Charo approved this task as P1 HIGH priority
- Prevents SQL injection, XSS, and malformed data attacks

---

## 📋 YOUR TASKS

### Task 1: Audit All API Endpoints (1h)

**Files to check:**
```
apps/backend/src/api/
├── __init__.py
├── portfolio.py
├── trading.py
├── assets.py
├── social_sentiment.py
└── brokers.py
```

**For each endpoint:**
1. List all request bodies (POST/PUT/PATCH)
2. List all query parameters (GET)
3. List all path parameters
3. Identify which have validation, which don't

**Create checklist:**
```markdown
- [ ] portfolio.py - 5 endpoints
- [ ] trading.py - 8 endpoints
- [ ] assets.py - 12 endpoints
- [ ] social_sentiment.py - 7 endpoints
- [ ] brokers.py - 6 endpoints
```

### Task 2: Create Validation Schemas (2-3h)

**For each endpoint, create Pydantic schema:**

**Example Pattern:**
```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional

class CreateOrderSchema(BaseModel):
    """Schema for creating paper trading order"""

    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    order_type: str = Field(..., regex="^(market|limit|stop)$", description="Order type")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    price: Optional[Decimal] = Field(None, gt=0, description="Limit price (required for limit orders)")
    side: str = Field(..., regex="^(buy|sell)$", description="Order side")

    @validator('price')
    def validate_limit_price(cls, v, values):
        if values.get('order_type') == 'limit' and v is None:
            raise ValueError('Price required for limit orders')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "order_type": "limit",
                "quantity": 10,
                "price": "150.25",
                "side": "buy"
            }
        }
```

**Validation Requirements:**
- **Strings:** min_length, max_length, regex patterns
- **Numbers:** gt (greater than), lt (less than), ge (greater or equal)
- **Emails:** EmailStr type
- **URLs:** HttpUrl type
- **Dates:** date, datetime types
- **Decimals:** Decimal type for financial data

**Critical Endpoints to Validate:**
1. **Trading API:**
   - POST /api/trading/orders (create order)
   - DELETE /api/trading/orders/{id} (cancel order)
   - POST /api/trading/positions/close (close position)

2. **Portfolio API:**
   - POST /api/portfolio (create portfolio)
   - PUT /api/portfolio/{id} (update portfolio)

3. **Social Sentiment API:**
   - POST /api/sentiment/analyze (analyze sentiment)
   - GET /api/sentiment/data/{symbol} (get sentiment data)

4. **Broker API:**
   - POST /api/brokers/connect (connect broker)
   - POST /api/brokers/orders (execute real order)

### Task 3: Apply Validation to Endpoints (2-3h)

**Update each endpoint to use schema:**

**Before:**
```python
@router.post("/orders")
def create_order(request: HttpRequest, data: dict):
    order = PaperTradingOrder.objects.create(**data)
    return order
```

**After:**
```python
@router.post("/orders")
def create_order(request: HttpRequest, data: CreateOrderSchema):
    """Create new paper trading order with validation"""
    order = PaperTradingOrder.objects.create(
        user=request.user,
        symbol=data.symbol,
        order_type=data.order_type,
        quantity=data.quantity,
        price=data.price,
        side=data.side
    )
    return order
```

**Benefits:**
- Automatic validation before reaching business logic
- Clear error messages for clients
- OpenAPI schema generation for documentation
- Type safety

### Task 4: Add Error Handling (1h)

**Create validation error handler:**

```python
# apps/backend/src/api/exceptions.py
from ninja import errors
from pydantic import ValidationError

@router.exception_handler(ValidationError)
def validation_error(request, exc):
    """Return clear validation errors"""
    return {
        "error": "Validation Error",
        "details": exc.errors()
    }, 422
```

**Return format:**
```json
{
  "error": "Validation Error",
  "details": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] All POST/PUT/PATCH endpoints have Pydantic schemas
- [ ] All query parameters validated
- [ ] All path parameters validated
- [ ] Error handler returns clear validation messages
- [ ] OpenAPI schema includes validation rules
- [ ] Test invalid inputs (negative numbers, empty strings, etc.)
- [ ] No unvalidated user input reaches business logic

---

## 🧪 TESTING

**Test cases:**
```python
def test_invalid_order_quantity():
    """Test that negative quantities are rejected"""
    response = client.post("/api/trading/orders", json={
        "symbol": "AAPL",
        "order_type": "market",
        "quantity": -10,  # Invalid
        "side": "buy"
    })
    assert response.status_code == 422
    assert "quantity" in response.json()["details"][0]["loc"]

def test_missing_limit_price():
    """Test that limit orders require price"""
    response = client.post("/api/trading/orders", json={
        "symbol": "AAPL",
        "order_type": "limit",  # Requires price
        "quantity": 10,
        "side": "buy"
        # Missing price
    })
    assert response.status_code == 422
    assert "price" in response.json()["details"][0]["loc"]
```

---

## 📚 REFERENCES

**Pydantic Documentation:**
- https://docs.pydantic.dev/latest/concepts/validators/
- https://docs.pydantic.dev/latest/concepts/json_schema/

**Django Ninja Validation:**
- https://django-ninja.rest-framework.com/guides/input/

**Security Best Practices:**
- Validate ALL user input
- Whitelist allowed values (not blacklist)
- Use strict validation (reject, don't sanitize)
- Return clear error messages (but don't expose internals)

---

## 🚨 SECURITY NOTES

**Critical validations:**
- **Financial data:** Must use Decimal, never float
- **Symbols:** Must match format (e.g., 1-10 uppercase letters)
- **Emails:** Must be valid email format
- **URLs:** Must be valid URL format
- **Dates:** Must be valid dates, not future dates for historical data
- **User input:** Sanitize HTML, prevent XSS

**Prevent:**
- SQL injection (validate query parameters)
- XSS (validate HTML/JSON input)
- Mass assignment (only allow expected fields)
- Type confusion (validate types, don't coerce)

---

## 📊 DELIVERABLES

1. ✅ Validation schemas for all endpoints
2. ✅ Updated endpoint handlers with schemas
3. ✅ Validation error handler
4. ✅ Test cases for invalid inputs
5. ✅ Updated API documentation (auto-generated from schemas)

---

## ✅ COMPLETION CHECKLIST

Before marking complete:
- [ ] All endpoints audited
- [ ] All POST/PUT/PATCH endpoints have schemas
- [ ] All GET query parameters validated
- [ ] Error handler configured
- [ ] Tests pass with invalid inputs
- [ ] API docs show validation rules
- [ ] No unvalidated user input
- [ ] Code reviewed by Charo (Security)

---

**Next Task:** S-013 Rate Limiting

---

**Questions?** Ask in COMMUNICATION_HUB.md

**Status Updates:** Add to COMMUNICATION_HUB.md Agent Updates section

**When Complete:** Update TASK_TRACKER.md, notify GAUDÍ
