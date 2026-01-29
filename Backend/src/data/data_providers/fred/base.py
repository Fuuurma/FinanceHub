"""
FRED API Base Scraper
Federal Reserve Economic Data - https://fred.stlouisfed.org/docs/api/fred/
"""

import requests
import time
from typing import Dict, Optional, Any
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class FREDBase:
    """Base class for FRED API scraper"""

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(self, api_key: str = None):
        """
        Initialize FRED scraper.

        Args:
            api_key: FRED API key (32 character alpha-numeric lowercase string)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params.update({"api_key": self.api_key, "file_type": "json"})
        self.last_request = 0
        self.rate_limit = 0.5  # 2 requests per second (120/day limit)

    def _rate_limit(self):
        """Apply rate limiting between requests"""
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """
        Make a request to FRED API.

        Args:
            endpoint: API endpoint (e.g., 'series', 'series/observations')
            params: Query parameters

        Returns:
            JSON response data
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"FRED API request failed for {endpoint}: {e}")
            return {}
