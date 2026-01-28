from typing import List, Optional
from decimal import Decimal
from ninja import Router
from pydantic import BaseModel, Field
from django.utils import timezone

from utils.services.fundamental_service import get_fundamental_service
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

router = Router()


class EquityValuationResponse(BaseModel):
    symbol: str
    market_cap: Optional[Decimal] = None
    enterprise_value: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    ps_ratio: Optional[Decimal] = None
    ev_ebitda: Optional[Decimal] = None
    ev_revenue: Optional[Decimal] = None
    peg_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    fetched_at: str
    source: str


class EquityFundamentalsResponse(BaseModel):
    symbol: str
    profile: Optional[dict] = None
    key_metrics: Optional[dict] = None
    financial_ratios: Optional[dict] = None
    income_statement: Optional[List[dict]] = None
    balance_sheet: Optional[List[dict]] = None
    cash_flow: Optional[List[dict]] = None
    fetched_at: str
    source: str


class CryptoProtocolResponse(BaseModel):
    protocol: str
    name: Optional[str] = None
    tvl: Optional[Decimal] = None
    tvl_change_24h: Optional[Decimal] = None
    tvl_change_7d: Optional[Decimal] = None
    chain: Optional[str] = None
    category: Optional[str] = None
    fetched_at: str
    source: str


class BondMetricsResponse(BaseModel):
    treasury_yields: dict
    full_yield_curve: dict
    yield_curve_spreads: dict
    credit_spreads: dict
    inflation: dict
    macro_indicators: dict
    fetched_at: str
    source: str


class YieldCurveResponse(BaseModel):
    curve: dict
    spreads: dict
    fetched_at: str
    source: str


class StockScreenerRequest(BaseModel):
    market_cap_min: Optional[int] = None
    market_cap_max: Optional[int] = None
    pe_min: Optional[float] = None
    pe_max: Optional[float] = None
    dividend_yield_min: Optional[float] = None
    sector: Optional[str] = None
    limit: int = 100


class StockScreenerResponse(BaseModel):
    stocks: List[dict]
    count: int
    fetched_at: str


class SectorPerformanceResponse(BaseModel):
    sectors: List[dict]
    fetched_at: str


@router.get("/fundamentals/{symbol}", response=EquityFundamentalsResponse)
async def get_equity_fundamentals(request, symbol: str, force_refresh: bool = False):
    """
    Get comprehensive fundamental data for an equity

    Includes: company profile, key metrics, financial ratios, income statement,
    balance sheet, and cash flow statement
    """
    service = get_fundamental_service()
    data = await service.get_equity_fundamentals(symbol, force_refresh=force_refresh)
    return data


@router.get("/valuation/{symbol}", response=EquityValuationResponse)
async def get_equity_valuation(request, symbol: str, force_refresh: bool = False):
    """
    Get valuation metrics for an equity

    Includes: P/E, P/B, P/S, EV/EBITDA, PEG ratio, dividend yield, beta, EPS
    """
    service = get_fundamental_service()
    data = await service.get_equity_valuation(symbol, force_refresh=force_refresh)
    return data


@router.get("/financials/{symbol}")
async def get_equity_financials(
    request,
    symbol: str,
    period: str = "annual",
    limit: int = 5
):
    """
    Get financial statements for an equity

    Args:
        symbol: Stock symbol
        period: 'annual' or 'quarterly'
        limit: Number of periods to return (default 5)
    """
    service = get_fundamental_service()
    data = await service.get_equity_financials(symbol, period=period, limit=limit)
    return data


@router.get("/crypto/protocol/{protocol}", response=CryptoProtocolResponse)
async def get_crypto_protocol(request, protocol: str, force_refresh: bool = False):
    """
    Get protocol metrics for a crypto protocol

    Examples: 'uniswap', 'aave', 'compound', 'makerdao', 'curve'
    """
    service = get_fundamental_service()
    data = await service.get_crypto_protocol_metrics(protocol, force_refresh=force_refresh)
    return data


@router.get("/crypto/protocols")
async def get_all_crypto_protocols(request):
    """
    Get all crypto protocols from DeFi Llama

    Returns TVL, chain, and category for all protocols
    """
    service = get_fundamental_service()
    protocols = await service.get_all_crypto_protocols()
    return {"protocols": protocols, "count": len(protocols)}


@router.get("/crypto/chain/{chain}")
async def get_chain_tvl(request, chain: str):
    """
    Get TVL data for a specific chain

    Examples: 'ethereum', 'bsc', 'polygon', 'avalanche', 'arbitrum', 'optimism'
    """
    service = get_fundamental_service()
    data = await service.get_chain_tvl(chain)
    return data


@router.get("/bonds/metrics", response=BondMetricsResponse)
async def get_bond_metrics(request, force_refresh: bool = False):
    """
    Get bond and macro metrics from FRED

    Includes: Treasury yields, yield curve, credit spreads, inflation data
    """
    service = get_fundamental_service()
    data = await service.get_bond_metrics(force_refresh=force_refresh)
    return data


@router.get("/bonds/yield-curve", response=YieldCurveResponse)
async def get_yield_curve(request, force_refresh: bool = False):
    """
    Get current treasury yield curve

    Returns: Complete yield curve from 1m to 30y with spreads
    """
    service = get_fundamental_service()
    data = await service.get_yield_curve(force_refresh=force_refresh)
    return data


@router.get("/bonds/treasury-history")
async def get_treasury_history(
    request,
    maturity: str = "10y",
    days: int = 365
):
    """
    Get historical treasury yields

    Args:
        maturity: '10y', '5y', '2y', or '30y'
        days: Number of days of history (default 365)
    """
    service = get_fundamental_service()
    history = await service.get_treasury_yields_history(maturity=maturity, days=days)
    return {"maturity": maturity, "days": days, "history": history}


@router.post("/screener", response=StockScreenerResponse)
async def screen_stocks(request, filters: StockScreenerRequest):
    """
    Screen stocks based on criteria

    Filter by market cap, P/E ratio, dividend yield, and sector
    """
    service = get_fundamental_service()
    stocks = await service.screen_stocks(
        market_cap_min=filters.market_cap_min,
        market_cap_max=filters.market_cap_max,
        pe_min=filters.pe_min,
        pe_max=filters.pe_max,
        dividend_yield_min=filters.dividend_yield_min,
        sector=filters.sector,
        limit=filters.limit
    )
    return {
        "stocks": stocks,
        "count": len(stocks),
        "fetched_at": timezone.now().isoformat()
    }


@router.get("/batch/equities")
async def batch_fetch_equities(
    request,
    symbols: str,
    data_type: str = "fundamentals"
):
    """
    Fetch fundamental data for multiple equities

    Args:
        symbols: Comma-separated list of symbols (e.g., "AAPL,MSFT,GOOGL")
        data_type: 'fundamentals', 'valuation', or 'financials'
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    service = get_fundamental_service()
    results = await service.batch_fetch_equities(symbol_list, data_type=data_type)
    return {"results": results, "count": len(results)}


@router.get("/sectors", response=SectorPerformanceResponse)
async def get_sector_performance(request):
    """
    Get sector performance data

    Returns average P/E and 24h change for each sector
    """
    service = get_fundamental_service()
    data = await service.get_sector_performance()
    return data
