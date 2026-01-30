"""
CDN Utilities for Cache Management

Provides utilities for interacting with CloudFlare CDN API
for cache purging and monitoring.

Usage:
    from utils.cdn import purge_cdn_cache, get_cache_status
"""

import os
import requests
from typing import List, Dict, Optional
from django.conf import settings


class CloudFlareCDN:
    """CloudFlare CDN management class."""

    def __init__(self):
        self.zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
        self.api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
        self.base_url = "https://api.cloudflare.com/client/v4"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _get_zone_url(self, endpoint: str) -> str:
        """Build URL for zone-specific endpoint."""
        return f"{self.base_url}/zones/{self.zone_id}{endpoint}"

    def is_configured(self) -> bool:
        """Check if CloudFlare is configured."""
        return bool(self.zone_id and self.api_token)

    def purge_cache(self, urls: List[str]) -> Dict:
        """
        Purge CDN cache for specific URLs.

        Args:
            urls: List of URLs to purge from cache

        Returns:
            Dict with success status and response data
        """
        if not self.is_configured():
            return {"success": False, "error": "CloudFlare not configured"}

        try:
            response = requests.post(
                self._get_zone_url("/purge_cache"),
                headers=self._get_headers(),
                json={"files": urls},
                timeout=30,
            )
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def purge_everything(self) -> Dict:
        """
        Purge entire CDN cache.

        Warning: This will cause all cached content to be re-fetched from origin.

        Returns:
            Dict with success status and response data
        """
        if not self.is_configured():
            return {"success": False, "error": "CloudFlare not configured"}

        try:
            response = requests.post(
                self._get_zone_url("/purge_cache"),
                headers=self._get_headers(),
                json={"purge_everything": True},
                timeout=30,
            )
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_analytics(self) -> Dict:
        """
        Get CDN analytics data.

        Returns:
            Dict with analytics data
        """
        if not self.is_configured():
            return {"success": False, "error": "CloudFlare not configured"}

        try:
            response = requests.get(
                self._get_zone_url("/analytics/dashboard"),
                headers=self._get_headers(),
                timeout=30,
            )
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache hit/miss statistics
        """
        if not self.is_configured():
            return {"success": False, "error": "CloudFlare not configured"}

        try:
            response = requests.get(
                self._get_zone_url("/analytics/colos"),
                headers=self._get_headers(),
                timeout=30,
            )
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}


cdn_client = CloudFlareCDN()


def purge_cdn_cache(urls: List[str]) -> Dict:
    """
    Convenience function to purge CDN cache for specific URLs.

    Args:
        urls: List of URLs to purge from cache

    Returns:
        Dict with success status and message
    """
    result = cdn_client.purge_cache(urls)
    if result.get("success"):
        return {
            "success": True,
            "message": f"Successfully purged {len(urls)} URLs from CDN cache",
        }
    return {
        "success": False,
        "message": f"Failed to purge CDN cache: {result.get('error', 'Unknown error')}",
    }


def purge_static_files_cache() -> Dict:
    """
    Purge cache for all static file URLs.

    Useful after deploying new static assets.

    Returns:
        Dict with success status and message
    """
    if not settings.CDN_ENABLED:
        return {"success": False, "message": "CDN is not enabled"}

    base_url = settings.CDN_URL.rstrip("/")
    static_urls = [
        f"{base_url}/static/",
        f"{base_url}/static/css/",
        f"{base_url}/static/js/",
        f"{base_url}/media/",
    ]

    return purge_cdn_cache(static_urls)


def get_cache_status() -> Dict:
    """
    Get current CDN cache status.

    Returns:
        Dict with cache configuration and statistics
    """
    return {
        "cdn_enabled": settings.CDN_ENABLED,
        "cdn_url": settings.CDN_URL if settings.CDN_ENABLED else None,
        "configured": cdn_client.is_configured(),
        "analytics": cdn_client.get_analytics() if cdn_client.is_configured() else None,
    }
