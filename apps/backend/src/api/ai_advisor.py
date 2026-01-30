"""
AI Advisor API
Paid subscription feature for AI-powered financial advice.
"""
from typing import Optional
from ninja import Router, Query
from pydantic import BaseModel, Field
from django.http import Http404

from utils.services.llm_advisor.ai_advisor import get_ai_advisor, AIAdvisorError
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint
from core.exceptions import (
    APIException, 
    ValidationException, 
    AuthorizationException, 
    BusinessLogicException,
    ServiceException
)

router = Router(tags=["AI Advisor (Premium)"])


class StrategyExplanationRequest(BaseModel):
    """Request for options strategy explanation."""
    strategy_type: str = Field(..., description="Strategy type: call, put, straddle, spread, iron_condor, etc.")
    underlying: str = Field(..., description="Underlying asset symbol", min_length=1, max_length=10)
    strike: float = Field(..., gt=0, description="Strike price")
    expiry: str = Field(..., description="Expiration date (YYYY-MM-DD)")
    premium: float = Field(..., ge=0, description="Option premium")
    direction: str = Field(default="long", description="Position direction: long or short")
    user_context: str = Field(default="", description="Additional context about the trade")


class StrategyExplanationResponse(BaseModel):
    """Response with strategy explanation."""
    text: str
    model_used: str
    tokens_used: int
    compute_time_ms: float


class StrategySuggestionRequest(BaseModel):
    """Request for strategy suggestions."""
    market_outlook: str = Field(..., description="Market outlook: bullish, bearish, neutral")
    risk_tolerance: str = Field(..., description="Risk tolerance: low, medium, high")
    underlying: str = Field(..., description="Underlying asset symbol", min_length=1, max_length=10)
    current_price: float = Field(..., gt=0, description="Current asset price")
    time_horizon: str = Field(..., description="Time horizon: days, weeks, months")
    preferred_direction: str = Field(default="both", description="Preferred direction: long, short, both")


class StrategySuggestionResponse(BaseModel):
    """Response with strategy suggestions."""
    text: str
    model_used: str
    tokens_used: int
    compute_time_ms: float


class ForecastNarrativeRequest(BaseModel):
    """Request for forecast narrative."""
    symbol: str = Field(..., description="Asset symbol", min_length=1, max_length=10)
    current_price: float = Field(..., gt=0, description="Current price")
    forecast_data: dict = Field(..., description="Forecast results from ARIMA/GARCH")
    model_type: str = Field(..., description="Model type: ARIMA or GARCH")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    user_question: str = Field(default="", description="Specific question about the forecast")


class ForecastNarrativeResponse(BaseModel):
    """Response with forecast narrative."""
    text: str
    model_used: str
    tokens_used: int
    compute_time_ms: float


class RiskExplanationRequest(BaseModel):
    """Request for risk metric explanation."""
    metric_name: str = Field(..., description="Metric name: VaR, CVaR, Beta, Sharpe, Duration, etc.")
    value: float = Field(..., description="Metric value")
    asset_type: str = Field(default="portfolio", description="Asset type: portfolio, position, bond, etc.")
    context: Optional[dict] = Field(default=None, description="Additional context (confidence level, etc.)")


class RiskExplanationResponse(BaseModel):
    """Response with risk explanation."""
    text: str
    model_used: str
    tokens_used: int
    compute_time_ms: float


class UsageStatsResponse(BaseModel):
    """Response with AI usage statistics."""
    requests_today: int
    tokens_used_today: int
    remaining_today: int
    max_requests: int
    last_request_at: Optional[str]


def check_ai_access(request) -> None:
    """
    Check if user has access to AI features.
    Raises AuthorizationException if not.
    """
    if not request.user.is_authenticated:
        raise BusinessLogicException(
            "AI Advisor requires authentication",
            {"feature": "AI Advisor"}
        )

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    if not access["has_access"]:
        raise BusinessLogicException(
            "AI Advisor requires a premium subscription",
            {
                "feature": "AI Advisor",
                "account_type": access["account_type"],
                "upgrade_url": "/pricing"
            }
        )


@router.post("/explain-strategy", response=StrategyExplanationResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['premium'], key_prefix="ai_advisor")
def explain_options_strategy(request, data: StrategyExplanationRequest):
    """
    Explain an options strategy in plain language.
    
    Requires premium subscription.
    """
    check_ai_access(request)

    valid_strategies = ["call", "put", "straddle", "strangle", "spread", "iron_condor", 
                        "butterfly", "covered_call", "protective_put", "married_put",
                        "bull_call_spread", "bear_put_spread", "ratio_spread"]
    
    if data.strategy_type.lower() not in valid_strategies:
        raise ValidationException(
            f"Unknown strategy: {data.strategy_type}",
            {"valid_strategies": valid_strategies}
        )

    try:
        advisor = get_ai_advisor()
        result = advisor.explain_options_strategy(
            strategy_type=data.strategy_type,
            underlying=data.underlying.upper(),
            strike=data.strike,
            expiry=data.expiry,
            premium=data.premium,
            direction=data.direction.lower(),
            user_context=data.user_context
        )

        advisor.record_usage(str(request.user.id), result.tokens_used)

        return StrategyExplanationResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            compute_time_ms=result.compute_time_ms
        )

    except AIAdvisorError as e:
        raise ServiceException(str(e))


@router.post("/suggest-strategy", response=StrategySuggestionResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['premium'], key_prefix="ai_advisor")
def suggest_options_strategy(request, data: StrategySuggestionRequest):
    """
    Suggest appropriate options strategies based on outlook.
    
    Requires premium subscription.
    """
    check_ai_access(request)

    valid_outlooks = ["bullish", "bearish", "neutral"]
    if data.market_outlook.lower() not in valid_outlooks:
        raise ValidationException(
            f"Invalid outlook: {data.market_outlook}",
            {"valid_outlooks": valid_outlooks}
        )

    valid_risk = ["low", "medium", "high"]
    if data.risk_tolerance.lower() not in valid_risk:
        raise ValidationException(
            f"Invalid risk tolerance: {data.risk_tolerance}",
            {"valid_levels": valid_risk}
        )

    try:
        advisor = get_ai_advisor()
        result = advisor.suggest_options_strategy(
            market_outlook=data.market_outlook.lower(),
            risk_tolerance=data.risk_tolerance.lower(),
            underlying=data.underlying.upper(),
            current_price=data.current_price,
            time_horizon=data.time_horizon,
            preferred_direction=data.preferred_direction.lower()
        )

        advisor.record_usage(str(request.user.id), result.tokens_used)

        return StrategySuggestionResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            compute_time_ms=result.compute_time_ms
        )

    except AIAdvisorError as e:
        raise ServiceException(str(e))


@router.post("/forecast-narrative", response=ForecastNarrativeResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['premium'], key_prefix="ai_advisor")
def generate_forecast_narrative(request, data: ForecastNarrativeRequest):
    """
    Generate natural language explanation of ARIMA/GARCH forecasts.
    
    Requires premium subscription.
    """
    check_ai_access(request)

    if data.model_type.upper() not in ["ARIMA", "GARCH"]:
        raise ValidationException(
            f"Invalid model type: {data.model_type}",
            {"valid_types": ["ARIMA", "GARCH"]}
        )

    try:
        advisor = get_ai_advisor()
        result = advisor.generate_forecast_narrative(
            symbol=data.symbol.upper(),
            current_price=data.current_price,
            forecast_data=data.forecast_data,
            model_type=data.model_type.upper(),
            confidence_level=data.confidence_level,
            user_question=data.user_question
        )

        advisor.record_usage(str(request.user.id), result.tokens_used)

        return ForecastNarrativeResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            compute_time_ms=result.compute_time_ms
        )

    except AIAdvisorError as e:
        raise ServiceException(str(e))


@router.post("/explain-risk", response=RiskExplanationResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['premium'], key_prefix="ai_advisor")
def explain_risk_metric(request, data: RiskExplanationRequest):
    """
    Explain a risk metric in plain language.
    
    Requires premium subscription.
    """
    check_ai_access(request)

    try:
        advisor = get_ai_advisor()
        result = advisor.explain_risk_metric(
            metric_name=data.metric_name,
            value=data.value,
            context=data.context or {},
            asset_type=data.asset_type
        )

        advisor.record_usage(str(request.user.id), result.tokens_used)

        return RiskExplanationResponse(
            text=result.text,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            compute_time_ms=result.compute_time_ms
        )

    except AIAdvisorError as e:
        raise ServiceException(str(e))


@router.get("/usage", response=UsageStatsResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['default'], key_prefix="ai_advisor")
def get_ai_usage_stats(request):
    """
    Get AI feature usage statistics for current user.
    
    Shows requests remaining today and usage stats.
    """
    if not request.user.is_authenticated:
        raise BusinessLogicException(
            "Authentication required",
            {"feature": "AI Advisor"}
        )

    from django.utils import timezone

    advisor = get_ai_advisor()
    stats = advisor.get_usage_stats(str(request.user.id))

    return UsageStatsResponse(
        requests_today=stats.requests_today,
        tokens_used_today=stats.tokens_used_today,
        remaining_today=stats.remaining_today,
        max_requests=advisor.check_feature_access(request.user)["max_requests"],
        last_request_at=stats.last_request_at.isoformat() if stats.last_request_at else None
    )


@router.get("/access")
def check_ai_access_status(request):
    """
    Check if current user has access to AI features.
    
    Returns subscription status and feature availability.
    """
    if not request.user.is_authenticated:
        return {
            "has_access": False,
            "reason": "Authentication required",
            "upgrade_url": "/pricing"
        }

    advisor = get_ai_advisor()
    access = advisor.check_feature_access(request.user)

    return {
        "has_access": access["has_access"],
        "is_paid": access["is_paid"],
        "is_trial": access["is_trial"],
        "account_type": access["account_type"],
        "max_daily_requests": access["max_requests"],
        "upgrade_url": "/pricing" if not access["is_paid"] else None
    }
