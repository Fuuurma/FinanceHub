from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from .base import FREDBase
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class FREDScraper(FREDBase):
    """FRED API Scraper - Federal Reserve Economic Data"""

    # Popular Economic Series
    SERIES = {
        # GDP and Economic Growth
        "gdp": "GDP",
        "real_gdp": "GDPC1",
        "nominal_gdp": "GDP",
        "gdp_per_capita": "A939RX0Q048SBEA",
        # Inflation
        "cpi": "CPIAUCSL",
        "core_cpi": "CPILFESL",
        "pce": "PCEPI",
        "core_pce": "PCEPILFE",
        "inflation_expectation": "T5YIE",
        "breakeven_5y": "T5YBE",
        "breakeven_10y": "T10YIE",
        # Employment
        "unemployment_rate": "UNRATE",
        "labor_force_participation": "CIVPART",
        "nonfarm_payrolls": "PAYEMS",
        "initial_claims": "ICSA",
        # Interest Rates
        "fed_funds_rate": "FEDFUNDS",
        "treasury_10y": "DGS10",
        "treasury_2y": "DGS2",
        "treasury_5y": "DGS5",
        "treasury_30y": "DGS30",
        "treasury_1y": "DGS1",
        "treasury_3m": "DGS3M",
        # Mortgage Rates
        "mortgage_30y": "MORTGAGE30US",
        "mortgage_15y": "MORTGAGE15US",
        # Housing
        "housing_starts": "HOUST",
        "building_permits": "PERMIT",
        "existing_home_sales": "EXHOSLODN289S",
        "s_and_p_case_shiller": "SPCS20RSA",
        # Consumer
        "retail_sales": "RSXFS",
        "consumer_sentiment": "UMCSENT",
        "personal_saving_rate": "PSAVERT",
        # Industrial Production
        "industrial_production": "IPMAN",
        "capacity_utilization": "TCU",
        # Stock Market
        "s_and_p_500": "SP500",
        "dow_jones": "DJIA",
        # Trade
        "trade_balance": "BOPGSTB",
        "exports": "BOPGSTLA",
        "imports": "BOPGSTLM",
    }

    BOND_CURVE_SERIES = {
        "treasury_1m": "DTB1M",
        "treasury_3m": "DTB3",
        "treasury_6m": "DTB6",
        "treasury_1y": "DTB1YR",
        "tresury_2y": "DTB2YR",
        "treasury_3y": "DTB3YR",
        "treasury_5y": "DTB5YR",
        "treasury_7y": "DTB7YR",
        "treasury_10y": "DTB10YR",
        "treasury_20y": "DTB20YR",
        "treasury_30y": "DTB30YR",
    }

    CREDIT_SPREAD_SERIES = {
        "baa_aa": "BAA10Y",
        "aaa_aa": "AAA10Y",
        "high_yield_spread": "BAMLH0A0HYM2",
        "ig_spread": "BAMLH0A0HYM2",
    }

    def get_series_data(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
        limit: int = 100000,
        frequency: Optional[str] = None,
        units: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get observations for an economic data series.

        Args:
            series_id: Series ID (e.g., 'GDP', 'CPIAUCSL', 'UNRATE')
            observation_start: Start date (YYYY-MM-DD format)
            observation_end: End date (YYYY-MM-DD format)
            limit: Maximum number of results (1-100000)
            frequency: Aggregation frequency (d, w, bw, m, q, sa, a)
            units: Data transformation (lin, chg, ch1, pch, pc1, pca, cch, cca, log)

        Returns:
            Dictionary with observations data
        """
        params = {
            "series_id": series_id,
            "limit": limit,
            "api_key": self.api_key,
            "file_type": "json",
        }

        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if frequency:
            params["frequency"] = frequency
        if units:
            params["units"] = units

        try:
            response = self.session.get(
                f"{self.BASE_URL}/series/observations", params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching series {series_id}: {e}")
            return {}

    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata for an economic data series.

        Args:
            series_id: Series ID

        Returns:
            Dictionary with series information
        """
        params = {"series_id": series_id, "api_key": self.api_key, "file_type": "json"}

        try:
            response = self.session.get(f"{self.BASE_URL}/series", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching series info for {series_id}: {e}")
            return {}

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all FRED categories"""
        params = {"api_key": self.api_key, "file_type": "json"}

        try:
            response = self.session.get(f"{self.BASE_URL}/category", params=params)
            response.raise_for_status()
            return response.json().get("categories", [])
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def get_category_children(self, category_id: int) -> List[Dict[str, Any]]:
        """Get child categories for a parent category"""
        params = {
            "category_id": category_id,
            "api_key": self.api_key,
            "file_type": "json",
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/category/children", params=params
            )
            response.raise_for_status()
            return response.json().get("categories", [])
        except Exception as e:
            logger.error(f"Error fetching category children for {category_id}: {e}")
            return []

    def get_releases(self) -> List[Dict[str, Any]]:
        """Get all releases of economic data"""
        params = {"api_key": self.api_key, "file_type": "json"}

        try:
            response = self.session.get(f"{self.BASE_URL}/releases", params=params)
            response.raise_for_status()
            return response.json().get("releases", [])
        except Exception as e:
            logger.error(f"Error fetching releases: {e}")
            return []

    def get_release(self, release_id: int = None) -> Dict[str, Any]:
        """Get a release of economic data"""
        if release_id:
            params = {
                "release_id": release_id,
                "api_key": self.api_key,
                "file_type": "json",
            }
            endpoint = "release"
        else:
            params = {"api_key": self.api_key, "file_type": "json"}
            endpoint = "releases"

        try:
            response = self.session.get(f"{self.BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching release {release_id}: {e}")
            return {}

    def get_release_series(
        self,
        release_id: int,
        limit: int = 1000,
        order_by: str = "series_id",
        sort_order: str = "asc",
    ) -> List[Dict[str, Any]]:
        """Get the series on a release of economic data"""
        params = {
            "release_id": release_id,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/release/series", params=params
            )
            response.raise_for_status()
            return response.json().get("seriess", [])
        except Exception as e:
            logger.error(f"Error fetching release series for {release_id}: {e}")
            return []

    def get_sources(self) -> List[Dict[str, Any]]:
        """Get all sources of economic data"""
        params = {"api_key": self.api_key, "file_type": "json"}

        try:
            response = self.session.get(f"{self.BASE_URL}/sources", params=params)
            response.raise_for_status()
            return response.json().get("sources", [])
        except Exception as e:
            logger.error(f"Error fetching sources: {e}")
            return []

    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags, search for tags, or get tags by name"""
        params = {"api_key": self.api_key, "file_type": "json"}

        try:
            response = self.session.get(f"{self.BASE_URL}/tags", params=params)
            response.raise_for_status()
            return response.json().get("tags", [])
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return []

    def get_series_search(
        self,
        search_text: str,
        limit: int = 1000,
        order_by: str = "search_rank",
        sort_order: str = "asc",
    ) -> List[Dict[str, Any]]:
        """
        Get economic data series that match keywords.

        Args:
            search_text: Text to search for in series names
            limit: Maximum number of results
            order_by: Order results by field
            sort_order: Sort order (asc/desc)

        Returns:
            List of matching series
        """
        params = {
            "search_text": search_text,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        try:
            response = self.session.get(f"{self.BASE_URL}/series/search", params=params)
            response.raise_for_status()
            return response.json().get("seriess", [])
        except Exception as e:
            logger.error(f"Error searching series for '{search_text}': {e}")
            return []

    def get_series_updates(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get economic data series sorted by when observations were updated.

        Args:
            limit: Maximum number of results

        Returns:
            List of recently updated series
        """
        params = {
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit,
            "order_by": "updated",
            "sort_order": "desc",
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/series/updates", params=params
            )
            response.raise_for_status()
            return response.json().get("seriess", [])
        except Exception as e:
            logger.error(f"Error fetching series updates: {e}")
            return []

    def get_gdp(
        self,
        real_gdp: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get GDP data (real or nominal)"""
        series_id = "GDPC1" if real_gdp else "GDP"
        return self.get_series_data(
            series_id, observation_start=start_date, observation_end=end_date
        )

    def get_cpi(
        self,
        core: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get Consumer Price Index (CPI) data"""
        series_id = "CPILFESL" if core else "CPIAUCSL"
        return self.get_series_data(
            series_id, observation_start=start_date, observation_end=end_date
        )

    def get_unemployment_rate(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get unemployment rate data"""
        return self.get_series_data(
            "UNRATE", observation_start=start_date, observation_end=end_date
        )

    def get_federal_funds_rate(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Federal Funds Rate"""
        return self.get_series_data(
            "FEDFUNDS", observation_start=start_date, observation_end=end_date
        )

    def get_treasury_yield(
        self,
        maturity: str = "10y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get Treasury yield for a specific maturity.

        Args:
            maturity: Maturity ('1y', '2y', '5y', '10y', '30y', '3m')
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with observations
        """
        maturity_map = {
            "3m": "DGS3M",
            "1y": "DGS1",
            "2y": "DGS2",
            "5y": "DGS5",
            "10y": "DGS10",
            "30y": "DGS30",
        }

        series_id = maturity_map.get(maturity, "DGS10")
        return self.get_series_data(
            series_id, observation_start=start_date, observation_end=end_date
        )

    def get_all_treasury_yields(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get all Treasury yields (1m to 30y)"""
        yields = {}
        maturity_map = {
            "3m": "3-Month",
            "1y": "1-Year",
            "2y": "2-Year",
            "5y": "5-Year",
            "7y": "7-Year",
            "10y": "10-Year",
            "20y": "20-Year",
            "30y": "30-Year",
        }

        for maturity_key, maturity_name in maturity_map.items():
            data = self.get_treasury_yield(maturity_key, start_date, end_date)
            if data and "observations" in data:
                latest = data["observations"][-1]
                yields[maturity_key] = {
                    "name": maturity_name,
                    "rate": float(latest["value"]) if latest.get("value") else None,
                    "date": latest.get("date"),
                    "series_id": data.get("seriess", [{}])[0].get("series_id", "")
                    if data.get("seriess")
                    else "",
                }

        return yields

    def get_mortgage_rates(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get mortgage rates (30y and 15y)"""
        rates = {}

        data_30y = self.get_series_data("MORTGAGE30US", start_date, end_date)
        if data_30y and "observations" in data_30y:
            latest_30y = data_30y["observations"][-1]
            rates["30y"] = {
                "rate": float(latest_30y["value"]) if latest_30y.get("value") else None,
                "date": latest_30y.get("date"),
            }

        data_15y = self.get_series_data("MORTGAGE15US", start_date, end_date)
        if data_15y and "observations" in data_15y:
            latest_15y = data_15y["observations"][-1]
            rates["15y"] = {
                "rate": float(latest_15y["value"]) if latest_15y.get("value") else None,
                "date": latest_15y.get("date"),
            }

        return rates

    def get_housing_data(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get housing market indicators"""
        housing = {}

        # Housing Starts
        data = self.get_series_data("HOUST", start_date, end_date)
        if data and "observations" in data:
            latest = data["observations"][-1]
            housing["housing_starts"] = {
                "value": float(latest["value"]) if latest.get("value") else None,
                "date": latest.get("date"),
                "units": data.get("seriess", [{}])[0].get(
                    "units", "Thousands of Units"
                ),
            }

        # Building Permits
        data = self.get_series_data("PERMIT", start_date, end_date)
        if data and "observations" in data:
            latest = data["observations"][-1]
            housing["building_permits"] = {
                "value": float(latest["value"]) if latest.get("value") else None,
                "date": latest.get("date"),
                "units": data.get("seriess", [{}])[0].get(
                    "units", "Thousands of Units"
                ),
            }

        return housing

    def get_consumer_sentiment(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get University of Michigan Consumer Sentiment"""
        return self.get_series_data("UMCSENT", start_date, end_date)

    def get_retail_sales(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Advance Retail Sales"""
        return self.get_series_data("RSXFS", start_date, end_date)

    def get_industrial_production(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Industrial Production Index"""
        return self.get_series_data("IPMAN", start_date, end_date)

    def get_capacity_utilization(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Capacity Utilization Rate"""
        return self.get_series_data("TCU", start_date, end_date)

    def get_personal_saving_rate(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Personal Saving Rate"""
        return self.get_series_data("PSAVERT", start_date, end_date)

    def get_latest_macro_data(self) -> Dict[str, Any]:
        """
        Get latest values for all key macro indicators.
        Useful for dashboard display.
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        return {
            "gdp": self.get_gdp(end_date=end_date),
            "cpi": self.get_cpi(end_date=end_date),
            "unemployment": self.get_unemployment_rate(end_date=end_date),
            "fed_funds_rate": self.get_federal_funds_rate(end_date=end_date),
            "treasury_yields": self.get_all_treasury_yields(end_date=end_date),
            "mortgage_rates": self.get_mortgage_rates(end_date=end_date),
            "housing": self.get_housing_data(end_date=end_date),
            "consumer_sentiment": self.get_consumer_sentiment(end_date=end_date),
            "retail_sales": self.get_retail_sales(end_date=end_date),
            "industrial_production": self.get_industrial_production(end_date=end_date),
            "capacity_utilization": self.get_capacity_utilization(end_date=end_date),
            "personal_saving_rate": self.get_personal_saving_rate(end_date=end_date),
        }

    def get_yield_curve_spread(self) -> Dict[str, Any]:
        """Get yield curve spreads (10y-2y, 10y-3m, 30y-5y)"""
        curve = self.get_all_treasury_yields()

        spreads = {}
        if curve.get("10y") and curve.get("2y"):
            spreads["10y_2y_spread"] = curve["10y"]["rate"] - curve["2y"]["rate"]
        if curve.get("10y") and curve.get("3m"):
            spreads["10y_3m_spread"] = curve["10y"]["rate"] - curve["3m"]["rate"]
        if curve.get("30y") and curve.get("5y"):
            spreads["30y_5y_spread"] = curve["30y"]["rate"] - curve["5y"]["rate"]

        return spreads

    def get_credit_spreads(self) -> Dict[str, Any]:
        """Get credit spreads (BAA-AA, AAA-AA)"""
        spreads = {}
        series_map = {
            "baa_aa_spread": "BAA10Y",
            "aaa_aa_spread": "AAA10Y",
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and "observations" in series_data:
                latest = series_data["observations"][-1]
                spreads[name] = float(latest["value"]) if latest["value"] else None

        return spreads

    def get_inflation_data(self) -> Dict[str, Any]:
        """Get comprehensive inflation indicators"""
        data = {}
        series_map = {
            "cpi": "CPIAUCSL",
            "pce": "PCEPI",
            "core_cpi": "CPILFESL",
            "core_pce": "PCEPILFE",
            "inflation_expectation_5y": "T5YIE",
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and "observations" in series_data:
                latest = series_data["observations"][-1]
                data[name] = float(latest["value"]) if latest["value"] else None

        return data

    def get_bond_yield_history(
        self, maturity: str = "10y", days: int = 365
    ) -> List[Dict[str, Any]]:
        """Get historical bond yield data"""
        series_map = {
            "10y": "DGS10",
            "5y": "DGS5",
            "2y": "DGS2",
            "30y": "DGS30",
        }

        series_id = series_map.get(maturity, "DGS10")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        series_data = self.get_series_data(
            series_id,
            observation_start=start_date.strftime("%Y-%m-%d"),
            observation_end=end_date.strftime("%Y-%m-%d"),
        )

        if series_data and "observations" in series_data:
            return [
                {
                    "date": obs["date"],
                    "value": float(obs["value"]) if obs["value"] else None,
                }
                for obs in series_data["observations"]
            ]

        return []

    def get_macro_indicators(self) -> Dict[str, Any]:
        data = {}
        series_map = {
            "gdp": "GDP",
            "cpi": "CPIAUCSL",
            "unemployment": "UNRATE",
            "fed_funds": "DFF",
            "mortgage_30y": "MORTGAGE30US",
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and "observations" in series_data:
                latest = series_data["observations"][-1]
                data[name] = float(latest["value"]) if latest["value"] else None

        return data
