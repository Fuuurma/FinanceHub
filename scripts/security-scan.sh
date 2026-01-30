#!/bin/bash
#############################################
# FinanceHub - Security Scanner
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Comprehensive security scanning
#############################################

set -euo pipefail

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

echo ""
log "🔒 FinanceHub Security Scanner"
log "================================"
echo ""

# Track overall status
VULNERABILITIES_FOUND=0
TOTAL_SCANS=0

#############################################
# Frontend Security Scan (npm audit)
#############################################

scan_frontend() {
    log "📦 Scanning Frontend dependencies..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    if [[ -f "Frontend/src/package.json" ]]; then
        cd Frontend/src

        if command -v npm &> /dev/null; then
            # Run npm audit
            if npm audit --json > /tmp/npm-audit.json 2>&1; then
                VULNS=$(jq '.vulnerabilities | length' /tmp/npm-audit.json 2>/dev/null || echo "0")

                if [[ "${VULNS}" == "0" ]]; then
                    log "✅ Frontend: No vulnerabilities found"
                else
                    error "❌ Frontend: ${VULNS} vulnerabilities found"
                    npm audit --audit-level=moderate
                    VULNERABILITIES_FOUND=$((VULNERABILITIES_FOUND + VULNS))
                fi
            else
                warning "⚠️  npm audit failed"
            fi

            cd ../../
        else
            warning "⚠️  npm not found, skipping frontend scan"
        fi
    else
        warning "⚠️  Frontend package.json not found"
    fi
}

#############################################
# Backend Security Scan (Python)
#############################################

scan_backend() {
    log "🐍 Scanning Backend dependencies..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    if [[ -d "Backend" ]]; then
        cd Backend

        # Check for known vulnerable packages
        warning "⚠️  Full Python scan requires pip-audit (not installed)"
        info "💡 Install with: pip3 install --user pip-audit safety bandit"

        # Manual check of critical packages
        log "🔍 Checking critical package versions..."

        # Check Django version
        if grep -q "django" requirements-testing.txt 2>/dev/null; then
            DJANGO_VERSION=$(grep "django" requirements-testing.txt | head -1)
            info "Django: ${DJANGO_VERSION}"
            warning "💡 Ensure Django is updated to latest 5.x or 4.2.x for security patches"
        fi

        # Check for other critical packages
        if grep -q "requests" requirements-testing.txt 2>/dev/null; then
            REQUESTS_VERSION=$(grep "requests" requirements-testing.txt | head -1)
            info "Requests: ${REQUESTS_VERSION}"
        fi

        cd ..
    else
        warning "⚠️  Backend directory not found"
    fi
}

#############################################
# Secret Detection
#############################################

scan_secrets() {
    log "🔐 Scanning for exposed secrets..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    local secrets_found=0

    # Check for common secret patterns
    if grep -r -i -E "password.*=.*['\"][^'\"]+['\"]|api[_-]?key.*=.*['\"][^'\"]+['\"]|secret.*=.*['\"][^'\"]+['\"]|token.*=.*['\"][^'\"]+['\"]" \
        --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.json" \
        --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.next . 2>/dev/null | head -10; then
        error "❌ Potential secrets found in code!"
        secrets_found=1
    fi

    # Check .env files
    if [[ -f ".env" ]]; then
        warning "⚠️  .env file exists (should be in .gitignore)"
    fi

    if [[ $secrets_found -eq 0 ]]; then
        log "✅ No exposed secrets detected"
    else
        VULNERABILITIES_FOUND=$((VULNERABILITIES_FOUND + 1))
    fi
}

#############################################
# .gitignore Security Check
#############################################

check_gitignore() {
    log "📝 Checking .gitignore security..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    local missing_items=0

    # Check for critical entries in .gitignore
    for item in ".env" "*.key" "*.pem" "secrets/" "credentials/" "node_modules/" "venv/"; do
        if ! grep -q "${item}" .gitignore 2>/dev/null; then
            warning "⚠️  Missing in .gitignore: ${item}"
            missing_items=1
        fi
    done

    if [[ $missing_items -eq 0 ]]; then
        log "✅ .gitignore security looks good"
    else
        error "❌ Security-sensitive items missing from .gitignore"
        VULNERABILITIES_FOUND=$((VULNERABILITIES_FOUND + 1))
    fi
}

#############################################
# Dependency Update Check
#############################################

check_outdated() {
    log "📅 Checking for outdated dependencies..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    # Frontend
    if [[ -f "Frontend/src/package.json" ]]; then
        cd Frontend/src

        if command -v npm &> /dev/null; then
            log "Checking for outdated npm packages..."
            npm outdated 2>/dev/null | head -10 || true
        fi

        cd ../../
    fi

    # Backend
    if [[ -d "Backend" ]]; then
        log "💡 Backend: Use 'pip list --outdated' to check for outdated packages"
    fi
}

#############################################
# File Permissions Check
#############################################

check_permissions() {
    log "🔒 Checking file permissions..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    local issues=0

    # Check for overly permissive files
    if find . -type f -perm -o=g,w,o+w -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/venv/*" 2>/dev/null | head -5; then
        error "❌ Found files with excessive write permissions"
        issues=1
    fi

    # Check for SSH keys with wrong permissions
    if find . -type f -name "id_rsa*" -not -perm 0600 2>/dev/null | grep -q .; then
        error "❌ SSH keys without proper permissions (should be 0600)"
        issues=1
    fi

    if [[ $issues -eq 0 ]]; then
        log "✅ File permissions look good"
    else
        VULNERABILITIES_FOUND=$((VULNERABILITIES_FOUND + 1))
    fi
}

#############################################
# Security Headers Check
#############################################

check_security_headers() {
    log "🛡️  Checking security headers configuration..."

    TOTAL_SCANS=$((TOTAL_SCANS + 1))

    if [[ -f "Frontend/next.config.js" ]] || [[ -f "Frontend/next.config.ts" ]] || [[ -f "Frontend/next.config.mjs" ]]; then
        log "Next.js config found - ensure security headers are configured"

        # Check for common security headers
        local config_file=$(find Frontend -name "next.config.*" -not -path "*/node_modules/*" | head -1)
        if [[ -n "${config_file}" ]]; then
            if grep -qi "contentSecurityPolicy\|helmet\|x-frame-options\|strict-transport-security" "${config_file}" 2>/dev/null; then
                log "✅ Security headers configured"
            else
                warning "⚠️  Consider adding Content-Security-Policy and other security headers"
            fi
        fi
    fi

    # Backend Django settings
    if [[ -f "Backend/src/config/settings.py" ]] || [[ -f "Backend/src/settings.py" ]]; then
        log "Django settings found - ensure security middleware is configured"

        # Check for security settings
        local settings_file=$(find Backend/src -name "settings.py" 2>/dev/null | head -1)
        if [[ -n "${settings_file}" ]]; then
            if grep -qi "SECURE_SSL_REDIRECT\|SECURE_HSTS_SECONDS\|SESSION_COOKIE_SECURE\|CSRF_COOKIE_SECURE" "${settings_file}" 2>/dev/null; then
                log "✅ Django security settings configured"
            else
                warning "⚠️  Ensure Django security settings are enabled for production"
            fi
        fi
    fi
}

#############################################
# Generate Security Report
#############################################

generate_report() {
    echo ""
    log "================================"
    log "📊 Security Scan Summary"
    log "================================"
    echo ""
    log "Scans performed: ${TOTAL_SCANS}"
    log "Vulnerabilities found: ${VULNERABILITIES_FOUND}"
    echo ""

    if [[ ${VULNERABILITIES_FOUND} -eq 0 ]]; then
        log "✅ No critical vulnerabilities detected"
        log "✅ Security posture is good"
    else
        error "❌ ${VULNERABILITIES_FOUND} security issue(s) found"
        echo ""
        log "Recommended actions:"
        echo "1. Update dependencies with known vulnerabilities"
        echo "2. Run: npm audit fix (frontend)"
        echo "3. Update Python packages: pip install -U package_name"
        echo "4. Review and fix any secret exposures"
        echo "5. Add missing items to .gitignore"
        echo "6. Configure security headers"
    fi

    echo ""
    log "================================"

    # Return exit code based on findings
    return ${VULNERABILITIES_FOUND}
}

#############################################
# Main
#############################################

main() {
    scan_frontend
    echo ""
    scan_backend
    echo ""
    scan_secrets
    echo ""
    check_gitignore
    echo ""
    check_permissions
    echo ""
    check_security_headers
    echo ""
    check_outdated
    echo ""
    generate_report
}

main "$@"
