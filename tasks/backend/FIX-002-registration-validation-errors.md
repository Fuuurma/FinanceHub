# Task: Improve User Registration Error Handling

**Priority:** MEDIUM
**Status:** OPEN
**Assigned To:** Backend Team
**Created:** February 1, 2026
**Estimated Time:** 2-3 hours

## Problem

User registration works for valid data, but validation errors are not properly caught and return 500 errors instead of 4xx validation errors.

### Current Behavior

**Valid registration:** ✅ Works
```json
{
  "id": "8ca1e439-952e-46c2-9841-88ddd3e2f199",
  "username": "dbtest",
  "email": "dbtest@example.com",
  "first_name": "DB",
  "last_name": "Test",
  "message": "User registered successfully"
}
```

**Invalid registration (weak password):** ❌ Returns 500 instead of 422
```json
{
  "error": {
    "code": "database_error",
    "message": "Database error",
    "status": 500
  }
}
```

### Expected Behavior

Validation errors should be caught by Pydantic validators and return 422 (Unprocessable Entity) with clear error messages.

## Root Cause

The `RegisterIn` schema has validators for:
1. Password strength (uppercase, lowercase, digit, special char)
2. Password confirmation matching

But when these validators fail, the error isn't being caught properly and the code attempts database operations, leading to IntegrityError.

## Investigation Tasks

1. [ ] Check if Pydantic validators are being called
2. [ ] Verify error handling in the register endpoint
3. [ ] Check error handler middleware configuration
4. [ ] Test all validation scenarios

## Fix Requirements

### 1. Test Pydantic Validation
```python
# Test that validators work
from users.schemas.register import RegisterIn

# Should fail with weak password
try:
    RegisterIn(
        username="test",
        email="test@example.com",
        password="weak",
        password_confirm="weak"
    )
except ValidationError as e:
    print(e)  # Should show password validation errors
```

### 2. Improve Error Handling in Register Endpoint

File: `/apps/backend/src/users/api/auth/register.py`

Current code (lines 38-54):
```python
@router.post("/register", response=RegisterOut)
def register(request, payload: RegisterIn):
    user = UserService.create_user(payload.model_dump())
    # ... logging
    return RegisterOut(...)
```

**Should add:**
- Try/except block for IntegrityError
- Proper validation error handling
- Clear error messages for users

### 3. Test Cases

- [ ] Weak password (no uppercase)
- [ ] Weak password (no lowercase)
- [ ] Weak password (no digit)
- [ ] Weak password (no special char)
- [ ] Passwords don't match
- [ ] Missing required fields
- [ ] Invalid email format
- [ ] Duplicate username
- [ ] Duplicate email
- [ ] Valid registration (should work)

## Implementation

### Option 1: Fix in Endpoint (Recommended)

```python
@router.post("/register", response=RegisterOut)
def register(request, payload: RegisterIn):
    try:
        user = UserService.create_user(payload.model_dump())
        # ... logging and return
    except IntegrityError as e:
        if "email" in str(e):
            raise ValidationError("Email already registered", code="email_exists")
        elif "username" in str(e):
            raise ValidationError("Username already taken", code="username_exists")
        else:
            raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise
```

### Option 2: Improve UserService

Add duplicate checking in `UserService.create_user()` before attempting to create.

## Success Criteria

✅ Validation errors return 422 status code
✅ Clear error messages for each validation failure
✅ Duplicate email/username returns proper error
✅ Valid registration still works
✅ No 500 errors for validation failures

## Files to Modify

1. `/apps/backend/src/users/api/auth/register.py` - Add error handling
2. `/apps/backend/src/utils/services/user.py` - Add duplicate checking
3. `/apps/backend/src/users/schemas/register.py` - Verify validators work

## Testing Script

```bash
# Test weak password
curl -X POST 'http://localhost:8000/users/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "weakpass",
    "email": "weak@example.com",
    "password": "weak",
    "password_confirm": "weak"
  }'

# Expected: 422 with validation errors
# Actual: 500 database error
```

## Related Tasks

- TEST-001: Test All Backend API Endpoints (broader testing task)
- Previous fix: User Registration Pydantic V2 compatibility

## Priority Context

This is MEDIUM priority because:
- Registration works for valid data ✅
- Users can still register ✅
- But error messages are poor ❌
- Validation doesn't provide clear feedback ❌
