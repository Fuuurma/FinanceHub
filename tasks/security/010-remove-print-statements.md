# Task S-010: Remove Print Statements & Use Logging

**Task ID:** S-010
**Assigned To:** Any Developer (1 Developer)
**Priority:** P0 (CRITICAL)
**Status:** ✅ APPROVED - Ready for Coder Assignment
**Created:** 2026-01-30
**Estimated Time:** 1-2 hours

---

## Overview

Replace all `print()` statements in production code with proper logging to prevent information leakage in production environments.

## Why This Matters

### Current Vulnerability
**Location:** `apps/backend/src/migrations/timescale_migration.py`

**Issue:** Production code contains print statements:

```python
print(f"  - Hypertables created: {len(result['validation']['hypertables_created'])}")
print(f"  - Continuous aggregates: {len(result['validation']['continuous_aggregates'])}")
print(f"\n✗ Migration failed: {result['error']}")
```

**Risk Assessment:**
| Factor | Score | Impact |
|--------|-------|--------|
| Exploitability | 🟡 MEDIUM | Requires access to logs/stdout |
| Impact | 🟠 HIGH | Information disclosure |
| Likelihood | 🟡 MEDIUM | Common in production |
| **Overall** | 🔴 **CRITICAL** | **Immediate action required** |

### Impact of Print Statements in Production
1. **Information Disclosure:** System details exposed to attackers
2. **Log Pollution:** print() output mixes with application logs
3. **Performance:** print() is synchronous and slow
4. **Debug Info:** Internal paths, versions, configurations leaked
5. **No Log Levels:** Cannot filter by severity

### Real-World Attack
```
# Attacker analyzes logs
✗ Migration failed: Database connection failed to postgres:5432
# Attacker knows: Database type, port, potential vulnerability
```

---

## Task Requirements

### Phase 1: Audit Print Statements (15 min)

#### 1.1 Find All Print Statements
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/backend/src
grep -rn "print(" --include="*.py" | grep -v "test" | grep -v ".pyc"
```

**Found in:**
- `migrations/timescale_migration.py` - 15 print statements
- `tasks/ai_template_generation.py` - 2 print statements
- `utils/management/commands/seed_top_stocks.py` - 5 print statements

### Phase 2: Replace with Logging (45 min)

#### 2.1 Update Migration File
**File:** `apps/backend/src/migrations/timescale_migration.py`

**Before:**
```python
import logging
logger = logging.getLogger(__name__)

# Replace print with logger
print(f"  - Hypertables created: {len(result['validation']['hypertables_created'])}")
```

**After:**
```python
import logging
logger = logging.getLogger(__name__)

# Replace with proper logging
logger.info(
    f"Hypertables created: {len(result['validation']['hypertables_created'])}"
)

# For errors
logger.error(f"Migration failed: {result['error']}")
logger.exception("Migration error details", exc_info=True)
```

#### 2.2 Update Print Patterns

| Old Pattern | New Pattern |
|-------------|-------------|
| `print("✓ Success")` | `logger.info("Migration completed successfully")` |
| `print(f"Value: {x}")` | `logger.debug(f"Value: {x}")` |
| `print(f"✗ Error: {e}")` | `logger.error(f"Error: {e}")` |
| `print(f"\nStatus: {status}")` | `logger.info(f"Status: {status}")` |

### Phase 3: Verify Logging Configuration (15 min)

#### 3.1 Check Logging Config
**File:** `apps/backend/src/core/settings.py`

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/financehub.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'financehub': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## Files to Modify

| File | Print Statements | Changes |
|------|-----------------|---------|
| `migrations/timescale_migration.py` | 15 | Replace with logger |
| `tasks/ai_template_generation.py` | 2 | Replace with logger |
| `utils/management/commands/seed_top_stocks.py` | 5 | Replace with logger |

## Acceptance Criteria

- [ ] No print() statements in production code
- [ ] All logging uses proper log levels
- [ ] Logs written to configured handlers
- [ ] No sensitive data in log messages
- [ ] Tests verify logging behavior

---

## Testing

### Verify No Print Statements
```bash
cd apps/backend/src
grep -rn "print(" --include="*.py" | grep -v test | grep -v ".pyc"
# Should return no results (excluding test files)
```

### Verify Logging Works
```python
# Test logging configuration
import logging
logger = logging.getLogger(__name__)
logger.info("Test message")
# Should appear in console and logs/financehub.log
```

---

## Rollback Plan

If issues occur:
1. Restore from version control
2. `git checkout -- <file>`
3. Re-run migrations

---

## Questions for Gaudí

1. Should I proceed with implementing S-010?
2. Should we also add log aggregation (e.g., to cloudwatch/sentry)?
3. Should we implement log rotation?

---

**Task S-010 Created: Ready for Approval**

**Status:** ⏳ Waiting for Gaudí's decision
**Priority:** P0 (CRITICAL) - Prevents information disclosure
