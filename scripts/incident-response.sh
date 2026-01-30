#!/bin/bash
#############################################
# FinanceHub - Automated Incident Response
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Automated incident detection and response
#############################################

set -euo pipefail

# Configuration
INCIDENT_LOG="${INCIDENT_LOG:-./logs/incidents.log}"
ALERT_THRESHOLD="${ALERT_THRESHOLD:-5}"  # Consecutive failures before alert
RECOVERY_CHECK_INTERVAL="${RECOVERY_CHECK_INTERVAL:-30}"  # seconds
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
AUTO_REMEDIATE="${AUTO_REMEDIATE:-true}"  # Auto-fix issues

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${INCIDENT_LOG}"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "${INCIDENT_LOG}" >&2; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${INCIDENT_LOG}"; }
incident() { echo -e "${RED}[INCIDENT]${NC} $1" | tee -a "${INCIDENT_LOG}"; }

# Ensure log directory exists
mkdir -p "$(dirname "${INCIDENT_LOG}")"

#############################################
# Health Checks
#############################################

check_api_health() {
    local url="${1:-http://localhost:8000/api/v1/health/}"
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${url}")
    echo "${response}"
}

check_database_health() {
    if command -v psql &> /dev/null; then
        if psql "${DATABASE_URL}" -c "SELECT 1;" &> /dev/null; then
            echo "200"
        else
            echo "503"
        fi
    else
        echo "000"
    fi
}

check_redis_health() {
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            echo "200"
        else
            echo "503"
        fi
    else
        echo "000"
    fi
}

check_docker_containers() {
    local unhealthy=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" | wc -l | tr -d ' ')
    local stopped=$(docker ps -a --filter "status=exited" --format "{{.Names}}" | wc -l | tr -d ' ')
    echo "${unhealthy},${stopped}"
}

#############################################
# Incident Detection
#############################################

detect_api_failure() {
    local status=$(check_api_health)
    if [[ "${status}" != "200" ]]; then
        incident "🚨 API FAILURE: API returned status ${status}"
        return 1
    fi
    return 0
}

detect_database_failure() {
    local status=$(check_database_health)
    if [[ "${status}" != "200" ]]; then
        incident "🚨 DATABASE FAILURE: Database health check returned ${status}"
        return 1
    fi
    return 0
}

detect_redis_failure() {
    local status=$(check_redis_health)
    if [[ "${status}" != "200" ]]; then
        incident "🚨 REDIS FAILURE: Redis health check returned ${status}"
        return 1
    fi
    return 0
}

detect_container_failure() {
    local result=$(check_docker_containers)
    local unhealthy=$(echo "${result}" | cut -d',' -f1)
    local stopped=$(echo "${result}" | cut -d',' -f2)

    if [[ "${unhealthy}" -gt 0 ]]; then
        incident "🚨 CONTAINER FAILURE: ${unhealthy} unhealthy containers"
        return 1
    fi

    if [[ "${stopped}" -gt 0 ]]; then
        incident "🚨 CONTAINER FAILURE: ${stopped} stopped containers"
        return 1
    fi
    return 0
}

detect_high_memory() {
    local mem_percent=$(free | awk '/Mem/{printf("%.0f"), $3/$2*100}')
    if [[ "${mem_percent}" -gt 90 ]]; then
        incident "⚠️  HIGH MEMORY USAGE: ${mem_percent}% used"
        return 1
    fi
    return 0
}

detect_high_cpu() {
    # Check 1-minute load average
    local load=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | xargs)
    local cpus=$(nproc)
    local load_per_cpu=$(echo "${load} / ${cpus}" | bc -l)

    if (( $(echo "${load_per_cpu} > 2.0" | bc -l) )); then
        incident "⚠️  HIGH CPU LOAD: ${load} (load per CPU: ${load_per_cpu})"
        return 1
    fi
    return 0
}

detect_disk_space() {
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ "${usage}" -gt 85 ]]; then
        incident "⚠️  LOW DISK SPACE: ${usage}% used"
        return 1
    fi
    return 0
}

#############################################
# Automated Remediation
#############################################

restart_unhealthy_containers() {
    log "🔧 Attempting to restart unhealthy containers..."

    local unhealthy=$(docker ps --filter "health=unhealthy" --format "{{.Names}}")
    if [[ -n "${unhealthy}" ]]; then
        echo "${unhealthy}" | while read -r container; do
            log "Restarting container: ${container}"
            docker restart "${container}"
        done
        log "✅ Container restart initiated"
        return 0
    fi
    return 1
}

restart_stopped_containers() {
    log "🔧 Attempting to restart stopped containers..."

    local stopped=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    if [[ -n "${stopped}" ]]; then
        echo "${stopped}" | while read -r container; do
            log "Starting container: ${container}"
            docker start "${container}"
        done
        log "✅ Container start initiated"
        return 0
    fi
    return 1
}

clear_docker_cache() {
    log "🔧 Clearing Docker cache to free disk space..."

    docker system prune -f --volumes
    log "✅ Docker cache cleared"
}

restart_api_service() {
    log "🔧 Restarting API service..."

    if [[ -f "docker-compose.yml" ]]; then
        docker-compose restart backend
        log "✅ API service restarted"
    fi
}

scale_up_backend() {
    log "🔧 Scaling up backend due to high load..."

    if [[ -f "docker-compose.yml" ]]; then
        docker-compose up -d --scale backend=3
        log "✅ Backend scaled to 3 instances"
    fi
}

#############################################
# Notifications
#############################################

send_slack_alert() {
    local message="$1"

    if [[ -n "${SLACK_WEBHOOK}" ]] && command -v curl &> /dev/null; then
        local payload=$(cat <<EOF
{
  "text": "🚨 FinanceHub Incident Alert",
  "attachments": [
    {
      "color": "danger",
      "title": "Incident Detected",
      "text": "${message}",
      "footer": "FinanceHub Automated Incident Response",
      "ts": $(date +%s)
    }
  ]
}
EOF
)
        curl -s -X POST "${SLACK_WEBHOOK}" \
            -H "Content-Type: application/json" \
            -d "${payload}" &> /dev/null
        log "📱 Slack alert sent"
    fi
}

send_slack_recovery() {
    local message="$1"

    if [[ -n "${SLACK_WEBHOOK}" ]] && command -v curl &> /dev/null; then
        local payload=$(cat <<EOF
{
  "text": "✅ FinanceHub Incident Resolved",
  "attachments": [
    {
      "color": "good",
      "title": "Service Recovered",
      "text": "${message}",
      "footer": "FinanceHub Automated Incident Response",
      "ts": $(date +%s)
    }
  ]
}
EOF
)
        curl -s -X POST "${SLACK_WEBHOOK}" \
            -H "Content-Type: application/json" \
            -d "${payload}" &> /dev/null
        log "📱 Slack recovery notification sent"
    fi
}

#############################################
# Incident Lifecycle Management
#############################################

declare -A incident_count
declare -A incident_start_time

track_incident() {
    local incident_type="$1"
    incident_count["${incident_type}"]=$((${incident_count[${incident_type}]:-0} + 1))
    incident_start_time["${incident_type}"]=$(date +%s)

    local count=${incident_count[${incident_type}]}

    if [[ "${count}" -ge "${ALERT_THRESHOLD}" ]]; then
        incident "🚨 THRESHOLD REACHED: ${incident_type} failed ${count} times"
        send_slack_alert "${incident_type} has failed ${count} consecutive checks"

        # Trigger automated remediation
        if [[ "${AUTO_REMEDIATE}" == "true" ]]; then
            remediate_incident "${incident_type}"
        fi
    fi
}

clear_incident() {
    local incident_type="$1"
    local count=${incident_count[${incident_type}]:-0}
    local start_time=${incident_start_time[${incident_type}]:-0}
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [[ "${count}" -gt 0 ]]; then
        incident "✅ RESOLVED: ${incident_type} recovered after ${count} failures (duration: ${duration}s)"
        send_slack_recovery "${incident_type} is back to normal. Downtime: ${duration}s"

        # Reset counters
        incident_count["${incident_type}"]=0
        incident_start_time["${incident_type}"]=0
    fi
}

remediate_incident() {
    local incident_type="$1"

    log "🔧 Attempting automated remediation for: ${incident_type}"

    case "${incident_type}" in
        "api_failure")
            restart_api_service
            ;;
        "container_failure")
            restart_unhealthy_containers
            restart_stopped_containers
            ;;
        "disk_space")
            clear_docker_cache
            ;;
        "high_cpu")
            scale_up_backend
            ;;
        *)
            warning "No automated remediation available for: ${incident_type}"
            ;;
    esac
}

#############################################
# Main Monitoring Loop
#############################################

monitor_systems() {
    log "🚀 Starting automated incident monitoring..."
    log "Threshold: ${ALERT_THRESHOLD} consecutive failures"
    log "Auto-remediation: ${AUTO_REMEDIATE}"
    log "================================"

    while true; do
        local current_time=$(date +'%Y-%m-%d %H:%M:%S')
        log "⏱️  Health check at ${current_time}"

        # Check API
        if detect_api_failure; then
            track_incident "api_failure"
        else
            clear_incident "api_failure"
        fi

        # Check Database
        if detect_database_failure; then
            track_incident "database_failure"
        else
            clear_incident "database_failure"
        fi

        # Check Redis
        if detect_redis_failure; then
            track_incident "redis_failure"
        else
            clear_incident "redis_failure"
        fi

        # Check Containers
        if detect_container_failure; then
            track_incident "container_failure"
        else
            clear_incident "container_failure"
        fi

        # Check Memory
        if detect_high_memory; then
            track_incident "high_memory"
        else
            clear_incident "high_memory"
        fi

        # Check CPU
        if detect_high_cpu; then
            track_incident "high_cpu"
        else
            clear_incident "high_cpu"
        fi

        # Check Disk
        if detect_disk_space; then
            track_incident "disk_space"
        else
            clear_incident "disk_space"
        fi

        log "⏳ Waiting ${RECOVERY_CHECK_INTERVAL}s before next check..."
        sleep "${RECOVERY_CHECK_INTERVAL}"
    done
}

single_check() {
    log "🔍 Running single health check..."

    local issues=0

    detect_api_failure || ((issues++))
    detect_database_failure || ((issues++))
    detect_redis_failure || ((issues++))
    detect_container_failure || ((issues++))
    detect_high_memory || ((issues++))
    detect_high_cpu || ((issues++))
    detect_disk_space || ((issues++))

    if [[ "${issues}" -eq 0 ]]; then
        log "✅ All systems healthy"
        return 0
    else
        error "❌ ${issues} issue(s) detected"
        return 1
    fi
}

#############################################
# Incident Report
#############################################

show_incident_report() {
    log "📊 Recent Incident Report"
    log "================================"

    if [[ -f "${INCIDENT_LOG}" ]]; then
        echo ""
        grep "INCIDENT" "${INCIDENT_LOG}" | tail -20
        echo ""
        log "================================"
        log "📄 Full log: ${INCIDENT_LOG}"
    else
        warning "No incident log found"
    fi
}

#############################################
# Main
#############################################

main() {
    local command="${1:-monitor}"
    shift || true

    case "${command}" in
        monitor)
            monitor_systems
            ;;
        check)
            single_check
            ;;
        report)
            show_incident_report
            ;;
        remediate)
            remediate_incident "$@"
            ;;
        help|--help|-h)
            cat << EOF
FinanceHub Automated Incident Response

Usage: $0 <command> [options]

Commands:
  monitor               Run continuous monitoring (default)
  check                 Run single health check
  report                Show recent incident report
  remediate <type>      Manually trigger remediation

Examples:
  $0 monitor            # Start monitoring loop
  $0 check              # Single health check
  $0 report             # Show recent incidents
  $0 remediate api_failure

Environment Variables:
  SLACK_WEBHOOK         Slack webhook for alerts
  ALERT_THRESHOLD       Failures before alert (default: 5)
  RECOVERY_CHECK_INTERVAL Seconds between checks (default: 30)
  AUTO_REMEDIATE        Enable auto-fix (default: true)
  INCIDENT_LOG          Log file path

Automated Actions:
  • Detects failures in API, database, Redis, containers
  • Monitors CPU, memory, disk usage
  • Tracks consecutive failures
  • Triggers automated remediation
  • Sends Slack alerts
  • Logs all incidents
  • Tracks recovery time (MTTR)

Author: KAREN (DevOps Engineer)
Date: 2026-01-30
EOF
            ;;
        *)
            error "Unknown command: ${command}"
            exit 1
            ;;
    esac
}

main "$@"
