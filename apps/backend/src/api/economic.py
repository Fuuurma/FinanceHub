"""
Economic Indicators API Router
FRED Economic Data endpoints for frontend integration
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from ninja import Router, Schema
from ninja.pagination import paginate

from investments.models.economic_indicator import (
    EconomicIndicator,
    EconomicDataPoint,
    EconomicDataCache,
)
from data.data_providers.fred.scraper import FREDScraper
import os

router = Router(tags=["Economic Indicators"])

# Cache durations
CACHE_TTL_SHORT = 60 * 5  # 5 minutes
CACHE_TTL_MEDIUM = 60 * 15  # 15 minutes
CACHE_TTL_LONG = 60 * 60  # 1 hour


# Schemas
class MacroDashboardData(Schema):
    gdp: Optional[Dict[str, Any]] = None
    cpi: Optional[Dict[str, Any]] = None
    unemployment: Optional[Dict[str, Any]] = None
    fed_funds_rate: Optional[Dict[str, Any]] = None
    treasury_yields: Optional[Dict[str, Dict[str, Any]]] = None
    mortgage_rates: Optional[Dict[str, Dict[str, Any]]] = None
    housing: Optional[Dict[str, Any]] = None
    consumer_sentiment: Optional[Dict[str, Any]] = None
    retail_sales: Optional[Dict[str, Any]] = None
    industrial_production: Optional[Dict[str, Any]] = None
    capacity_utilization: Optional[Dict[str, Any]] = None
    personal_saving_rate: Optional[Dict[str, Any]] = None


class IndicatorOut(Schema):
    id: str
    series_id: str
    title: str
    description: str
    units: str
    frequency: str
    seasonal_adjustment: str
    last_updated: datetime
    observation_start: Optional[datetime]
    observation_end: Optional[datetime]
    popularity_score: int
    tags: List[str]


class DataPointOut(Schema):
    id: str
    indicator: str
    date: datetime
    value: float
    realtime_start: datetime
    realtime_end: datetime


class YieldCurveOut(Schema):
    maturity: str
    name: str
    rate: Optional[float]
    date: Optional[str]
    series_id: str


class CreditSpreadsOut(Schema):
    baa_aa_spread: Optional[float]
    aaa_aa_spread: Optional[float]


class InflationOut(Schema):
    cpi: Optional[float]
    pce: Optional[float]
    core_cpi: Optional[float]
    core_pce: Optional[float]
    inflation_expectation_5y: Optional[float]


class ErrorResponse(Schema):
    error: str
    code: str = "error"


def get_fred_scraper() -> FREDScraper:
    """Get FRED scraper instance"""
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not configured")
    return FREDScraper(api_key=api_key)


def get_cached_or_fetch(cache_key: str, fetch_func, ttl: int = CACHE_TTL_MEDIUM) -> Any:
    """Get data from cache or fetch from API"""
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    # Fetch fresh data
    data = fetch_func()
    if data is not None:
        cache.set(cache_key, data, ttl)
    return data


@router.get("/macro-dashboard", response=MacroDashboardData)
def get_macro_dashboard(request) -> Dict[str, Any]:
    """
    Get latest macro economic dashboard data.
    Returns cached data for fast loading.
    """
    cache_key = "macro_dashboard_v1"

    def fetch_dashboard():
        try:
            scraper = get_fred_scraper()
            return scraper.get_latest_macro_data()
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            return None

    dashboard_data = get_cached_or_fetch(cache_key, fetch_dashboard, CACHE_TTL_MEDIUM)
    return dashboard_data or {}


@router.get("/indicators/{series_id}", response=IndicatorOut)
def get_indicator(request, series_id: str) -> EconomicIndicator:
    """
    Get specific economic indicator by series ID.
    Fetches from FRED API and stores in database.
    """
    scraper = get_fred_scraper()

    # Fetch series info
    series_info = scraper.get_series_info(series_id)
    if not series_info or "seriess" not in series_info:
        raise ValueError(f"Series {series_id} not found")

    series_data = series_info["seriess"][0]

    # Get or create indicator
    indicator, created = EconomicIndicator.objects.update_or_create(
        series_id=series_id,
        defaults={
            "title": series_data.get("title", series_id),
            "description": series_data.get("notes", ""),
            "units": series_data.get("units", ""),
            "frequency": series_data.get("frequency", ""),
            "seasonal_adjustment": series_data.get("seasonal_adjustment", ""),
            "last_updated": datetime.now(),
            "observation_start": datetime.strptime(
                series_data.get("observation_start", "1900-01-01"), "%Y-%m-%d"
            ).date()
            if series_data.get("observation_start")
            else None,
            "observation_end": datetime.strptime(
                series_data.get("observation_end", "1900-01-01"), "%Y-%m-%d"
            ).date()
            if series_data.get("observation_end")
            else None,
            "popularity_score": series_data.get("popularity", 0),
        },
    )

    return indicator


@router.get("/data/{series_id}", response=List[DataPointOut])
@paginate
def get_data_points(
    request,
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Get time series data points for an indicator.
    Returns paginated results.
    """
    indicator = get_object_or_404(EconomicIndicator, series_id=series_id)

    queryset = EconomicDataPoint.objects.filter(indicator=indicator).order_by("-date")

    if start_date:
        queryset = queryset.filter(
            date__gte=datetime.strptime(start_date, "%Y-%m-%d").date()
        )
    if end_date:
        queryset = queryset.filter(
            date__lte=datetime.strptime(end_date, "%Y-%m-%d").date()
        )

    return list(queryset)


@router.get("/yield-curve", response=Dict[str, YieldCurveOut])
def get_yield_curve(
    request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Get complete Treasury yield curve data.
    Returns yields for all maturities (3m to 30y).
    """
    cache_key = f"yield_curve_{start_date}_{end_date}"

    def fetch_curve():
        scraper = get_fred_scraper()
        return scraper.get_all_treasury_yields(
            observation_start=start_date,
            observation_end=end_date,
        )

    yield_data = get_cached_or_fetch(cache_key, fetch_curve, CACHE_TTL_SHORT)
    return yield_data or {}


@router.get("/credit-spreads", response=CreditSpreadsOut)
def get_credit_spreads(request) -> Dict[str, Optional[float]]:
    """
    Get credit spread data (BAA-AA, AAA-AA).
    """
    cache_key = "credit_spreads_v1"

    def fetch_spreads():
        scraper = get_fred_scraper()
        return scraper.get_credit_spreads()

    spreads = get_cached_or_fetch(cache_key, fetch_spreads, CACHE_TTL_MEDIUM)
    return spreads or {}


@router.get("/inflation", response=InflationOut)
def get_inflation_data(request) -> Dict[str, Optional[float]]:
    """
    Get inflation indicators bundle.
    Returns CPI, PCE, core measures, and expectations.
    """
    cache_key = "inflation_bundle_v1"

    def fetch_inflation():
        scraper = get_fred_scraper()
        return scraper.get_inflation_data()

    inflation = get_cached_or_fetch(cache_key, fetch_inflation, CACHE_TTL_MEDIUM)
    return inflation or {}


@router.get("/gdp")
def get_gdp(
    request,
    real_gdp: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get GDP data with optional date range.
    """
    cache_key = f"gdp_{real_gdp}_{start_date}_{end_date}"

    def fetch_gdp():
        scraper = get_fred_scraper()
        return scraper.get_gdp(
            real_gdp=real_gdp, start_date=start_date, end_date=end_date
        )

    gdp_data = get_cached_or_fetch(cache_key, fetch_gdp, CACHE_TTL_LONG)
    return gdp_data or {}


@router.get("/unemployment")
def get_unemployment(
    request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get unemployment rate data.
    """
    cache_key = f"unemployment_{start_date}_{end_date}"

    def fetch_unemployment():
        scraper = get_fred_scraper()
        return scraper.get_unemployment_rate(start_date=start_date, end_date=end_date)

    unemployment = get_cached_or_fetch(cache_key, fetch_unemployment, CACHE_TTL_MEDIUM)
    return unemployment or {}


@router.get("/interest-rates")
def get_interest_rates(
    request,
    maturity: str = "10y",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get interest rate data by maturity.
    Maturity options: 3m, 1y, 2y, 5y, 10y, 30y
    """
    cache_key = f"interest_rates_{maturity}_{start_date}_{end_date}"

    def fetch_rates():
        scraper = get_fred_scraper()
        return scraper.get_treasury_yield(
            maturity=maturity,
            start_date=start_date,
            end_date=end_date,
        )

    rates = get_cached_or_fetch(cache_key, fetch_rates, CACHE_TTL_SHORT)
    return rates or {}


@router.get("/housing")
def get_housing_data(
    request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get housing market indicators (starts, permits, mortgage rates).
    """
    cache_key = f"housing_{start_date}_{end_date}"

    def fetch_housing():
        scraper = get_fred_scraper()
        return scraper.get_housing_data(
            start_date=start_date,
            end_date=end_date,
        )

    housing = get_cached_or_fetch(cache_key, fetch_housing, CACHE_TTL_MEDIUM)
    return housing or {}


@router.post("/refresh")
def refresh_dashboard(request) -> Dict[str, Any]:
    """
    Refresh macro dashboard cache.
    Triggers background update of cached economic data.
    """
    try:
        # Clear all economic data caches
        cache_keys = [
            "macro_dashboard_v1",
            "yield_curve_",
            "credit_spreads_v1",
            "inflation_bundle_v1",
        ]

        for key in cache_keys:
            cache.delete_pattern(f"{key}*")

        # Trigger background task to update cache
        from investments.tasks.fred_tasks import update_macro_dashboard_fred

        update_macro_dashboard_fred.delay()

        return {
            "success": True,
            "message": "Dashboard refresh initiated. Check back in a few moments.",
        }
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        return {
            "success": False,
            "message": f"Failed to refresh: {str(e)}",
        }


@router.get("/categories/{category}", response=List[IndicatorOut])
def get_category_indicators(request, category: str) -> List[EconomicIndicator]:
    """
    Get economic indicators by category.
    Categories: gdp, inflation, employment, interest_rates, housing, consumer, industrial
    """
    category_mappings = {
        "gdp": ["GDP", "GDPC1", "GNPCA"],
        "inflation": ["CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE"],
        "employment": ["UNRATE", "PAYEMS", "ICSA", "CIVPART"],
        "interest_rates": [
            "FEDFUNDS",
            "DGS3M",
            "DGS1",
            "DGS2",
            "DGS5",
            "DGS10",
            "DGS30",
        ],
        "housing": ["HOUST", "PERMIT", "MORTGAGE30US", "MORTGAGE15US"],
        "consumer": ["UMCSENT", "RSXFS", "PSAVERT"],
        "industrial": ["IPMAN", "TCU"],
    }

    series_ids = category_mappings.get(category.lower(), [])
    indicators = EconomicIndicator.objects.filter(series_id__in=series_ids)

    return list(indicators)


@router.get("/search", response=List[IndicatorOut])
def search_indicators(
    request,
    query: str,
    limit: int = 20,
) -> List[EconomicIndicator]:
    """
    Search economic indicators by title, description, or series ID.
    """
    indicators = (
        EconomicIndicator.objects.filter(title__icontains=query)
        | EconomicIndicator.objects.filter(description__icontains=query)
        | EconomicIndicator.objects.filter(series_id__icontains=query)
    )

    return indicators.distinct()[:limit]


@router.get("/list", response=List[IndicatorOut])
@paginate
def list_indicators(request):
    """
    List all available economic indicators with pagination.
    """
    return EconomicIndicator.objects.all().order_by("-popularity_score")


@router.get("/popular", response=List[IndicatorOut])
def get_popular_indicators(request, limit: int = 10) -> List[EconomicIndicator]:
    """
    Get most popular economic indicators.
    """
    return list(
        EconomicIndicator.objects.filter(popularity_score__gt=0).order_by(
            "-popularity_score"
        )[:limit]
    )
