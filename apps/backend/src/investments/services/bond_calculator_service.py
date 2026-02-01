"""
Bond Calculator Service

Comprehensive bond yield and price calculations using Decimal for precision.
Supports: Current Yield, YTM, YTC, Zero-Coupon, T-Bill, and Price calculations.
"""

import logging
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class BondType(str, Enum):
    TREASURY = "treasury"
    CORPORATE = "corporate"
    MUNICIPAL = "municipal"
    AGENCY = "agency"
    TREASURY_NOTE = "treasury_note"
    TREASURY_BILL = "treasury_bill"
    ZERO_COUPON = "zero_coupon"
    FLOATING_RATE = "floating_rate"
    PERPETUAL = "perpetual"
    FIXED = "fixed"


class CouponFrequency(int, Enum):
    ANNUAL = 1
    SEMIANNUAL = 2
    QUARTERLY = 4
    MONTHLY = 12


@dataclass
class BondCalculationResult:
    """Result of a bond calculation."""

    current_yield: Optional[Decimal] = None
    ytm: Optional[Decimal] = None
    ytc: Optional[Decimal] = None
    zero_coupon_yield: Optional[Decimal] = None
    treasury_yield: Optional[Decimal] = None
    bond_price: Optional[Decimal] = None
    macaulay_duration: Optional[Decimal] = None
    modified_duration: Optional[Decimal] = None
    convexity: Optional[Decimal] = None
    error_message: Optional[str] = None
    iterations: int = 0


def to_decimal(value) -> Decimal:
    """Convert value to Decimal safely."""
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (ValueError, InvalidOperation):
        return Decimal("0")


def round_decimal(value: Decimal, places: int = 4) -> Decimal:
    """Round Decimal to specified places."""
    quantizer = Decimal("10") ** -places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


class BondCalculatorService:
    """
    Service for calculating bond yields and prices.

    All calculations use Decimal for financial precision.
    """

    MAX_ITERATIONS = 100
    YTM_TOLERANCE = Decimal("0.0001")
    DEFAULT_YTM_GUESS = Decimal("0.05")

    def current_yield(
        self, face_value: Decimal, coupon_rate: Decimal, current_price: Decimal
    ) -> Decimal:
        """
        Calculate Current Yield.

        Formula: Current Yield = (Annual Coupon Payment / Current Price) × 100
        """
        price = to_decimal(current_price)
        if price <= 0:
            raise ValueError("Current price must be positive")

        annual_coupon = to_decimal(face_value) * to_decimal(coupon_rate)
        yield_value = (annual_coupon / price) * 100

        return round_decimal(yield_value)

    def yield_to_maturity(
        self,
        face_value: Decimal,
        coupon_rate: Decimal,
        current_price: Decimal,
        years_to_maturity: float,
        frequency: int = 2,
    ) -> Decimal:
        """
        Calculate Yield to Maturity (YTM) using Newton-Raphson method.
        """
        price = to_decimal(current_price)
        if price <= 0:
            raise ValueError("Price must be positive")

        if years_to_maturity <= 0:
            raise ValueError("Years to maturity must be positive")

        face = to_decimal(face_value)
        coupon = to_decimal(coupon_rate)
        total_periods = int(years_to_maturity * frequency)
        coupon_payment = (face * coupon) / frequency

        if total_periods == 0:
            return round_decimal((face - price) / price * 100)

        ytm = self.DEFAULT_YTM_GUESS

        for iteration in range(self.MAX_ITERATIONS):
            periods_yield = ytm / frequency

            pv_coupons = Decimal("0")
            for t in range(1, total_periods + 1):
                discount_factor = (Decimal("1") + periods_yield) ** t
                pv_coupons += coupon_payment / discount_factor

            pv_face = face / ((Decimal("1") + periods_yield) ** total_periods)
            calculated_price = pv_coupons + pv_face

            price_diff = calculated_price - price

            if abs(price_diff) < self.YTM_TOLERANCE * price:
                return round_decimal(ytm * 100, 4)

            adjustment = price_diff / 10000
            ytm -= adjustment

            if ytm <= -Decimal("1"):
                ytm = Decimal("0.001")
            elif ytm > Decimal("2"):
                ytm = Decimal("0.10")

        return round_decimal(ytm * 100, 4)

    def yield_to_call(
        self,
        face_value: Decimal,
        coupon_rate: Decimal,
        current_price: Decimal,
        years_to_call: float,
        call_price: Decimal,
        frequency: int = 2,
    ) -> Decimal:
        """Calculate Yield to Call (YTC)."""
        price = to_decimal(current_price)
        if price <= 0:
            raise ValueError("Price must be positive")

        call = to_decimal(call_price)
        if call <= 0:
            raise ValueError("Call price must be positive")

        if years_to_call <= 0:
            raise ValueError("Years to call must be positive")

        face = to_decimal(face_value)
        coupon = to_decimal(coupon_rate)
        total_periods = int(years_to_call * frequency)
        coupon_payment = (face * coupon) / frequency

        if total_periods == 0:
            return round_decimal((call - price) / price * 100)

        ytc = self.DEFAULT_YTM_GUESS

        for iteration in range(self.MAX_ITERATIONS):
            periods_yield = ytc / frequency

            pv_coupons = Decimal("0")
            for t in range(1, total_periods + 1):
                discount_factor = (Decimal("1") + periods_yield) ** t
                pv_coupons += coupon_payment / discount_factor

            pv_call = call / ((Decimal("1") + periods_yield) ** total_periods)
            calculated_price = pv_coupons + pv_call

            price_diff = calculated_price - price

            if abs(price_diff) < self.YTM_TOLERANCE * price:
                return round_decimal(ytc * 100, 4)

            adjustment = price_diff / 10000
            ytc -= adjustment

            if ytc <= -Decimal("1"):
                ytc = Decimal("0.001")
            elif ytc > Decimal("2"):
                ytc = Decimal("0.10")

        return round_decimal(ytc * 100, 4)

    def zero_coupon_yield(
        self, current_price: Decimal, face_value: Decimal, years_to_maturity: float
    ) -> Decimal:
        """
        Calculate Zero-Coupon Bond Yield.

        Formula: Yield = (Face / Price)^(1/n) - 1
        """
        price = to_decimal(current_price)
        face = to_decimal(face_value)

        if price <= 0:
            raise ValueError("Price must be positive")

        if years_to_maturity <= 0:
            raise ValueError("Years to maturity must be positive")

        if price >= face:
            return Decimal("0")

        yield_value = (face / price) ** (Decimal("1") / years_to_maturity) - Decimal(
            "1"
        )

        return round_decimal(yield_value * 100, 4)

    def treasury_bill_yield(
        self, discount_rate: Decimal, days_to_maturity: int
    ) -> Dict[str, Decimal]:
        """
        Calculate Treasury Bill Yields.
        """
        discount = to_decimal(discount_rate)

        if days_to_maturity <= 0:
            raise ValueError("Days to maturity must be positive")

        discount_yield = discount * 100

        denominator = Decimal("360") - (discount * days_to_maturity)
        if denominator <= 0:
            investment_yield = Decimal("0")
        else:
            investment_yield = (Decimal("360") * discount) / denominator * 100

        return {
            "discount_yield": round_decimal(discount_yield, 4),
            "investment_yield": round_decimal(investment_yield, 4),
        }

    def bond_price(
        self,
        face_value: Decimal,
        coupon_rate: Decimal,
        ytm: Decimal,
        years_to_maturity: int,
        frequency: int = 2,
    ) -> Decimal:
        """
        Calculate Bond Price given YTM.
        """
        face = to_decimal(face_value)
        coupon = to_decimal(coupon_rate)
        ytm_decimal = to_decimal(ytm) / 100

        if years_to_maturity <= 0:
            return face

        total_periods = years_to_maturity * frequency
        coupon_payment = face * coupon / frequency
        period_yield = ytm_decimal / frequency

        pv_coupons = Decimal("0")
        for t in range(1, total_periods + 1):
            discount_factor = (Decimal("1") + period_yield) ** t
            pv_coupons += coupon_payment / discount_factor

        pv_face = face / ((Decimal("1") + period_yield) ** total_periods)

        return round_decimal(pv_coupons + pv_face, 4)

    def calculate_all(
        self,
        face_value: Decimal,
        coupon_rate: Decimal,
        current_price: Decimal,
        years_to_maturity: float,
        frequency: int = 2,
        call_price: Optional[Decimal] = None,
        years_to_call: Optional[float] = None,
    ) -> BondCalculationResult:
        """Calculate all available metrics for a bond."""
        result = BondCalculationResult()

        try:
            result.current_yield = self.current_yield(
                face_value, coupon_rate, current_price
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Current yield error: {e}")

        try:
            result.ytm = self.yield_to_maturity(
                face_value, coupon_rate, current_price, years_to_maturity, frequency
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"YTM error: {e}")

        try:
            result.bond_price = self.bond_price(
                face_value,
                coupon_rate,
                result.ytm or Decimal("5"),
                years_to_maturity,
                frequency,
            )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Bond price error: {e}")

        return result
