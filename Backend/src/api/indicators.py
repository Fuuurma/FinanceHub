from typing import List, Optional, Dict, Any
from ninja import Router, Schema, Query
from django.shortcuts import get_object_or_404

from utils.helpers.logger.logger import get_logger
from utils.services.technical_indicators import get_technical_indicators, IndicatorType
from utils.services.data_orchestrator import get_data_orchestrator
from utils.services.cache_manager import get_cache_manager
from assets.models.asset import Asset

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
    try:
        orchestrator = get_data_orchestrator()
        cache_manager = get_cache_manager()
        
        asset = get_object_or_404(Asset, symbol__iexact=payload.symbol)
        
        cache_key = f"indicators_{payload.symbol}_{payload.days}"
        cached_result = await cache_manager.get(
            'technical_indicators',
            cache_key
        )
        
        if cached_result:
            logger.info(f"Returning cached indicators for {payload.symbol}")
            return cached_result
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        
        historical_response = await orchestrator.get_market_data(
            data_type=data_type,
            symbol=payload.symbol,
            params={'days': payload.days},
            priority='medium'
        )
        
        if not historical_response.data or len(historical_response.data) == 0:
            return {"error": "No historical data available"}
        
        if isinstance(historical_response.data, list):
            ohlcv_data = historical_response.data
        elif isinstance(historical_response.data, dict):
            ohlcv_data = historical_response.data.get('results', [])
        else:
            return {"error": "Invalid data format"}
        
        technical_indicators = get_technical_indicators()
        
        indicator_map = {
            'sma': IndicatorType.SMA,
            'ema': IndicatorType.EMA,
            'rsi': IndicatorType.RSI,
            'macd': IndicatorType.MACD,
            'bollinger': IndicatorType.BOLLINGER,
            'stochastic': IndicatorType.STOCHASTIC,
            'williams_r': IndicatorType.WILLIAMS_R,
            'atr': IndicatorType.ATR,
            'obv': IndicatorType.OBV,
            'cci': IndicatorType.CCI
        }
        
        indicators_to_calculate = payload.indicators or list(indicator_map.keys())
        indicator_types = [indicator_map[ind] for ind in indicators_to_calculate if ind in indicator_map]
        
        results = await technical_indicators.calculate_all(ohlcv_data, indicator_types)
        
        output = {
            'symbol': payload.symbol,
            'sma': results.get('sma', []),
            'ema': results.get('ema', []),
            'rsi': results.get('rsi', []),
            'macd': results.get('macd', []),
            'bollinger': results.get('bollinger', []),
            'stochastic': results.get('stochastic', []),
            'williams_r': results.get('williams_r', []),
            'atr': results.get('atr', []),
            'obv': results.get('obv', []),
            'cci': results.get('cci', [])
        }
        
        await cache_manager.set(
            'technical_indicators',
            cache_key,
            value=output,
            ttl=3600
        )
        
        return output
        
    except Exception as e:
        logger.error(f"Failed to calculate indicators for {payload.symbol}: {e}")
        return {"error": str(e), "symbol": payload.symbol}


@router.get("/{symbol}/sma")
async def get_sma(
    request,
    symbol: str,
    period: int = 20,
    days: int = 90
):
    """Get Simple Moving Average (SMA)"""
    try:
        orchestrator = get_data_orchestrator()
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        historical_response = await orchestrator.get_market_data(data_type, symbol, {'days': days})
        
        if not historical_response.data:
            return {"error": "No historical data available"}
        
        ohlcv_data = historical_response.data if isinstance(historical_response.data, list) else []
        
        technical_indicators = get_technical_indicators()
        sma_data = await technical_indicators.calculate_sma(ohlcv_data, period)
        
        return {
            "symbol": symbol,
            "period": period,
            "data": sma_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get SMA for {symbol}: {e}")
        return {"error": str(e)}


@router.get("/{symbol}/ema")
async def get_ema(
    request,
    symbol: str,
    period: int = 20,
    days: int = 90
):
    """Get Exponential Moving Average (EMA)"""
    try:
        orchestrator = get_data_orchestrator()
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        historical_response = await orchestrator.get_market_data(data_type, symbol, {'days': days})
        
        if not historical_response.data:
            return {"error": "No historical data available"}
        
        ohlcv_data = historical_response.data if isinstance(historical_response.data, list) else []
        
        technical_indicators = get_technical_indicators()
        ema_data = await technical_indicators.calculate_ema(ohlcv_data, period)
        
        return {
            "symbol": symbol,
            "period": period,
            "data": ema_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get EMA for {symbol}: {e}")
        return {"error": str(e)}


@router.get("/{symbol}/rsi")
async def get_rsi(
    request,
    symbol: str,
    period: int = 14,
    days: int = 90
):
    """Get Relative Strength Index (RSI)"""
    try:
        orchestrator = get_data_orchestrator()
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        historical_response = await orchestrator.get_market_data(data_type, symbol, {'days': days})
        
        if not historical_response.data:
            return {"error": "No historical data available"}
        
        ohlcv_data = historical_response.data if isinstance(historical_response.data, list) else []
        
        technical_indicators = get_technical_indicators()
        rsi_data = await technical_indicators.calculate_rsi(ohlcv_data, period)
        
        return {
            "symbol": symbol,
            "period": period,
            "data": rsi_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get RSI for {symbol}: {e}")
        return {"error": str(e)}


@router.get("/{symbol}/macd")
async def get_macd(
    request,
    symbol: str,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    days: int = 90
):
    """Get MACD (Moving Average Convergence Divergence)"""
    try:
        orchestrator = get_data_orchestrator()
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        historical_response = await orchestrator.get_market_data(data_type, symbol, {'days': days})
        
        if not historical_response.data:
            return {"error": "No historical data available"}
        
        ohlcv_data = historical_response.data if isinstance(historical_response.data, list) else []
        
        technical_indicators = get_technical_indicators()
        macd_data = await technical_indicators.calculate_macd(
            ohlcv_data,
            fast_period,
            slow_period,
            signal_period
        )
        
        return {
            "symbol": symbol,
            "parameters": {
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period
            },
            "data": macd_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get MACD for {symbol}: {e}")
        return {"error": str(e)}


@router.get("/{symbol}/bollinger")
async def get_bollinger_bands(
    request,
    symbol: str,
    period: int = 20,
    std_dev: float = 2.0,
    days: int = 90
):
    """Get Bollinger Bands"""
    try:
        orchestrator = get_data_orchestrator()
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        historical_response = await orchestrator.get_market_data(data_type, symbol, {'days': days})
        
        if not historical_response.data:
            return {"error": "No historical data available"}
        
        ohlcv_data = historical_response.data if isinstance(historical_response.data, list) else []
        
        technical_indicators = get_technical_indicators()
        bollinger_data = await technical_indicators.calculate_bollinger_bands(
            ohlcv_data,
            period,
            std_dev
        )
        
        return {
            "symbol": symbol,
            "parameters": {
                "period": period,
                "std_dev": std_dev
            },
            "data": bollinger_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get Bollinger Bands for {symbol}: {e}")
        return {"error": str(e)}


@router.get("/{symbol}/stochastic")
async def get_stochastic(
    request,
    symbol: str,
    k_period: int = 14,
    d_period: int = 3,
    smooth_k: int = 3,
    days: int = 90
):
    """Get Stochastic Oscillator"""
    try:
        orchestrator = get_data_orchestrator()
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        
        data_type = 'crypto_historical' if 'crypto' in asset.asset_type.name.lower() else 'stock_historical'
        historical_response = await orchestrator.get_market_data(data_type, symbol, {'days': days})
        
        if not historical_response.data:
            return {"error": "No historical data available"}
        
        ohlcv_data = historical_response.data if isinstance(historical_response.data, list) else []
        
        technical_indicators = get_technical_indicators()
        stochastic_data = await technical_indicators.calculate_stochastic(
            ohlcv_data,
            k_period,
            d_period,
            smooth_k
        )
        
        return {
            "symbol": symbol,
            "parameters": {
                "k_period": k_period,
                "d_period": d_period,
                "smooth_k": smooth_k
            },
            "data": stochastic_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get Stochastic for {symbol}: {e}")
        return {"error": str(e)}
