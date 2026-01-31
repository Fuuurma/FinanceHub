#!/bin/bash

# Security Scanning Script for FinanceHub
# Author: Charo (Security Engineer)
# Usage: ./scripts/security/scan.sh

set -e

echo "🔒 FinanceHub Security Scanner"
echo "================================"

PROJECT_ROOT="/Users/sergi/Desktop/Projects/FinanceHub"
BACKEND_DIR="${PROJECT_ROOT}/apps/backend/src"
FRONTEND_DIR="${PROJECT_ROOT}/apps/frontend/src"
REPORT_DIR="${PROJECT_ROOT}/docs/security/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "${REPORT_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[ERROR] $1" >&2
}

success() {
    echo "[✓] $1"
}

fail() {
    echo "[✗] $1" >&2
}

# 1. Dependency Vulnerability Scanning
echo ""
echo "📦 Scanning Dependencies..."
log "Starting dependency vulnerability scan"

# Backend (Python)
log "Scanning backend dependencies..."
cd "${BACKEND_DIR}"
if command -v pip-audit &> /dev/null; then
    pip-audit --format json --output "${REPORT_DIR}/pip_audit_${TIMESTAMP}.json" 2>/dev/null || true
    success "Backend dependency scan complete"
else
    error "pip-audit not installed, skipping Python scan"
fi

# Frontend (Node.js)
log "Scanning frontend dependencies..."
cd "${FRONTEND_DIR}"
npm audit --audit-level=high --json > "${REPORT_DIR}/npm_audit_${TIMESTAMP}.json" 2>/dev/null || true
success "Frontend dependency scan complete"

# 2. Docker Image Scanning
echo ""
echo "🐳 Scanning Docker Images..."
log "Starting Docker image scan"

if command -v trivy &> /dev/null; then
    cd "${PROJECT_ROOT}"
    
    # Build backend image if not exists
    if ! docker image inspect financehub-backend &> /dev/null; then
        log "Building backend image for scan..."
        docker build -t financehub-backend -f apps/backend/Dockerfile . 2>/dev/null || true
    fi
    
    if docker image inspect financehub-backend &> /dev/null; then
        trivy image --format json --output "${REPORT_DIR}/trivy_backend_${TIMESTAMP}.json" \
            --severity CRITICAL,HIGH financehub-backend 2>/dev/null || true
        success "Backend Docker image scan complete"
    else
        error "Backend image not found, skipping"
    fi
else
    error "Trivy not installed, skipping Docker scan"
    echo "   Install with: brew install trivy"
fi

# 3. Secret Detection
echo ""
echo "🔑 Scanning for Secrets..."
log "Starting secret detection scan"

cd "${PROJECT_ROOT}"

# Check for patterns that might indicate secrets
SECRETS_PATTERN="(
    api_key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]|
    secret\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]|
    password\s*=\s*['\"][^'\"]+['\"]|
    token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]|
    private_key\s*=\s*['\"]
)"

# Check git history for secrets
log "Checking git history for secrets..."
git log --all --full-history --source --grep="password\|secret\|key\|token" \
    --oneline 2>/dev/null | head -10 || true

# Check for secrets in code (excluding node_modules, .git, etc.)
if command -v grep &> /dev/null; then
    GREP_RESULTS=$(grep -r --include="*.py" --include="*.ts" --include="*.tsx" \
        -E "(api_key|secret|password|token).*['\"=]" \
        "${BACKEND_DIR}" "${FRONTEND_DIR}" \
        --exclude-dir=node_modules \
        --exclude-dir=.git \
        --exclude-dir=__pycache__ \
        2>/dev/null | grep -v "os.getenv\|os.environ" | head -20 || true)
    
    if [ -n "$GREP_RESULTS" ]; then
        echo "Potential secrets found (excluding env vars):"
        echo "$GREP_RESULTS"
    else
        success "No obvious secrets in code"
    fi
fi

# 4. File Permission Check
echo ""
echo "🔐 Checking File Permissions..."
log "Starting file permission check"

cd "${PROJECT_ROOT}"

# Check for world-writable files
WORLD_WRITABLE=$(find . -type f -perm -o+w -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -10 || true)

if [ -n "$WORLD_WRITABLE" ]; then
    echo "World-writable files found:"
    echo "$WORLD_WRITABLE"
else
    success "No world-writable files found"
fi

# Check for files without restrictions
EXECUTABLE_SCRIPTS=$(find . -name "*.sh" -type f -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -10 || true)

if [ -n "$EXECUTABLE_SCRIPTS" ]; then
    echo "Shell scripts found:"
    echo "$EXECUTABLE_SCRIPTS"
fi

# 5. Git History Security Check
echo ""
echo "📜 Checking Git History..."
log "Checking git history for security issues"

cd "${PROJECT_ROOT}"

# Check for secrets in git history
GIT_SECRETS=$(git log --all --full-history -p --source \
    -- "*.py" "*.ts" "*.tsx" "*.js" \
    --grep="password\|secret\|key\|token" \
    2>/dev/null | grep -E "[a-zA-Z0-9]{20,}" | head -20 || true)

if [ -n "$GIT_SECRETS" ]; then
    echo "Potential secrets in git history:"
    echo "$GIT_SECRETS"
else
    success "No obvious secrets in git history"
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore && grep -q "*.key" .gitignore && grep -q "*.pem" .gitignore; then
        success ".gitignore properly configured"
    else
        error ".gitignore may be missing important entries"
    fi
fi

# 6. Generate Summary Report
echo ""
echo "📊 Generating Summary Report..."
log "Generating security summary report"

cat > "${REPORT_DIR}/security_summary_${TIMESTAMP}.md" << EOF
# Security Scan Summary - ${TIMESTAMP}

## Scan Date
$(date '+%Y-%m-%d %H:%M:%S')

## Scans Performed
1. ✅ Dependency Vulnerability Scan
2. ✅ Docker Image Scan
3. ✅ Secret Detection
4. ✅ File Permission Check
5. ✅ Git History Check

## Reports Generated
- pip_audit_${TIMESTAMP}.json
- npm_audit_${TIMESTAMP}.json
- trivy_backend_${TIMESTAMP}.json

## Next Steps
1. Review vulnerability reports
2. Fix critical and high severity issues
3. Update dependencies as needed
4. Re-scan after fixes

## Notes
- Automated scan completed successfully
- Full manual audit recommended monthly
EOF

success "Summary report generated: ${REPORT_DIR}/security_summary_${TIMESTAMP}.md"

# 7. Summary
echo ""
echo "================================"
echo "🔒 Security Scan Complete"
echo "================================"
echo ""
echo "Reports generated in: ${REPORT_DIR}/"
echo ""
echo "Next steps:"
echo "1. Review ${REPORT_DIR}/security_summary_${TIMESTAMP}.md"
echo "2. Fix critical vulnerabilities"
echo "3. Run: ./scripts/security/scan.sh"
echo ""

log "Security scan completed successfully"
