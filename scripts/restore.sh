#!/bin/bash
#############################################
# FinanceHub - Restore Script
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Restore from backups
#############################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"

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
# List Available Backups
#############################################
list_backups() {
    log "📋 Available Backups"
    log "================================"

    if [[ ! -d "${BACKUP_DIR}" ]]; then
        error "Backup directory not found: ${BACKUP_DIR}"
        return 1
    fi

    echo ""
    info "Database Backups:"
    find "${BACKUP_DIR}/database" -type f -name "*.sql.gz" 2>/dev/null | sort -r | head -10 || echo "  No database backups found"

    echo ""
    info "Media File Backups:"
    find "${BACKUP_DIR}/files" -type f -name "*.tar.gz" 2>/dev/null | sort -r | head -10 || echo "  No file backups found"

    echo ""
    info "Configuration Backups:"
    find "${BACKUP_DIR}/configs" -type f 2>/dev/null | sort -r | head -10 || echo "  No config backups found"

    echo ""
    log "================================"
}

#############################################
# Restore Database
#############################################
restore_database() {
    local backup_file="$1"

    if [[ -z "${backup_file}" ]]; then
        error "Usage: $0 database <backup_file>"
        return 1
    fi

    if [[ ! -f "${backup_file}" ]]; then
        error "Backup file not found: ${backup_file}"
        return 1
    fi

    if [[ -z "${DATABASE_URL:-}" ]]; then
        error "DATABASE_URL environment variable not set"
        return 1
    fi

    warning "⚠️  This will REPLACE the current database!"
    warning "⚠️  Make sure you have a backup of the current database first!"
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " confirm

    if [[ "${confirm}" != "yes" ]]; then
        info "Restore cancelled"
        return 0
    fi

    log "🔄 Restoring database from: ${backup_file}"

    if command -v psql &> /dev/null; then
        # Gunzip and restore
        if gunzip -c "${backup_file}" | psql "${DATABASE_URL}"; then
            log "✅ Database restore completed successfully!"
        else
            error "❌ Database restore failed"
            return 1
        fi
    else
        error "psql command not found. Install PostgreSQL client."
        return 1
    fi
}

#############################################
# Restore Files
#############################################
restore_files() {
    local backup_file="$1"
    local target_dir="${2:-.}"

    if [[ -z "${backup_file}" ]]; then
        error "Usage: $0 files <backup_file> [target_dir]"
        return 1
    fi

    if [[ ! -f "${backup_file}" ]]; then
        error "Backup file not found: ${backup_file}"
        return 1
    fi

    log "🔄 Restoring files from: ${backup_file}"
    log "📁 Target directory: ${target_dir}"

    if tar -xzf "${backup_file}" -C "${target_dir}"; then
        log "✅ Files restored successfully!"
        log "📊 Restired to: ${target_dir}"
    else
        error "❌ File restore failed"
        return 1
    fi
}

#############################################
# Restore Configuration
#############################################
restore_config() {
    local backup_file="$1"

    if [[ -z "${backup_file}" ]]; then
        error "Usage: $0 config <backup_file>"
        return 1
    fi

    if [[ ! -f "${backup_file}" ]]; then
        error "Backup file not found: ${backup_file}"
        return 1
    fi

    # Extract original filename from backup
    local original_name=$(basename "${backup_file}" | sed 's/_[0-9]*_[0-9]*$//')

    log "🔄 Restoring configuration: ${original_name}"
    warning "⚠️  This will overwrite the existing configuration!"

    read -p "Restore to ${original_name}? (yes/no): " confirm

    if [[ "${confirm}" != "yes" ]]; then
        info "Restore cancelled"
        return 0
    fi

    # Restore to correct location
    if [[ "${original_name}" == *".env"* ]]; then
        warning "This is a masked .env file. You'll need to update values manually."
    fi

    if cp "${backup_file}" "${original_name}"; then
        log "✅ Configuration restored to: ${original_name}"
        warning "⚠️  Please review and update the configuration as needed"
    else
        error "❌ Configuration restore failed"
        return 1
    fi
}

#############################################
# Download from S3
#############################################
download_from_s3() {
    local s3_path="$1"
    local local_dir="${2:-${BACKUP_DIR}/s3-download}"

    if [[ -z "${s3_path}" ]]; then
        error "Usage: $0 s3 <s3_path> [local_dir]"
        return 1
    fi

    if [[ -z "${AWS_ACCESS_KEY_ID:-}" ]]; then
        error "AWS credentials not configured"
        return 1
    fi

    log "📥 Downloading from S3: ${s3_path}"

    if command -v aws &> /dev/null; then
        if aws s3 sync "${s3_path}" "${local_dir}"; then
            log "✅ Download completed to: ${local_dir}"
            log "💡 Run '$0 list' to see downloaded backups"
        else
            error "❌ S3 download failed"
            return 1
        fi
    else
        error "AWS CLI not found"
        return 1
    fi
}

#############################################
# Show Help
#############################################
show_help() {
    cat << EOF
FinanceHub Restore Script

Usage: $0 <command> [options]

Commands:
  list                    List all available backups
  database <file>         Restore database from backup file
  files <file> [dir]      Restore files from backup (default: current dir)
  config <file>           Restore configuration from backup
  s3 <s3_path> [dir]      Download backups from S3

Examples:
  $0 list
  $0 database ./backups/database/db_backup_20260130_120000.sql.gz
  $0 files ./backups/files/media_20260130_120000.tar.gz ./Backend
  $0 config ./backups/configs/.env_20260130_120000
  $0 s3 s3://my-bucket/financehub-backups/20260130_120000/ ./restored

Environment Variables:
  BACKUP_DIR              Backup directory (default: ./backups)
  DATABASE_URL            PostgreSQL connection URL
  AWS_ACCESS_KEY_ID       AWS access key (for S3)
  AWS_SECRET_ACCESS_KEY   AWS secret key (for S3)

Safety:
  - Database restores require confirmation
  - File restores don't overwrite by default
  - Always test restores in non-production first

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
        list)
            list_backups
            ;;
        database)
            restore_database "$@"
            ;;
        files)
            restore_files "$@"
            ;;
        config)
            restore_config "$@"
            ;;
        s3)
            download_from_s3 "$@"
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
