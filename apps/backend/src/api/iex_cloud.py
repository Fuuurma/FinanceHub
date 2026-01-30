"""
IEX Cloud API Router
Exposes IEX Cloud endpoints for frontend integration - company info, key stats, earnings, ownership data
"""

from ninja import Router
from ninja_jwt import authenticate
from investments.tasks.iex_cloud_tasks import (
    fetch_stock_fundamentals_iex,
    fetch_key_stats_iex,
    fetch_analyst_estimates_iex,
    fetch_peers_iex,
    fetch_insider_transactions_iex,
    fetch_institutional_ownership_iex,
    fetch_market_movers_iex,
    fetch_sector_performance_iex,
)
from data.data_providers.iex_cloud.scraper import IEXCloudScraper

router = Router(tags=["IEX Cloud"])
scraper = IEXCloudScraper()


@router.get("/company/{symbol}")
@authenticate
def get_company_info(request, symbol: str):
    """Get company information for a symbol"""
    result = fetch_stock_fundamentals_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/quote/{symbol}")
@authenticate
def get_quote(request, symbol: str):
    """Get real-time quote for a symbol"""
    return scraper.get_quote(symbol)


@router.post("/quotes")
@authenticate
def get_quotes(request, data: dict):
    """Batch quotes for multiple symbols"""
    symbols = data.get("symbols", [])
    return scraper.get_quotes(symbols)


@router.get("/chart/{symbol}")
@authenticate
def get_chart(request, symbol: str, period: str = "1y"):
    """Get historical OHLCV chart data"""
    return scraper.get_chart(symbol, period)


@router.get("/keystats/{symbol}")
@authenticate
def get_key_stats(request, symbol: str):
    """Get key statistics for a symbol"""
    result = fetch_key_stats_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/advancedstats/{symbol}")
@authenticate
def get_advanced_stats(request, symbol: str):
    """Get advanced statistics for a symbol"""
    return scraper.get_advanced_stats(symbol)


@router.get("/earnings/{symbol}")
@authenticate
def get_earnings(request, symbol: str, period: str = "annual", last: int = 4):
    """Get earnings history for a symbol"""
    result = fetch_analyst_estimates_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/estimates/{symbol}")
@authenticate
def get_estimates(request, symbol: str, period: str = "annual", last: int = 4):
    """Get analyst estimates for a symbol"""
    result = fetch_analyst_estimates_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/insiders/{symbol}")
@authenticate
def get_insider_transactions(request, symbol: str):
    """Get insider trading data for a symbol"""
    result = fetch_insider_transactions_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/institutions/{symbol}")
@authenticate
def get_institutional_ownership(request, symbol: str):
    """Get institutional ownership for a symbol"""
    result = fetch_institutional_ownership_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/peers/{symbol}")
@authenticate
def get_peers(request, symbol: str):
    """Get peer companies for a symbol"""
    result = fetch_peers_iex.delay(symbol)
    return result.get(timeout=30)


@router.get("/marketlist")
@authenticate
def get_market_list(request, list_type: str = "mostactive"):
    """Get market movers (most active, gainers, losers)"""
    result = fetch_market_movers_iex.delay(list_type)
    return result.get(timeout=30)


@router.get("/sectorperformance")
@authenticate
def get_sector_performance(request):
    """Get sector performance data"""
    result = fetch_sector_performance_iex.delay()
    return result.get(timeout=30)


@router.get("/dividends/{symbol}")
@authenticate
def get_dividends(request, symbol: str, range: str = "1y"):
    """Get dividend history for a symbol"""
    return scraper.get_dividends(symbol, range)


@router.get("/splits/{symbol}")
@authenticate
def get_splits(request, symbol: str, range: str = "5y"):
    """Get stock split history for a symbol"""
    return scraper.get_splits(symbol, range)
