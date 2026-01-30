#!/bin/bash
#############################################
# FinanceHub - Database Migration Helper
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Database migration management helper
#############################################

set -euo pipefail

# Configuration
BACKEND_DIR="${BACKEND_DIR:-./Backend}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-${BACKEND_DIR}/src/migrations}"
VENV_DIR="${VENV_DIR:-${BACKEND_DIR}/venv}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

#############################################
# Activate Virtual Environment
#############################################
activate_venv() {
    if [[ -f "${VENV_DIR}/bin/activate" ]]; then
        source "${VENV_DIR}/bin/activate"
        log "✅ Virtual environment activated"
    else
        warning "Virtual environment not found at ${VENV_DIR}"
        warning "Create it with: python3 -m venv ${VENV_DIR}"
    fi
}

#############################################
# Check Database Connection
#############################################
check_db_connection() {
    if [[ -z "${DATABASE_URL:-}" ]]; then
        error "DATABASE_URL environment variable not set"
        error "Example: export DATABASE_URL='postgresql://user:pass@host:port/db'"
        return 1
    fi

    log "🔍 Checking database connection..."

    if command -v psql &> /dev/null; then
        if psql "${DATABASE_URL}" -c "SELECT 1;" &> /dev/null; then
            log "✅ Database connection successful"
            return 0
        else
            error "❌ Database connection failed"
            return 1
        fi
    else
        warning "psql not found, skipping database check"
        return 0
    fi
}

#############################################
# Create New Migration
#############################################
create_migration() {
    local migration_name="$1"

    if [[ -z "${migration_name}" ]]; then
        error "Usage: $0 create <migration_name>"
        return 1
    fi

    log "📝 Creating migration: ${migration_name}"

    activate_venv

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        # Using Django's makemigrations
        if python manage.py makemigrations --name "${migration_name}"; then
            log "✅ Migration created successfully!"
            log "📄 Review the migration file in ${MIGRATIONS_DIR}"
            log "💡 Apply with: $0 migrate"
        else
            error "❌ Failed to create migration"
            return 1
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Show Migration Status
#############################################
show_status() {
    log "📊 Migration Status"
    log "================================"

    activate_venv

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        # Show Django migration status
        if python manage.py showmigrations; then
            log "================================"
            log "✅ Migration status displayed"
        else
            error "❌ Failed to show migration status"
            return 1
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Apply Migrations
#############################################
apply_migrations() {
    local app_label="${1:-}"

    log "🚀 Applying database migrations..."

    activate_venv
    check_db_connection || return 1

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        # Create backup before migration
        log "💾 Creating backup before migration..."
        if [[ -f "../../scripts/backup.sh" ]]; then
            ../../scripts/backup.sh || warning "Backup failed, continuing anyway..."
        fi

        # Apply migrations
        if [[ -n "${app_label}" ]]; then
            log "Applying migrations for: ${app_label}"
            python manage.py migrate "${app_label}"
        else
            log "Applying all pending migrations..."
            python manage.py migrate
        fi

        if [[ $? -eq 0 ]]; then
            log "✅ Migrations applied successfully!"
            log "💡 Check status with: $0 status"
        else
            error "❌ Migration failed!"
            error "💡 Restore backup with: ./scripts/restore.sh"
            return 1
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Rollback Migration
#############################################
rollback_migration() {
    local app_label="$1"
    local migration_name="${2:-}"

    if [[ -z "${app_label}" ]]; then
        error "Usage: $0 rollback <app_label> [migration_name]"
        error "Example: $0 rollback portfolio 0002_initial"
        return 1
    fi

    warning "⚠️  This will rollback migrations!"
    warning "⚠️  Data may be lost!"
    echo ""
    read -p "Are you sure? (yes/no): " confirm

    if [[ "${confirm}" != "yes" ]]; then
        info "Rollback cancelled"
        return 0
    fi

    log "🔙 Rolling back migration..."

    activate_venv
    check_db_connection || return 1

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        # Create backup before rollback
        log "💾 Creating backup before rollback..."
        if [[ -f "../../scripts/backup.sh" ]]; then
            ../../scripts/backup.sh || warning "Backup failed, continuing anyway..."
        fi

        # Rollback migration
        if [[ -n "${migration_name}" ]]; then
            python manage.py migrate "${app_label}" "${migration_name}"
        else
            python manage.py migrate "${app_label}" zero
        fi

        if [[ $? -eq 0 ]]; then
            log "✅ Migration rolled back successfully!"
        else
            error "❌ Rollback failed!"
            return 1
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Fake Migration (mark as applied)
#############################################
fake_migration() {
    local app_label="${1:-}"

    log "🎭 Marking migrations as applied (without running them)..."

    activate_venv

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        if [[ -n "${app_label}" ]]; then
            python manage.py migrate "${app_label}" --fake
        else
            python manage.py migrate --fake
        fi

        if [[ $? -eq 0 ]]; then
            log "✅ Migrations marked as applied!"
        else
            error "❌ Failed to fake migrations"
            return 1
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Create Migration SQL
#############################################
sqlmigrate() {
    local app_label="$1"
    local migration_name="$2"

    if [[ -z "${app_label}" ]] || [[ -z "${migration_name}" ]]; then
        error "Usage: $0 sql <app_label> <migration_name>"
        return 1
    fi

    log "📄 Generating SQL for migration..."

    activate_venv

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        python manage.py sqlmigrate "${app_label}" "${migration_name}"

        if [[ $? -eq 0 ]]; then
            log ""
            log "✅ SQL generated successfully!"
        else
            error "❌ Failed to generate SQL"
            return 1
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Show Migration Plan
#############################################
show_plan() {
    log "📋 Migration Plan (Pending Migrations)"
    log "================================"

    activate_venv

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        python manage.py showmigrations --plan

        log "================================"
        log "💡 Apply with: $0 migrate"
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Check for Drift
#############################################
check_drift() {
    log "🔍 Checking for database schema drift..."

    activate_venv
    check_db_connection || return 1

    if [[ -d "${BACKEND_DIR}" ]]; then
        cd "${BACKEND_DIR}"

        # Create a migration to check for differences
        python manage.py makemigrations --dry-run --check

        if [[ $? -eq 0 ]]; then
            log "✅ No schema drift detected!"
        else
            warning "⚠️  Schema drift detected!"
            warning "Database schema doesn't match models."
            warning "💡 Create migration with: $0 create auto"
        fi
    else
        error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi
}

#############################################
# Show Help
#############################################
show_help() {
    cat << EOF
FinanceHub Database Migration Helper

Usage: $0 <command> [options]

Commands:
  create <name>          Create a new migration
  migrate [app]          Apply all migrations (or specific app)
  rollback <app> [name]  Rollback migration (to specific or zero)
  status                 Show migration status
  plan                   Show migration plan
  sql <app> <migration>  Show SQL for a migration
  fake [app]             Mark migrations as applied (fake)
  check                  Check for schema drift
  help                   Show this help

Examples:
  $0 create add_user_profile_field
  $0 migrate
  $0 migrate portfolio
  $0 rollback portfolio 0003_previous
  $0 status
  $0 plan
  $0 sql portfolio 0004_add_new_field
  $0 fake
  $0 check

Environment Variables:
  DATABASE_URL           PostgreSQL connection URL
  BACKEND_DIR            Backend directory (default: ./Backend)
  MIGRATIONS_DIR         Migrations directory
  VENV_DIR               Virtual environment directory

Safety Features:
  - Automatic backup before migrations/rollbacks
  - Database connection check
  - Confirmation for destructive operations

Author: KAREN (DevOps Engineer)
Date: 2026-01-30
EOF
}

#############################################
# Main
#############################################
main() {
    local command="${1:-}"
    shift || true

    case "${command}" in
        create)
            create_migration "$@"
            ;;
        migrate)
            apply_migrations "$@"
            ;;
        rollback)
            rollback_migration "$@"
            ;;
        status)
            show_status
            ;;
        plan)
            show_plan
            ;;
        sql)
            sqlmigrate "$@"
            ;;
        fake)
            fake_migration "$@"
            ;;
        check)
            check_drift
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: ${command}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
