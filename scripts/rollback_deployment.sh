#!/bin/bash
#
# Rollback Full Deployment Script
# Rolls back entire deployment to previous version
#
# Usage: ./rollback_deployment.sh [--commit HASH]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

COMMIT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --commit)
            COMMIT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=================================="
echo "Deployment Rollback"
echo "=================================="
echo ""

log_warn "This will rollback the entire deployment"
log_warn "All recent changes will be reverted"
echo ""

read -p "Continue with rollback? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    log_info "Rollback cancelled"
    exit 0
fi

# Step 1: Stop services
log_info "Step 1: Stopping services..."
docker-compose stop backend frontend

# Step 2: Checkout previous commit (if specified)
if [ -n "$COMMIT" ]; then
    log_info "Step 2: Checking out commit $COMMIT..."
    git checkout "$COMMIT"
else
    log_info "Step 2: Git rollback not specified, skipping"
fi

# Step 3: Rebuild containers
log_info "Step 3: Rebuilding containers..."
docker-compose build --no-cache backend

# Step 4: Start services
log_info "Step 4: Starting services..."
docker-compose up -d backend

# Step 5: Wait for services to be ready
log_info "Step 5: Waiting for services to be ready..."
sleep 20

# Step 6: Verify
log_info "Step 6: Verifying deployment..."
if ./scripts/post_deployment_validate.sh; then
    log_info "✓ Rollback successful"
else
    log_error "Rollback verification failed"
    log_error "Manual intervention required"
    exit 1
fi

echo ""
echo "=================================="
log_info "Deployment Rollback Complete"
echo "=================================="
echo ""
echo "If issues persist:"
echo "1. Check logs: docker-compose logs --tail 100"
echo "2. Check health: curl http://localhost:8000/health/v2/detailed"
echo "3. Restore database: ./scripts/rollback_migration.sh"
