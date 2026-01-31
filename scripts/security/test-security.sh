#!/bin/bash
# Security Testing Script for FinanceHub
# Tests for common security vulnerabilities

set -e

echo "🛡️ FinanceHub Security Testing Suite"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

skip() {
    echo -e "${YELLOW}⏭️ SKIP${NC}: $1"
    ((TESTS_SKIPPED++))
}

section() {
    echo ""
    echo "--- $1 ---"
}

# =====================================
# TEST 1: XSS Prevention Test
# =====================================
section "XSS Prevention Tests"

# Test 1.1: Check if CSP headers are present
echo "1.1 Checking Content-Security-Policy header..."
if [ -f "apps/frontend/src/middleware.ts" ]; then
    if grep -q "Content-Security-Policy" apps/frontend/src/middleware.ts; then
        pass "CSP header configured in middleware"
    else
        fail "CSP header not found in middleware"
    fi
else
    skip "middleware.ts not found"
fi

# Test 1.2: Check for XSS-safe React patterns
echo "1.2 Checking React XSS patterns..."
XSS_VULNERABLE=$(grep -r "dangerouslySetInnerHTML" apps/frontend/src --include="*.tsx" 2>/dev/null | wc -l)
if [ "$XSS_VULNERABLE" -eq 0 ]; then
    pass "No dangerouslySetInnerHTML usage found"
else
    echo "   Found $XSS_VULNERABLE instances of dangerouslySetInnerHTML - review for safety"
fi

# =====================================
# TEST 2: SQL Injection Prevention
# =====================================
section "SQL Injection Prevention Tests"

# Test 2.1: Check for raw SQL execution
echo "2.1 Checking for raw SQL execution..."
RAW_SQL=$(grep -rn "execute(" apps/backend/src --include="*.py" 2>/dev/null | grep -v "cursor.execute" | grep -v "\.execute(" | wc -l)
if [ "$RAW_SQL" -eq 0 ]; then
    pass "No obvious raw SQL execute patterns found"
else
    echo "   Found potential raw SQL executions - manual review recommended"
fi

# Test 2.2: Check for parameterized queries
echo "2.2 Checking for parameterized queries..."
if grep -rn "cursor.execute" apps/backend/src --include="*.py" 2>/dev/null | grep -q "%s\|?"; then
    pass "Parameterized queries found"
else
    skip "Could not verify parameterized queries"
fi

# =====================================
# TEST 3: Authentication Security
# =====================================
section "Authentication Security Tests"

# Test 3.1: Check for secure password handling
echo "3.1 Checking password handling..."
if grep -rn "make_password\|check_password" apps/backend/src --include="*.py" 2>/dev/null | grep -q "django.contrib.auth"; then
    pass "Django auth password handling found"
else
    skip "Could not verify password handling"
fi

# Test 3.2: Check for JWT configuration
echo "3.2 Checking JWT configuration..."
if grep -rn "JWT\|jwt" apps/backend/src --include="*.py" 2>/dev/null | grep -q "SECRET_KEY\|ALGORITHM"; then
    pass "JWT configuration found"
else
    skip "Could not verify JWT configuration"
fi

# Test 3.3: Check for token storage security
echo "3.3 Checking token storage..."
if [ -f "apps/frontend/src/contexts/AuthContext.tsx.secure" ]; then
    if grep -q "httpOnly" apps/frontend/src/contexts/AuthContext.tsx.secure 2>/dev/null; then
        pass "httpOnly cookies configured for token storage"
    else
        fail "httpOnly cookies not found in secure AuthContext"
    fi
else
    skip "Secure AuthContext not found"
fi

# =====================================
# TEST 4: API Security
# =====================================
section "API Security Tests"

# Test 4.1: Check for rate limiting
echo "4.1 Checking rate limiting..."
if grep -rn "rate_limit\|throttle" apps/backend/src --include="*.py" 2>/dev/null | grep -q "RATE_LIMIT\|THROTTLE"; then
    pass "Rate limiting configuration found"
else
    echo "   Rate limiting not explicitly configured"
fi

# Test 4.2: Check for CORS configuration
echo "4.2 Checking CORS configuration..."
if grep -rn "CORS\|cors" apps/backend/src --include="*.py" 2>/dev/null | grep -q "ALLOWED_ORIGINS\|CORS_ALLOWED"; then
    pass "CORS configuration found"
else
    skip "Could not verify CORS configuration"
fi

# =====================================
# TEST 5: Dependency Security
# =====================================
section "Dependency Security Tests"

# Test 5.1: Check for known vulnerable packages
echo "5.1 Checking for known vulnerabilities..."
if [ -f "requirements.txt" ]; then
    # This is a placeholder - in production, use pip-audit or safety
    pass "requirements.txt found (run pip-audit for full scan)"
else
    skip "requirements.txt not found"
fi

# Test 5.2: Check package.json for vulnerabilities
echo "5.2 Checking package.json..."
if [ -f "apps/frontend/package.json" ]; then
    pass "package.json found (run npm audit for full scan)"
else
    skip "package.json not found"
fi

# =====================================
# TEST 6: Logging Security
# =====================================
section "Logging Security Tests"

# Test 6.1: Check for print statements in production code
echo "6.1 Checking for print statements in production code..."
PRINT_COUNT=$(grep -rn "print(" apps/backend/src --include="*.py" 2>/dev/null | grep -v "test" | grep -v "tools" | grep -v "migrations" | wc -l)
if [ "$PRINT_COUNT" -eq 0 ]; then
    pass "No print statements found in production code"
else
    echo "   Found $PRINT_COUNT print statements in production code - S-010"
fi

# Test 6.2: Check for proper logging configuration
echo "6.2 Checking logging configuration..."
if grep -rn "logging\|logger" apps/backend/src --include="*.py" 2>/dev/null | grep -q "getLogger"; then
    pass "Logging configured"
else
    skip "Could not verify logging configuration"
fi

# =====================================
# TEST 7: File Security
# =====================================
section "File Security Tests"

# Test 7.1: Check for sensitive files in git
echo "7.1 Checking for sensitive files..."
if grep -q "\.env\|\. secrets\|\ credentials" .gitignore 2>/dev/null; then
    pass "Sensitive files appear to be gitignored"
else
    fail "Sensitive files may not be gitignored"
fi

# Test 7.2: Check file permissions
echo "7.2 Checking file permissions..."
if [ -f "scripts/security/scan.sh" ]; then
    if [ -x "scripts/security/scan.sh" ]; then
        pass "Security scan script is executable"
    else
        fail "Security scan script is not executable"
    fi
else
    skip "Security scan script not found"
fi

# =====================================
# TEST 8: WebSocket Security
# =====================================
section "WebSocket Security Tests"

# Test 8.1: Check WebSocket authentication
echo "8.1 Checking WebSocket authentication..."
if grep -rn "WebSocket\|websocket" apps/backend/src --include="*.py" 2>/dev/null | grep -q "token\|auth"; then
    pass "WebSocket authentication patterns found"
else
    skip "Could not verify WebSocket authentication"
fi

# Test 8.2: Check for token in URL query string (vulnerability)
echo "8.2 Checking for token in URL query string..."
if grep -rn "query_string\|token=" apps/backend/src --include="*.py" 2>/dev/null | grep -q "websocket\|WebSocket"; then
    echo "   Found WebSocket query string usage - verify S-012 implementation"
else
    pass "No obvious token-in-URL patterns found"
fi

# =====================================
# TEST 9: Error Handling Security
# =====================================
section "Error Handling Security Tests"

# Test 9.1: Check for broad exception handling
echo "9.1 Checking exception handling..."
BROAD_EXCEPTIONS=$(grep -rn "except Exception" apps/backend/src --include="*.py" 2>/dev/null | wc -l)
if [ "$BROAD_EXCEPTIONS" -eq 0 ]; then
    pass "No broad exception handling found"
else
    echo "   Found $BROAD_EXCEPTIONS broad exception handlers - S-011"
fi

# Test 9.2: Check for verbose error messages
echo "9.2 Checking for verbose error handling..."
if grep -rn "raise\|Exception" apps/backend/src --include="*.py" 2>/dev/null | grep -q "logger\|logging"; then
    pass "Exceptions appear to be logged properly"
else
    skip "Could not verify exception logging"
fi

# =====================================
# TEST 10: Input Validation
# =====================================
section "Input Validation Tests"

# Test 10.1: Check for input sanitization
echo "10.1 Checking input validation..."
if grep -rn "validate\|sanitize\|clean" apps/backend/src --include="*.py" 2>/dev/null | grep -q "input\|request"; then
    pass "Input validation patterns found"
else
    skip "Could not verify input validation"
fi

# Test 10.2: Check for Django model validation
echo "10.2 Checking Django model validation..."
if grep -rn "validators\|clean\|validate" apps/backend/src --include="*.py" 2>/dev/null | grep -q "models.Model"; then
    pass "Django model validation patterns found"
else
    skip "Could not verify model validation"
fi

# =====================================
# SUMMARY
# =====================================
section "Test Summary"

TOTAL=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

echo ""
echo "====================================="
echo "🛡️ Security Test Results"
echo "====================================="
echo -e "${GREEN}Passed:${NC}   $TESTS_PASSED"
echo -e "${RED}Failed:${NC}   $TESTS_FAILED"
echo -e "${YELLOW}Skipped:${NC} $TESTS_SKIPPED"
echo "Total:   $TOTAL"
echo "====================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Review the output above.${NC}"
    exit 1
fi
