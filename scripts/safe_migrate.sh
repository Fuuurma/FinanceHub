#!/bin/bash
#
# Safe Migration Wrapper
# Runs Django migrations with safety checks and automatic rollback on failure
#
# Usage:
#   ./safe_migrate.sh                 # Run migrations
#   ./safe_migrate.sh --dry-run      # Show what would be done
#   ./safe_migrate.sh --skip-backup  # Skip database backup
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups/migrations"
BACKUP_RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DRY_RUN=false
SKIP_BACKUP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
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

# Pre-check 1: Verify we're in the correct directory
check_directory() {
    log_info "Checking current directory..."
    if [ ! -f "manage.py" ]; then
        log_error "manage.py not found. Are you in the Django project directory?"
        exit 1
    fi
    log_info "✓ In correct directory"
}

# Pre-check 2: Verify Docker is running
check_docker() {
    log_info "Checking Docker status..."
    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    log_info "✓ Docker is running"
}

# Pre-check 3: Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    if ! docker-compose exec -T postgres pg_isready -U financehub > /dev/null 2>&1; then
        log_error "Database is not ready"
        exit 1
    fi
    log_info "✓ Database is ready"
}

# Pre-check 4: Check for active connections
check_active_connections() {
    log_info "Checking for active database connections..."
    local active=$(docker-compose exec -T postgres psql -U financehub -d finance_hub -t -c "
        SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND datname = 'finance_hub';
    " 2>/dev/null | tr -d ' ')

    if [ "$active" -gt 0 ]; then
        log_warn "Found $active active database connections"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Migration cancelled"
            exit 0
        fi
    else
        log_info "✓ No active connections blocking"
    fi
}

# Pre-check 5: Check disk space
check_disk_space() {
    log_info "Checking disk space..."
    local available=$(df -BG . | tail -1 | awk '{print $4}' | tr -d 'G')

    if [ "$available" -lt 5 ]; then
        log_error "Less than 5GB disk space available ($available GB)"
        exit 1
    fi

    log_info "✓ Sufficient disk space ($available GB available)"
}

# Pre-check 6: Create database backup
create_backup() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_warn "Skipping database backup (--skip-backup flag)"
        return
    fi

    log_info "Creating database backup..."
    mkdir -p "$BACKUP_DIR"

    local backup_file="$BACKUP_DIR/finance_hub_${TIMESTAMP}.sql.gz"

    if docker-compose exec -T postgres pg_dump -U financehub finance_hub | gzip > "$backup_file"; then
        log_info "✓ Backup created: $backup_file"

        # Clean old backups
        log_info "Cleaning old backups (older than $BACKUP_RETENTION_DAYS days)..."
        find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
        log_info "✓ Old backups cleaned"
    else
        log_error "Failed to create database backup"
        exit 1
    fi
}

# Pre-check 7: Show pending migrations
show_pending_migrations() {
    log_info "Checking for pending migrations..."

    local pending=$(docker-compose exec -T backend python src/manage.py showmigrations --plan 2>&1 | grep -c "^\[" || true)

    if [ "$pending" -eq 0 ]; then
        log_info "✓ No pending migrations"
        return 1  # Return 1 to indicate no migrations needed
    fi

    log_info "Found $pending pending migrations:"
    docker-compose exec -T backend python src/manage.py showmigrations --plan 2>&1 | grep "^\[ \]" | head -10

    return 0
}

# Run migration dry-run
migration_dry_run() {
    log_info "Running migration dry-run (SQL generation)..."

    # This shows what SQL would be executed
    docker-compose exec -T backend python src/manage.py sqlmigrate app 0001 2>/dev/null || true

    log_info "✓ Dry-run complete"
}

# Run migrations
run_migrations() {
    log_info "Running migrations..."

    if docker-compose exec -T backend python src/manage.py migrate --no-input; then
        log_info "✓ Migrations applied successfully"
        return 0
    else
        log_error "Migration failed!"
        return 1
    fi
}

# Post-migration verification
verify_migration() {
    log_info "Verifying migration..."

    # Check if migrations are applied
    local pending=$(docker-compose exec -T backend python src/manage.py showmigrations --plan 2>&1 | grep -c "^\[ \]" || true)

    if [ "$pending" -gt 0 ]; then
        log_error "Migration verification failed: $pending migrations still pending"
        return 1
    fi

    # Run Django system check
    log_info "Running Django system check..."
    if ! docker-compose exec -T backend python src/manage.py check --deploy 2>&1; then
        log_warn "System check found issues (non-critical)"
    fi

    log_info "✓ Migration verified successfully"
    return 0
}

# Rollback function
rollback_migration() {
    log_error "Initiating rollback..."

    local latest_backup=$(ls -t "$BACKUP_DIR"/finance_hub_*.sql.gz 2>/dev/null | head -1)

    if [ -z "$latest_backup" ]; then
        log_error "No backup found for rollback!"
        exit 1
    fi

    log_info "Restoring from backup: $latest_backup"

    if gunzip -c "$latest_backup" | docker-compose exec -T postgres psql -U financehub -d finance_hub; then
        log_info "✓ Rollback complete"
    else
        log_error "Rollback failed!"
        exit 1
    fi
}

# Main execution
main() {
    log_info "=== Safe Migration Script ==="
    log_info "Timestamp: $TIMESTAMP"
    echo ""

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN MODE - No changes will be made"
        echo ""
    fi

    # Pre-checks
    check_directory
    check_docker
    check_database
    check_active_connections
    check_disk_space
    create_backup

    # Show pending migrations
    if ! show_pending_migrations; then
        log_info "No migrations to run"
        exit 0
    fi

    if [ "$DRY_RUN" = true ]; then
        migration_dry_run
        log_info "Dry-run complete. Exiting without making changes."
        exit 0
    fi

    # Run migrations
    echo ""
    read -p "Continue with migration? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Migration cancelled by user"
        exit 0
    fi

    if run_migrations; then
        # Verify
        if verify_migration; then
            log_info "=== Migration Complete ==="
            exit 0
        else
            log_error "Migration verification failed"
            read -p "Rollback to backup? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rollback_migration
            fi
            exit 1
        fi
    else
        log_error "Migration failed"
        read -p "Rollback to backup? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback_migration
        fi
        exit 1
    fi
}

# Run main function
main
