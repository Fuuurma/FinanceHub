"""
Advanced Options Pricing API
High-performance options analytics with Black-Scholes model and Greeks.
"""
from typing import List, Union, Optional
from decimal import Decimal
from ninja import Router, Query
from pydantic import BaseModel, Field

from utils.services.pricing.black_scholes import get_black_scholes_pricer, BlackScholesResult
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint
from core.exceptions import ValidationException

router = Router(tags=["Options Pricing"])


class OptionPriceRequest(BaseModel):
    """Request for single option pricing."""
    underlying_price: float = Field(..., gt=0, description="Current underlying asset price")
    strike_price: float = Field(..., gt=0, description="Option strike price")
    time_to_expiration: float = Field(..., gt=0, description="Time to expiration in years")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    volatility: float = Field(..., gt=0, description="Annualized volatility (as decimal, e.g., 0.20 for 20%)")
    option_type: str = Field(default="call", description="Option type: 'call' or 'put'")


class GreeksResponse(BaseModel):
    """Greeks response with all sensitivities."""
    price: float
    delta: float = Field(..., description="Price sensitivity to underlying price")
    gamma: float = Field(..., description="Rate of change of delta")
    vega: float = Field(..., description="Sensitivity to volatility")
    theta: float = Field(..., description="Time decay (per day)")
    rho: float = Field(..., description="Sensitivity to interest rate")


class OptionPriceResponse(BaseModel):
    """Response for option pricing."""
    underlying_price: float
    strike_price: float
    time_to_expiration: float
    option_type: str
    price: float
    greeks: GreeksResponse
    computed_in_ms: float


class BatchPriceRequest(BaseModel):
    """Request for batch option pricing."""
    underlying_prices: List[float] = Field(..., min_length=1, description="List of underlying prices")
    strikes: List[float] = Field(..., min_length=1, description="List of strike prices")
    expirations: List[float] = Field(..., min_length=1, description="List of expirations in years")
    volatilities: List[float] = Field(..., min_length=1, description="List of volatilities")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    option_type: str = Field(default="call", description="Option type: 'call' or 'put'")


class BatchPriceResponse(BaseModel):
    """Response for batch pricing."""
    results: List[dict] = Field(..., description="Pricing results for each combination")
    total_calculations: int = Field(..., description="Total number of options priced")
    computed_in_ms: float


class ImpliedVolatilityRequest(BaseModel):
    """Request for implied volatility calculation."""
    market_price: float = Field(..., gt=0, description="Observed market price")
    underlying_price: float = Field(..., gt=0, description="Current underlying price")
    strike_price: float = Field(..., gt=0, description="Option strike price")
    time_to_expiration: float = Field(..., gt=0, description="Time to expiration in years")
    risk_free_rate: float = Field(default=0.03, ge=0, description="Annualized risk-free rate")
    option_type: str = Field(default="call", description="Option type: 'call' or 'put'")
    max_iterations: int = Field(default=100, ge=1, le=500, description="Maximum Newton-Raphson iterations")
    tolerance: float = Field(default=1e-6, gt=0, description="Convergence tolerance")


class ImpliedVolatilityResponse(BaseModel):
    """Response for implied volatility."""
    market_price: float
    implied_volatility: float = Field(..., description="Implied volatility (as decimal)")
    iterations: int = Field(..., description="Iterations to converge")
    computed_in_ms: float


@router.post("/price", response=OptionPriceResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="options")
def price_option(request, data: OptionPriceRequest):
    """Price a single option using Black-Scholes model.

    Returns option price and all Greeks (Delta, Gamma, Vega, Theta, Rho).
    """
    if data.option_type not in ['call', 'put']:
        raise ValidationException(
            f"Invalid option_type '{data.option_type}'. Must be 'call' or 'put'",
            {"valid_types": ['call', 'put']}
        )
    
    pricer = get_black_scholes_pricer()
    result: BlackScholesResult = pricer.calculate_greeks(
        S=data.underlying_price,
        K=data.strike_price,
        T=data.time_to_expiration,
        r=data.risk_free_rate,
        sigma=data.volatility,
        option_type=data.option_type
    )
    
    # Extract scalar values from arrays
    price = float(result.prices.item()) if result.prices.ndim > 0 else float(result.prices)
    delta = float(result.deltas.item()) if result.deltas.ndim > 0 else float(result.deltas)
    gamma = float(result.gammas.item()) if result.gammas.ndim > 0 else float(result.gammas)
    vega = float(result.vegas.item()) if result.vegas.ndim > 0 else float(result.vegas)
    theta = float(result.thetas.item()) if result.thetas.ndim > 0 else float(result.thetas)
    rho = float(result.rhos.item()) if result.rhos.ndim > 0 else float(result.rhos)
    
    return OptionPriceResponse(
        underlying_price=data.underlying_price,
        strike_price=data.strike_price,
        time_to_expiration=data.time_to_expiration,
        option_type=data.option_type,
        price=price,
        greeks=GreeksResponse(
            price=price,
            delta=delta,
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho=rho
        ),
        computed_in_ms=result.compute_time_ms
    )


@router.post("/batch-price", response=BatchPriceResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['data_intensive'], key_prefix="options")
def price_options_batch(request, data: BatchPriceRequest):
    """Price multiple options in batch for performance.

    Efficiently prices all combinations of:
    - Multiple underlying prices
    - Multiple strikes
    - Multiple expirations
    - Multiple volatilities

    Returns flattened results with full metadata.
    """
    if data.option_type not in ['call', 'put']:
        raise ValidationException(
            f"Invalid option_type '{data.option_type}'. Must be 'call' or 'put'",
            {"valid_types": ['call', 'put']}
        )
    
    # Convert to NumPy arrays
    import numpy as np
    underlying_prices = np.array(data.underlying_prices, dtype=np.float64)
    strikes = np.array(data.strikes, dtype=np.float64)
    expirations = np.array(data.expirations, dtype=np.float64)
    volatilities = np.array(data.volatilities, dtype=np.float64)
    
    pricer = get_black_scholes_pricer()
    result: BlackScholesResult = pricer.price_batch(
        underlying_prices=underlying_prices,
        strikes=strikes,
        expirations=expirations,
        r=data.risk_free_rate,
        volatilities=volatilities,
        option_type=data.option_type
    )
    
    # Flatten results into list of dictionaries
    results = []
    total_calculations = 0
    
    shape = result.prices.shape
    for i, S in enumerate(data.underlying_prices):
        for j, K in enumerate(data.strikes):
            for k, T in enumerate(data.expirations):
                for l, sigma in enumerate(data.volatilities):
                    idx = (i, j, k, l)
                    total_calculations += 1
                    
                    results.append({
                        "underlying_price": S,
                        "strike_price": K,
                        "expiration": T,
                        "volatility": sigma,
                        "option_type": data.option_type,
                        "price": float(result.prices[idx]),
                        "delta": float(result.deltas[idx]),
                        "gamma": float(result.gammas[idx]),
                        "vega": float(result.vegas[idx]),
                        "theta": float(result.thetas[idx]),
                        "rho": float(result.rhos[idx])
                    })
    
    return BatchPriceResponse(
        results=results,
        total_calculations=total_calculations,
        computed_in_ms=result.compute_time_ms
    )


@router.post("/implied-volatility", response=ImpliedVolatilityResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="options")
def calculate_implied_volatility(request, data: ImpliedVolatilityRequest):
    """Calculate implied volatility from market price using Newton-Raphson.

    Iteratively solves for volatility that yields the observed market price.
    """
    if data.option_type not in ['call', 'put']:
        raise ValidationException(
            f"Invalid option_type '{data.option_type}'. Must be 'call' or 'put'",
            {"valid_types": ['call', 'put']}
        )
    
    pricer = get_black_scholes_pricer()
    
    # Handle single values vs arrays
    market_price = data.market_price
    S = data.underlying_price
    K = data.strike_price
    T = data.time_to_expiration
    
    iv = pricer.implied_volatility(
        market_price=market_price,
        S=S,
        K=K,
        T=T,
        r=data.risk_free_rate,
        option_type=data.option_type,
        max_iterations=data.max_iterations,
        tolerance=data.tolerance
    )
    
    # Extract scalar if array
    iv_value = float(iv.item()) if hasattr(iv, 'item') else float(iv)
    
    return ImpliedVolatilityResponse(
        market_price=market_price,
        implied_volatility=iv_value,
        iterations=data.max_iterations,
        computed_in_ms=0  # Not tracked in current implementation
    )


@router.get("/greeks", response=GreeksResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="options")
def get_greeks(
    request,
    underlying_price: float = Query(..., gt=0, description="Current underlying asset price"),
    strike_price: float = Query(..., gt=0, description="Option strike price"),
    time_to_expiration: float = Query(..., gt=0, description="Time to expiration in years"),
    risk_free_rate: float = Query(default=0.03, ge=0, description="Annualized risk-free rate"),
    volatility: float = Query(..., gt=0, description="Annualized volatility"),
    option_type: str = Query(default="call", description="Option type: 'call' or 'put'")
):
    """Calculate all Greeks for an option.

    Returns Delta, Gamma, Vega, Theta, and Rho in a single call.
    """
    if option_type not in ['call', 'put']:
        raise ValidationException(
            f"Invalid option_type '{option_type}'. Must be 'call' or 'put'",
            {"valid_types": ['call', 'put']}
        )
    
    pricer = get_black_scholes_pricer()
    result: BlackScholesResult = pricer.calculate_greeks(
        S=underlying_price,
        K=strike_price,
        T=time_to_expiration,
        r=risk_free_rate,
        sigma=volatility,
        option_type=option_type
    )
    
    # Extract scalar values
    price = float(result.prices.item()) if result.prices.ndim > 0 else float(result.prices)
    delta = float(result.deltas.item()) if result.deltas.ndim > 0 else float(result.deltas)
    gamma = float(result.gammas.item()) if result.gammas.ndim > 0 else float(result.gammas)
    vega = float(result.vegas.item()) if result.vegas.ndim > 0 else float(result.vegas)
    theta = float(result.thetas.item()) if result.thetas.ndim > 0 else float(result.thetas)
    rho = float(result.rhos.item()) if result.rhos.ndim > 0 else float(result.rhos)
    
    return GreeksResponse(
        price=price,
        delta=delta,
        gamma=gamma,
        vega=vega,
        theta=theta,
        rho=rho
    )
