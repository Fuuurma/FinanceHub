from decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional
from ninja import Router
from pydantic import BaseModel, Field
from investments.services.bond_calculator_service import (
    BondCalculatorService,
    BondType,
    CouponFrequency,
)

router = Router()

service = BondCalculatorService()


class BondCalculationInput(BaseModel):
    face_value: Decimal = Field(..., description="Face/par value of the bond")
    coupon_rate: Decimal = Field(
        ..., description="Annual coupon rate as decimal (0.05 = 5%)"
    )
    current_price: Decimal = Field(..., description="Current market price")
    years_to_maturity: Optional[Decimal] = Field(None, description="Years to maturity")
    years_to_call: Optional[Decimal] = Field(
        None, description="Years until bond can be called"
    )
    call_price: Optional[Decimal] = Field(
        None, description="Price at which bond can be called"
    )
    coupon_frequency: str = Field("annual", description="Coupon payment frequency")
    bond_type: str = Field("fixed", description="Type of bond")


class BondCalculationResponse(BaseModel):
    current_yield: Optional[Decimal] = None
    yield_to_maturity: Optional[Decimal] = None
    yield_to_call: Optional[Decimal] = None
    zero_coupon_yield: Optional[Decimal] = None
    treasury_yield: Optional[Decimal] = None
    bond_price: Optional[Decimal] = None
    macaulay_duration: Optional[Decimal] = None
    modified_duration: Optional[Decimal] = None
    convexity: Optional[Decimal] = None
    annual_coupon: Optional[Decimal] = None
    coupon_payment: Optional[Decimal] = None
    years_to_maturity: Optional[Decimal] = None


class CurrentYieldInput(BaseModel):
    face_value: Decimal
    coupon_rate: Decimal
    current_price: Decimal


class CurrentYieldResponse(BaseModel):
    current_yield: Decimal


class YTMInput(BaseModel):
    face_value: Decimal
    coupon_rate: Decimal
    current_price: Decimal
    years_to_maturity: Decimal


class YTMResponse(BaseModel):
    yield_to_maturity: Decimal


class ZeroCouponInput(BaseModel):
    face_value: Decimal
    current_price: Decimal
    years_to_maturity: Decimal


class ZeroCouponResponse(BaseModel):
    zero_coupon_yield: Decimal


class TreasuryBillInput(BaseModel):
    face_value: Decimal
    current_price: Decimal
    days_to_maturity: int


class TreasuryBillResponse(BaseModel):
    treasury_yield: Decimal


class BondComparisonInput(BaseModel):
    bonds: List[BondCalculationInput]


class BondComparisonResponse(BaseModel):
    comparisons: List[dict]
    recommendations: List[str]


@router.get("/types")
def get_bond_types(request):
    """Get supported bond types and coupon frequencies."""
    return {
        "bond_types": [
            {"value": "treasury", "label": "Treasury Bond"},
            {"value": "treasury_note", "label": "Treasury Note"},
            {"value": "treasury_bill", "label": "Treasury Bill"},
            {"value": "corporate", "label": "Corporate Bond"},
            {"value": "municipal", "label": "Municipal Bond"},
            {"value": "agency", "label": "Agency Bond"},
            {"value": "zero_coupon", "label": "Zero-Coupon Bond"},
            {"value": "floating_rate", "label": "Floating Rate Note"},
            {"value": "perpetual", "label": "Perpetual Bond"},
        ],
        "coupon_frequencies": [
            {"value": "annual", "label": "Annual (1 payment/year)"},
            {"value": "semiannual", "label": "Semi-Annual (2 payments/year)"},
            {"value": "quarterly", "label": "Quarterly (4 payments/year)"},
            {"value": "monthly", "label": "Monthly (12 payments/year)"},
        ],
    }


@router.get("/formulas")
def get_formulas(request):
    """Get bond yield calculation formulas."""
    return {
        "formulas": [
            {
                "name": "Current Yield",
                "formula": "CY = Annual Coupon / Current Price",
                "description": "Measures the annual return on a bond if held to maturity, ignoring capital gains/losses.",
            },
            {
                "name": "Yield to Maturity (YTM)",
                "formula": "Price = Σ(Coupon / (1+y)^t) + Face / (1+y)^n",
                "description": "The total return anticipated if held to maturity, solving for y.",
            },
            {
                "name": "Macaulay Duration",
                "formula": "D = Σ(t × PV(CF)) / Price",
                "description": "Weighted average time until cash flows are received.",
            },
            {
                "name": "Modified Duration",
                "formula": "MD = D / (1 + y/f)",
                "description": "Measure of price sensitivity to interest rate changes.",
            },
            {
                "name": "Convexity",
                "formula": "C = Σ(t × (t+1) × PV(CF)) / (Price × (1+y)²)",
                "description": "Measures the curvature of the price-yield relationship.",
            },
        ]
    }


@router.post("/calculate", response=BondCalculationResponse)
def calculate_bond_metrics(request, input: BondCalculationInput):
    """Calculate all bond metrics including yield, duration, and convexity."""
    freq_map = {
        "annual": CouponFrequency.ANNUAL,
        "semiannual": CouponFrequency.SEMIANNUAL,
        "quarterly": CouponFrequency.QUARTERLY,
        "monthly": CouponFrequency.MONTHLY,
    }
    frequency = freq_map.get(input.coupon_frequency, CouponFrequency.ANNUAL)

    bond_type = BondType(input.bond_type) if input.bond_type else BondType.FIXED

    result = service.calculate_all(
        face_value=input.face_value,
        coupon_rate=input.coupon_rate,
        current_price=input.current_price,
        years_to_maturity=input.years_to_maturity or Decimal("10"),
        coupon_frequency=frequency,
        bond_type=bond_type,
    )

    return {
        "current_yield": result.current_yield,
        "yield_to_maturity": result.yield_to_maturity,
        "yield_to_call": result.yield_to_call,
        "zero_coupon_yield": result.zero_coupon_yield,
        "treasury_yield": result.treasury_yield,
        "bond_price": result.bond_price,
        "macaulay_duration": result.macaulay_duration,
        "modified_duration": result.modified_duration,
        "convexity": result.convexity,
        "annual_coupon": service.current_yield(
            input.face_value, input.coupon_rate, input.face_value
        )
        * input.face_value,
        "coupon_payment": (input.face_value * input.coupon_rate)
        / Decimal(frequency.value),
        "years_to_maturity": input.years_to_maturity,
    }


@router.post("/calculate/current-yield", response=CurrentYieldResponse)
def calculate_current_yield(request, input: CurrentYieldInput):
    """Calculate the current yield of a bond."""
    result = service.current_yield(
        face_value=input.face_value,
        coupon_rate=input.coupon_rate,
        current_price=input.current_price,
    )
    return {"current_yield": result}


@router.post("/calculate/ytm", response=YTMResponse)
def calculate_ytm(request, input: YTMInput):
    """Calculate yield to maturity."""
    result = service.yield_to_maturity(
        face_value=input.face_value,
        coupon_rate=input.coupon_rate,
        current_price=input.current_price,
        years_to_maturity=input.years_to_maturity,
    )
    return {"yield_to_maturity": result}


@router.post("/calculate/zero-coupon", response=ZeroCouponResponse)
def calculate_zero_coupon_yield(request, input: ZeroCouponInput):
    """Calculate yield for zero-coupon bonds."""
    result = service.zero_coupon_yield(
        face_value=input.face_value,
        current_price=input.current_price,
        years_to_maturity=input.years_to_maturity,
    )
    return {"zero_coupon_yield": result}


@router.post("/calculate/treasury", response=TreasuryBillResponse)
def calculate_treasury_yield(request, input: TreasuryBillInput):
    """Calculate Treasury bill yield."""
    result = service.treasury_bill_yield(
        face_value=input.face_value,
        current_price=input.current_price,
        days_to_maturity=input.days_to_maturity,
    )
    return {"treasury_yield": result}


@router.post("/compare", response=BondComparisonResponse)
def compare_bonds(request, input: BondComparisonInput):
    """Compare multiple bonds and provide recommendations."""
    comparisons = []
    recommendations = []

    for i, bond in enumerate(input.bonds):
        result = service.calculate_all(
            face_value=bond.face_value,
            coupon_rate=bond.coupon_rate,
            current_price=bond.current_price,
            years_to_maturity=bond.years_to_maturity or Decimal("10"),
        )

        comparisons.append(
            {
                "index": i + 1,
                "face_value": str(bond.face_value),
                "coupon_rate": str(bond.coupon_rate),
                "current_yield": str(result.current_yield),
                "yield_to_maturity": str(result.yield_to_maturity),
                "modified_duration": str(result.modified_duration),
                "convexity": str(result.convexity),
            }
        )

    best_ytm = max(comparisons, key=lambda x: float(x["yield_to_maturity"]))
    lowest_duration = min(comparisons, key=lambda x: float(x["modified_duration"]))

    recommendations.append(
        f"Highest YTM: Bond #{best_ytm['index']} at {best_ytm['yield_to_maturity']}"
    )
    recommendations.append(
        f"Lowest Interest Rate Risk: Bond #{lowest_duration['index']} "
        f"(Duration: {lowest_duration['modified_duration']})"
    )

    if len(comparisons) >= 2:
        best_convexity = max(comparisons, key=lambda x: float(x["convexity"]))
        recommendations.append(
            f"Best Risk-Adjusted: Bond #{best_convexity['index']} "
            f"(Highest Convexity: {best_convexity['convexity']})"
        )

    return {"comparisons": comparisons, "recommendations": recommendations}
