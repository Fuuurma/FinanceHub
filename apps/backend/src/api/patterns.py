from typing import List, Optional, Dict, Any
from ninja import Router, Schema
from django.shortcuts import get_object_or_404

from utils.helpers.logger.logger import get_logger
from utils.services.pattern_recognition import get_pattern_recognition, PatternType
from utils.services.data_orchestrator import get_data_orchestrator
from assets.models.asset import Asset
from core.exceptions import ExternalAPIException, ValidationException

logger = get_logger(__name__)

router = Router(tags=["Pattern Recognition"])


class PatternDetectionRequest(Schema):
    symbol: str
    pattern_types: Optional[List[str]] = None
    min_confidence: float = 60.0
    days: int = 90


class PatternPointOut(Schema):
    index: int
    price: float
    timestamp: str
    point_type: str


class DetectedPatternOut(Schema):
    pattern_type: str
    direction: str
    confidence: float
    start_index: int
    end_index: int
    start_timestamp: str
    end_timestamp: str
    points: List[PatternPointOut]
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    description: str
    metadata: Dict[str, Any]


class SupportResistanceOut(Schema):
    price: float
    strength: float
    touch_count: int
    timestamps: List[str]


class PatternDetectionResponse(Schema):
    symbol: str
    patterns: List[DetectedPatternOut]
    support_levels: List[SupportResistanceOut]
    resistance_levels: List[SupportResistanceOut]
    analyzed_at: str


@router.post("/detect", response=PatternDetectionResponse)
async def detect_patterns(request, payload: PatternDetectionRequest):
    """
    Detect chart patterns for a symbol

    Available patterns:
    - head_and_shoulders: Head and Shoulders pattern
    - inverse_head_and_shoulders: Inverse Head and Shoulders
    - double_top: Double Top reversal pattern
    - double_bottom: Double Bottom reversal pattern
    - ascending_triangle: Bullish continuation pattern
    - descending_triangle: Bearish continuation pattern
    - symmetrical_triangle: Neutral continuation pattern
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

    pattern_recognition = get_pattern_recognition()
    all_patterns = pattern_recognition.detect_all_patterns(
        ohlcv_data, payload.min_confidence
    )

    sr_levels = pattern_recognition.detect_support_resistance(ohlcv_data, min_touches=3)

    patterns_out = []
    for pattern in all_patterns:
        pattern_dict = {
            "pattern_type": pattern.pattern_type.value,
            "direction": pattern.direction.value,
            "confidence": pattern.confidence,
            "start_index": pattern.start_index,
            "end_index": pattern.end_index,
            "start_timestamp": pattern.start_timestamp,
            "end_timestamp": pattern.end_timestamp,
            "points": [
                {
                    "index": p.index,
                    "price": p.price,
                    "timestamp": p.timestamp,
                    "point_type": p.point_type,
                }
                for p in pattern.points
            ],
            "target_price": pattern.target_price,
            "stop_loss": pattern.stop_loss,
            "description": pattern.description,
            "metadata": pattern.metadata,
        }
        patterns_out.append(DetectedPatternOut(**pattern_dict))

    support_out = [SupportResistanceOut(**s) for s in sr_levels.get("support", [])]
    resistance_out = [
        SupportResistanceOut(**r) for r in sr_levels.get("resistance", [])
    ]

    return {
        "symbol": payload.symbol,
        "patterns": patterns_out,
        "support_levels": support_out,
        "resistance_levels": resistance_out,
        "analyzed_at": str(__import__("datetime").datetime.now()),
    }


@router.get("/{symbol}/patterns")
async def get_patterns(
    request,
    symbol: str,
    pattern_types: Optional[str] = None,
    min_confidence: float = 60.0,
    days: int = 90,
):
    """
    Get detected patterns for a symbol

    Query params:
    - pattern_types: comma-separated list of patterns to detect
    - min_confidence: minimum confidence score (0-100)
    - days: number of days of historical data to analyze
    """
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )

    historical_response = await orchestrator.get_market_data(
        data_type=data_type,
        symbol=symbol,
        params={"days": days},
        priority="medium",
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    if len(ohlcv_data) < 10:
        raise ValidationException("Insufficient data for pattern recognition")

    pattern_recognition = get_pattern_recognition()

    patterns = []
    if not pattern_types or "head_and_shoulders" in pattern_types:
        patterns.extend(
            pattern_recognition.detect_head_and_shoulders(ohlcv_data, min_confidence)
        )
    if not pattern_types or "double_top" in pattern_types:
        patterns.extend(
            pattern_recognition.detect_double_top(ohlcv_data, min_confidence)
        )
    if not pattern_types or "double_bottom" in pattern_types:
        patterns.extend(
            pattern_recognition.detect_double_bottom(ohlcv_data, min_confidence)
        )
    if not pattern_types or "triangle" in pattern_types:
        patterns.extend(pattern_recognition.detect_triangle(ohlcv_data, min_confidence))

    patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)

    return {
        "symbol": symbol,
        "patterns": [
            {
                "pattern_type": p.pattern_type.value,
                "direction": p.direction.value,
                "confidence": p.confidence,
                "description": p.description,
                "target_price": p.target_price,
                "stop_loss": p.stop_loss,
            }
            for p in patterns
        ],
    }


@router.get("/{symbol}/support-resistance")
async def get_support_resistance(
    request,
    symbol: str,
    min_touches: int = 3,
    days: int = 90,
):
    """
    Get support and resistance levels for a symbol

    Query params:
    - min_touches: minimum number of touches to consider a level significant
    - days: number of days of historical data to analyze
    """
    orchestrator = get_data_orchestrator()
    asset = get_object_or_404(Asset, symbol__iexact=symbol)

    data_type = (
        "crypto_historical"
        if "crypto" in asset.asset_type.name.lower()
        else "stock_historical"
    )

    historical_response = await orchestrator.get_market_data(
        data_type=data_type,
        symbol=symbol,
        params={"days": days},
        priority="medium",
    )

    if not historical_response.data:
        raise ExternalAPIException("historical_data", "No historical data available")

    ohlcv_data = (
        historical_response.data if isinstance(historical_response.data, list) else []
    )

    if len(ohlcv_data) < 10:
        raise ValidationException("Insufficient data for analysis")

    pattern_recognition = get_pattern_recognition()
    levels = pattern_recognition.detect_support_resistance(
        ohlcv_data, min_touches=min_touches
    )

    return {
        "symbol": symbol,
        "support_levels": levels.get("support", []),
        "resistance_levels": levels.get("resistance", []),
    }
