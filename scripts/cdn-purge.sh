#!/bin/bash

# CDN Cache Purge Script
# Usage: ./scripts/cdn-purge.sh [--all | --static | --media]
# This script purges the CloudFlare CDN cache after deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CDN_URL="${CDN_URL:-https://assets.financehub.app}"
CLOUDFLARE_ZONE_ID="${CLOUDFLARE_ZONE_ID:-}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if CloudFlare is configured
check_config() {
    if [[ -z "$CLOUDFLARE_ZONE_ID" || -z "$CLOUDFLARE_API_TOKEN" ]]; then
        log_error "CloudFlare credentials not configured."
        log_error "Please set CLOUDFLARE_ZONE_ID and CLOUDFLARE_API_TOKEN environment variables."
        exit 1
    fi
}

# Purge specific URLs
purge_urls() {
    local urls=("$@")
    local url_json=$(printf '"%s"' "${urls[@]}" | tr ' ' ',')

    log_info "Purging ${#urls[@]} URLs from CDN cache..."

    response=$(curl -s -X POST \
        "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"files\": [${url_json}]}")

    if echo "$response" | grep -q '"success":true'; then
        log_info "Successfully purged CDN cache for ${#urls[@]} URLs"
        return 0
    else
        log_error "Failed to purge CDN cache"
        echo "$response"
        return 1
    fi
}

# Purge entire cache
purge_all() {
    log_warn "This will purge the ENTIRE CDN cache. This may cause temporary increased load on origin servers."
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [[ "$confirm" != "yes" ]]; then
        log_info "Aborted cache purge."
        exit 0
    fi

    log_info "Purging entire CDN cache..."

    response=$(curl -s -X POST \
        "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"purge_everything": true}')

    if echo "$response" | grep -q '"success":true'; then
        log_info "Successfully purged entire CDN cache"
        return 0
    else
        log_error "Failed to purge CDN cache"
        echo "$response"
        return 1
    fi
}

# Purge static files
purge_static() {
    log_info "Purging static files cache..."

    local static_urls=(
        "${CDN_URL}/static/"
        "${CDN_URL}/static/css/"
        "${CDN_URL}/static/js/"
        "${CDN_URL}/_next/static/"
    )

    purge_urls "${static_urls[@]}"
}

# Purge media files
purge_media() {
    log_info "Purging media files cache..."

    local media_urls=(
        "${CDN_URL}/media/"
    )

    purge_urls "${media_urls[@]}"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all       Purge entire CDN cache (use with caution)"
    echo "  --static    Purge static files (CSS, JS)"
    echo "  --media     Purge media files (uploads)"
    echo "  --help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  CDN_URL              CDN base URL (default: https://assets.financehub.app)"
    echo "  CLOUDFLARE_ZONE_ID   CloudFlare zone ID"
    echo "  CLOUDFLARE_API_TOKEN CloudFlare API token"
    echo ""
    echo "Examples:"
    echo "  $0 --static                    # Purge static files"
    echo "  CLOUDFLARE_ZONE_ID=xxx $0 --all  # Purge entire cache"
}

# Main
main() {
    log_info "CDN Cache Purge Script"

    case "${1:-}" in
        --all)
            check_config
            purge_all
            ;;
        --static)
            check_config
            purge_static
            ;;
        --media)
            check_config
            purge_media
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        "")
            log_error "No option specified. Use --help for usage information."
            exit 1
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@"
