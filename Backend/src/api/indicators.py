from typing import List, Optional, Dict, Any
from ninja import Router, Schema, Query
from django.shortcuts import get_object_or_404

from utils.helpers.logger.logger import get_logger
from utils.services.technical_indicators import get_technical_indicators, IndicatorType
from utils.services.data_orchestrator import get_data_orchestrator
from assets.models.asset import Asset
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from core.exceptions import NotFoundException, ValidationException, ExternalAPIException

logger = get_logger(__name__)

router = Router(tags=["Technical Indicators"])


class IndicatorRequest(Schema):
    symbol: str
    indicators: Optional[List[str]] = None
    period: Optional[int] = None
    days: int = 90


class IndicatorResponse(Schema):
    indicator: str
    data: List[Dict[str, Any]]
    calculated_at: str

    class Config:
        from_attributes = True


class IndicatorDataPoint(Schema):
    timestamp: str
    value: float
    close: Optional[float] = None

    class Config:
        from_attributes = True


class TechnicalIndicatorsOut(Schema):
    symbol: str
    sma: Optional[List[Dict[str, float]]] = None
    ema: Optional[List[Dict[str, float]]] = None
    rsi: Optional[List[Dict[str, float]]] = None
    macd: Optional[List[Dict[str, float]]] = None
    bollinger: Optional[List[Dict[str, float]]] = None
    stochastic: Optional[List[Dict[str, float]]] = None
    williams_r: Optional[List[Dict[str, float]]] = None
    atr: Optional[List[Dict[str, float]]] = None
    obv: Optional[List[Dict[str, float]]] = None
    cci: Optional[List[Dict[str, float]]] = None


@router.post("/calculate", response=TechnicalIndicatorsOut)
async def calculate_indicators(request, payload: IndicatorRequest):
    """
    Calculate technical indicators for a symbol

    Available indicators: sma, ema, rsi, macd, bollinger, stochastic,
                            williams_r, atr, obv, cci
    """
    orchestrator = get_data_orchestrator()

    asset = get_object_or_404(Asset, symbol__iexact=payload.symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )

    historical_response = await orchestrator.get_market_data(
        data_type=data_type,
        symbol=payload.symbol,
        params={"days": payload.days},
        priority="medium",
    )

    if not historical_response.data or len(historical_response.data) == 0:
        raise ExternalAPIException("historical_data", "No historical data available")

    if isinstance(historical_response.data, list):
        ohlcv_data = historical_response.data
    elif isinstance(historical_response.data, dict):
        ohlcv_data = historical_response.data.get("results", [])
    else:
        raise ValidationException("Invalid data format received from data provider")

    technical_indicators = get_technical_indicators()

    indicator_map = {
        "sma": IndicatorType.SMA,
        "ema": IndicatorType.EMA,
        "rsi": IndicatorType.RSI,
        "macd": IndicatorType.MACD,
        "bollinger": IndicatorType.BOLLINGER,
        "stochastic": IndicatorType.STOCHASTIC,
        "williams_r": IndicatorType.WILLIAMS_R,
        "atr": IndicatorType.ATR,
        "obv": IndicatorType.OBV,
        "cci": IndicatorType.CCI,
    }

    indicators_to_calculate = payload.indicators or list(indicator_map.keys())
    indicator_types = [
        indicator_map[ind] for ind in indicators_to_calculate if ind in indicator_map
    ]

    results = await technical_indicators.calculate_all(ohlcv_data, indicator_types)

    return {
        "symbol": payload.symbol,
        "sma": results.get("sma", []),
        "ema": results.get("ema", []),
        "rsi": results.get("rsi", []),
        "macd": results.get("macd", []),
        "bollinger": results.get("bollinger", []),
        "stochastic": results.get("stochastic", []),
        "williams_r": results.get("williams_r", []),
        "atr": results.get("atr", []),
        "obv": results.get("obv", []),
        "cci": results.get("cci", []),
    }


@router.get("/{symbol}/sma")
async def get_sma(request, symbol: str, period: int = 20, days: int = 90):
    """Get Simple Moving Average (SMA)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    sma_data = technical_indicators.calculate_sma(ohlcv_data, period)

    return {"symbol": symbol, "period": period, "data": sma_data}


@router.get("/{symbol}/ema")
async def get_ema(request, symbol: str, period: int = 20, days: int = 90):
    """Get Exponential Moving Average (EMA)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    ema_data = technical_indicators.calculate_ema(ohlcv_data, period)

    return {"symbol": symbol, "period": period, "data": ema_data}


@router.get("/{symbol}/rsi")
async def get_rsi(request, symbol: str, period: int = 14, days: int = 90):
    """Get Relative Strength Index (RSI)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    rsi_data = technical_indicators.calculate_rsi(ohlcv_data, period)

    return {"symbol": symbol, "period": period, "data": rsi_data}


@router.get("/{symbol}/macd")
async def get_macd(
    request,
    symbol: str,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    days: int = 90,
):
    """Get MACD (Moving Average Convergence Divergence)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    macd_data = technical_indicators.calculate_macd(
        ohlcv_data, fast_period, slow_period, signal_period
    )

    return {
        "symbol": symbol,
        "parameters": {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period,
        },
        "data": macd_data,
    }


@router.get("/{symbol}/bollinger")
async def get_bollinger_bands(
    request, symbol: str, period: int = 20, std_dev: float = 2.0, days: int = 90
):
    """Get Bollinger Bands"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    bollinger_data = technical_indicators.calculate_bollinger_bands(
        ohlcv_data, period, std_dev
    )

    return {
        "symbol": symbol,
        "parameters": {"period": period, "std_dev": std_dev},
        "data": bollinger_data,
    }


@router.get("/{symbol}/stochastic")
async def get_stochastic(
    request,
    symbol: str,
    k_period: int = 14,
    d_period: int = 3,
    smooth_k: int = 3,
    days: int = 90,
):
    """Get Stochastic Oscillator"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    stochastic_data = technical_indicators.calculate_stochastic(
        ohlcv_data, k_period, d_period, smooth_k
    )

    return {
        "symbol": symbol,
        "parameters": {
            "k_period": k_period,
            "d_period": d_period,
            "smooth_k": smooth_k,
        },
        "data": stochastic_data,
    }


@router.get("/{symbol}/wma")
async def get_wma(request, symbol: str, period: int = 20, days: int = 90):
    """Get Weighted Moving Average (WMA)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    wma_data = technical_indicators.calculate_wma(ohlcv_data, period)

    return {"symbol": symbol, "period": period, "data": wma_data}


@router.get("/{symbol}/mfi")
async def get_mfi(request, symbol: str, period: int = 14, days: int = 90):
    """Get Money Flow Index (MFI)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    mfi_data = technical_indicators.calculate_mfi(ohlcv_data, period)

    return {"symbol": symbol, "period": period, "data": mfi_data}


@router.get("/{symbol}/vwap")
async def get_vwap(request, symbol: str, days: int = 90):
    """Get Volume Weighted Average Price (VWAP)"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    vwap_data = technical_indicators.calculate_vwap(ohlcv_data)

    return {"symbol": symbol, "data": vwap_data}


@router.get("/{symbol}/ichimoku")
async def get_ichimoku(
    request,
    symbol: str,
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_span_b_period: int = 52,
    days: int = 180,
):
    """Get Ichimoku Cloud indicators"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    ichimoku_data = technical_indicators.calculate_ichimoku(
        ohlcv_data, tenkan_period, kijun_period, senkou_span_b_period
    )

    return {
        "symbol": symbol,
        "parameters": {
            "tenkan_period": tenkan_period,
            "kijun_period": kijun_period,
            "senkou_span_b_period": senkou_span_b_period,
        },
        "data": ichimoku_data,
    }


@router.get("/{symbol}/parabolic-sar")
async def get_parabolic_sar(
    request,
    symbol: str,
    acceleration: float = 0.02,
    maximum: float = 0.2,
    days: int = 90,
):
    """Get Parabolic SAR"""
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )
    historical_response = await orchestrator.get_market_data(
        data_type, symbol, {"days": days}
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    technical_indicators = get_technical_indicators()
    psar_data = technical_indicators.calculate_parabolic_sar(
        ohlcv_data, acceleration, maximum
    )

    return {
        "symbol": symbol,
        "parameters": {"acceleration": acceleration, "maximum": maximum},
        "data": psar_data,
    }
