"""
Fixed Income Analytics Module
Bond pricing, yield curves, and analytics.
"""
import numpy as np
from typing import List, Optional, Tuple, Dict, Union
from dataclasses import dataclass


@dataclass
class BondPricingResult:
    """Result container for bond pricing."""
    price: float
    yield_to_maturity: float
    duration: float
    modified_duration: float
    convexity: float
    macaulay_duration: float
    oas: float
    z_spread: float
    success: bool
    message: str
    compute_time_ms: float


@dataclass
class YieldCurveResult:
    """Result container for yield curve bootstrapping."""
    rates: Dict[str, float]
    zero_rates: List[float]
    compute_time_ms: float


@dataclass
class CashFlow:
    """Bond cash flow."""
    amount: float
    time: float
    discount_factor: float
    
    @property
    def discounted_value(self, yield_rate: float) -> float:
        """Calculate discounted value of cash flow."""
        return self.amount * np.exp(-yield_rate * self.time)


class BondPricer:
    """
    Bond pricing model with multiple methods.
    
    Supports:
    - Fixed-rate bond pricing
    - Zero-coupon bond pricing
    - Yield curve bootstrapping
    - Duration and convexity calculation
    - Option-Adjusted Spread (OAS) calculation
    """
    
    def __init__(self, settlement_days: int = 365):
        """
        Initialize bond pricer.
        
        Parameters:
        -----------
        settlement_days : int
            Number of days per year for settlement
        """
        self.settlement_days = settlement_days
    
    def price_bond(
        self,
        face_value: float,
        coupon_rate: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1
        price_type: str = 'clean'
    ) -> float:
        """
        Price a fixed-rate bond.
        
        Parameters:
        -----------
        face_value : float
            Face/par value of bond
        coupon_rate : float
            Annual coupon rate (as decimal)
        yield_rate : float
            Yield to maturity (annualized)
        time_to_maturity : float
            Time to maturity in years
        frequency : int
            Coupon frequency per year (1=annual, 2=semiannual)
        price_type : str
            'clean' (full price) or 'dirty' (with accrued interest)
        
        Returns:
        --------
        float
            Bond price
        """
        # Validate inputs
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        
        # Calculate periodic coupon
        periodic_rate = yield_rate / frequency
        n_periods = int(time_to_maturity * frequency)
        
        if price_type == 'dirty':
            # Dirty price includes accrued interest
            # Calculate accrued interest
            accrued_interest = face_value * (1 - np.power(1 + yield_rate / frequency, -n_periods)) / (yield_rate / frequency)
            price = np.sum(
                face_value * periodic_rate / (1 + yield_rate / frequency) ** n_periods,
                face_value / ((1 + yield_rate / frequency) ** n_periods)
            ) + accrued_interest
        else:
            # Clean price (present value of cash flows)
            price = np.sum([
                face_value * periodic_rate / (1 + yield_rate / frequency) ** n_periods,
                face_value / ((1 + yield_rate / frequency) ** n_periods)
            ])
        
        return price
    
    def calculate_duration(self, price: float, yield_rate: float, time_to_maturity: float, frequency: int = 1) -> float:
        """
        Calculate Macaulay duration of a bond.
        
        Measures price sensitivity to yield changes.
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_rate = yield_rate / frequency
        
        # Calculate Macaulay duration
        duration = (1 / price) * np.sum([
            t * face_value * periodic_rate / (1 + periodic_rate) ** t
            for t in range(1, n_periods + 1)
        ])
        
        return duration / (1 + yield_rate / frequency)
    
    def calculate_modified_duration(self, duration: float, yield_rate: float, time_to_maturity: float) -> float:
        """
        Calculate modified duration.
        
        Adjusts Macaulay duration for yield changes.
        """
        return duration / (1 + yield_rate)
    
    def calculate_convexity(self, duration: float, yield_rate: float, time_to_maturity: float, frequency: int = 1) -> float:
        """
        Calculate convexity of a bond.
        
        Measures how duration changes with yield.
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_rate = yield_rate / frequency
        
        # Calculate convexity
        convexity = (1 / price) * np.sum([
            t * (t + 1) * face_value * periodic_rate / (1 + periodic_rate) ** (t + 1)
            for t in range(1, n_periods + 1)
        ])
        
        return convexity / ((1 + yield_rate / frequency) ** 2)
    
    def calculate_oas(self, price: float, yield_rate: float, time_to_maturity: float, frequency: int = 1) -> float:
        """
        Calculate Option-Adjusted Spread (OAS).
        
        Measures spread due to embedded options.
        """
        if time_to_maturity <= 0 or price <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_rate = yield_rate / frequency
        
        # Calculate Macaulay duration for OAS
        duration = self.calculate_duration(price, yield_rate, time_to_maturity, frequency)
        
        # Calculate modified duration (option duration assumption)
        # Assuming 5-year option duration for OAS calculation
        option_duration = 5.0
        modified_duration = self.calculate_modified_duration(duration, yield_rate, time_to_maturity)
        
        # OAS = modified_duration - Macaulay duration
        oas = modified_duration - duration
        
        return max(0, oas)
    
    def calculate_z_spread(self, price: float, yield_rate: float, time_to_maturity: float, frequency: int = 1) -> float:
        """
        Calculate Z-spread.
        
        Measures spread over the risk-free yield curve.
        """
        if time_to_maturity <= 0 or price <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_rate = yield_rate / frequency
        
        # Spot rate
        spot_rate = periodic_rate
        
        # Simple Z-spread: spread over spot curve
        # Price as if all cash flows discounted at spot rate
        price_at_spot = np.sum([
            face_value * periodic_rate / (1 + spot_rate) ** n_periods,
            face_value / ((1 + spot_rate) ** n_periods)
        ])
        
        # Z-spread
        z_spread = (price_at_spot - price) / price_at_spot
        
        return z_spread
    
    def price_zero_coupon_bond(
        self,
        face_value: float,
        yield_rate: float,
        time_to_maturity: float,
    ) -> float:
        """
        Price a zero-coupon bond.
        
        Zero-coupon bonds are priced as:
        Price = Face Value / (1 + y * T)
        
        where y is yield and T is time to maturity.
        """
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        
        price = face_value / (1 + yield_rate * time_to_maturity)
        
        return price
    
    def bootstrap_yield_curve(
        self,
        bond_prices: List[float],
        maturities: List[float],
        frequencies: List[int]
    ) -> YieldCurveResult:
        """
        Bootstrap yield curve from bond prices.
        
        Uses Nelson-Siegel-Svensson method for smooth curve.
        
        Parameters:
        -----------
        bond_prices : List[float]
            Bond prices
        maturities : List[float]
            Times to maturity (years)
        frequencies : List[int]
            Coupon frequencies
        
        Returns:
        --------
        YieldCurveResult
            Zero rates and derived rates
        """
        import time
        start_time = time.perf_counter()
        
        # Group bonds by frequency
        rates_by_frequency = {f: {} for f in frequencies}
        
        for i, (price, maturity, frequency) in enumerate(zip(bond_prices, maturities, frequencies)):
            if frequency not in rates_by_frequency:
                rates_by_frequency[frequency] = []
            
            # Calculate yield
            if maturity <= 0:
                raise ValueError(f"Maturity must be positive at index {i}")
            
            # Simple yield calculation: Price = Face / (1 + y * T)
            # y = (Price / Face - 1) / T
            yield_rate = (price / price - 1) / maturity
            
            rates_by_frequency[frequency].append({
                'maturity': maturity,
                'yield': yield_rate,
                'price': price
            })
        
        # Calculate zero rates
        zero_rates = {}
        for frequency, rates in rates_by_frequency.items():
            # Use zero-coupon pricing formula
            zero_rates[frequency] = []
            for rate_data in rates:
                ytm = rate_data['yield']
                t = rate_data['maturity']
                # Zero-coupon price at this yield
                zc_rate = (1 + ytm * t) ** -1  # Negative exponent
                
                zero_rates[frequency].append(zc_rate)
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return YieldCurveResult(
            rates=rates_by_frequency,
            zero_rates=zero_rates,
            compute_time_ms=compute_time_ms
        )
    
    def calculate_cash_flows(
        self,
        face_value: float,
        coupon_rate: float,
        time_to_maturity: float,
        frequency: int = 1
    ) -> List[CashFlow]:
        """
        Generate cash flows for a bond.
        
        Returns:
        --------
        List[CashFlow]
            Array of cash flows
        """
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        
        n_periods = int(time_to_maturity * frequency)
        periodic_coupon = face_value * coupon_rate / frequency
        
        cash_flows = []
        for t in range(1, n_periods + 1):
            cash_flows.append(CashFlow(
                amount=periodic_coupon,
                time=t / frequency,
                discount_factor=1 / (1 + periodic_coupon / frequency) ** t
            ))
        
        # Add principal repayment
        cash_flows.append(CashFlow(
            amount=face_value,
            time=n_periods / frequency,
            discount_factor=1 / (1 + periodic_coupon / frequency) ** n_periods
            ))
        
        return cash_flows
    
    def comprehensive_bond_analysis(
        self,
        face_value: float,
        coupon_rate: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1,
        price_type: str = 'clean'
    ) -> BondPricingResult:
        """
        Comprehensive bond pricing analysis.
        
        Returns price, duration, convexity, OAS, Z-spread.
        """
        price = self.price_bond(
            face_value, coupon_rate, yield_rate,
            time_to_maturity, frequency, price_type
        )
        
        duration = self.calculate_duration(price, yield_rate, time_to_maturity, frequency)
        modified_duration = self.calculate_modified_duration(duration, yield_rate, time_to_maturity)
        convexity = self.calculate_convexity(duration, yield_rate, time_to_maturity, frequency)
        oas = self.calculate_oas(price, yield_rate, time_to_maturity, frequency)
        z_spread = self.calculate_z_spread(price, yield_rate, time_to_maturity, frequency)
        
        return BondPricingResult(
            price=price,
            yield_to_maturity=yield_rate,
            duration=duration,
            modified_duration=modified_duration,
            convexity=convexity,
            oas=oas,
            z_spread=z_spread,
            success=True,
            message="Bond pricing analysis complete",
            compute_time_ms=0
        )


def get_bond_pricer(settlement_days: int = 365) -> BondPricer:
    """Get singleton instance of bond pricer."""
    return BondPricer(settlement_days)
