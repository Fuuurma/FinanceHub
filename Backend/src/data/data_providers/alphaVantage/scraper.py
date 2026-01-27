"""
Alpha Vantage Scraper using BaseAPIFetcher for key rotation
"""
import aiohttp
from typing import Dict, Optional, List

from data.data_providers.base_fetcher import BaseAPIFetcher
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class AlphaVantageScraper(BaseAPIFetcher):
    """
    Alpha Vantage API implementation with key rotation
    
    Free tier: 5 API calls/minute, 500 calls/day per key
    Strategy: Rotate between multiple free accounts
    """
    
    def __init__(self):
        super().__init__(provider_name="alpha_vantage")
    
    def get_base_url(self) -> str:
        return "https://www.alphavantage.co/query"
    
    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        """Extract rate limit error from Alpha Vantage response"""
        if "Note" in response:
            note = response["Note"]
            if "frequency" in note.lower() or "call" in note.lower():
                return note
        if "Error Message" in response:
            error_msg = response["Error Message"]
            if "frequency" in error_msg.lower() or "call" in error_msg.lower():
                return error_msg
        return None
    
    def _get_headers(self, api_key) -> Dict:
        """Alpha Vantage uses query params, not headers"""
        return {}
    
    async def _make_request(self, endpoint: str, params: Optional[Dict], method: str, api_key) -> Dict:
        """Make request with API key in params"""
        if params is None:
            params = {}
        params["apikey"] = api_key.key_value
        
        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)
        
        async with self.session.request(method, url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    # Stock Time Series
    
    async def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        return await self.request("", params=params)
    
    async def get_intraday(self, symbol: str, interval: str = "5min") -> Dict:
        """Get intraday time series"""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": "compact"
        }
        return await self.request("", params=params)
    
    async def get_daily(self, symbol: str) -> Dict:
        """Get daily time series"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact"
        }
        return await self.request("", params=params)
    
    # Fundamental Data
    
    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol
        }
        return await self.request("", params=params)
    
    async def get_income_statement(self, symbol: str) -> Dict:
        """Get income statement"""
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol
        }
        return await self.request("", params=params)
    
    async def get_balance_sheet(self, symbol: str) -> Dict:
        """Get balance sheet"""
        params = {
            "function": "BALANCE_SHEET",
            "symbol": symbol
        }
        return await self.request("", params=params)
    
    async def get_cash_flow(self, symbol: str) -> Dict:
        """Get cash flow"""
        params = {
            "function": "CASH_FLOW",
            "symbol": symbol
        }
        return await self.request("", params=params)
    
    async def get_earnings(self, symbol: str) -> Dict:
        """Get earnings data"""
        params = {
            "function": "EARNINGS",
            "symbol": symbol
        }
        return await self.request("", params=params)
    
    # Convenience methods for data_fetcher.py
    
    async def fetch_multiple_stocks(self, symbols: List[str]) -> Dict[str, bool]:
        """Fetch multiple stocks, returns dict of success status"""
        results = {}
        async with self:
            for symbol in symbols:
                try:
                    quote = await self.get_quote(symbol)
                    if quote and "Global Quote" in quote:
                        results[symbol] = True
                        logger.info(f"Successfully fetched {symbol}")
                    else:
                        results[symbol] = False
                        logger.warning(f"No data for {symbol}")
                except Exception as e:
                    results[symbol] = False
                    logger.error(f"Error fetching {symbol}: {str(e)}")
        return results
    
    async def fetch_and_save_stock(self, symbol: str) -> bool:
        """Fetch and save a single stock"""
        # TODO: Integrate with Django models
        try:
            async with self:
                quote = await self.get_quote(symbol)
                if quote and "Global Quote" in quote:
                    # Process and save to database
                    logger.info(f"Successfully saved {symbol}")
                    return True
                else:
                    logger.warning(f"No data for {symbol}")
                    return False
        except Exception as e:
            logger.error(f"Error saving {symbol}: {str(e)}")
            return False
    
    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings
        scraper = cls()
        # Note: This will be overridden by key rotation system
        # Keeping for backward compatibility with existing data_fetcher.py
        return scraper