#!/bin/bash

# Smoke test script for FinanceHub
# Tests critical endpoints after deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-staging}"
BASE_URL=""

if [ "$ENVIRONMENT" = "staging" ]; then
    BASE_URL="https://staging.financehub.com"
    API_URL="https://staging-api.financehub.com"
elif [ "$ENVIRONMENT" = "production" ]; then
    BASE_URL="https://financehub.com"
    API_URL="https://api.financehub.com"
else
    echo -e "${RED}Invalid environment. Use 'staging' or 'production'${NC}"
    exit 1
fi

echo -e "${YELLOW}Running smoke tests on ${ENVIRONMENT}...${NC}"
echo ""

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    echo -n "Testing ${name}... "

    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}✓ PASS${NC} (${expected_code})"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (expected ${expected_code})"
        ((FAILED++))
        return 1
    fi
}

# Run tests
echo "=== Health Checks ==="
test_endpoint "Frontend Health" "${BASE_URL}/health" "200"
test_endpoint "API Health" "${API_URL}/api/health" "200"
test_endpoint "API Status" "${API_URL}/api/v1/status" "200"

echo ""
echo "=== Critical Endpoints ==="
test_endpoint "Frontend Root" "${BASE_URL}/" "200"
test_endpoint "API Root" "${API_URL}/api/" "200"

echo ""
echo "=== Static Assets ==="
test_endpoint "CSS Bundle" "${BASE_URL}/_next/static/css/main.css" "200"
test_endpoint "JS Bundle" "${BASE_URL}/_next/static/js/main.js" "200"

echo ""
echo "=== Security Headers ==="
echo "Testing security headers..."
if curl -s -I "${BASE_URL}" | grep -q "X-Content-Type-Options"; then
    echo -e "${GREEN}✓ X-Content-Type-Options header present${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ X-Content-Type-Options header missing${NC}"
    ((FAILED++))
fi

if curl -s -I "${BASE_URL}" | grep -q "X-Frame-Options"; then
    echo -e "${GREEN}✓ X-Frame-Options header present${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ X-Frame-Options header missing${NC}"
    ((FAILED++))
fi

echo ""
echo "=== Performance Checks ==="
FRONTEND_TTFB=$(curl -o /dev/null -s -w '%{time_starttransfer}' "${BASE_URL}")
echo "Frontend TTFB: ${FRONTEND_TTFB}s"

API_TTFB=$(curl -o /dev/null -s -w '%{time_starttransfer}' "${API_URL}/api/health")
echo "API TTFB: ${API_TTFB}s"

# Check if TTFB is acceptable (< 1s)
if (( $(echo "$FRONTEND_TTFB < 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ Frontend TTFB acceptable${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Frontend TTFB too high${NC}"
    ((FAILED++))
fi

echo ""
echo "=== Summary ==="
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Smoke tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All smoke tests passed!${NC}"
    exit 0
fi
