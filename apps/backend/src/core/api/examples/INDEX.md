# FinanceHub - Example Files Index

## Location

`/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/core/api/examples/`

## File Structure

```
examples/
├── __init__.py    Package marker
├── README.md      Quick reference
├── GUIDE.md       Migration guide
├── filters.py     FilterSchema examples
├── endpoints.py   Endpoint examples
├── tests.py       Test examples
└── INDEX.md       This file
```

## Patterns

| Pattern | File | Description |
|---------|------|-------------|
| FilterSchema | `filters.py` | Django Ninja built-in filtering |
| Response Envelopes | `endpoints.py`, `GUIDE.md` | Consistent API responses |
| Custom Exceptions | `endpoints.py` | Centralized error handling |
| Structured Logging | `endpoints.py` | JSON-formatted logs |
| Pagination | `endpoints.py` | Built-in pagination |
| Testing | `tests.py` | Test examples |

## Exception Reference

```python
NotFoundException(resource, id)      # 404
ValidationException(message, field)  # 422
DuplicateException(resource, f, v)   # 409
BadRequestException(message)         # 400
```

## Response Formats

### Success
```json
{"success": true, "data": {...}, "message": "OK", "timestamp": "..."}
```

### Error
```json
{"success": false, "error": "...", "code": "...", "timestamp": "..."}
```

## Related Documentation

- Backend Guide: `/Users/sergi/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md`
- FilterSchema Guide: `/Users/sergi/Desktop/Projects/development-guides/cheatsheets/DJANGO-NINJA-FILTER-SCHEMA.md`
- QArt Examples: `/Users/sergi/Desktop/Projects/QArt/QART-backend/qart/api/endpoints/examples/`
- LinkUp Examples: `/Users/sergi/Desktop/Projects/LinkUp/backend/src/core/api/examples/`
- Restaurant Examples: `/Users/sergi/Desktop/Projects/RestaurantManagement/Backend/backend/api/examples/`

## Quick Start

1. Read `README.md` for overview
2. Read `GUIDE.md` for migration
3. See `endpoints.py` for examples
4. Use `filters.py` as template

## Important Notes

1. Reference only - do not modify existing code
2. Use patterns for new endpoints only
3. Gradual migration recommended
