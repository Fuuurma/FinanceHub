# Task S-011: Narrow Exception Handling

**Task ID:** S-011
**Priority:** P1 (HIGH)
**Status:** ✅ APPROVED - Ready for Coder Assignment
**Estimated Time:** 3-4 hours
**Action:** Replace 662 broad `except Exception` with specific exception handling

---

## Overview
Replace all broad `except Exception` patterns with specific exception types to prevent silent failures and improve debugging.

## Files to Modify
- `migrations/timescale_migration.py` - 12 instances
- `tasks/ai_template_generation.py` - 8 instances
- Multiple API and service files

## Key Changes
```python
# Before
try:
    operation()
except Exception as e:
    pass  # Silent failure!

# After  
try:
    operation()
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise
except TimeoutError as e:
    logger.warning(f"Operation timeout: {e}")
    raise
```

## Acceptance Criteria
- [ ] No bare `except Exception` in production code
- [ ] All exceptions properly logged
- [ ] Tests verify exception handling
