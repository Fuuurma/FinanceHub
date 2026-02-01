#!/bin/bash
#
# Post-Deployment Validation Script
# Validates deployment success and catches issues early
#
# Usage: ./post_deployment_validate.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

log_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

echo "=================================="
echo "Post-Deployment Validation"
echo "=================================="
echo ""

# Give containers time to start
echo "Waiting for containers to stabilize..."
sleep 10

# Check 1: All services healthy
echo "1. Checking service health..."
unhealthy=$(docker-compose ps | grep -c "unhealthy" || true)
if [ $unhealthy -eq 0 ]; then
    log_pass "All services healthy"
else
    log_fail "$unhealthy services unhealthy"
fi

# Check 2: Backend responding
echo ""
echo "2. Checking backend API..."
if curl -sf http://localhost:8000/health/v2/simple > /dev/null 2>&1; then
    log_pass "Backend API responding"
else
    log_fail "Backend API not responding"
fi

# Check 3: Health check details
echo ""
echo "3. Checking detailed health status..."
health_status=$(curl -s http://localhost:8000/health/v2/simple 2>&1 | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$health_status" = "healthy" ]; then
    log_pass "System health: healthy"
else
    log_fail "System health: $health_status"
fi

# Check 4: Database queries working
echo ""
echo "4. Checking database operations..."
if docker-compose exec -T postgres psql -U financehub -d finance_hub -c "SELECT COUNT(*) FROM users_user;" > /dev/null 2>&1; then
    log_pass "Database queries working"
else
    log_fail "Database queries failing"
fi

# Check 5: No error spikes in logs
echo ""
echo "5. Checking for errors in logs..."
recent_errors=$(docker-compose logs backend --since 2m 2>&1 | grep -c "ERROR" || true)
if [ $recent_errors -lt 5 ]; then
    log_pass "No error spikes in logs ($recent_errors errors)"
else
    log_fail "High error rate in logs ($recent_errors errors in last 2 minutes)"
fi

# Check 6: API endpoints responding
echo ""
echo "6. Checking API endpoints..."
endpoints=("/health/v2/simple" "/health/v2/detailed")
for endpoint in "${endpoints[@]}"; do
    if curl -sf "http://localhost:8000${endpoint}" > /dev/null 2>&1; then
        log_pass "Endpoint $endpoint responding"
    else
        log_fail "Endpoint $endpoint not responding"
    fi
done

# Check 7: Performance baseline
echo ""
echo "7. Checking response times..."
response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health/v2/simple 2>&1)
response_ms=$(echo "$response_time * 1000" | bc)
if (( $(echo "$response_time < 1.0" | bc -l) )); then
    log_pass "Response time acceptable (${response_ms}ms)"
else
    log_warn "Slow response time (${response_ms}ms)"
fi

# Check 8: Docker resource usage
echo ""
echo "8. Checking container resources..."
backend_mem=$(docker stats financehub-backend --no-stream --format "{{.MemUsage}}" 2>/dev/null | awk '{print $1}')
log_pass "Backend memory usage: $backend_mem"

# Summary
echo ""
echo "=================================="
echo "Validation Summary"
echo "=================================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ POST-DEPLOYMENT VALIDATION FAILED${NC}"
    echo ""
    echo "Recommended actions:"
    echo "1. Check logs: docker-compose logs backend --tail 100"
    echo "2. Check health: curl http://localhost:8000/health/v2/detailed"
    echo "3. Consider rollback if critical failures"
    exit 1
else
    echo -e "${GREEN}✅ POST-DEPLOYMENT VALIDATION PASSED${NC}"
    echo "Deployment successful!"
    exit 0
fi
