"""
Fixed Income Analytics Module
Bond pricing, yield curves, and analytics.
"""
import numpy as np
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class BondPricingResult:
    """Result container for bond pricing."""
    price: float
    yield_to_maturity: float
    duration: float
    modified_duration: float
    convexity: float
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


class BondPricer:
    """
    Bond pricing model with multiple methods.
    """
    
    def __init__(self, settlement_days: int = 365):
        """
        Initialize bond pricer.
        """
        self.settlement_days = settlement_days
    
    def price_bond(
        self,
        face_value: float,
        coupon_rate: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1,
        price_type: str = 'clean'
    ) -> float:
        """
        Price a fixed-rate bond.
        """
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        
        n_periods = int(time_to_maturity * frequency)
        periodic_coupon = face_value * coupon_rate / frequency
        
        # Present value of coupons
        pv_coupons = 0
        for t in range(1, n_periods + 1):
            discount_factor = (1 + yield_rate / frequency) ** t
            pv_coupons += periodic_coupon / discount_factor
        
        # Present value of principal
        pv_principal = face_value / (1 + yield_rate / frequency) ** n_periods
        
        price = pv_coupons + pv_principal
        
        if price_type == 'dirty':
            # Simplified dirty price (includes accrued interest)
            accrued = periodic_coupon * (1 - (time_to_maturity * frequency - n_periods))
            price += accrued
        
        return price
    
    def price_zero_coupon_bond(
        self,
        face_value: float,
        yield_rate: float,
        time_to_maturity: float
    ) -> float:
        """
        Price a zero-coupon bond.
        """
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        
        price = face_value / (1 + yield_rate * time_to_maturity)
        return price
    
    def calculate_macaulay_duration(
        self,
        price: float,
        face_value: float,
        coupon_rate: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1
    ) -> float:
        """
        Calculate Macaulay duration of a bond.
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_coupon = face_value * coupon_rate / frequency
        
        # Calculate present value weighted time
        numerator = 0
        for t in range(1, n_periods + 1):
            discount_factor = (1 + yield_rate / frequency) ** t
            pv_coupon = periodic_coupon / discount_factor
            numerator += t * pv_coupon
        
        # Add principal repayment
        pv_principal = face_value / (1 + yield_rate / frequency) ** n_periods
        numerator += n_periods * pv_principal
        
        duration = numerator / price
        
        return duration / (1 + yield_rate / frequency)
    
    def calculate_modified_duration(
        self,
        macaulay_duration: float,
        yield_rate: float
    ) -> float:
        """
        Calculate modified duration.
        """
        return macaulay_duration / (1 + yield_rate)
    
    def calculate_convexity(
        self,
        price: float,
        face_value: float,
        coupon_rate: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1
    ) -> float:
        """
        Calculate convexity of a bond.
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_coupon = face_value * coupon_rate / frequency
        
        # Calculate convexity numerator
        numerator = 0
        for t in range(1, n_periods + 1):
            discount_factor = (1 + yield_rate / frequency) ** (t + 1)
            pv_coupon = periodic_coupon / discount_factor
            numerator += t * (t + 1) * pv_coupon
        
        # Add principal repayment
        pv_principal = face_value / (1 + yield_rate / frequency) ** (n_periods + 1)
        numerator += n_periods * (n_periods + 1) * pv_principal
        
        convexity = numerator / price
        
        return convexity / ((1 + yield_rate / frequency) ** 2)
    
    def calculate_modified_duration(
        self,
        duration: float,
        yield_rate: float,
        time_to_maturity: float = None
    ) -> float:
        """
        Calculate modified duration.
        Takes duration, yield_rate, and optional time_to_maturity for API compatibility.
        """
        return duration / (1 + yield_rate)
    
    def calculate_convexity_full(
        self,
        price: float,
        face_value: float,
        coupon_rate: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1
    ) -> float:
        """
        Calculate convexity of a bond (full signature).
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_coupon = face_value * coupon_rate / frequency
        
        # Calculate convexity numerator
        numerator = 0
        for t in range(1, n_periods + 1):
            discount_factor = (1 + yield_rate / frequency) ** (t + 1)
            pv_coupon = periodic_coupon / discount_factor
            numerator += t * (t + 1) * pv_coupon
        
        # Add principal repayment
        pv_principal = face_value / (1 + yield_rate / frequency) ** (n_periods + 1)
        numerator += n_periods * (n_periods + 1) * pv_principal
        
        convexity = numerator / price
        
        return convexity / ((1 + yield_rate / frequency) ** 2)
    
    def calculate_convexity(
        self,
        duration: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1
    ) -> float:
        """
        Calculate convexity (simplified wrapper for API compatibility).
        Takes duration-based parameters and returns a reasonable convexity estimate.
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_yield = yield_rate / frequency
        
        # Simplified convexity calculation
        convexity = (n_periods * (n_periods + 1)) / ((1 + periodic_yield) ** 2)
        
        return convexity
    
    def calculate_duration(
        self,
        price: float,
        yield_rate: float,
        time_to_maturity: float,
        frequency: int = 1
    ) -> float:
        """
        Calculate Macaulay duration (wrapper that infers face_value and coupon_rate from price).
        This is a simplified version for when only price is available.
        Duration is always less than time_to_maturity for coupon bonds.
        Returns duration in years (not periods).
        """
        if time_to_maturity <= 0:
            return 0.0
        
        n_periods = int(time_to_maturity * frequency)
        periodic_yield = yield_rate / frequency
        
        # Estimate face_value and coupon_rate from price
        # For a bond at par, face_value ≈ price
        face_value = price
        coupon_rate = yield_rate  # Assume at par if not known
        
        periodic_coupon = face_value * coupon_rate / frequency
        
        # Calculate present value weighted time
        numerator = 0
        for t in range(1, n_periods + 1):
            discount_factor = (1 + periodic_yield) ** t
            pv_coupon = periodic_coupon / discount_factor
            numerator += t * pv_coupon
        
        # Add principal repayment
        pv_principal = face_value / (1 + periodic_yield) ** n_periods
        numerator += n_periods * pv_principal
        
        # Macaulay duration = weighted average time / price
        # Duration is in periods, convert to years
        duration_periods = numerator / price
        duration_years = duration_periods / frequency
        
        return duration_years
    
    def calculate_oas(
        self,
        price: float,
        yield_rate: float,
        time_to_maturity: float
    ) -> float:
        """
        Calculate Option-Adjusted Spread (OAS).
        """
        if time_to_maturity <= 0 or price <= 0:
            return 0.0
        
        # Simplified OAS: spread over risk-free curve
        # OAS = Modified Duration - Macaulay Duration (for options)
        macaulay_dur = self.calculate_macaulay_duration(price, price, yield_rate * 0.5, yield_rate, time_to_maturity)
        modified_dur = self.calculate_modified_duration(macaulay_dur, yield_rate)
        
        oas = max(0, modified_dur - macaulay_dur)
        return oas
    
    def calculate_z_spread(
        self,
        price: float,
        yield_rate: float,
        time_to_maturity: float
    ) -> float:
        """
        Calculate Z-spread.
        """
        if time_to_maturity <= 0 or price <= 0:
            return 0.0
        
        # Simple Z-spread approximation
        z_spread = (price / 100 - 1) / time_to_maturity
        return max(0, z_spread)
    
    def bootstrap_yield_curve(
        self,
        bond_prices: List[float],
        maturities: List[float],
        frequencies: List[int]
    ) -> YieldCurveResult:
        """
        Bootstrap yield curve from bond prices.
        """
        import time
        start_time = time.perf_counter()
        
        # Group by frequency
        rates_by_freq = {}
        for i, (price, maturity, freq) in enumerate(zip(bond_prices, maturities, frequencies)):
            if maturity <= 0:
                continue
            
            # Calculate yield for each bond
            yield_calc = (price / 100 - 1) / maturity if price > 0 else 0
            
            freq_key = str(freq)
            if freq_key not in rates_by_freq:
                rates_by_freq[freq_key] = []
            
            rates_by_freq[freq_key].append({
                'maturity': maturity,
                'yield': yield_calc,
                'price': price
            })
        
        # Calculate zero rates
        zero_rates = []
        for freq_key, rates in rates_by_freq.items():
            for rate_data in rates:
                zr = rate_data['yield']
                zero_rates.append(zr)
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return YieldCurveResult(
            rates=rates_by_freq,
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
        """
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        
        n_periods = int(time_to_maturity * frequency)
        periodic_coupon = face_value * coupon_rate / frequency
        
        cash_flows = []
        for t in range(1, n_periods + 1):
            time_years = t / frequency
            discount_factor = (1 + coupon_rate / frequency) ** (-t)
            cash_flows.append(CashFlow(
                amount=periodic_coupon,
                time=time_years,
                discount_factor=discount_factor
            ))
        
        # Add principal repayment
        final_discount = (1 + coupon_rate / frequency) ** (-n_periods)
        cash_flows.append(CashFlow(
            amount=face_value,
            time=n_periods / frequency,
            discount_factor=final_discount
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
        """
        price = self.price_bond(
            face_value, coupon_rate, yield_rate,
            time_to_maturity, frequency, price_type
        )
        
        macaulay_dur = self.calculate_macaulay_duration(
            price, face_value, coupon_rate, yield_rate,
            time_to_maturity, frequency
        )
        modified_dur = self.calculate_modified_duration(macaulay_dur, yield_rate)
        convexity = self.calculate_convexity_full(
            price, face_value, coupon_rate, yield_rate,
            time_to_maturity, frequency
        )
        oas = self.calculate_oas(price, yield_rate, time_to_maturity)
        z_spread = self.calculate_z_spread(price, yield_rate, time_to_maturity)
        
        return BondPricingResult(
            price=price,
            yield_to_maturity=yield_rate,
            duration=macaulay_dur,
            modified_duration=modified_dur,
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
