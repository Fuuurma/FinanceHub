"""
Alpha Vantage Scraper using BaseAPIFetcher for key rotation
"""

import aiohttp
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional, List, Any

from data.data_providers.base_fetcher import BaseAPIFetcher
from investments.models import DataProvider
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


def parse_decimal(value: Any) -> Optional[Decimal]:
    """Parse a value to Decimal, handling None and empty strings"""
    if value is None or value == "" or value == "None":
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def parse_date(value: str) -> Optional[datetime]:
    """Parse a date string to datetime"""
    if not value or value == "None":
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def parse_fiscal_period(fiscal_year: int, period_end: str) -> tuple:
    """Parse fiscal period from period end date"""
    end_date = parse_date(period_end)
    if not end_date:
        return fiscal_year, None

    month = end_date.month
    if month in [1, 2, 3]:
        fiscal_period = 2
    elif month in [4, 5, 6]:
        fiscal_period = 3
    elif month in [7, 8, 9]:
        fiscal_period = 4
    else:
        fiscal_period = 1

    return fiscal_year, fiscal_period


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

    async def _make_request(
        self, endpoint: str, params: Optional[Dict], method: str, api_key
    ) -> Dict:
        """Make request with API key in params"""
        if params is None:
            params = {}
        params["apikey"] = api_key.key_value

        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)

        async with self.session.request(
            method, url, params=params, headers=headers
        ) as response:
            response.raise_for_status()
            return await response.json()

    # Stock Time Series

    async def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol}
        return await self.request("", params=params)

    async def get_intraday(self, symbol: str, interval: str = "5min") -> Dict:
        """Get intraday time series"""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": "compact",
        }
        return await self.request("", params=params)

    async def get_daily(self, symbol: str) -> Dict:
        """Get daily time series"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
        }
        return await self.request("", params=params)

    # Fundamental Data

    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data"""
        params = {"function": "OVERVIEW", "symbol": symbol}
        return await self.request("", params=params)

    async def get_income_statement(self, symbol: str) -> Dict:
        """Get income statement"""
        params = {"function": "INCOME_STATEMENT", "symbol": symbol}
        return await self.request("", params=params)

    async def get_balance_sheet(self, symbol: str) -> Dict:
        """Get balance sheet"""
        params = {"function": "BALANCE_SHEET", "symbol": symbol}
        return await self.request("", params=params)

    async def get_cash_flow(self, symbol: str) -> Dict:
        """Get cash flow"""
        params = {"function": "CASH_FLOW", "symbol": symbol}
        return await self.request("", params=params)

    async def get_earnings(self, symbol: str) -> Dict:
        """Get earnings data"""
        params = {"function": "EARNINGS", "symbol": symbol}
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
                except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                    results[symbol] = False
                    logger.error(f"Error fetching {symbol}: {str(e)}")
        return results

    async def fetch_and_save_stock(self, symbol: str) -> bool:
        """Fetch and save a single stock with fundamental data"""
        try:
            from django.utils import timezone
            from assets.models.asset import Asset
            from investments.models import DataProvider
            from fundamentals.equities.financials import (
                IncomeStatement,
                BalanceSheet,
                CashFlowStatement,
            )
            from fundamentals.equities.earnings import EarningsReport

            async with self:
                quote = await self.get_quote(symbol)
                if quote and "Global Quote" in quote:
                    quote_data = quote.get("Global Quote", {})

                    asset = Asset.objects.filter(
                        symbol=symbol, asset_type__name__in=["stock", "etf"]
                    ).first()

                    if asset:
                        data_provider, _ = DataProvider.objects.get_or_create(
                            code="alpha_vantage", defaults={"name": "Alpha Vantage"}
                        )

                        quote_info = quote_data.get("09. previous close", {})
                        if isinstance(quote_info, dict):
                            from decimal import Decimal

                            asset.last_price = Decimal(str(quote_info.get("price", 0)))
                            asset.last_price_updated = timezone.now()
                            asset.save(
                                update_fields=["last_price", "last_price_updated"]
                            )
                        logger.info(f"Updated price for {symbol}: {quote_data}")

                    overview = await self.get_company_overview(symbol)
                    if overview and "Symbol" in overview:
                        await self._save_company_overview(
                            symbol, overview, data_provider
                        )

                    income_stmt = await self.get_income_statement(symbol)
                    if income_stmt and "incomeStatement" in income_stmt:
                        await self._save_income_statements(
                            symbol, income_stmt, data_provider
                        )

                    balance_sheet = await self.get_balance_sheet(symbol)
                    if balance_sheet and "balanceSheet" in balance_sheet:
                        await self._save_balance_sheets(
                            symbol, balance_sheet, data_provider
                        )

                    cash_flow = await self.get_cash_flow(symbol)
                    if cash_flow and "cashFlow" in cash_flow:
                        await self._save_cash_flows(symbol, cash_flow, data_provider)

                    earnings = await self.get_earnings(symbol)
                    if earnings and "quarterlyEarnings" in earnings:
                        await self._save_earnings(symbol, earnings, data_provider)

                    logger.info(f"Successfully saved all fundamental data for {symbol}")
                    return True
                else:
                    logger.warning(f"No data for {symbol}")
                    return False
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error saving {symbol}: {str(e)}")
            return False

    async def _save_company_overview(
        self, symbol: str, data: Dict, data_provider: DataProvider
    ):
        """Save company overview data to Asset model"""
        from django.utils import timezone
        from assets.models.asset import Asset
        from decimal import Decimal

        asset = Asset.objects.filter(symbol=symbol).first()
        if not asset:
            return

        overview_fields = {
            "market_cap": "MarketCapitalization",
            "pe_ratio": "PERatio",
            "pe_forward": "PERatio",
            "pb_ratio": "PriceToBookRatio",
            "ps_ratio": "PriceToSalesRatioTTM",
            "dividend_yield": "DividendYield",
            "eps": "EPS",
            "eps_forward": "EPSForward",
            "beta": "Beta",
            "high_52w": "52WeekHigh",
            "low_52w": "52WeekLow",
            "ma_50": "50DayMovingAverage",
            "ma_200": "200DayMovingAverage",
            "shares_outstanding": "SharesOutstanding",
            "shares_float": "SharesFloat",
            "insider_ownership": " InsiderHolder",
            "institutional_ownership": " InstitutionalHolder",
            "short_float": "ShortPercent",
            "short_ratio": "ShortRatio",
            "payout_ratio": "PayoutRatio",
        }

        updates = {}
        for field, key in overview_fields.items():
            if key in data:
                value = parse_decimal(data[key])
                if value is not None:
                    updates[field] = value

        if updates:
            updates["last_fundamentals_updated"] = timezone.now()
            asset.save(update_fields=list(updates.keys()))

        logger.info(f"Saved company overview for {symbol}")

    async def _save_income_statements(
        self, symbol: str, data: Dict, data_provider: DataProvider
    ):
        """Save income statement data"""
        from assets.models.asset import Asset
        from fundamentals.equities.financials import IncomeStatement
        from decimal import Decimal

        asset = Asset.objects.filter(symbol=symbol).first()
        if not asset:
            return

        statements = data.get("incomeStatement", {}).get("quarterlyReports", [])
        for report in statements[:4]:
            fiscal_year = int(report.get("fiscalDateEnding", "2020")[:4])
            period_end = report.get("fiscalDateEnding", "")
            fiscal_year, fiscal_period = parse_fiscal_period(fiscal_year, period_end)

            period_type = "quarterly" if fiscal_period else "annual"

            fields = {
                "total_revenue": "totalRevenue",
                "cost_of_revenue": "costOfRevenue",
                "gross_profit": "grossProfit",
                "research_and_development": "researchAndDevelopment",
                "selling_general_and_admin": "sellingGeneralAndAdministrative",
                "operating_expenses": "totalOperatingExpenses",
                "operating_income": "operatingIncome",
                "interest_expense": "interestExpense",
                "net_income": "netIncome",
                "ebitda": "ebitda",
                "basic_eps": "basicEPS",
                "diluted_eps": "dilutedEPS",
                "depreciation": "depreciation",
                "amortization": "amortization",
            }

            report_date = parse_date(period_end)
            if not report_date:
                continue

            income_stmt, created = IncomeStatement.objects.update_or_create(
                asset=asset,
                period_type=period_type,
                fiscal_year=fiscal_year,
                fiscal_period=fiscal_period,
                defaults={
                    "report_date": report_date,
                    "source": data_provider,
                    **{k: parse_decimal(report.get(v)) for k, v in fields.items()},
                },
            )

        logger.info(f"Saved {len(statements)} income statements for {symbol}")

    async def _save_balance_sheets(
        self, symbol: str, data: Dict, data_provider: DataProvider
    ):
        """Save balance sheet data"""
        from assets.models.asset import Asset
        from fundamentals.equities.financials import BalanceSheet

        asset = Asset.objects.filter(symbol=symbol).first()
        if not asset:
            return

        reports = data.get("balanceSheet", {}).get("quarterlyReports", [])
        for report in reports[:4]:
            fiscal_year = int(report.get("fiscalDateEnding", "2020")[:4])
            period_end = report.get("fiscalDateEnding", "")
            fiscal_year, fiscal_period = parse_fiscal_period(fiscal_year, period_end)
            period_type = "quarterly" if fiscal_period else "annual"

            fields = {
                "cash_and_equivalents": "cashAndCashEquivalents",
                "short_term_investments": "shortTermInvestments",
                "accounts_receivable": "netReceivables",
                "inventory": "inventory",
                "total_current_assets": "totalCurrentAssets",
                "property_plant_equipment": "propertyPlantEquipment",
                "goodwill": "goodwill",
                "intangible_assets": "intangibleAssets",
                "total_assets": "totalAssets",
                "accounts_payable": "accountsPayable",
                "short_term_debt": "shortTermDebt",
                "total_current_liabilities": "totalCurrentLiabilities",
                "long_term_debt": "longTermDebt",
                "total_liabilities": "totalLiabilities",
                "common_stock": "commonStock",
                "retained_earnings": "retainedEarnings",
                "total_stockholders_equity": "totalStockholderEquity",
                "total_liabilities_and_equity": "totalLiabilitiesAndStockholderEquity",
            }

            report_date = parse_date(period_end)
            if not report_date:
                continue

            BalanceSheet.objects.update_or_create(
                asset=asset,
                period_type=period_type,
                fiscal_year=fiscal_year,
                fiscal_period=fiscal_period,
                defaults={
                    "report_date": report_date,
                    "source": data_provider,
                    **{k: parse_decimal(report.get(v)) for k, v in fields.items()},
                },
            )

        logger.info(f"Saved {len(reports)} balance sheets for {symbol}")

    async def _save_cash_flows(
        self, symbol: str, data: Dict, data_provider: DataProvider
    ):
        """Save cash flow data"""
        from assets.models.asset import Asset
        from fundamentals.equities.financials import CashFlowStatement

        asset = Asset.objects.filter(symbol=symbol).first()
        if not asset:
            return

        reports = data.get("cashFlow", {}).get("quarterlyReports", [])
        for report in reports[:4]:
            fiscal_year = int(report.get("fiscalDateEnding", "2020")[:4])
            period_end = report.get("fiscalDateEnding", "")
            fiscal_year, fiscal_period = parse_fiscal_period(fiscal_year, period_end)
            period_type = "quarterly" if fiscal_period else "annual"

            fields = {
                "net_income": "netIncome",
                "depreciation": "depreciation",
                "stock_based_compensation": "stockBasedCompensation",
                "change_in_working_capital": "changeInWorkingCapital",
                "operating_cash_flow": "operatingCashflow",
                "capital_expenditures": "capitalExpenditures",
                "acquisition_of_businesses": "acquisitionsAndPurchases",
                "investing_cash_flow": "investingCashflow",
                "debt_issued": "debtIssuance",
                "dividends_paid": "dividendsPaid",
                "financing_cash_flow": "financingCashflow",
                "net_change_in_cash": "changeInCash",
                "free_cash_flow": "freeCashFlow",
            }

            report_date = parse_date(period_end)
            if not report_date:
                continue

            CashFlowStatement.objects.update_or_create(
                asset=asset,
                period_type=period_type,
                fiscal_year=fiscal_year,
                fiscal_period=fiscal_period,
                defaults={
                    "report_date": report_date,
                    "source": data_provider,
                    **{k: parse_decimal(report.get(v)) for k, v in fields.items()},
                },
            )

        logger.info(f"Saved {len(reports)} cash flow statements for {symbol}")

    async def _save_earnings(
        self, symbol: str, data: Dict, data_provider: DataProvider
    ):
        """Save earnings data"""
        from assets.models.asset import Asset
        from fundamentals.equities.earnings import EarningsReport

        asset = Asset.objects.filter(symbol=symbol).first()
        if not asset:
            return

        reports = data.get("quarterlyEarnings", [])
        for report in reports[:4]:
            fiscal_year = int(report.get("fiscalDateEnding", "2020")[:4])
            period_end = report.get("fiscalDateEnding", "")
            fiscal_year, fiscal_period = parse_fiscal_period(fiscal_year, period_end)
            period_type = "quarterly" if fiscal_period else "annual"

            fields = {
                "eps_actual": "reportedEPS",
                "eps_estimate": "estimatedEPS",
                "eps_surprise_pct": "surprisePercentage",
                "revenue_actual": "reportedEPS",
                "revenue_estimate": "totalEstimatedEPS",
            }

            report_date = parse_date(period_end)
            if not report_date:
                continue

            EarningsReport.objects.update_or_create(
                asset=asset,
                period_type=period_type,
                fiscal_year=fiscal_year,
                fiscal_period=fiscal_period,
                defaults={
                    "report_date": report_date,
                    "source": data_provider,
                    **{k: parse_decimal(report.get(v)) for k, v in fields.items()},
                },
            )

        logger.info(f"Saved {len(reports)} earnings reports for {symbol}")

    @classmethod
    def from_settings(cls):
        """Create scraper using settings API key (legacy compatibility)"""
        from django.conf import settings

        scraper = cls()
        # Note: This will be overridden by key rotation system
        # Keeping for backward compatibility with existing data_fetcher.py
        return scraper
