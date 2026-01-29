# Migration Guide: FinanceHub Django Ninja Patterns

## Overview

Guide for integrating core patterns into FinanceHub endpoints.

Location: `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/core/api/examples/`

## Step 1: Import Core

```python
from core import (
    create_success_response,
    create_error_response,
    ErrorCode,
    NotFoundException,
    ValidationException,
    get_logger,
    LogCategory,
    CustomPageNumberPagination,
)
```

## Step 2: Error Handling

### Before
```python
@router.get("/portfolios/{portfolio_id}")
def get_portfolio(request, portfolio_id: int):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
        return {"success": True, "data": portfolio.to_dict()}
    except Portfolio.DoesNotExist:
        return {"success": False, "error": "Not found"}, 404
```

### After
```python
@router.get("/portfolios/{portfolio_id}")
def get_portfolio(request, portfolio_id: int):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
        return create_success_response(data=portfolio.to_dict())
    except Portfolio.DoesNotExist:
        raise NotFoundException("Portfolio", portfolio_id)
```

## Step 3: Filtering

### Before (Custom Pydantic)
```python
class PortfolioFilter(BaseModel):
    status: Optional[str] = None
```

### After (FilterSchema)
```python
from ninja import FilterSchema, Query
from pydantic import Field

class PortfolioFilter(FilterSchema):
    status: Optional[str] = None
    search: Optional[str] = Field(None, q="name__icontains,description__icontains")
    order_by: Optional[str] = Field(None, order_by="created_at,-created_at,name")
```

## Step 4: Logging

```python
from core import get_logger, LogCategory

logger = get_logger("portfolios", category=LogCategory.API)

@router.get("/portfolios/{portfolio_id}")
def get_portfolio(request, portfolio_id: int):
    logger.info("Retrieving portfolio", extra={"portfolio_id": portfolio_id})
```

## Exception Reference

| Exception | Status Code |
|-----------|-------------|
| NotFoundException | 404 |
| ValidationException | 422 |
| DuplicateException | 409 |
| BadRequestException | 400 |

## Related Files

- Examples: `/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/core/api/examples/`
- Backend Guide: `/Users/sergi/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md`
