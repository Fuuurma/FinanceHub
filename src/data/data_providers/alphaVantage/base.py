import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, date
from decimal import Decimal

from apps.core.logger import get_logger

logger = get_logger(__name__)


class AlphaVantageFetcher:
    """
    Alpha Vantage API Fetcher
    Free: 5 API calls/minute, 500 calls/day
    Premium: Higher limits
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, params: Dict) -> Dict:
        """Make API request"""
        params["apikey"] = self.api_key

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                # Check for API limit error
                if "Note" in data:
                    logger.warning("Alpha Vantage rate limit reached")
                    await asyncio.sleep(60)
                    return await self._request(params)

                # Rate limiting: 5 calls/min = 12 seconds between calls
                await asyncio.sleep(12)

                return data

        except Exception as e:
            logger.error(f"Alpha Vantage API error: {str(e)}")
            raise

    # Stock Time Series

    async def get_intraday(
        self, symbol: str, interval: str = "5min", outputsize: str = "compact"
    ) -> Dict:
        """
        Get intraday time series

        Args:
            symbol: Stock symbol
            interval: 1min, 5min, 15min, 30min, 60min
            outputsize: compact (latest 100 data points) or full (full-length)
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
        }
        return await self._request(params)

    async def get_daily(self, symbol: str, outputsize: str = "compact") -> Dict:
        """Get daily time series"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
        }
        return await self._request(params)

    async def get_daily_adjusted(self, symbol: str, outputsize: str = "full") -> Dict:
        """Get daily adjusted time series (includes dividends and splits)"""
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize,
        }
        return await self._request(params)

    async def get_weekly(self, symbol: str) -> Dict:
        """Get weekly time series"""
        params = {"function": "TIME_SERIES_WEEKLY", "symbol": symbol}
        return await self._request(params)

    async def get_weekly_adjusted(self, symbol: str) -> Dict:
        """Get weekly adjusted time series"""
        params = {"function": "TIME_SERIES_WEEKLY_ADJUSTED", "symbol": symbol}
        return await self._request(params)

    async def get_monthly(self, symbol: str) -> Dict:
        """Get monthly time series"""
        params = {"function": "TIME_SERIES_MONTHLY", "symbol": symbol}
        return await self._request(params)

    async def get_monthly_adjusted(self, symbol: str) -> Dict:
        """Get monthly adjusted time series"""
        params = {"function": "TIME_SERIES_MONTHLY_ADJUSTED", "symbol": symbol}
        return await self._request(params)

    async def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol}
        return await self._request(params)

    async def symbol_search(self, keywords: str) -> Dict:
        """Search for symbols"""
        params = {"function": "SYMBOL_SEARCH", "keywords": keywords}
        return await self._request(params)

    # Forex (FX)

    async def get_fx_intraday(
        self,
        from_symbol: str,
        to_symbol: str,
        interval: str = "5min",
        outputsize: str = "compact",
    ) -> Dict:
        """Get forex intraday data"""
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "interval": interval,
            "outputsize": outputsize,
        }
        return await self._request(params)

    async def get_fx_daily(
        self, from_symbol: str, to_symbol: str, outputsize: str = "compact"
    ) -> Dict:
        """Get forex daily data"""
        params = {
            "function": "FX_DAILY",
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "outputsize": outputsize,
        }
        return await self._request(params)

    async def get_fx_exchange_rate(self, from_currency: str, to_currency: str) -> Dict:
        """Get real-time exchange rate"""
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency,
        }
        return await self._request(params)

    # Cryptocurrencies

    async def get_crypto_rating(self, symbol: str) -> Dict:
        """Get cryptocurrency rating"""
        params = {"function": "CRYPTO_RATING", "symbol": symbol}
        return await self._request(params)

    async def get_crypto_daily(self, symbol: str, market: str = "USD") -> Dict:
        """Get daily crypto data"""
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
        }
        return await self._request(params)

    async def get_crypto_weekly(self, symbol: str, market: str = "USD") -> Dict:
        """Get weekly crypto data"""
        params = {
            "function": "DIGITAL_CURRENCY_WEEKLY",
            "symbol": symbol,
            "market": market,
        }
        return await self._request(params)

    async def get_crypto_monthly(self, symbol: str, market: str = "USD") -> Dict:
        """Get monthly crypto data"""
        params = {
            "function": "DIGITAL_CURRENCY_MONTHLY",
            "symbol": symbol,
            "market": market,
        }
        return await self._request(params)

    # Technical Indicators

    async def get_sma(
        self,
        symbol: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
    ) -> Dict:
        """Get Simple Moving Average"""
        params = {
            "function": "SMA",
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
        }
        return await self._request(params)

    async def get_ema(
        self,
        symbol: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
    ) -> Dict:
        """Get Exponential Moving Average"""
        params = {
            "function": "EMA",
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
        }
        return await self._request(params)

    async def get_rsi(
        self,
        symbol: str,
        interval: str = "daily",
        time_period: int = 14,
        series_type: str = "close",
    ) -> Dict:
        """Get Relative Strength Index"""
        params = {
            "function": "RSI",
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
        }
        return await self._request(params)

    async def get_macd(
        self, symbol: str, interval: str = "daily", series_type: str = "close"
    ) -> Dict:
        """Get MACD"""
        params = {
            "function": "MACD",
            "symbol": symbol,
            "interval": interval,
            "series_type": series_type,
        }
        return await self._request(params)

    async def get_bbands(
        self,
        symbol: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
    ) -> Dict:
        """Get Bollinger Bands"""
        params = {
            "function": "BBANDS",
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
        }
        return await self._request(params)

    # Fundamental Data

    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data"""
        params = {"function": "OVERVIEW", "symbol": symbol}
        return await self._request(params)

    async def get_income_statement(self, symbol: str) -> Dict:
        """Get annual and quarterly income statements"""
        params = {"function": "INCOME_STATEMENT", "symbol": symbol}
        return await self._request(params)

    async def get_balance_sheet(self, symbol: str) -> Dict:
        """Get annual and quarterly balance sheets"""
        params = {"function": "BALANCE_SHEET", "symbol": symbol}
        return await self._request(params)

    async def get_cash_flow(self, symbol: str) -> Dict:
        """Get annual and quarterly cash flow"""
        params = {"function": "CASH_FLOW", "symbol": symbol}
        return await self._request(params)

    async def get_earnings(self, symbol: str) -> Dict:
        """Get earnings data"""
        params = {"function": "EARNINGS", "symbol": symbol}
        return await self._request(params)

    # Commodities

    async def get_wti(self, interval: str = "monthly") -> Dict:
        """Get WTI crude oil prices"""
        params = {"function": "WTI", "interval": interval}
        return await self._request(params)

    async def get_brent(self, interval: str = "monthly") -> Dict:
        """Get Brent crude oil prices"""
        params = {"function": "BRENT", "interval": interval}
        return await self._request(params)

    async def get_natural_gas(self, interval: str = "monthly") -> Dict:
        """Get natural gas prices"""
        params = {"function": "NATURAL_GAS", "interval": interval}
        return await self._request(params)

    async def get_copper(self, interval: str = "monthly") -> Dict:
        """Get copper prices"""
        params = {"function": "COPPER", "interval": interval}
        return await self._request(params)

    async def get_aluminum(self, interval: str = "monthly") -> Dict:
        """Get aluminum prices"""
        params = {"function": "ALUMINUM", "interval": interval}
        return await self._request(params)

    async def get_wheat(self, interval: str = "monthly") -> Dict:
        """Get wheat prices"""
        params = {"function": "WHEAT", "interval": interval}
        return await self._request(params)

    async def get_corn(self, interval: str = "monthly") -> Dict:
        """Get corn prices"""
        params = {"function": "CORN", "interval": interval}
        return await self._request(params)

    async def get_cotton(self, interval: str = "monthly") -> Dict:
        """Get cotton prices"""
        params = {"function": "COTTON", "interval": interval}
        return await self._request(params)

    async def get_sugar(self, interval: str = "monthly") -> Dict:
        """Get sugar prices"""
        params = {"function": "SUGAR", "interval": interval}
        return await self._request(params)

    async def get_coffee(self, interval: str = "monthly") -> Dict:
        """Get coffee prices"""
        params = {"function": "COFFEE", "interval": interval}
        return await self._request(params)

    # Economic Indicators

    async def get_real_gdp(self, interval: str = "quarterly") -> Dict:
        """Get US Real GDP"""
        params = {"function": "REAL_GDP", "interval": interval}
        return await self._request(params)

    async def get_cpi(self, interval: str = "monthly") -> Dict:
        """Get Consumer Price Index"""
        params = {"function": "CPI", "interval": interval}
        return await self._request(params)

    async def get_inflation(self) -> Dict:
        """Get inflation rate"""
        params = {"function": "INFLATION"}
        return await self._request(params)

    async def get_unemployment(self) -> Dict:
        """Get unemployment rate"""
        params = {"function": "UNEMPLOYMENT"}
        return await self._request(params)

    async def get_treasury_yield(
        self, interval: str = "monthly", maturity: str = "10year"
    ) -> Dict:
        """
        Get Treasury yield

        Args:
            maturity: 3month, 2year, 5year, 7year, 10year, 30year
        """
        params = {
            "function": "TREASURY_YIELD",
            "interval": interval,
            "maturity": maturity,
        }
        return await self._request(params)
