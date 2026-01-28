"""
Analytics API Endpoints
Expose analytics services via REST API.
"""
from typing import Optional, List, Dict, Any
from ninja import Router, Schema, Query, Field
from pydantic import BaseModel, validator
from datetime import datetime
from utils.api.decorators import api_endpoint

from utils.services.performance import PerformanceAnalyzer, PerformanceReport, RiskAdjustedReport, FactorReport
from utils.services.risk import RiskAnalyzer, VolatilityReport, DrawdownReport, VaRReport, CVaRReport
from utils.services.correlation import CorrelationAnalyzer, CorrelationReport, DiversificationReport
from utils.services.options import OptionsAnalyzer, OptionAnalysisReport, OptionsChainReport
from utils.constants.analytics import DEFAULT_CONFIDENCE_LEVEL, DEFAULT_RISK_FREE_RATE
from utils.constants.api import RATE_LIMITS, CACHE_TTLS

router = Router(tags=["Analytics"])


class PerformanceRequest(BaseModel):
    symbol: str
    period: str = "1y"
    benchmark: Optional[str] = None


class PerformanceResponse(BaseModel):
    symbol: str
    total_return: float
    annualized_return: float
    best_period: List[Any]
    worst_period: List[Any]
    hit_rate: Optional[float]
    benchmark_return: Optional[float]
    excess_return: Optional[float]
    interpretation: str
    fetched_at: str


class RiskAdjustedRequest(BaseModel):
    symbol: str = ""
    benchmark_returns: Optional[List[float]] = None
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE


class RiskAdjustedResponse(BaseModel):
    sharpe_ratio: float
    sortino_ratio: float
    treynor_ratio: Optional[float]
    information_ratio: Optional[float]
    beta: Optional[float]
    alpha: Optional[float]
    r_squared: Optional[float]
    interpretation: str
    fetched_at: str


class VolatilityRequest(BaseModel):
    symbol: str


class VolatilityResponse(BaseModel):
    symbol: str
    daily_volatility: float
    annualized_volatility: float
    semivariance: float
    skewness: float
    kurtosis: float
    interpretation: str
    fetched_at: str


class VaRRequest(BaseModel):
    symbol: str
    confidence: float = Field(default=DEFAULT_CONFIDENCE_LEVEL, ge=0.9, le=0.99)
    method: str = "historical"


class VaRResponse(BaseModel):
    symbol: str
    var_daily: float
    var_weekly: Optional[float]
    var_monthly: Optional[float]
    confidence_level: float
    method: str
    exceedances: int
    interpretation: str
    fetched_at: str


class CVaRRequest(BaseModel):
    symbol: str
    confidence: float = Field(default=DEFAULT_CONFIDENCE_LEVEL, ge=0.9, le=0.99)


class CVaRResponse(BaseModel):
    symbol: str
    cvar_daily: float
    confidence_level: float
    var_at_level: float
    interpretation: str
    fetched_at: str


class DrawdownRequest(BaseModel):
    symbol: str


class DrawdownResponse(BaseModel):
    symbol: str
    max_drawdown: float
    max_drawdown_date: str
    recovery_date: Optional[str]
    current_drawdown: float
    drawdown_duration: int
    interpretation: str
    fetched_at: str


class CorrelationRequest(BaseModel):
    assets: Dict[str, List[float]]  # symbol -> returns


class CorrelationResponse(BaseModel):
    symbol: str
    assets: List[str]
    diversification_score: float
    clusters: List[List[str]]
    strongest_correlation: List[Any]
    weakest_correlation: List[Any]
    average_correlation: float
    interpretation: str
    fetched_at: str


class OptionAnalysisRequest(BaseModel):
    underlying_price: float
    strike_price: float
    time_to_expiration: float
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    volatility: float = 0.2
    option_type: str = "call"

    @validator("option_type")
    def validate_option_type(cls, v):
        if v not in ["call", "put"]:
            raise ValueError("option_type must be 'call' or 'put'")
        return v


class OptionAnalysisResponse(BaseModel):
    underlying_price: float
    strike_price: float
    time_to_expiration: float
    option_type: str
    fair_price: float
    greeks: Dict[str, float]
    probability_itm: float
    breakeven: float
    interpretation: str
    fetched_at: str


class OptionsChainRequest(BaseModel):
    underlying_price: float
    strikes: List[float]
    time_to_expiration: float
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    option_type: str = "call"


class OptionsChainResponse(BaseModel):
    underlying_price: float
    time_to_expiration: float
    option_type: str
    strikes: List[float]
    greeks_by_strike: Dict[str, Dict[str, float]]
    interpretation: str
    fetched_at: str


@router.get("/performance", response=PerformanceResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['analytics'], key_prefix="analytics")
async def get_performance(
    request,
    symbol: str = Query(...),
    period: str = Query(default="1y"),
    benchmark: Optional[str] = Query(default=None)
):
    """
    Get performance metrics for a symbol.
    
    Returns total return, annualized return, best/worst periods, and interpretation.
    """
    analyzer = PerformanceAnalyzer()
    
    prices = await _get_price_series(symbol, period)
    benchmark_prices = await _get_price_series(benchmark, period) if benchmark else None
    
    report = analyzer.analyze_returns(prices, symbol, benchmark_prices, period)
    
    return PerformanceResponse(
        symbol=report.symbol,
        total_return=report.total_return,
        annualized_return=report.annualized_return,
        best_period=list(report.best_period),
        worst_period=list(report.worst_period),
        hit_rate=report.hit_rate,
        benchmark_return=report.benchmark_return,
        excess_return=report.excess_return,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.get("/performance/risk-adjusted", response=RiskAdjustedResponse)
@api_endpoint(ttl=CACHE_TTLS['analytics'], rate=RATE_LIMITS['analytics'], key_prefix="analytics")
async def get_risk_adjusted(
    request,
    returns: List[float] = Query(...),
    benchmark_returns: Optional[List[float]] = Query(default=None),
    risk_free_rate: float = Query(default=DEFAULT_RISK_FREE_RATE)
):
    """
    Get risk-adjusted performance metrics.
    
    Returns Sharpe, Sortino, Treynor ratios, alpha, beta, and interpretation.
    """
    import polars as pl
    
    analyzer = PerformanceAnalyzer()
    returns_series = pl.Series(returns)
    benchmark_series = pl.Series(benchmark_returns) if benchmark_returns else None
    
    report = analyzer.analyze_risk_adjusted(
        returns_series, "", benchmark_series, risk_free_rate
    )
    
    return RiskAdjustedResponse(
        sharpe_ratio=report.sharpe_ratio,
        sortino_ratio=report.sortino_ratio,
        treynor_ratio=report.treynor_ratio,
        information_ratio=report.information_ratio,
        beta=report.beta,
        alpha=report.alpha,
        r_squared=report.r_squared,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.get("/risk/volatility", response=VolatilityResponse)
async def get_volatility(
    request,
    symbol: str = Query(...)
):
    """
    Get volatility analysis for a symbol.
    
    Returns daily/annualized volatility, semivariance, skewness, kurtosis.
    """
    analyzer = RiskAnalyzer()
    
    returns = await _get_return_series(symbol, "1y")
    report = analyzer.analyze_volatility(returns, symbol)
    
    return VolatilityResponse(
        symbol=report.symbol,
        daily_volatility=report.daily_volatility,
        annualized_volatility=report.annualized_volatility,
        semivariance=report.semivariance,
        skewness=report.skewness,
        kurtosis=report.kurtosis,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.get("/risk/var", response=VaRResponse)
async def get_var(
    request,
    symbol: str = Query(...),
    confidence: float = Query(default=DEFAULT_CONFIDENCE_LEVEL),
    method: str = Query(default="historical")
):
    """
    Calculate Value at Risk for a symbol.
    
    Returns daily/weekly/monthly VaR with interpretation.
    """
    analyzer = RiskAnalyzer()
    
    returns = await _get_return_series(symbol, "1y")
    report = analyzer.calculate_var(returns, symbol, confidence, method)
    
    return VaRResponse(
        symbol=report.symbol,
        var_daily=report.var_daily,
        var_weekly=report.var_weekly,
        var_monthly=report.var_monthly,
        confidence_level=report.confidence_level,
        method=report.method,
        exceedances=report.exceedances,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.get("/risk/cvar", response=CVaRResponse)
async def get_cvar(
    request,
    symbol: str = Query(...),
    confidence: float = Query(default=DEFAULT_CONFIDENCE_LEVEL)
):
    """
    Calculate Conditional Value at Risk (Expected Shortfall).
    """
    analyzer = RiskAnalyzer()
    
    returns = await _get_return_series(symbol, "1y")
    report = analyzer.calculate_cvar(returns, symbol, confidence)
    
    return CVaRResponse(
        symbol=report.symbol,
        cvar_daily=report.cvar_daily,
        confidence_level=report.confidence_level,
        var_at_level=report.var_at_level,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.get("/risk/drawdown", response=DrawdownResponse)
async def get_drawdown(
    request,
    symbol: str = Query(...)
):
    """
    Get drawdown analysis for a symbol.
    
    Returns max drawdown, recovery time, current drawdown.
    """
    analyzer = RiskAnalyzer()
    
    prices = await _get_price_series(symbol, "1y")
    report = analyzer.analyze_drawdown(prices, symbol)
    
    return DrawdownResponse(
        symbol=report.symbol,
        max_drawdown=report.max_drawdown,
        max_drawdown_date=report.max_drawdown_date,
        recovery_date=report.recovery_date,
        current_drawdown=report.current_drawdown,
        drawdown_duration=report.drawdown_duration,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.post("/correlation", response=CorrelationResponse)
async def post_correlation(request, data: CorrelationRequest):
    """
    Calculate correlation matrix and diversification score.
    """
    import polars as pl
    
    analyzer = CorrelationAnalyzer()
    
    returns_dict = {
        symbol: pl.Series(returns) 
        for symbol, returns in data.assets.items()
    }
    
    report = analyzer.analyze_correlations(returns_dict, "portfolio")
    
    return CorrelationResponse(
        symbol=report.symbol,
        assets=report.assets,
        diversification_score=report.diversification_score,
        clusters=report.clusters,
        strongest_correlation=list(report.strongest_correlation),
        weakest_correlation=list(report.weakest_correlation),
        average_correlation=report.average_correlation,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.post("/options/analyze", response=OptionAnalysisResponse)
async def post_option_analysis(request, data: OptionAnalysisRequest):
    """
    Analyze a single option with Greeks and interpretation.
    """
    analyzer = OptionsAnalyzer()
    
    report = analyzer.analyze_option(
        S=data.underlying_price,
        K=data.strike_price,
        T=data.time_to_expiration,
        r=data.risk_free_rate,
        sigma=data.volatility,
        option_type=data.option_type
    )
    
    return OptionAnalysisResponse(
        underlying_price=report.underlying_price,
        strike_price=report.strike_price,
        time_to_expiration=report.time_to_expiration,
        option_type=report.option_type,
        fair_price=report.fair_price,
        greeks=report.greeks,
        probability_itm=report.probability_itm,
        breakeven=report.breakeven,
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


@router.post("/options/chain", response=OptionsChainResponse)
async def post_options_chain(request, data: OptionsChainRequest):
    """
    Analyze options chain with Greeks by strike.
    """
    analyzer = OptionsAnalyzer()
    
    report = analyzer.analyze_options_chain(
        underlying_price=data.underlying_price,
        strikes=data.strikes,
        T=data.time_to_expiration,
        r=data.risk_free_rate,
        option_type=data.option_type
    )
    
    return OptionsChainResponse(
        underlying_price=report.underlying_price,
        time_to_expiration=report.time_to_expiration,
        option_type=report.option_type,
        strikes=report.strikes,
        greeks_by_strike={
            str(k): v for k, v in report.greeks_by_strike.items()
        },
        interpretation=report.interpretation,
        fetched_at=report.fetched_at,
    )


async def _get_price_series(symbol: str, period: str) -> "pl.Series":
    """Helper to get price series (placeholder)."""
    import polars as pl
    import numpy as np
    
    np.random.seed(42)
    n_days = {"1y": 252, "6m": 126, "3m": 63, "1m": 21}.get(period, 252)
    prices = 100 * np.cumprod(1 + np.random.randn(n_days) * 0.01 + 0.0005)
    
    return pl.Series(prices)


async def _get_return_series(symbol: str, period: str) -> "pl.Series":
    """Helper to get return series (placeholder)."""
    import polars as pl
    import numpy as np
    
    np.random.seed(42)
    n_days = {"1y": 252, "6m": 126, "3m": 63, "1m": 21}.get(period, 252)
    returns = np.random.randn(n_days) * 0.01 + 0.0005
    
    return pl.Series(returns)
