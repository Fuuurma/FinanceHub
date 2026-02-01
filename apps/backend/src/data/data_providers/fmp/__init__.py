import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class FMPFetcher:
    """
    Financial Modeling Prep API Fetcher
    Free Tier: 250 API calls/day, 5 API calls/minute
    Premium: Higher limits

    API Docs: https://site.financialmodelingprep.com/developer/docs/
    """

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request"""
        params = params or {}
        params["apikey"] = self.api_key

        try:
            async with self.session.get(f"{self.BASE_URL}/{endpoint}", params=params) as response:
                if response.status == 429:
                    logger.warning("FMP rate limit reached, waiting 60s")
                    await asyncio.sleep(60)
                    return await self._request(endpoint, params)

                response.raise_for_status()
                data = await response.json()

                await asyncio.sleep(0.5)
                return data

        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"FMP API error: {str(e)}")
            raise

    async def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile and key metrics"""
        params = {"symbol": symbol}
        return await self._request("profile", params)

    async def get_company_profile_batch(self, symbols: List[str]) -> List[Dict]:
        """Get profiles for multiple companies (more efficient)"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str}
        return await self._request("profile", params)

    async def get_key_metrics(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Get key financial metrics"""
        params = {"symbol": symbol, "period": period}
        return await self._request("key-metrics", params)

    async def get_key_metrics_batch(self, symbols: List[str], period: str = "annual") -> List[Dict]:
        """Get key metrics for multiple companies"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str, "period": period}
        return await self._request("key-metrics", params)

    async def get_financial_ratios(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Get financial ratios"""
        params = {"symbol": symbol, "period": period}
        return await self._request("financial-ratios", params)

    async def get_financial_ratios_batch(self, symbols: List[str], period: str = "annual") -> List[Dict]:
        """Get financial ratios for multiple companies"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str, "period": period}
        return await self._request("financial-ratios", params)

    async def get_enterprise_value(self, symbol: str, period: str = "annual") -> List[Dict]:
        """Get enterprise value data"""
        params = {"symbol": symbol, "period": period}
        return await self._request("enterprise-value", params)

    async def get_enterprise_value_batch(self, symbols: List[str], period: str = "annual") -> List[Dict]:
        """Get enterprise value for multiple companies"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str, "period": period}
        return await self._request("enterprise-value", params)

    async def get_income_statement(self, symbol: str, period: str = "annual", limit: int = 10) -> List[Dict]:
        """Get income statement"""
        params = {"symbol": symbol, "period": period, "limit": limit}
        return await self._request("income-statement", params)

    async def get_balance_sheet(self, symbol: str, period: str = "annual", limit: int = 10) -> List[Dict]:
        """Get balance sheet"""
        params = {"symbol": symbol, "period": period, "limit": limit}
        return await self._request("balance-sheet-statement", params)

    async def get_cash_flow(self, symbol: str, period: str = "annual", limit: int = 10) -> List[Dict]:
        """Get cash flow statement"""
        params = {"symbol": symbol, "period": period, "limit": limit}
        return await self._request("cashflow-statement", params)

    async def get_dcf(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict]:
        """Get discounted cash flow"""
        params = {"symbol": symbol, "period": period, "limit": limit}
        return await self._request("dcf", params)

    async def get_dcf_batch(self, symbols: List[str]) -> List[Dict]:
        """Get DCF for multiple companies"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str}
        return await self._request("dcf", params)

    async def get_market_cap(self, symbol: str) -> Dict:
        """Get real-time market cap"""
        params = {"symbol": symbol}
        return await self._request("market-capitalization", params)

    async def get_market_cap_batch(self, symbols: List[str]) -> List[Dict]:
        """Get market cap for multiple companies"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str}
        return await self._request("market-capitalization", params)

    async def get_stock_screener(
        self,
        market_cap_more_than: Optional[int] = None,
        market_cap_less_than: Optional[int] = None,
        beta_more_than: Optional[float] = None,
        beta_less_than: Optional[float] = None,
        volume_more_than: Optional[int] = None,
        volume_less_than: Optional[int] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        country: Optional[str] = None,
        exchange: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Screen stocks based on criteria

        Free tier: limited screening options
        Premium: full screening capabilities
        """
        params = {
            "limit": limit,
            "offset": offset,
            "marketCapMoreThan": market_cap_more_than,
            "marketCapLessThan": market_cap_less_than,
            "betaMoreThan": beta_more_than,
            "betaLessThan": beta_less_than,
            "volumeMoreThan": volume_more_than,
            "volumeLessThan": volume_less_than,
            "sector": sector,
            "industry": industry,
            "country": country,
            "exchange": exchange,
        }

        params = {k: v for k, v in params.items() if v is not None}
        return await self._request("stock-screener", params)

    async def get_earning_calendar(self, from_date: str, to_date: str) -> List[Dict]:
        """Get earnings calendar"""
        params = {"from": from_date, "to": to_date}
        return await self._request("earning-calendar", params)

    async def get_earnings_surprises(self, symbol: str) -> List[Dict]:
        """Get earnings surprises"""
        params = {"symbol": symbol}
        return await self._request("earnings-supprises", params)

    async def get_analyst_estimates(self, symbol: str, period: str = "annual", limit: int = 10) -> List[Dict]:
        """Get analyst estimates"""
        params = {"symbol": symbol, "period": period, "limit": limit}
        return await self._request("analyst-estimates", params)

    async def get_shares_float(self, symbol: str) -> Dict:
        """Get shares float and outstanding"""
        params = {"symbol": symbol}
        return await self._request("shares-float", params)

    async def get_shares_float_batch(self, symbols: List[str]) -> List[Dict]:
        """Get shares float for multiple companies"""
        symbols_str = ",".join(symbols)
        params = {"symbols": symbols_str}
        return await self._request("shares-float", params)

    async def get_institutional_holders(self, symbol: str) -> List[Dict]:
        """Get institutional holders"""
        params = {"symbol": symbol}
        return await self._request("institutional-holders", params)

    async def get_mutual_fund_holders(self, symbol: str) -> List[Dict]:
        """Get mutual fund holders"""
        params = {"symbol": symbol}
        return await self._request("mutual-fund-holders", params)

    async def get_etf_holders(self, symbol: str) -> List[Dict]:
        """Get ETF holders"""
        params = {"symbol": symbol}
        return await self._request("etf-holders", params)

    async def get_company_outlook(self, symbol: str) -> Dict:
        """Get company outlook (comprehensive)"""
        params = {"symbol": symbol}
        return await self._request("company-outlook", params)

    async def get_sec_filings(self, symbol: str) -> List[Dict]:
        """Get SEC filings"""
        params = {"symbol": symbol}
        return await self._request("sec-filings", params)

    async def get_stock_dividend(self, symbol: str) -> List[Dict]:
        """Get stock dividend history"""
        params = {"symbol": symbol}
        return await self._request("stock-dividend", params)

    async def get_stock_splits(self, symbol: str) -> List[Dict]:
        """Get stock splits history"""
        params = {"symbol": symbol}
        return await self._request("stock-split", params)

    async def get_symbol_change(self) -> List[Dict]:
        """Get symbol changes"""
        return await self._request("symbol-change")

    async def get_s_and_p500(self) -> List[Dict]:
        """Get S&P 500 companies"""
        return await self._request("sp500")

    async def get_nasdaq100(self) -> List[Dict]:
        """Get Nasdaq 100 companies"""
        return await self._request("nasdaq100")

    async def get_dow_jones(self) -> List[Dict]:
        """Get Dow Jones companies"""
        return await self._request("dow30")

    async def get_available_sectors(self) -> List[str]:
        """Get available sectors"""
        return await self._request("sectors")

    async def get_available_industries(self) -> List[str]:
        """Get available industries"""
        return await self._request("industries")

    async def get_available_countries(self) -> List[str]:
        """Get available countries"""
        return await self._request("countries")

    async def get_historical_market_cap(self, symbol: str, limit: int = 365) -> List[Dict]:
        """Get historical market cap"""
        params = {"symbol": symbol, "limit": limit}
        return await self._request("historical-market-capitalization", params)
