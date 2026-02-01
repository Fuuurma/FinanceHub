import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Type
from django.utils import timezone
from django.db import DatabaseError, OperationalError
from redis import RedisError as CacheError
from httpx import NetworkError, TimeoutException

from utils.helpers.logger.logger import get_logger
from utils.services.cache_manager import get_cache_manager
from data.data_providers.fmp import FMPFetcher
from data.data_providers.defi_llama import DeFiLlamaFetcher
from data.data_providers.fred.scraper import FREDScraper
from investments.models.api_key import APIKey

logger = get_logger(__name__)


class FundamentalDataService:
    """
    Service for fetching and managing fundamental data

    Supports:
    - Equities (via FMP, Yahoo Finance, Alpha Vantage)
    - Crypto (via DeFi Llama, CoinGecko)
    - Bonds/Macro (via FRED)
    """

    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.fmp_api_key = None
        self.fred_api_key = None
        self._initialize_api_keys()

    def _initialize_api_keys(self):
        """Load API keys from database"""
        try:
            fmp_keys = APIKey.objects.filter(provider="fmp", is_active=True)
            if fmp_keys.exists():
                self.fmp_api_key = fmp_keys.first().key_value

            fred_keys = APIKey.objects.filter(provider="fred", is_active=True)
            if fred_keys.exists():
                self.fred_api_key = fred_keys.first().key_value

        except (DatabaseError, OperationalError) as e:
            logger.warning(f"Could not load API keys: {e}")

    async def get_equity_fundamentals(
        self, symbol: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get comprehensive fundamental data for an equity

        Returns:
            Dict with keys: profile, valuation, financials, earnings, ownership
        """
        cache_key = f"equity_fundamentals:{symbol.upper()}"

        if not force_refresh:
            cached = await self.cache_manager.get("fundamental_data", symbol.upper())
            if cached:
                return cached

        try:
            async with FMPFetcher(self.fmp_api_key or "demo") as fmp:
                profile_data = await fmp.get_company_profile(symbol.upper())

                if profile_data and len(profile_data) > 0:
                    profile = profile_data[0]
                    key_metrics = await fmp.get_key_metrics(symbol.upper())
                    financial_ratios = await fmp.get_financial_ratios(symbol.upper())
                    income_statement = await fmp.get_income_statement(symbol.upper())
                    balance_sheet = await fmp.get_balance_sheet(symbol.upper())
                    cash_flow = await fmp.get_cash_flow(symbol.upper())

                    fundamentals = {
                        "symbol": symbol.upper(),
                        "profile": profile,
                        "key_metrics": key_metrics[0] if key_metrics else None,
                        "financial_ratios": financial_ratios[0]
                        if financial_ratios
                        else None,
                        "income_statement": income_statement[:1]
                        if income_statement
                        else None,
                        "balance_sheet": balance_sheet[:1] if balance_sheet else None,
                        "cash_flow": cash_flow[:1] if cash_flow else None,
                        "fetched_at": timezone.now().isoformat(),
                        "source": "fmp",
                    }

                    await self.cache_manager.set(
                        "fundamental_data",
                        symbol.upper(),
                        value=fundamentals,
                        ttl=86400,
                    )

                    return fundamentals

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")

        return {
            "symbol": symbol.upper(),
            "error": str(e) if "e" in locals() else "Unknown error",
            "fetched_at": timezone.now().isoformat(),
        }

    async def get_equity_valuation(
        self, symbol: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get valuation metrics for an equity"""
        cache_key = f"equity_valuation:{symbol.upper()}"

        if not force_refresh:
            cached = await self.cache_manager.get("equity_valuation", symbol.upper())
            if cached:
                return cached

        try:
            async with FMPFetcher(self.fmp_api_key or "demo") as fmp:
                key_metrics = await fmp.get_key_metrics(symbol.upper())
                enterprise_value = await fmp.get_enterprise_value(symbol.upper())
                market_cap = await fmp.get_market_cap(symbol.upper())

                if key_metrics:
                    valuation = {
                        "symbol": symbol.upper(),
                        "market_cap": market_cap[0] if market_cap else None,
                        "enterprise_value": enterprise_value[0]
                        if enterprise_value
                        else None,
                        "pe_ratio": key_metrics[0].get("peRatio"),
                        "pb_ratio": key_metrics[0].get("pbRatio"),
                        "ps_ratio": key_metrics[0].get("psRatio"),
                        "ev_ebitda": key_metrics[0].get("evEbitda"),
                        "ev_revenue": key_metrics[0].get("evRevenue"),
                        "peg_ratio": key_metrics[0].get("pegRatio"),
                        "price_to_book": key_metrics[0].get("pbRatio"),
                        "price_to_sales": key_metrics[0].get("psRatio"),
                        "dividend_yield": key_metrics[0].get("dividendYield"),
                        "payout_ratio": key_metrics[0].get("payoutRatio"),
                        "beta": key_metrics[0].get("beta"),
                        "eps": key_metrics[0].get("eps"),
                        "eps_growth": key_metrics[0].get("epsGrowth"),
                        "revenue_growth": key_metrics[0].get("revenueGrowth"),
                        "net_profit_margin": key_metrics[0].get("netProfitMargin"),
                        "roe": key_metrics[0].get("roe"),
                        "roa": key_metrics[0].get("roa"),
                        "debt_to_equity": key_metrics[0].get("debtToEquity"),
                        "current_ratio": key_metrics[0].get("currentRatio"),
                        "gross_margin": key_metrics[0].get("grossMargin"),
                        "operating_margin": key_metrics[0].get("operatingMargin"),
                        "fetched_at": timezone.now().isoformat(),
                        "source": "fmp",
                    }

                    await self.cache_manager.set(
                        "equity_valuation", symbol.upper(), value=valuation, ttl=86400
                    )

                    return valuation

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching valuation for {symbol}: {e}")

        return {
            "symbol": symbol.upper(),
            "error": str(e) if "e" in locals() else "Unknown error",
        }

    async def get_equity_financials(
        self, symbol: str, period: str = "annual", limit: int = 5
    ) -> Dict[str, Any]:
        """Get financial statements for an equity"""
        try:
            async with FMPFetcher(self.fmp_api_key or "demo") as fmp:
                income = await fmp.get_income_statement(
                    symbol.upper(), period=period, limit=limit
                )
                balance = await fmp.get_balance_sheet(
                    symbol.upper(), period=period, limit=limit
                )
                cash_flow = await fmp.get_cash_flow(
                    symbol.upper(), period=period, limit=limit
                )

                return {
                    "symbol": symbol.upper(),
                    "period": period,
                    "income_statements": income,
                    "balance_sheets": balance,
                    "cash_flow_statements": cash_flow,
                    "fetched_at": timezone.now().isoformat(),
                }

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            return {"symbol": symbol.upper(), "error": str(e)}

    async def get_crypto_protocol_metrics(
        self, protocol: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get protocol metrics for a crypto protocol"""
        cache_key = f"crypto_protocol:{protocol.lower()}"

        if not force_refresh:
            cached = await self.cache_manager.get("crypto_protocol", protocol.lower())
            if cached:
                return cached

        try:
            async with DeFiLlamaFetcher() as defi:
                protocol_data = await defi.get_protocol_data(protocol.lower())
                tvl_history = await defi.get_tvl(protocol.lower())

                metrics = {
                    "protocol": protocol.lower(),
                    "name": protocol_data.get("name"),
                    "tvl": protocol_data.get("tvl"),
                    "tvl_change_24h": protocol_data.get("tvlChange24h"),
                    "tvl_change_7d": protocol_data.get("tvlChange7d"),
                    "chain": protocol_data.get("chain"),
                    "category": protocol_data.get("category"),
                    "logo_url": protocol_data.get("logo"),
                    "description": protocol_data.get("description"),
                    "url": protocol_data.get("url"),
                    "tvl_history": tvl_history,
                    "fetched_at": timezone.now().isoformat(),
                    "source": "defi_llama",
                }

                await self.cache_manager.set(
                    "crypto_protocol", protocol.lower(), value=metrics, ttl=3600
                )

                return metrics

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching crypto protocol {protocol}: {e}")
            return {"protocol": protocol.lower(), "error": str(e)}

    async def get_all_crypto_protocols(self) -> List[Dict[str, Any]]:
        """Get all crypto protocols from DeFi Llama"""
        try:
            async with DeFiLlamaFetcher() as defi:
                protocols = await defi.get_all_protocols()
                return DeFiLlamaFetcher.transform_protocol_list(protocols)

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching all protocols: {e}")
            return []

    async def get_chain_tvl(self, chain: str) -> Dict[str, Any]:
        """Get TVL data for a specific chain"""
        try:
            async with DeFiLlamaFetcher() as defi:
                chain_data = await defi.get_tvl_by_chain(chain)
                protocols = await defi.get_protocols_by_chain(chain)

                return {
                    "chain": chain,
                    "total_tvl": chain_data.get("tvl"),
                    "protocols_count": len(protocols),
                    "protocols": DeFiLlamaFetcher.transform_protocol_list(protocols),
                    "fetched_at": timezone.now().isoformat(),
                }

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching chain TVL for {chain}: {e}")
            return {"chain": chain, "error": str(e)}

    async def get_bond_metrics(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get bond/macro metrics from FRED"""
        cache_key = "bond_metrics"

        if not force_refresh:
            cached = await self.cache_manager.get("bond_metrics", "global")
            if cached:
                return cached

        try:
            scraper = FREDScraper(self.fred_api_key or "")

            treasury_yields = scraper.get_treasury_yields()
            full_curve = scraper.get_full_treasury_curve()
            yield_curve_spreads = scraper.get_yield_curve_spread()
            credit_spreads = scraper.get_credit_spreads()
            inflation_data = scraper.get_inflation_data()
            macro_indicators = scraper.get_macro_indicators()

            metrics = {
                "treasury_yields": treasury_yields,
                "full_yield_curve": full_curve,
                "yield_curve_spreads": yield_curve_spreads,
                "credit_spreads": credit_spreads,
                "inflation": inflation_data,
                "macro_indicators": macro_indicators,
                "fetched_at": timezone.now().isoformat(),
                "source": "fred",
            }

            await self.cache_manager.set(
                "bond_metrics", "global", value=metrics, ttl=3600
            )

            return metrics

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching bond metrics: {e}")
            return {"error": str(e)}

    async def get_yield_curve(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get current yield curve data"""
        cache_key = "yield_curve"

        if not force_refresh:
            cached = await self.cache_manager.get("yield_curve", "current")
            if cached:
                return cached

        try:
            scraper = FREDScraper(self.fred_api_key or "")
            curve = scraper.get_full_treasury_curve()
            spreads = scraper.get_yield_curve_spread()

            result = {
                "curve": curve,
                "spreads": spreads,
                "fetched_at": timezone.now().isoformat(),
                "source": "fred",
            }

            await self.cache_manager.set(
                "yield_curve", "current", value=result, ttl=3600
            )

            return result

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching yield curve: {e}")
            return {"error": str(e)}

    async def get_treasury_yields_history(
        self, maturity: str = "10y", days: int = 365
    ) -> List[Dict[str, Any]]:
        """Get historical treasury yields"""
        try:
            scraper = FREDScraper(self.fred_api_key or "")
            history = scraper.get_bond_yield_history(maturity=maturity, days=days)
            return history

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching treasury history: {e}")
            return []

    async def screen_stocks(
        self,
        market_cap_min: Optional[int] = None,
        market_cap_max: Optional[int] = None,
        pe_min: Optional[float] = None,
        pe_max: Optional[float] = None,
        dividend_yield_min: Optional[float] = None,
        sector: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Screen stocks based on criteria"""
        try:
            async with FMPFetcher(self.fmp_api_key or "demo") as fmp:
                results = await fmp.get_stock_screener(
                    market_cap_more_than=market_cap_min,
                    market_cap_less_than=market_cap_max,
                    sector=sector,
                    limit=limit,
                )

                screened = []
                for stock in results:
                    if pe_min and stock.get("pe") and stock["pe"] < pe_min:
                        continue
                    if pe_max and stock.get("pe") and stock["pe"] > pe_max:
                        continue
                    if (
                        dividend_yield_min
                        and stock.get("dividendYield", 0) < dividend_yield_min
                    ):
                        continue
                    screened.append(stock)

                return screened

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error screening stocks: {e}")
            return []

    async def batch_fetch_equities(
        self, symbols: List[str], data_type: str = "fundamentals"
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch fundamental data for multiple equities with caching"""
        results = {}

        async def fetch_with_cache(symbol: str) -> tuple:
            cache_key = f"batch_{data_type}:{symbol.upper()}"
            cached = await self.cache_manager.get(f"batch_{data_type}", symbol.upper())
            if cached:
                return symbol.upper(), cached

            try:
                if data_type == "fundamentals":
                    result = await self.get_equity_fundamentals(symbol)
                elif data_type == "valuation":
                    result = await self.get_equity_valuation(symbol)
                elif data_type == "financials":
                    result = await self.get_equity_financials(symbol)
                else:
                    result = {"error": f"Unknown data_type: {data_type}"}

                await self.cache_manager.set(
                    f"batch_{data_type}", symbol.upper(), value=result, ttl=86400
                )
                return symbol.upper(), result
            except (NetworkError, TimeoutException, ValueError, KeyError) as e:
                logger.error(f"Error fetching {data_type} for {symbol}: {e}")
                return symbol.upper(), {"error": str(e)}

        tasks = [fetch_with_cache(symbol) for symbol in symbols]
        results = dict(await asyncio.gather(*tasks))

        return results

    async def get_historical_fundamentals(
        self,
        symbol: str,
        period_type: str = "annual",
        limit: int = 5,
        force_refresh: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get historical fundamental data with caching"""
        cache_key = f"historical_fundamentals:{symbol.upper()}:{period_type}:{limit}"

        if not force_refresh:
            cached = await self.cache_manager.get(
                "historical_fundamentals", f"{symbol.upper()}:{period_type}"
            )
            if cached:
                return cached

        try:
            async with FMPFetcher(self.fmp_api_key or "demo") as fmp:
                key_metrics = await fmp.get_key_metrics(
                    symbol.upper(), period=period_type, limit=limit
                )

                await self.cache_manager.set(
                    "historical_fundamentals",
                    f"{symbol.upper()}:{period_type}",
                    value=key_metrics,
                    ttl=86400,
                )

                return key_metrics
        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching historical fundamentals for {symbol}: {e}")
            return []

    async def invalidate_fundamentals_cache(self, symbol: str) -> bool:
        """Invalidate all cached data for a symbol"""
        try:
            keys_to_delete = [
                ("fundamental_data", symbol.upper()),
                ("equity_valuation", symbol.upper()),
                ("historical_fundamentals", f"{symbol.upper()}:annual"),
                ("historical_fundamentals", f"{symbol.upper()}:quarterly"),
                ("batch_fundamentals", symbol.upper()),
                ("batch_valuation", symbol.upper()),
            ]

            for key_type, key_value in keys_to_delete:
                await self.cache_manager.delete(key_type, key_value)

            logger.info(f"Invalidated cache for {symbol}")
            return True
        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error invalidating cache for {symbol}: {e}")
            return False

    async def get_cached_stats(self) -> Dict[str, Any]:
        """Get caching statistics for fundamentals"""
        try:
            stats = self.cache_manager.statistics.get_summary()

            fundamentals_keys = {
                "fundamental_data": "Equity fundamentals (24h TTL)",
                "equity_valuation": "Equity valuation metrics (24h TTL)",
                "crypto_protocol": "Crypto protocol metrics (1h TTL)",
                "bond_metrics": "Bond/macro metrics (1h TTL)",
                "yield_curve": "Yield curve data (1h TTL)",
                "historical_fundamentals": "Historical fundamentals (24h TTL)",
            }

            return {
                "general_stats": stats,
                "fundamentals_keys": fundamentals_keys,
                "cache_ttl_recommendations": {
                    "equity_valuation": "24h - Updates daily",
                    "crypto_protocol": "1h - Updates frequently",
                    "bond_metrics": "1h - Updates intraday",
                    "historical_data": "24h - Updates quarterly",
                },
            }
        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error getting cached stats: {e}")
            return {"error": str(e)}

    async def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data"""
        try:
            async with FMPFetcher(self.fmp_api_key or "demo") as fmp:
                sectors = await fmp.get_available_sectors()

                sector_data = []
                for sector in sectors:
                    try:
                        stocks = await fmp.get_stock_screener(sector=sector, limit=10)
                        if stocks:
                            avg_pe = sum(s.get("pe", 0) for s in stocks) / len(stocks)
                            avg_change = sum(
                                s.get("changesPercentage", 0) for s in stocks
                            ) / len(stocks)
                            sector_data.append(
                                {
                                    "sector": sector,
                                    "stocks_count": len(stocks),
                                    "avg_pe": avg_pe,
                                    "avg_change_24h": avg_change,
                                }
                            )
                    except (ValueError, TypeError, KeyError):
                        pass

                return {
                    "sectors": sector_data,
                    "fetched_at": timezone.now().isoformat(),
                }

        except (NetworkError, TimeoutException, ValueError, KeyError) as e:
            logger.error(f"Error fetching sector performance: {e}")
            return {"error": str(e)}


_fundamental_service_instance: Optional[FundamentalDataService] = None


def get_fundamental_service() -> FundamentalDataService:
    global _fundamental_service_instance
    if _fundamental_service_instance is None:
        _fundamental_service_instance = FundamentalDataService()
    return _fundamental_service_instance
