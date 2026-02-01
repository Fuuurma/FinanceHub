#!/bin/bash
#
# Pre-Deployment Verification Script
# Checks all prerequisites before deployment
#
# Usage: ./pre_deployment_check.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

log_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "=================================="
echo "Pre-Deployment Verification Check"
echo "=================================="
echo ""

# Check 1: Git Status
echo "1. Checking git status..."
if git diff-index --quiet HEAD --; then
    log_pass "No uncommitted changes"
else
    log_fail "There are uncommitted changes"
    git status --short
fi

# Check 2: All tests pass
echo ""
echo "2. Running tests..."
if docker-compose exec -T backend python src/manage.py test --keepdb 2>&1 | grep -q "OK"; then
    log_pass "All tests passing"
else
    log_warn "Some tests failing or no tests found"
fi

# Check 3: Environment variables
echo ""
echo "3. Checking environment variables..."
if [ -f .env ]; then
    required_vars=("POSTGRES_PASSWORD" "DJANGO_SECRET_KEY")
    missing=0

    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            log_pass "Environment variable $var is set"
        else
            log_fail "Missing environment variable: $var"
            ((missing++))
        fi
    done

    if [ $missing -eq 0 ]; then
        log_pass "All required environment variables set"
    fi
else
    log_fail ".env file not found"
fi

# Check 4: Docker containers
echo ""
echo "4. Checking Docker containers..."
if docker-compose ps | grep -q "Up"; then
    log_pass "Docker containers running"
else
    log_fail "Docker containers not running"
fi

# Check 5: Database connectivity
echo ""
echo "5. Checking database connectivity..."
if docker-compose exec -T postgres pg_isready -U financehub > /dev/null 2>&1; then
    log_pass "Database is ready"
else
    log_fail "Database is not ready"
fi

# Check 6: Redis connectivity
echo ""
echo "7. Checking Redis connectivity..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    log_pass "Redis is ready"
else
    log_fail "Redis is not ready"
fi

# Check 7: Disk space
echo ""
echo "8. Checking disk space..."
available_gb=$(df -BG . | tail -1 | awk '{print $4}' | tr -d 'G')
if [ "$available_gb" -gt 5 ]; then
    log_pass "Sufficient disk space (${available_gb}GB available)"
else
    log_fail "Low disk space (${available_gb}GB available, need at least 5GB)"
fi

# Check 8: Database backup recent
echo ""
echo "9. Checking database backup..."
backup_dir="./backups/migrations"
if [ -d "$backup_dir" ]; then
    latest_backup=$(ls -t "$backup_dir"/finance_hub_*.sql.gz 2>/dev/null | head -1)
    if [ -n "$latest_backup" ]; then
        backup_age=$(( ($(date +%s) - $(stat -f %m "$latest_backup" 2>/dev/null || stat -c %Y "$latest_backup" 2>/dev/null)) / 86400 ))
        if [ $backup_age -lt 2 ]; then
            log_pass "Recent database backup found (${backup_age} days old)"
        else
            log_warn "Database backup is old (${backup_age} days)"
        fi
    else
        log_warn "No database backup found"
    fi
else
    log_warn "No backup directory found"
fi

# Check 9: Pending migrations
echo ""
echo "10. Checking for pending migrations..."
pending=$(docker-compose exec -T backend python src/manage.py showmigrations --plan 2>&1 | grep -c "^\[ \]" || true)
if [ $pending -eq 0 ]; then
    log_pass "No pending migrations"
else
    log_warn "Found $pending pending migrations"
fi

# Check 10: Health endpoint
echo ""
echo "11. Checking health endpoint..."
if curl -sf http://localhost:8000/health/v2/simple > /dev/null 2>&1; then
    log_pass "Health endpoint responding"
else
    log_fail "Health endpoint not responding"
fi

# Summary
echo ""
echo "=================================="
echo "Summary"
echo "=================================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ PRE-DEPLOYMENT CHECKS FAILED${NC}"
    echo "Please fix the failed checks before deploying."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  PRE-DEPLOYMENT CHECKS PASSED WITH WARNINGS${NC}"
    echo "You may proceed, but review the warnings above."
    exit 0
else
    echo -e "${GREEN}✅ ALL PRE-DEPLOYMENT CHECKS PASSED${NC}"
    echo "Safe to proceed with deployment."
    exit 0
fi
