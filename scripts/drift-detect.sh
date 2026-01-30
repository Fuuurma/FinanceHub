#!/bin/bash
#############################################
# FinanceHub - Infrastructure Drift Detection
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Detect infrastructure drift from expected state
#############################################

set -euo pipefail

# Configuration
STATE_FILE="${STATE_FILE:-./config/infrastructure-state.json}"
DRIFT_REPORT="${DRIFT_REPORT:-./reports/dift-report-$(date +%Y%m%d-%H%M%S).txt}"
AUTO_FIX="${AUTO_FIX:-false}"

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

# Ensure directories exist
mkdir -p "$(dirname "${STATE_FILE}")"
mkdir -p "$(dirname "${DRIFT_REPORT}")"

#############################################
# State Capture
#############################################

capture_docker_state() {
    log "🐳 Capturing Docker state..."

    local docker_state="{"
    docker_state+="\"containers\": $(docker ps -a --format '{{json .}}' | jq -s '.'),"
    docker_state+="\"images\": $(docker images --format '{{json .}}' | jq -s '.'),"
    docker_state+="\"networks\": $(docker network ls --format '{{json .}}' | jq -s '.'),"
    docker_state+="\"volumes\": $(docker volume ls --format '{{json .}}' | jq -s '.')"
    docker_state+="}"

    echo "${docker_state}" | jq '.' > "${STATE_FILE}.docker.json"
    log "✅ Docker state captured"
}

capture_system_state() {
    log "🖥️  Capturing system state..."

    local system_state="{"
    system_state+="\"hostname\": \"$(hostname)\","
    system_state+="\"os\": \"$(uname -a)\","
    system_state+="\"uptime\": \"$(uptime -p)\","
    system_state+="\"cpu_cores\": $(nproc),"
    system_state+="\"memory_gb\": $(free -g | awk '/Mem/{print $2}'),"
    system_state+="\"disk_usage\": $(df -h / | awk 'NR==2 {print $5}' | sed 's/%//'),"
    system_state+="\"timestamp\": \"$(date -Iseconds)\""
    system_state+="}"

    echo "${system_state}" | jq '.' > "${STATE_FILE}.system.json"
    log "✅ System state captured"
}

capture_git_state() {
    log "📦 Capturing Git state..."

    local git_state="{"
    git_state+="\"branch\": \"$(git rev-parse --abbrev-ref HEAD)\","
    git_state+="\"commit\": \"$(git rev-parse HEAD)\","
    git_state+="\"origin\": \"$(git remote get-url origin)\","
    git_state+="\"status\": \"$(git status --porcelain | wc -l | tr -d ' ') uncommitted files\","
    git_state+="\"timestamp\": \"$(date -Iseconds)\""
    git_state+="}"

    echo "${git_state}" | jq '.' > "${STATE_FILE}.git.json"
    log "✅ Git state captured"
}

capture_environment_state() {
    log "🌍 Capturing environment state..."

    # Capture .env file (excluding secrets)
    local env_state="{"
    env_state+="\"database_host\": \"${DATABASE_URL:-not_set}\","
    env_state+="\"redis_host\": \"${REDIS_URL:-not_set}\","
    env_state+="\"debug\": \"${DEBUG:-false}\","
    env_state+="\"environment\": \"${ENVIRONMENT:-development}\","
    env_state+="\"timestamp\": \"$(date -Iseconds)\""
    env_state+="}"

    echo "${env_state}" | jq '.' > "${STATE_FILE}.env.json"
    log "✅ Environment state captured"
}

capture_full_state() {
    log "📸 Capturing full infrastructure state..."

    capture_docker_state
    capture_system_state
    capture_git_state
    capture_environment_state

    # Create combined state file
    local combined_state="{"
    combined_state+="\"docker\": $(cat ${STATE_FILE}.docker.json),"
    combined_state+="\"system\": $(cat ${STATE_FILE}.system.json),"
    combined_state+="\"git\": $(cat ${STATE_FILE}.git.json),"
    combined_state+="\"environment\": $(cat ${STATE_FILE}.env.json),"
    combined_state+="\"captured_at\": \"$(date -Iseconds)\""
    combined_state+="}"

    echo "${combined_state}" | jq '.' > "${STATE_FILE}"
    log "✅ Full infrastructure state captured to ${STATE_FILE}"
}

#############################################
# Drift Detection
#############################################

detect_docker_drift() {
    log "🔍 Detecting Docker drift..."

    if [[ ! -f "${STATE_FILE}.docker.json" ]]; then
        warning "No baseline Docker state found. Run with 'capture' first."
        return 1
    fi

    local baseline_containers=$(cat "${STATE_FILE}.docker.json" | jq -r '.containers | length')
    local current_containers=$(docker ps -a --format '{{json .}}' | jq -s '.' | jq -r '. | length')

    if [[ "${baseline_containers}" -ne "${current_containers}" ]]; then
        warning "Container count drift: baseline=${baseline_containers}, current=${current_containers}"
        return 1
    fi

    # Check for stopped containers that should be running
    local stopped_containers=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    if [[ -n "${stopped_containers}" ]]; then
        warning "Stopped containers detected: ${stopped_containers}"
        return 1
    fi

    log "✅ No Docker drift detected"
    return 0
}

detect_system_drift() {
    log "🔍 Detecting system drift..."

    if [[ ! -f "${STATE_FILE}.system.json" ]]; then
        warning "No baseline system state found. Run with 'capture' first."
        return 1
    fi

    # Check disk usage
    local baseline_disk=$(cat "${STATE_FILE}.system.json" | jq -r '.disk_usage')
    local current_disk=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [[ "${current_disk}" -gt $((baseline_disk + 10)) ]]; then
        warning "Disk usage increased significantly: baseline=${baseline_disk}%, current=${current_disk}%"
        return 1
    fi

    log "✅ No system drift detected"
    return 0
}

detect_git_drift() {
    log "🔍 Detecting Git drift..."

    if [[ ! -f "${STATE_FILE}.git.json" ]]; then
        warning "No baseline Git state found. Run with 'capture' first."
        return 1
    fi

    local baseline_commit=$(cat "${STATE_FILE}.git.json" | jq -r '.commit')
    local current_commit=$(git rev-parse HEAD)

    if [[ "${baseline_commit}" != "${current_commit}" ]]; then
        warning "Git commit drift: baseline=${baseline_commit}, current=${current_commit}"
        return 1
    fi

    local uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
    if [[ "${uncommitted}" -gt 0 ]]; then
        warning "Uncommitted changes detected: ${uncommitted} files"
        return 1
    fi

    log "✅ No Git drift detected"
    return 0
}

detect_environment_drift() {
    log "🔍 Detecting environment drift..."

    if [[ ! -f "${STATE_FILE}.env.json" ]]; then
        warning "No baseline environment state found. Run with 'capture' first."
        return 1
    fi

    # Check if critical environment variables changed
    local baseline_debug=$(cat "${STATE_FILE}.env.json" | jq -r '.debug')
    local current_debug="${DEBUG:-false}"

    if [[ "${baseline_debug}" != "${current_debug}" ]]; then
        warning "DEBUG mode changed: baseline=${baseline_debug}, current=${current_debug}"
        return 1
    fi

    log "✅ No environment drift detected"
    return 0
}

detect_all_drift() {
    log "🔍 Detecting all infrastructure drift..."

    {
        echo "═══════════════════════════════════════════════════════════════"
        echo "         FinanceHub Infrastructure Drift Report"
        echo "         Generated: $(date)"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
    } | tee "${DRIFT_REPORT}"

    local drift_found=0

    # Docker drift
    if ! detect_docker_drift 2>&1 | tee -a "${DRIFT_REPORT}"; then
        drift_found=1
    fi
    echo "" | tee -a "${DRIFT_REPORT}"

    # System drift
    if ! detect_system_drift 2>&1 | tee -a "${DRIFT_REPORT}"; then
        drift_found=1
    fi
    echo "" | tee -a "${DRIFT_REPORT}"

    # Git drift
    if ! detect_git_drift 2>&1 | tee -a "${DRIFT_REPORT}"; then
        drift_found=1
    fi
    echo "" | tee -a "${DRIFT_REPORT}"

    # Environment drift
    if ! detect_environment_drift 2>&1 | tee -a "${DRIFT_REPORT}"; then
        drift_found=1
    fi
    echo "" | tee -a "${DRIFT_REPORT}"

    {
        echo "═══════════════════════════════════════════════════════════════"
        if [[ "${drift_found}" -eq 0 ]]; then
            echo "✅ RESULT: No drift detected"
        else
            echo "⚠️  RESULT: Drift detected - review report above"
        fi
        echo "═══════════════════════════════════════════════════════════════"
    } | tee -a "${DRIFT_REPORT}"

    log "📄 Drift report saved to: ${DRIFT_REPORT}"

    return ${drift_found}
}

#############################################
# Auto-Fix Drift
#############################################

fix_docker_drift() {
    log "🔧 Attempting to fix Docker drift..."

    # Restart stopped containers
    local stopped=$(docker ps -a --filter "status=exited" --format "{{.Names}}")
    if [[ -n "${stopped}" ]]; then
        log "Starting stopped containers..."
        echo "${stopped}" | while read -r container; do
            docker start "${container}"
        done
        log "✅ Containers restarted"
    fi
}

fix_git_drift() {
    log "🔧 Git drift detected - please review manually"
    log "💡 Run: git status"
}

fix_all_drift() {
    log "🔧 Attempting to fix detected drift..."

    fix_docker_drift

    warning "Some drift may require manual intervention"
    log "📄 Review the drift report for details"
}

#############################################
# Show Drift Summary
#############################################

show_summary() {
    log "📊 Infrastructure Drift Summary"
    log "================================"

    if [[ ! -f "${STATE_FILE}" ]]; then
        warning "No baseline state found."
        log "💡 Run: $0 capture"
        return 1
    fi

    local captured_at=$(cat "${STATE_FILE}" | jq -r '.captured_at')
    log "Baseline captured: ${captured_at}"

    echo ""
    info "Docker containers: $(docker ps -a --format '{{json .}}' | jq -s '. | length')"
    info "Git commit: $(git rev-parse --short HEAD)"
    info "Disk usage: $(df -h / | awk 'NR==2 {print $5}')"
}

#############################################
# Main
#############################################

main() {
    local command="${1:-help}"
    shift || true

    case "${command}" in
        capture)
            capture_full_state
            ;;
        detect)
            detect_all_drift
            ;;
        docker)
            detect_docker_drift
            ;;
        system)
            detect_system_drift
            ;;
        git)
            detect_git_drift
            ;;
        env)
            detect_environment_drift
            ;;
        fix)
            if [[ "${AUTO_FIX}" == "true" ]]; then
                fix_all_drift
            else
                warning "AUTO_FIX is disabled. Set AUTO_FIX=true to enable auto-remediation."
            fi
            ;;
        summary)
            show_summary
            ;;
        help|--help|-h)
            cat << EOF
FinanceHub Infrastructure Drift Detection

Usage: $0 <command> [options]

Commands:
  capture              Capture current infrastructure state as baseline
  detect               Detect all infrastructure drift
  docker               Detect Docker-specific drift
  system               Detect system-specific drift
  git                  Detect Git-specific drift
  env                  Detect environment-specific drift
  fix                  Attempt to auto-fix detected drift (requires AUTO_FIX=true)
  summary              Show drift summary
  help                 Show this help

Environment Variables:
  STATE_FILE           Baseline state file (default: ./config/infrastructure-state.json)
  DRIFT_REPORT         Report file path
  AUTO_FIX             Enable auto-fix (default: false)

Examples:
  $0 capture           # Capture baseline state
  $0 detect            # Detect drift
  $0 docker            # Check Docker only
  AUTO_FIX=true $0 fix # Auto-fix drift

Use Cases:
  • Pre-deployment verification
  • Post-deployment validation
  • Compliance auditing
  • Configuration management
  • Troubleshooting

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
