#!/bin/bash
#############################################
# FinanceHub - Backup Script
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Automated backup for databases and critical files
#############################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create backup directory
mkdir -p "${BACKUP_DIR}/database"
mkdir -p "${BACKUP_DIR}/files"
mkdir -p "${BACKUP_DIR}/configs"

log "Starting backup process..."

#############################################
# Database Backup (PostgreSQL)
#############################################
backup_database() {
    log "Backing up PostgreSQL database..."

    if [[ -z "${DATABASE_URL:-}" ]]; then
        error "DATABASE_URL environment variable not set"
        return 1
    fi

    local backup_file="${BACKUP_DIR}/database/db_backup_${TIMESTAMP}.sql.gz"

    # Extract database connection info from DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    local db_url="${DATABASE_URL}"

    if command -v pg_dump &> /dev/null; then
        if pg_dump "${db_url}" | gzip > "${backup_file}"; then
            log "✅ Database backup completed: ${backup_file}"
            log "📊 Size: $(du -h "${backup_file}" | cut -f1)"
        else
            error "❌ Database backup failed"
            return 1
        fi
    else
        warning "pg_dump not found, skipping database backup"
        warning "Install PostgreSQL client: apt-get install postgresql-client"
    fi
}

#############################################
# Redis Backup
#############################################
backup_redis() {
    log "Backing up Redis data..."

    if [[ -z "${REDIS_URL:-}" ]]; then
        warning "REDIS_URL not set, skipping Redis backup"
        return 0
    fi

    local backup_file="${BACKUP_DIR}/database/redis_backup_${TIMESTAMP}.rdb"

    if command -v redis-cli &> /dev/null; then
        # Trigger Redis BGSAVE
        if redis-cli -u "${REDIS_URL}" BGSAVE &> /dev/null; then
            log "✅ Redis backup triggered"
            # Wait for BGSAVE to complete
            sleep 5

            # Copy RDB file if accessible
            local redis_dir="/var/lib/redis"
            if [[ -f "${redis_dir}/dump.rdb" ]]; then
                cp "${redis_dir}/dump.rdb" "${backup_file}"
                log "✅ Redis backup completed: ${backup_file}"
            fi
        else
            warning "Redis backup failed, continuing..."
        fi
    else
        warning "redis-cli not found, skipping Redis backup"
    fi
}

#############################################
# Media Files Backup
#############################################
backup_media_files() {
    log "Backing up media files..."

    local media_dirs=("Backend/media" "Frontend/public/uploads")

    for dir in "${media_dirs[@]}"; do
        if [[ -d "${dir}" ]]; then
            local backup_name=$(basename "${dir}")
            local backup_file="${BACKUP_DIR}/files/${backup_name}_${TIMESTAMP}.tar.gz"

            if tar -czf "${backup_file}" -C "$(dirname ${dir})" "$(basename ${dir})" 2>/dev/null; then
                log "✅ Media files backup completed: ${backup_file}"
                log "📊 Size: $(du -h "${backup_file}" | cut -f1)"
            else
                warning "Failed to backup ${dir}"
            fi
        fi
    done
}

#############################################
# Configuration Files Backup
#############################################
backup_configs() {
    log "Backing up configuration files..."

    local config_files=(
        ".env"
        "docker-compose.yml"
        "Backend/.env"
        "Frontend/.env.local"
    )

    for config in "${config_files[@]}"; do
        if [[ -f "${config}" ]]; then
            local backup_file="${BACKUP_DIR}/configs/$(basename ${config})_${TIMESTAMP}"

            # Copy file, removing sensitive data if .env
            if [[ "${config}" == *".env"* ]]; then
                # Mask sensitive values in .env files
                sed 's/=.*/=***/g' "${config}" > "${backup_file}"
                log "✅ Config backup (masked): ${backup_file}"
            else
                cp "${config}" "${backup_file}"
                log "✅ Config backup: ${backup_file}"
            fi
        fi
    done
}

#############################################
# Old Backups Cleanup
#############################################
cleanup_old_backups() {
    log "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."

    if find "${BACKUP_DIR}" -type f -mtime +${RETENTION_DAYS} -delete 2>/dev/null; then
        log "✅ Old backups cleaned up"
    else
        warning "No old backups to clean or cleanup failed"
    fi

    # Show current backup usage
    local total_size=$(du -sh "${BACKUP_DIR}" 2>/dev/null | cut -f1)
    local backup_count=$(find "${BACKUP_DIR}" -type f | wc -l)

    log "📊 Current backup storage: ${total_size}"
    log "📊 Total backup files: ${backup_count}"
}

#############################################
# Backup Summary
#############################################
backup_summary() {
    log "================================"
    log "📋 Backup Summary"
    log "================================"

    local db_count=$(find "${BACKUP_DIR}/database" -type f 2>/dev/null | wc -l)
    local files_count=$(find "${BACKUP_DIR}/files" -type f 2>/dev/null | wc -l)
    local configs_count=$(find "${BACKUP_DIR}/configs" -type f 2>/dev/null | wc -l)

    log "Database backups: ${db_count}"
    log "File backups: ${files_count}"
    log "Config backups: ${configs_count}"
    log "Backup directory: ${BACKUP_DIR}"
    log "================================"
}

#############################################
# Main Execution
#############################################
main() {
    log "🚀 FinanceHub Backup Process Started"
    log "===================================="

    # Run all backups
    backup_database
    backup_redis
    backup_media_files
    backup_configs

    # Cleanup old backups
    cleanup_old_backups

    # Show summary
    backup_summary

    log "✅ Backup process completed successfully!"
    log "💡 Tip: Copy backups to off-site storage for disaster recovery"

    # Optional: Upload to S3 if AWS credentials available
    if [[ -n "${AWS_ACCESS_KEY_ID:-}" ]] && [[ -n "${S3_BUCKET:-}" ]]; then
        log "📤 Uploading backups to S3..."
        if command -v aws &> /dev/null; then
            aws s3 sync "${BACKUP_DIR}" "s3://${S3_BUCKET}/financehub-backups/${TIMESTAMP}/"
            log "✅ Backups uploaded to S3"
        else
            warning "AWS CLI not found, skipping S3 upload"
        fi
    fi
}

# Run main function
main "$@"
