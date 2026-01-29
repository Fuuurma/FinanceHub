# FinanceHub - Reference Examples

## Location

`/Users/sergi/Desktop/Projects/FinanceHub/Backend/src/core/api/examples/`

## Overview

Reference examples for Django Ninja core infrastructure patterns. No existing code modified.

## Patterns

| Pattern | File | Description |
|---------|------|-------------|
| FilterSchema | `filters.py` | Django Ninja filtering |
| Response Envelopes | `endpoints.py` | Consistent API |
| Custom Exceptions | `endpoints.py` | Centralized errors |
| Structured Logging | `endpoints.py` | JSON logs |
| Pagination | `endpoints.py` | Built-in pagination |
| Testing | `tests.py` | Test examples |

## File Index

- `__init__.py` - Package marker
- `README.md` - This file
- `GUIDE.md` - Migration guide
- `filters.py` - FilterSchema examples
- `endpoints.py` - Endpoint examples
- `tests.py` - Test examples
- `INDEX.md` - Navigation

## Response Formats

### Success
```json
{"success": true, "data": {...}, "message": "OK", "timestamp": "..."}
```

### Error
```json
{"success": false, "error": "...", "code": "...", "timestamp": "..."}
```

## Related

- Backend Guide: `/Users/sergi/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md`
- FilterSchema: `/Users/sergi/Desktop/Projects/development-guides/cheatsheets/DJANGO-NINJA-FILTER-SCHEMA.md`
- QArt Examples: `/Users/sergi/Desktop/Projects/QArt/QART-backend/qart/api/endpoints/examples/`
- LinkUp Examples: `/Users/sergi/Desktop/Projects/LinkUp/backend/src/core/api/examples/`
- Restaurant Examples: `/Users/sergi/Desktop/Projects/RestaurantManagement/Backend/backend/api/examples/`

## Important

1. Reference only - do not modify existing code
2. Use patterns for new endpoints only
