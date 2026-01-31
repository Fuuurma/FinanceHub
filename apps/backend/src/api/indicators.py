"""
Technical Indicators API
Endpoints for calculating and retrieving technical indicators.
"""

import logging
from typing import Optional, List
from ninja import Router, Query
from pydantic import BaseModel
from django.http import HttpResponse
from assets.models import Asset
from assets.models.historic.prices import AssetPricesHistoric
from investments.lib.indicators import TechnicalIndicators, IndicatorResult

router = Router(tags=["Indicators"])
logger = logging.getLogger(__name__)


class IndicatorRequest(BaseModel):
    symbol: str
    indicator: str
    period: int = 14
    fast: int = 12
    slow: int = 26
    signal: int = 9
    std_dev: int = 2


INDICATOR_MAP = {
    "sma": lambda prices, **kwargs: TechnicalIndicators.sma(
        prices, kwargs.get("period", 20)
    ),
    "ema": lambda prices, **kwargs: TechnicalIndicators.ema(
        prices, kwargs.get("period", 20)
    ),
    "wma": lambda prices, **kwargs: TechnicalIndicators.wma(
        prices, kwargs.get("period", 20)
    ),
    "rsi": lambda prices, **kwargs: TechnicalIndicators.rsi(
        prices, kwargs.get("period", 14)
    ),
    "macd": lambda prices, **kwargs: TechnicalIndicators.macd(
        prices, kwargs.get("fast", 12), kwargs.get("slow", 26), kwargs.get("signal", 9)
    ),
    "stochastic": lambda prices, **kwargs: TechnicalIndicators.stochastic(
        [], [], prices, kwargs.get("period", 14)
    )
    if False
    else IndicatorResult(values=[], timestamps=[]),
    "bollinger_bands": lambda prices, **kwargs: TechnicalIndicators.bollinger_bands(
        prices, kwargs.get("period", 20), kwargs.get("std_dev", 2)
    ),
    "atr": lambda prices, **kwargs: TechnicalIndicators.atr(
        [], [], prices, kwargs.get("period", 14)
    ),
    "obv": lambda prices, **kwargs: IndicatorResult(values=[], timestamps=[]),
    "williams_r": lambda prices, **kwargs: TechnicalIndicators.williams_r(
        [], [], prices, kwargs.get("period", 14)
    ),
    "cci": lambda prices, **kwargs: TechnicalIndicators.cci(
        [], [], prices, kwargs.get("period", 20)
    ),
    "momentum": lambda prices, **kwargs: TechnicalIndicators.momentum(
        prices, kwargs.get("period", 10)
    ),
    "roc": lambda prices, **kwargs: TechnicalIndicators.roc(
        prices, kwargs.get("period", 10)
    ),
}


@router.get("/indicators/{symbol}/{indicator}")
def get_indicator(
    request,
    symbol: str,
    indicator: str,
    period: int = Query(14),
    fast: int = Query(12),
    slow: int = Query(26),
    signal: int = Query(9),
    std_dev: int = Query(2),
    days: int = Query(365),
):
    """Calculate and return technical indicator data for a symbol."""
    try:
        asset = Asset.objects.get(symbol=symbol.upper())
    except Asset.DoesNotExist:
        return {"error": "Asset not found"}, 404

    prices = list(
        AssetPricesHistoric.objects.filter(asset=asset)
        .order_by("-timestamp")[:days]
        .values_list("close_price", flat=True)
    )
    prices.reverse()

    if len(prices) < 10:
        return {"error": "Insufficient price data"}, 400

    if indicator not in INDICATOR_MAP:
        return {"error": f"Unknown indicator: {indicator}"}, 400

    kwargs = {
        "period": period,
        "fast": fast,
        "slow": slow,
        "signal": signal,
        "std_dev": std_dev,
    }

    result = INDICATOR_MAP[indicator](prices, **kwargs)

    return {
        "symbol": symbol,
        "indicator": indicator,
        "values": result.values,
        "metadata": result.metadata,
        "count": len(result.values),
    }


@router.get("/indicators/list")
def list_indicators(request):
    """List available indicators."""
    return {
        "indicators": list(INDICATOR_MAP.keys()),
        "categories": {
            "trend": ["sma", "ema", "wma"],
            "momentum": [
                "rsi",
                "macd",
                "stochastic",
                "williams_r",
                "cci",
                "momentum",
                "roc",
            ],
            "volatility": ["bollinger_bands", "atr"],
            "volume": ["obv"],
        },
    }


@router.post("/indicators/calculate")
def calculate_indicator(request, data: IndicatorRequest):
    """Calculate indicator on provided price data."""
    try:
        asset = Asset.objects.get(symbol=data.symbol.upper())
    except Asset.DoesNotExist:
        return {"error": "Asset not found"}, 404

    prices = list(
        AssetPricesHistoric.objects.filter(asset=asset)
        .order_by("-timestamp")[:365]
        .values_list("close_price", flat=True)
    )[-100:]
    prices.reverse()

    if data.indicator not in INDICATOR_MAP:
        return {"error": f"Unknown indicator: {data.indicator}"}, 400

    kwargs = {
        "period": data.period,
        "fast": data.fast,
        "slow": data.slow,
        "signal": data.signal,
        "std_dev": data.std_dev,
    }

    result = INDICATOR_MAP[data.indicator](prices, **kwargs)

    return {
        "symbol": data.symbol,
        "indicator": data.indicator,
        "values": result.values[-50:],
        "metadata": result.metadata,
    }


@router.get("/indicators/batch/{symbols}")
def get_multiple_indicators(
    request, symbols: str, indicators: str = "rsi,macd", period: int = 14
):
    """Get indicators for multiple symbols."""
    symbol_list = symbols.split(",")
    result = {}

    for symbol in symbol_list[:10]:
        symbol = symbol.strip().upper()
        try:
            asset = Asset.objects.get(symbol=symbol)
        except Asset.DoesNotExist:
            result[symbol] = {"error": "Not found"}
            continue

        prices = list(
            AssetPricesHistoric.objects.filter(asset=asset)
            .order_by("-timestamp")[:100]
            .values_list("close_price", flat=True)
        )
        prices.reverse()

        if len(prices) < 10:
            result[symbol] = {"error": "Insufficient data"}
            continue

        result[symbol] = {}
        for ind in indicators.split(","):
            ind = ind.strip()
            if ind in INDICATOR_MAP:
                calc_result = INDICATOR_MAP[ind](prices, {"period": period})
                result[symbol][ind] = {
                    "value": calc_result.values[-1] if calc_result.values else None,
                    "metadata": calc_result.metadata,
                }

    return result
