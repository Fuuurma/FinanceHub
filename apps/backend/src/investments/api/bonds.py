"""
Bond API Endpoints
Django Ninja router for bond calculations.
"""

import logging
from decimal import Decimal
from typing import List, Optional
from ninja import Router, Schema
from pydantic import Field, validator

logger = logging.getLogger(__name__)

router = Router(tags=["Bonds"])


class BondCalculationInput(Schema):
    """Input for bond yield calculation."""

    face_value: float = Field(1000.0, description="Bond face/par value")
    coupon_rate: float = Field(0.05, description="Annual coupon rate (0.05 = 5%)")
    current_price: float = Field(..., description="Current market price")
    years_to_maturity: float = Field(..., description="Years to maturity")
    frequency: int = Field(2, description="Coupon payments per year (1, 2, 4, 12)")
    call_price: Optional[float] = Field(None, description="Call price (for YTC)")
    years_to_call: Optional[float] = Field(None, description="Years until call")


class BondComparisonInput(Schema):
    """Input for comparing multiple bonds."""

    bonds: List[BondCalculationInput]


class BondCalculationResponse(Schema):
    """Response with bond calculation results."""

    current_yield: Optional[float] = None
    ytm: Optional[float] = None
    ytc: Optional[float] = None
    zero_coupon_yield: Optional[float] = None
    bond_price: Optional[float] = None
    macaulay_duration: Optional[float] = None
    modified_duration: Optional[float] = None
    convexity: Optional[float] = None
    error_message: Optional[str] = None


class BondComparisonResponse(Schema):
    """Response for bond comparison."""

    bonds: List[BondCalculationResponse]
    best_yield: Optional[float] = None
    highest_current_yield: Optional[float] = None


@router.post("/bonds/calculate")
def calculate_bond_yield(request, data: BondCalculationInput):
    """
    Calculate bond yields and metrics.

    Calculates current yield, YTM, YTC, bond price, duration, and convexity.
    """
    try:
        from investments.services.bond_calculator_service import BondCalculatorService

        svc = BondCalculatorService()

        face = Decimal(str(data.face_value))
        coupon = Decimal(str(data.coupon_rate))
        price = Decimal(str(data.current_price))

        result = BondCalculationResponse()

        try:
            result.current_yield = float(svc.current_yield(face, coupon, price))
        except (ValueError, ZeroDivisionError) as e:
            result.error_message = f"Current yield error: {str(e)}"

        try:
            result.ytm = float(
                svc.yield_to_maturity(
                    face, coupon, price, data.years_to_maturity, data.frequency
                )
            )
        except (ValueError, ZeroDivisionError) as e:
            if not result.error_message:
                result.error_message = str(e)

        try:
            if data.call_price and data.years_to_call:
                result.ytc = float(
                    svc.yield_to_call(
                        face,
                        coupon,
                        price,
                        data.years_to_call,
                        Decimal(str(data.call_price)),
                        data.frequency,
                    )
                )
        except (ValueError, ZeroDivisionError) as e:
            pass

        try:
            ytm_for_price = result.ytm if result.ytm else Decimal("5")
            result.bond_price = float(
                svc.bond_price(
                    face,
                    coupon,
                    ytm_for_price,
                    int(data.years_to_maturity),
                    data.frequency,
                )
            )
        except (ValueError, TypeError) as e:
            pass

        try:
            result.macaulay_duration = float(
                svc.macaulay_duration(
                    face,
                    coupon,
                    ytm_for_price or Decimal("5"),
                    int(data.years_to_maturity),
                    data.frequency,
                )
            )
        except (ValueError, TypeError) as e:
            pass

        try:
            result.modified_duration = float(
                svc.modified_duration(
                    face,
                    coupon,
                    ytm_for_price or Decimal("5"),
                    int(data.years_to_maturity),
                    data.frequency,
                )
            )
        except (ValueError, TypeError) as e:
            pass

        try:
            result.convexity = float(
                svc.convexity(
                    face,
                    coupon,
                    ytm_for_price or Decimal("5"),
                    int(data.years_to_maturity),
                    data.frequency,
                )
            )
        except (ValueError, TypeError) as e:
            pass

        return result.model_dump(exclude_none=True)

    except (ValueError, ZeroDivisionError) as e:
        logger.error(f"Bond calculation error: {e}")
        return {"error": str(e)}, 500


@router.post("/bonds/calculate/current-yield")
def calculate_current_yield(request, data: BondCalculationInput):
    """Calculate current yield only."""
    try:
        from investments.services.bond_calculator_service import BondCalculatorService

        svc = BondCalculatorService()
        result = svc.current_yield(
            Decimal(str(data.face_value)),
            Decimal(str(data.coupon_rate)),
            Decimal(str(data.current_price)),
        )
        return {"current_yield": float(result)}
    except (ValueError, ZeroDivisionError) as e:
        return {"error": str(e)}, 500


@router.post("/bonds/calculate/ytm")
def calculate_ytm(request, data: BondCalculationInput):
    """Calculate yield to maturity only."""
    try:
        from investments.services.bond_calculator_service import BondCalculatorService

        svc = BondCalculatorService()
        result = svc.yield_to_maturity(
            Decimal(str(data.face_value)),
            Decimal(str(data.coupon_rate)),
            Decimal(str(data.current_price)),
            data.years_to_maturity,
            data.frequency,
        )
        return {"ytm": float(result)}
    except (ValueError, ZeroDivisionError) as e:
        return {"error": str(e)}, 500


@router.post("/bonds/calculate/zero-coupon")
def calculate_zero_coupon_yield(
    request, current_price: float, face_value: float, years_to_maturity: float
):
    """Calculate zero-coupon bond yield."""
    try:
        from investments.services.bond_calculator_service import BondCalculatorService

        svc = BondCalculatorService()
        result = svc.zero_coupon_yield(
            Decimal(str(current_price)), Decimal(str(face_value)), years_to_maturity
        )
        return {"zero_coupon_yield": float(result)}
    except (ValueError, ZeroDivisionError) as e:
        return {"error": str(e)}, 500


@router.post("/bonds/calculate/treasury")
def calculate_treasury_yield(request, discount_rate: float, days_to_maturity: int):
    """Calculate Treasury Bill yield."""
    try:
        from investments.services.bond_calculator_service import BondCalculatorService

        svc = BondCalculatorService()
        result = svc.treasury_bill_yield(Decimal(str(discount_rate)), days_to_maturity)
        return {
            "discount_yield": float(result["discount_yield"]),
            "investment_yield": float(result["investment_yield"]),
        }
    except (ValueError, ZeroDivisionError) as e:
        return {"error": str(e)}, 500


@router.post("/bonds/compare")
def compare_bonds(request, data: BondComparisonInput):
    """Compare yields across multiple bonds."""
    try:
        from investments.services.bond_calculator_service import BondCalculatorService

        svc = BondCalculatorService()
        results = []
        best_ytm = None
        best_current = None

        for bond in data.bonds:
            face = Decimal(str(bond.face_value))
            coupon = Decimal(str(bond.coupon_rate))
            price = Decimal(str(bond.current_price))

            result = BondCalculationResponse()

            try:
                result.current_yield = float(svc.current_yield(face, coupon, price))
                if best_current is None or result.current_yield > best_current:
                    best_current = result.current_yield
            except:
                pass

            try:
                result.ytm = float(
                    svc.yield_to_maturity(
                        face, coupon, price, bond.years_to_maturity, bond.frequency
                    )
                )
                if best_ytm is None or result.ytm > best_ytm:
                    best_ytm = result.ytm
            except (ValueError, ZeroDivisionError):
                pass

            results.append(result.model_dump(exclude_none=True))

        return BondComparisonResponse(
            bonds=results, best_yield=best_ytm, highest_current_yield=best_current
        ).model_dump(exclude_none=True)

    except (ValueError, ZeroDivisionError) as e:
        logger.error(f"Bond comparison error: {e}")
        return {"error": str(e)}, 500


@router.get("/bonds/types")
def get_bond_types(request):
    """Get supported bond types."""
    return {
        "bond_types": [
            {"value": "treasury", "label": "Treasury Bond"},
            {"value": "corporate", "label": "Corporate Bond"},
            {"value": "municipal", "label": "Municipal Bond"},
            {"value": "agency", "label": "Agency Bond"},
            {"value": "treasury_note", "label": "Treasury Note"},
            {"value": "treasury_bill", "label": "Treasury Bill"},
            {"value": "mbs", "label": "Mortgage-Backed Security"},
        ],
        "frequencies": [
            {"value": 1, "label": "Annual"},
            {"value": 2, "label": "Semi-Annual"},
            {"value": 4, "label": "Quarterly"},
            {"value": 12, "label": "Monthly"},
        ],
        "ratings": [
            "AAA",
            "AA+",
            "AA",
            "AA-",
            "A+",
            "A",
            "A-",
            "BBB+",
            "BBB",
            "BBB-",
            "BB+",
            "BB",
            "BB-",
            "B+",
            "B",
            "B-",
            "CCC+",
            "CCC",
            "CCC-",
            "CC",
            "C",
            "D",
            "NR",
        ],
    }


@router.get("/bonds/formulas")
def get_formula_references(request):
    """Get formula references for bond calculations."""
    return {
        "current_yield": {
            "formula": "Current Yield = (Annual Coupon / Current Price) × 100",
            "description": "Measures annual return relative to current price",
        },
        "ytm": {
            "formula": "Price = Σ(Coupon/(1+YTM/f)^t) + Face/(1+YTM/f)^n",
            "description": "Yield to Maturity - total return if held to maturity",
        },
        "zero_coupon_yield": {
            "formula": "Yield = (Face/Price)^(1/n) - 1",
            "description": "Yield for zero-coupon bonds",
        },
        "treasury_yield": {
            "formula": "Investment Yield = (360 × Discount) / (360 - Discount × Days)",
            "description": "T-Bill discount to investment yield conversion",
        },
        "bond_price": {
            "formula": "Price = Σ(Coupon/(1+YTM/f)^t) + Face/(1+YTM/f)^n",
            "description": "Calculate price given YTM",
        },
    }
