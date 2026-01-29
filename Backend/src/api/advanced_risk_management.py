"""
Advanced Risk Management API
Provides endpoints for VaR, stress testing, and risk analysis.
"""
from typing import List, Optional, Dict
from ninja import Router, Query, Field
from pydantic import BaseModel

from utils.services.risk.advanced_risk_management import get_risk_manager
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint
from core.exceptions import ValidationException

router = Router(tags=["Advanced Risk Management"])


class VaRRequest(BaseModel):
    """Request for VaR calculation."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    weights: List[float] = Field(..., description="Portfolio weights")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    confidence_level: float = Field(default=0.95, ge=0.9, le=0.99, description="Confidence level")
    n_simulations: int = Field(default=10000, ge=1000, le=50000, description="Number of Monte Carlo simulations")


class VaRResponse(BaseModel):
    """Response for VaR calculation."""
    var_95: float = Field(..., description="95% VaR")
    var_99: float = Field(..., description="99% VaR")
    expected_shortfall_95: float = Field(..., description="95% CVaR")
    expected_shortfall_99: float = Field(..., description="99% CVaR")
    method: str = Field(..., description="Calculation method")
    confidence_level: float = Field(..., description="Confidence level")
    n_scenarios: int = Field(..., description="Number of scenarios")
    computed_in_ms: float


class StressTestRequest(BaseModel):
    """Request for historical stress testing."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    weights: List[float] = Field(..., description="Portfolio weights")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    scenarios: List[Dict[str, float]] = Field(..., description="Stress scenarios")


class StressTestResponse(BaseModel):
    """Response for stress testing."""
    stress_scenarios: Dict[str, Dict[str, float]]
    worst_case_scenario: str
    worst_case_loss: float
    computed_in_ms: float


class FactorStressTestRequest(BaseModel):
    """Request for factor-based stress testing."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    weights: List[float] = Field(..., description="Portfolio weights")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")


class FactorStressTestResponse(BaseModel):
    """Response for factor stress testing."""
    factor_shocks: Dict[str, float]
    portfolio_impact: Dict[str, float]
    worst_factor: str
    worst_impact: float
    computed_in_ms: float


class ComprehensiveRiskAnalysisRequest(BaseModel):
    """Request for comprehensive risk analysis."""
    returns: List[List[float]] = Field(..., description="Historical returns matrix")
    weights: List[float] = Field(..., description="Portfolio weights")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    confidence_level: float = Field(default=0.95, ge=0.9, le=0.99, description="Confidence level")
    n_simulations: int = Field(default=10000, ge=1000, le=50000, description="Number of Monte Carlo simulations")
    stress_scenarios: Optional[List[Dict[str, float]] = Field(None, description="Stress scenarios")


@router.post("/var", response=VaRResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="risk")
def calculate_var(request, data: VaRRequest):
    """Calculate VaR and CVaR for a portfolio.

    Supports parametric, historical, and Monte Carlo methods.
    Returns VaR at multiple confidence levels and expected shortfall.
    """
    import numpy as np
    
    # Validate inputs
    if len(data.weights) != len(data.returns[0]):
        raise ValidationException(
            f"Weights length ({len(data.weights)}) must equal number of assets ({len(data.returns[0])})",
            {"weights_count": len(data.weights), "assets_count": len(data.returns[0])}
        )
    
    if data.confidence_level < 0.9 or data.confidence_level > 0.99:
        raise ValidationException(
            f"Confidence level must be between 0.9 and 0.99, got {data.confidence_level}",
            {"valid_range": [0.9, 0.99]}
        )
    
    returns_array = np.array(data.returns)
    weights_array = np.array(data.weights)
    
    # Get risk manager and calculate VaR
    risk_manager = get_risk_manager(returns_array, weights_array, data.risk_free_rate)
    result = risk_manager.monte_carlo_var(
        confidence_levels=[data.confidence_level],
        n_simulations=data.n_simulations
    )
    
    return VaRResponse(
        var_95=float(result.var_95),
        var_99=float(result.var_99),
        expected_shortfall_95=float(result.expected_shortfall_95),
        expected_shortfall_99=float(result.expected_shortfall_99),
        method=result.method,
        confidence_level=float(result.confidence_level),
        n_scenarios=int(result.n_scenarios),
        computed_in_ms=float(result.compute_time_ms)
    )


@router.post("/stress-test", response=StressTestResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="risk")
def stress_test(request, data: StressTestRequest):
    """Historical stress testing of portfolio.

    Tests portfolio performance under extreme market scenarios.
    Returns impact analysis and worst case identification.
    """
    import numpy as np
    
    if len(data.weights) != len(data.returns[0]):
        raise ValidationException(
            f"Weights length ({len(data.weights)}) must equal number of assets ({len(data.returns[0])})",
            {"weights_count": len(data.weights), "assets_count": len(data.returns[0])}
        )
    
    if len(data.scenarios) == 0:
        raise ValidationException(
            "At least one stress scenario required",
            {"min_scenarios": 1}
        )
    
    returns_array = np.array(data.returns)
    weights_array = np.array(data.weights)
    
    # Get risk manager and run stress test
    risk_manager = get_risk_manager(returns_array, weights_array, data.risk_free_rate)
    result = risk_manager.stress_test_historical(data.scenarios)
    
    return StressTestResponse(
        stress_scenarios=result.stress_scenarios,
        worst_case_scenario=result.worst_case_scenario,
        worst_case_loss=float(result.worst_case_loss),
        computed_in_ms=float(result.compute_time_ms)
    )


@router.post("/factor-stress-test", response=FactorStressTestResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="risk")
def factor_stress_test(request, data: FactorStressTestRequest):
    """Factor-based stress testing.

    Tests portfolio sensitivity to factor movements.
    Analyzes equity, size, value, quality, momentum factors.
    """
    import numpy as np
    
    if len(data.weights) != len(data.returns[0]):
        raise ValidationException(
            f"Weights length ({len(data.weights)}) must equal number of assets ({len(data.returns[0])})",
            {"weights_count": len(data.weights), "assets_count": len(data.returns[0])}
        )
    
    returns_array = np.array(data.returns)
    weights_array = np.array(data.weights)
    
    # Get risk manager and run factor stress test
    risk_manager = get_risk_manager(returns_array, weights_array, data.risk_free_rate)
    result = risk_manager.factor_stress_test()
    
    return FactorStressTestResponse(
        factor_shocks=result.factor_shocks,
        portfolio_impact=result.portfolio_impact,
        worst_factor=result.worst_factor,
        worst_impact=float(result.worst_impact),
        computed_in_ms=float(result.compute_time_ms)
    )


@router.post("/comprehensive-risk-analysis", response=dict)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="risk")
def comprehensive_risk_analysis(request, data: ComprehensiveRiskAnalysisRequest):
    """Comprehensive risk analysis combining all methodologies.

    Calculates:
    - Parametric VaR (normal distribution)
    - Historical VaR (empirical)
    - Monte Carlo VaR (simulation)
    - Expected Shortfall (CVaR)
    - Stress testing (historical scenarios)
    - Factor stress testing
    """
    import numpy as np
    
    if len(data.weights) != len(data.returns[0]):
        raise ValidationException(
            f"Weights length ({len(data.weights)}) must equal number of assets ({len(data.returns[0])})",
            {"weights_count": len(data.weights), "assets_count": len(data.returns[0])}
        )
    
    returns_array = np.array(data.returns)
    weights_array = np.array(data.weights)
    
    # Get risk manager and run comprehensive analysis
    risk_manager = get_risk_manager(returns_array, weights_array, data.risk_free_rate)
    
    risk_analysis = risk_manager.comprehensive_risk_analysis(
        confidence_level=data.confidence_level,
        n_simulations=data.n_simulations,
        stress_scenarios=data.stress_scenarios
    )
    
    return risk_analysis


@router.get("/var-historical", response=dict)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="risk")
def get_historical_var(
    request,
    returns: List[List[float]] = Query(..., description="Historical returns matrix"),
    weights: List[float] = Query(..., description="Portfolio weights"),
    risk_free_rate: float = Query(default=0.03, ge=0, description="Annualized risk-free rate"),
    confidence_level: float = Query(default=0.95, ge=0.9, le=0.99, description="Confidence level")
):
    """Get historical VaR (empirical distribution).

    Returns VaR based on actual historical returns.
    """
    import numpy as np
    
    returns_array = np.array(returns)
    weights_array = np.array(weights)
    
    risk_manager = get_risk_manager(returns_array, weights_array, risk_free_rate)
    var = risk_manager.historical_var(confidence_level)
    
    return {
        'var': float(var),
        'method': 'historical',
        'confidence_level': confidence_level
    }


@router.get("/expected-shortfall", response=dict)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="risk")
def get_expected_shortfall(
    request,
    returns: List[List[float]] = Query(..., description="Historical returns matrix"),
    weights: List[float] = Query(..., description="Portfolio weights"),
    risk_free_rate: float = Query(default=0.03, ge=0, description="Annualized risk-free rate"),
    confidence_level: float = Query(default=0.95, ge=0.9, le=0.99, description="Confidence level"),
    n_simulations: int = Query(default=5000, ge=1000, le=50000, description="Number of simulations")
):
    """Get Expected Shortfall (CVaR).

    Returns average loss beyond VaR.
    """
    import numpy as np
    
    returns_array = np.array(returns)
    weights_array = np.array(weights)
    
    risk_manager = get_risk_manager(returns_array, weights_array, risk_free_rate)
    cvar = risk_manager.expected_shortfall(confidence_level, n_simulations)
    
    return {
        'cvar': float(cvar),
        'method': 'monte_carlo',
        'confidence_level': confidence_level,
        'n_simulations': n_simulations
    }
