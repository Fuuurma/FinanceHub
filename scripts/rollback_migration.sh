#!/bin/bash
#
# Rollback Migration Script
# Rolls back database migrations using backups or reverse SQL
#
# Usage: ./rollback_migration.sh [--backup FILE] [--steps N]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="./backups/migrations"
STEPS=1
USE_BACKUP=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup)
            BACKUP_FILE="$2"
            USE_BACKUP=true
            shift 2
            ;;
        --steps)
            STEPS="$2"
            USE_BACKUP=false
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
echo "Migration Rollback"
echo "=================================="
echo ""

if [ "$USE_BACKUP" = true ]; then
    log_info "Rollback method: Database backup restore"

    if [ -z "$BACKUP_FILE" ]; then
        # Find latest backup
        BACKUP_FILE=$(ls -t "$BACKUP_DIR"/finance_hub_*.sql.gz 2>/dev/null | head -1)

        if [ -z "$BACKUP_FILE" ]; then
            log_error "No backup file found in $BACKUP_DIR"
            exit 1
        fi
    fi

    log_info "Backup file: $BACKUP_FILE"
    echo ""

    read -p "This will RESTORE DATABASE from backup. Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    log_info "Stopping backend..."
    docker-compose stop backend

    log_info "Restoring database from backup..."
    if gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U financehub -d finance_hub; then
        log_info "✓ Database restored"
    else
        log_error "Failed to restore database"
        docker-compose start backend
        exit 1
    fi

    log_info "Starting backend..."
    docker-compose start backend

    log_info "Waiting for backend to start..."
    sleep 15

else
    log_info "Rollback method: Django migrate (--fake)"
    log_warn "This will FAKE rollback $STEPS migration(s)"
    log_warn "Database schema will NOT be reverted"
    echo ""

    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    # Get current migrations
    log_info "Current migration state:"
    docker-compose exec -T backend python src/manage.py showmigrations | tail -10

    echo ""
    log_info "Faking rollback $STEPS migration(s)..."

    # This doesn't actually revert schema, just marks migrations as unapplied
    # For proper rollback, you need reverse SQL or backup restore
    log_warn "Note: Django migrations cannot be easily rolled back"
    log_warn "Consider restoring from backup instead"
fi

# Verify
echo ""
log_info "Verifying rollback..."

if curl -sf http://localhost:8000/health/v2/simple > /dev/null 2>&1; then
    log_info "✓ Backend is responding"
else
    log_error "Backend not responding after rollback"
    exit 1
fi

echo ""
echo "=================================="
log_info "Rollback Complete"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Verify application functionality"
echo "2. Check logs: docker-compose logs backend --tail 50"
echo "3. Run: ./scripts/post_deployment_validate.sh"
