"""
Fixed Income Analytics API
Bond pricing, yield curves, and fixed income analytics.
"""
from typing import List, Optional, Dict
from decimal import Decimal
from ninja import Router, Query, Field
from pydantic import BaseModel

from utils.services.fixed_income.bond_pricing import get_bond_pricer
from utils.constants.api import RATE_LIMITS, CACHE_TTLS
from utils.api.decorators import api_endpoint
from core.exceptions import ValidationException

router = Router(tags=["Fixed Income Analytics"])


class BondPricingRequest(BaseModel):
    """Request for bond pricing."""
    face_value: float = Field(..., gt=0, description="Face/par value of bond")
    coupon_rate: float = Field(..., ge=0, description="Annual coupon rate (as decimal)")
    yield_rate: float = Field(..., ge=0, description="Yield to maturity (annualized)")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity in years")
    frequency: int = Field(default=1, ge=1, le=4, description="Coupon frequency (1=annual, 2=semiannual, 4=quarterly)")
    price_type: str = Field(default="clean", description="Price type: 'clean' or 'dirty'")


class BondPricingResponse(BaseModel):
    """Response for bond pricing."""
    price: float
    yield_to_maturity: float
    duration: float
    modified_duration: float
    convexity: float
    oas: float
    z_spread: float
    computed_in_ms: float


class ZeroCouponBondRequest(BaseModel):
    """Request for zero-coupon bond pricing."""
    face_value: float = Field(..., gt=0, description="Face value")
    yield_rate: float = Field(..., ge=0, description="Yield to maturity")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity in years")


class ZeroCouponBondResponse(BaseModel):
    """Response for zero-coupon bond."""
    price: float
    yield_to_maturity: float
    time_to_maturity: float
    computed_in_ms: float


class YieldCurveBootstrapRequest(BaseModel):
    """Request for yield curve bootstrapping."""
    bond_prices: List[float] = Field(..., min_length=1, description="Bond prices")
    maturities: List[float] = Field(..., min_length=1, description="Times to maturity (years)")
    frequencies: List[int] = Field(..., min_length=1, description="Coupon frequencies")


class YieldCurveResponse(BaseModel):
    """Response for yield curve bootstrapping."""
    rates: Dict[str, float]
    zero_rates: List[float]
    computed_in_ms: float


class BondCashFlowRequest(BaseModel):
    """Request for bond cash flows."""
    face_value: float = Field(..., gt=0, description="Face/par value")
    coupon_rate: float = Field(..., ge=0, description="Annual coupon rate")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity")
    frequency: int = Field(default=1, ge=1, le=4, description="Coupon frequency")


class BondCashFlowResponse(BaseModel):
    """Response for bond cash flows."""
    cash_flows: List[Dict]
    total_coupons: float
    principal_repayment: float
    pv_coupons: float
    pv_principal: float


class DurationConvexityRequest(BaseModel):
    """Request for duration and convexity."""
    price: float = Field(..., gt=0, description="Bond price")
    yield_rate: float = Field(..., ge=0, description="Yield to maturity")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity")
    frequency: int = Field(default=1, ge=1, le=4, description="Coupon frequency")


class DurationConvexityResponse(BaseModel):
    """Response for duration and convexity."""
    macaulay_duration: float
    modified_duration: float
    convexity: float
    price_change_1bp_up: float
    price_change_1bp_down: float


@router.post("/price", response=BondPricingResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="fixed_income")
def price_bond(request, data: BondPricingRequest):
    """Price a fixed-rate bond with full analytics.

    Returns clean price, duration, convexity, OAS, and Z-spread.
    """
    if data.price_type not in ['clean', 'dirty']:
        raise ValidationException(
            f"Invalid price_type '{data.price_type}'. Must be 'clean' or 'dirty'",
            {"valid_types": ['clean', 'dirty']}
        )
    
    if data.frequency not in [1, 2, 4]:
        raise ValidationException(
            f"Invalid frequency {data.frequency}. Must be 1 (annual), 2 (semiannual), or 4 (quarterly)",
            {"valid_frequencies": [1, 2, 4]}
        )
    
    pricer = get_bond_pricer()
    
    result = pricer.comprehensive_bond_analysis(
        face_value=data.face_value,
        coupon_rate=data.coupon_rate,
        yield_rate=data.yield_rate,
        time_to_maturity=data.time_to_maturity,
        frequency=data.frequency,
        price_type=data.price_type
    )
    
    return BondPricingResponse(
        price=float(result.price),
        yield_to_maturity=float(result.yield_to_maturity),
        duration=float(result.duration),
        modified_duration=float(result.modified_duration),
        convexity=float(result.convexity),
        oas=float(result.oas),
        z_spread=float(result.z_spread),
        computed_in_ms=result.compute_time_ms
    )


@router.post("/zero-coupon", response=ZeroCouponBondResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="fixed_income")
def price_zero_coupon(request, data: ZeroCouponBondRequest):
    """Price a zero-coupon bond.

    Zero-coupon bonds are priced as: Price = Face Value / (1 + y * T)
    """
    pricer = get_bond_pricer()
    
    price = pricer.price_zero_coupon_bond(
        face_value=data.face_value,
        yield_rate=data.yield_rate,
        time_to_maturity=data.time_to_maturity
    )
    
    return ZeroCouponBondResponse(
        price=float(price),
        yield_to_maturity=data.yield_rate,
        time_to_maturity=data.time_to_maturity,
        computed_in_ms=0
    )


@router.post("/yield-curve", response=YieldCurveResponse)
@api_endpoint(ttl=CACHE_TTLS['medium'], rate=RATE_LIMITS['data_intensive'], key_prefix="fixed_income")
def bootstrap_yield_curve(request, data: YieldCurveBootstrapRequest):
    """Bootstrap yield curve from bond prices.

    Uses bond prices to derive zero rates and spot curve.
    """
    if len(data.bond_prices) != len(data.maturities):
        raise ValidationException(
            f"Length mismatch: bond_prices ({len(data.bond_prices)}) != maturities ({len(data.maturities)})",
            {"prices_count": len(data.bond_prices), "maturities_count": len(data.maturities)}
        )
    
    if len(data.bond_prices) != len(data.frequencies):
        raise ValidationException(
            f"Length mismatch: bond_prices ({len(data.bond_prices)}) != frequencies ({len(data.frequencies)})",
            {"prices_count": len(data.bond_prices), "frequencies_count": len(data.frequencies)}
        )
    
    pricer = get_bond_pricer()
    
    result = pricer.bootstrap_yield_curve(
        bond_prices=data.bond_prices,
        maturities=data.maturities,
        frequencies=data.frequencies
    )
    
    return YieldCurveResponse(
        rates=result.rates,
        zero_rates=result.zero_rates,
        computed_in_ms=result.compute_time_ms
    )


@router.post("/cash-flows", response=BondCashFlowResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="fixed_income")
def get_cash_flows(request, data: BondCashFlowRequest):
    """Generate bond cash flows schedule.

    Returns all coupon payments and principal repayment.
    """
    pricer = get_bond_pricer()
    
    cash_flows = pricer.calculate_cash_flows(
        face_value=data.face_value,
        coupon_rate=data.coupon_rate,
        time_to_maturity=data.time_to_maturity,
        frequency=data.frequency
    )
    
    total_coupons = sum(cf.amount for cf in cash_flows[:-1])  # Exclude principal
    principal_repayment = cash_flows[-1].amount
    
    # Calculate present values
    discount_rate = data.coupon_rate / 2  # Simplified
    pv_coupons = sum(cf.amount * cf.discount_factor for cf in cash_flows[:-1])
    pv_principal = cash_flows[-1].amount * cash_flows[-1].discount_factor
    
    return BondCashFlowResponse(
        cash_flows=[
            {
                "time_years": cf.time,
                "amount": cf.amount,
                "discount_factor": cf.discount_factor
            }
            for cf in cash_flows
        ],
        total_coupons=float(total_coupons),
        principal_repayment=float(principal_repayment),
        pv_coupons=float(pv_coupons),
        pv_principal=float(pv_principal)
    )


@router.post("/duration-convexity", response=DurationConvexityResponse)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="fixed_income")
def calculate_duration_convexity(request, data: DurationConvexityRequest):
    """Calculate bond duration and convexity.

    Returns Macaulay duration, modified duration, and convexity.
    Also shows price change for 1bp yield movement.
    """
    if data.frequency not in [1, 2, 4]:
        raise ValidationException(
            f"Invalid frequency {data.frequency}. Must be 1, 2, or 4",
            {"valid_frequencies": [1, 2, 4]}
        )
    
    pricer = get_bond_pricer()
    
    duration = pricer.calculate_duration(
        price=data.price,
        yield_rate=data.yield_rate,
        time_to_maturity=data.time_to_maturity,
        frequency=data.frequency
    )
    
    modified_duration = pricer.calculate_modified_duration(
        duration=duration,
        yield_rate=data.yield_rate,
        time_to_maturity=data.time_to_maturity
    )
    
    convexity = pricer.calculate_convexity(
        duration=duration,
        yield_rate=data.yield_rate,
        time_to_maturity=data.time_to_maturity,
        frequency=data.frequency
    )
    
    # Price change for 1bp move
    price_change_up = -modified_duration * 0.0001 * data.price
    price_change_down = modified_duration * 0.0001 * data.price
    
    return DurationConvexityResponse(
        macaulay_duration=float(duration),
        modified_duration=float(modified_duration),
        convexity=float(convexity),
        price_change_1bp_up=float(price_change_up),
        price_change_1bp_down=float(price_change_down)
    )


@router.get("/oas", response=dict)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="fixed_income")
def calculate_oas(
    request,
    price: float = Query(..., gt=0, description="Bond price"),
    yield_rate: float = Query(..., ge=0, description="Yield to maturity"),
    time_to_maturity: float = Query(..., gt=0, description="Time to maturity"),
    frequency: int = Query(default=1, ge=1, le=4, description="Coupon frequency")
):
    """Calculate Option-Adjusted Spread (OAS).

    Measures spread due to embedded options.
    """
    pricer = get_bond_pricer()
    
    oas = pricer.calculate_oas(
        price=price,
        yield_rate=yield_rate,
        time_to_maturity=time_to_maturity,
        frequency=frequency
    )
    
    return {
        "oas": float(oas),
        "method": "simplified_oas",
        "interpretation": f"Spread over risk-free curve due to options: {oas:.4f}"
    }


@router.get("/z-spread", response=dict)
@api_endpoint(ttl=CACHE_TTLS['short'], rate=RATE_LIMITS['analytics'], key_prefix="fixed_income")
def calculate_z_spread(
    request,
    price: float = Query(..., gt=0, description="Bond price"),
    yield_rate: float = Query(..., ge=0, description="Yield to maturity"),
    time_to_maturity: float = Query(..., gt=0, description="Time to maturity"),
    frequency: int = Query(default=1, ge=1, le=4, description="Coupon frequency")
):
    """Calculate Z-spread.

    Measures spread over the risk-free yield curve.
    """
    pricer = get_bond_pricer()
    
    z_spread = pricer.calculate_z_spread(
        price=price,
        yield_rate=yield_rate,
        time_to_maturity=time_to_maturity,
        frequency=frequency
    )
    
    return {
        "z_spread": float(z_spread),
        "method": "z_spread",
        "interpretation": f"Constant spread over spot curve: {z_spread:.4f}"
    }
