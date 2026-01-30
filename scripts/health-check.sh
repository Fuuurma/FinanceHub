#!/bin/bash

# Health check script for FinanceHub
# Checks system health and reports status

set -e

# Configuration
ENVIRONMENT="${1:-staging}"
BASE_URL=""

if [ "$ENVIRONMENT" = "staging" ]; then
    BASE_URL="https://staging-api.financehub.com"
elif [ "$ENVIRONMENT" = "production" ]; then
    BASE_URL="https://api.financehub.com"
else
    echo "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Health Check for ${ENVIRONMENT} ==="
echo ""

# Check API health
echo -n "API Health: "
HEALTH_STATUS=$(curl -s "${BASE_URL}/api/health")
if echo "$HEALTH_STATUS" | grep -q "healthy"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "$HEALTH_STATUS"
    exit 1
fi

# Check database connection
echo -n "Database: "
DB_STATUS=$(curl -s "${BASE_URL}/api/health" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
if [ "$DB_STATUS" = "connected" ]; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check cache connection
echo -n "Cache: "
CACHE_STATUS=$(curl -s "${BASE_URL}/api/health" | grep -o '"cache":"[^"]*"' | cut -d'"' -f4)
if [ "$CACHE_STATUS" = "connected" ]; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ DEGRADED${NC}"
fi

# Check response time
echo -n "Response Time: "
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' "${BASE_URL}/api/health")
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ ${RESPONSE_TIME}s${NC}"
else
    echo -e "${YELLOW}⚠ ${RESPONSE_TIME}s (slow)${NC}"
fi

echo ""
echo "=== Health Check Complete ==="
