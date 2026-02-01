"""
Quantitative Models API
Time series analysis, forecasting, and statistical models.
"""
from typing import Optional, List
from ninja import Router, Query, Field
from pydantic import BaseModel, conint
import numpy as np

from utils.services.quantitative.time_series_models import TimeSeriesModels, ARIMAResult, GARCHResult
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint

router = Router(tags=["Quantitative Models"])


class ARIMARequest(BaseModel):
    """Request for ARIMA forecasting."""
    data: List[float] = Field(..., min_length=10, max_length=5000, description="Time series data")
    order_p: int = Field(default=1, ge=0, le=10, description="AR order (p)")
    order_d: int = Field(default=0, ge=0, le=3, description="Differencing order (d)")
    order_q: int = Field(default=1, ge=0, le=10, description="MA order (q)")
    steps: int = Field(default=10, ge=1, le=100, description="Forecast horizon")
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99, description="Confidence level")


class ARIMAResponse(BaseModel):
    """Response for ARIMA forecast."""
    forecast: List[float]
    confidence_interval_lower: List[float]
    confidence_interval_upper: List[float]
    order: List[int]
    aic: float
    bic: float
    compute_time_ms: float


class GARCHRequest(BaseModel):
    """Request for GARCH volatility forecasting."""
    returns: List[float] = Field(..., min_length=10, max_length=5000, description="Returns series")
    omega: Optional[float] = Field(default=None, ge=0, description="Long-run variance (auto if None)")
    alpha: Optional[float] = Field(default=None, ge=0, le=1, description="ARCH coefficient")
    beta: Optional[float] = Field(default=None, ge=0, le=1, description="GARCH coefficient")
    steps: int = Field(default=10, ge=1, le=100, description="Forecast horizon")


class GARCHResponse(BaseModel):
    """Response for GARCH forecast."""
    conditional_volatility: List[float]
    forecast_volatility: float
    omega: float
    alpha: float
    beta: float
    total_volatility: float
    compute_time_ms: float


class KalmanFilterRequest(BaseModel):
    """Request for Kalman filter estimation."""
    observations: List[float] = Field(..., min_length=5, max_length=5000, description="Observation sequence")
    state_dim: int = Field(default=1, ge=1, le=10, description="State dimension")
    process_noise: float = Field(default=0.01, ge=0, description="Process noise covariance")
    observation_noise: float = Field(default=0.1, ge=0, description="Observation noise covariance")


class KalmanFilterResponse(BaseModel):
    """Response for Kalman filter."""
    filtered_state: List[float]
    filtered_covariance_diag: List[float]
    predicted_state: List[float]
    likelihood: float
    compute_time_ms: float


class HalfLifeRequest(BaseModel):
    """Request for mean reversion half-life calculation."""
    prices: List[float] = Field(..., min_length=10, max_length=5000, description="Price series")
    lookback: Optional[int] = Field(default=None, ge=10, description="Lookback period")


class HalfLifeResponse(BaseModel):
    """Response for half-life calculation."""
    half_life: float
    Hurst_exponent: float
    mean_reversion_strength: str
    compute_time_ms: float


class HurstExponentRequest(BaseModel):
    """Request for Hurst exponent estimation."""
    data: List[float] = Field(..., min_length=100, max_length=5000, description="Time series data")
    max_scale: int = Field(default=10, ge=2, le=100, description="Maximum scale for R/S analysis")


class HurstExponentResponse(BaseModel):
    """Response for Hurst exponent."""
    hurst_exponent: float
    trend_type: str
    interpretation: str
    compute_time_ms: float


@router.post("/arima-forecast", response=ARIMAResponse)
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['analytics'], key_prefix="quantitative")
def arima_forecast(request, data: ARIMARequest):
    """
    ARIMA forecasting with confidence intervals.
    
    Parameters:
    - data: Time series price/return data
    - order (p,d,q): ARIMA parameters
    - steps: Forecast horizon
    - confidence_level: CI width (0.95 = 95%)
    """
    try:
        models = TimeSeriesModels()
        data_array = np.array(data.data)
        
        result = models.arima_forecast(
            data=data_array,
            order=(data.order_p, data.order_d, data.order_q),
            steps=data.steps,
            confidence_level=data.confidence_level
        )
        
        return ARIMAResponse(
            forecast=result.forecast.tolist(),
            confidence_interval_lower=result.confidence_interval_lower.tolist(),
            confidence_interval_upper=result.confidence_interval_upper.tolist(),
            order=list(result.order),
            aic=float(result.aic),
            bic=float(result.bic),
            compute_time_ms=result.compute_time_ms
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        raise ValueError(f"ARIMA forecasting failed: {str(e)}")


@router.post("/garch-volatility", response=GARCHResponse)
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['analytics'], key_prefix="quantitative")
def garch_volatility_forecast(request, data: GARCHRequest):
    """
    GARCH(1,1) volatility forecasting.
    
    Parameters:
    - returns: Financial returns series
    - omega, alpha, beta: GARCH parameters (auto-estimated if None)
    - steps: Forecast horizon
    
    Returns:
    - Conditional volatility time series
    - Forecasted volatility level
    - Model parameters
    """
    try:
        models = TimeSeriesModels()
        returns_array = np.array(data.returns)
        
        result = models.garch11_forecast(
            data=returns_array,
            omega=data.omega if data.omega else 0.0001,
            alpha=data.alpha if data.alpha else 0.05,
            beta=data.beta if data.beta else 0.90,
            steps=data.steps
        )
        
        return GARCHResponse(
            conditional_volatility=result.conditional_volatility.tolist(),
            forecast_volatility=float(result.forecast_volatility),
            omega=float(result.omega),
            alpha=float(result.alpha),
            beta=float(result.beta),
            total_volatility=float(result.total_volatility),
            compute_time_ms=result.compute_time_ms
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        raise ValueError(f"GARCH forecasting failed: {str(e)}")


@router.post("/kalman-filter", response=KalmanFilterResponse)
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['analytics'], key_prefix="quantitative")
def run_kalman_filter(request, data: KalmanFilterRequest):
    """
    Kalman filter for dynamic state estimation.
    
    Tracks the underlying "true" state of a time series while
    filtering out observation noise.
    
    Parameters:
    - observations: Noisy observation sequence
    - state_dim: State dimension
    - process_noise: Process noise covariance
    - observation_noise: Observation noise covariance
    """
    try:
        models = TimeSeriesModels()
        obs_array = np.array(data.observations)
        
        result = models.kalman_filter(
            observations=obs_array,
            state_dim=data.state_dim,
            process_noise=data.process_noise,
            observation_noise=data.observation_noise
        )
        
        # Extract diagonal of covariance matrices
        cov_diag = [result.filtered_covariance[i, i] if result.filtered_covariance.ndim == 2 else 0 
                   for i in range(len(result.filtered_state))]
        
        return KalmanFilterResponse(
            filtered_state=result.filtered_state.flatten().tolist(),
            filtered_covariance_diag=cov_diag,
            predicted_state=result.predicted_state.flatten().tolist(),
            likelihood=float(result.likelihood),
            compute_time_ms=result.compute_time_ms
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        raise ValueError(f"Kalman filter failed: {str(e)}")


@router.post("/half-life", response=HalfLifeResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="quantitative")
def calculate_half_life(request, data: HalfLifeRequest):
    """
    Calculate mean reversion half-life.
    
    Measures how long it takes for a price series to revert
    halfway to its mean after a shock.
    
    Returns:
    - half_life: Days to mean reversion (half)
    - hurst_exponent: H < 0.5 = mean reverting, H > 0.5 = trending
    """
    try:
        models = TimeSeriesModels()
        prices_array = np.array(data.prices)
        
        result = models.calculate_half_life(prices_array, data.lookback)
        
        return HalfLifeResponse(
            half_life=float(result.half_life),
            Hurst_exponent=float(result.hurst_exponent),
            mean_reversion_strength=result.mean_reversion_strength,
            compute_time_ms=result.compute_time_ms
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        raise ValueError(f"Half-life calculation failed: {str(e)}")


@router.post("/hurst-exponent", response=HurstExponentResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="quantitative")
def calculate_hurst_exponent(request, data: HurstExponentRequest):
    """
    Estimate Hurst exponent using R/S analysis.
    
    Interpretation:
    - H < 0.5: Mean-reverting (anti-persistent)
    - H = 0.5: Random walk (Brownian motion)
    - H > 0.5: Trending (persistent)
    """
    try:
        models = TimeSeriesModels()
        data_array = np.array(data.data)
        
        result = models.estimate_hurst_exponent(data_array, data.max_scale)
        
        return HurstExponentResponse(
            hurst_exponent=float(result.hurst_exponent),
            trend_type=result.trend_type,
            interpretation=result.interpretation,
            compute_time_ms=result.compute_time_ms
        )
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        raise ValueError(f"Hurst exponent estimation failed: {str(e)}")


@router.get("/volatility-regimes")
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['analytics'], key_prefix="quantitative")
def detect_volatility_regimes(
    request,
    returns: str = Query(..., description="Comma-separated returns"),
    threshold_low: float = Query(default=0.5, ge=0, description="Low volatility threshold"),
    threshold_high: float = Query(default=1.5, ge=0, description="High volatility threshold")
):
    """
    Detect volatility regimes (low/normal/high).
    
    Classifies each period into volatility regimes based on
    annualized volatility levels.
    """
    try:
        import numpy as np
        from dataclasses import dataclass
        
        returns_list = [float(x.strip()) for x in returns.split(',')]
        returns_array = np.array(returns_list)
        
        # Calculate rolling volatility (annualized)
        vol = np.std(returns_array) * np.sqrt(252) * 100
        
        # Classify regimes
        regimes = []
        current_regime = "normal"
        
        for i, r in enumerate(returns_array):
            period_vol = abs(r) * np.sqrt(252) * 100
            
            if period_vol < threshold_low:
                regime = "low"
            elif period_vol > threshold_high:
                regime = "high"
            else:
                regime = "normal"
            
            regimes.append({
                "index": i,
                "return": r,
                "volatility": round(period_vol, 2),
                "regime": regime
            })
            current_regime = regime
        
        # Summary
        regime_counts = {
            "low": sum(1 for r in regimes if r["regime"] == "low"),
            "normal": sum(1 for r in regimes if r["regime"] == "normal"),
            "high": sum(1 for r in regimes if r["regime"] == "high")
        }
        
        return {
            "regimes": regimes,
            "summary": regime_counts,
            "current_regime": current_regime,
            "thresholds": {
                "low": threshold_low,
                "high": threshold_high
            },
            "overall_volatility": round(vol, 2)
        }
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        raise ValueError(f"Volatility regime detection failed: {str(e)}")


def get_time_series_models() -> TimeSeriesModels:
    """Get singleton time series models instance."""
    return TimeSeriesModels()
