"""
Tests for Fixed Income Analytics
"""
import pytest
import numpy as np
from utils.services.fixed_income.bond_pricing import BondPricer, BondPricingResult


@pytest.fixture
def bond_pricer():
    """Create bond pricer instance."""
    return BondPricer()


class TestBondPricing:
    """Tests for bond pricing functionality."""
    
    def test_zero_coupon_bond_pricing(self, bond_pricer):
        """Test zero-coupon bond pricing."""
        face_value = 1000
        yield_rate = 0.05
        time_to_maturity = 1.0
        
        price = bond_pricer.price_zero_coupon_bond(
            face_value=face_value,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity
        )
        
        # Price = Face / (1 + y * T)
        expected_price = face_value / (1 + yield_rate * time_to_maturity)
        
        assert abs(price - expected_price) < 0.01
        assert price < face_value  # Discount bond
        assert price > 0
    
    def test_zero_coupon_bond_long_maturity(self, bond_pricer):
        """Test zero-coupon bond with long maturity."""
        face_value = 1000
        yield_rate = 0.05
        time_to_maturity = 10.0
        
        price = bond_pricer.price_zero_coupon_bond(
            face_value=face_value,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity
        )
        
        expected_price = face_value / (1 + yield_rate * time_to_maturity)
        
        assert abs(price - expected_price) < 0.01
        assert price < 700  # Significantly discounted
    
    def test_fixed_coupon_bond_pricing(self, bond_pricer):
        """Test fixed-coupon bond pricing."""
        face_value = 1000
        coupon_rate = 0.05  # 5% annual coupon
        yield_rate = 0.05
        time_to_maturity = 1.0
        frequency = 1  # Annual
        
        price = bond_pricer.price_bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # At par, price should equal face value
        assert abs(price - face_value) < 1.0
    
    def test_fixed_coupon_bond_at_discount(self, bond_pricer):
        """Test bond trading at discount (yield > coupon)."""
        face_value = 1000
        coupon_rate = 0.03  # 3% coupon
        yield_rate = 0.05   # 5% yield
        time_to_maturity = 2.0
        frequency = 1
        
        price = bond_pricer.price_bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Should trade at discount
        assert price < face_value
        assert price > 0
    
    def test_fixed_coupon_bond_at_premium(self, bond_pricer):
        """Test bond trading at premium (yield < coupon)."""
        face_value = 1000
        coupon_rate = 0.07  # 7% coupon
        yield_rate = 0.05   # 5% yield
        time_to_maturity = 2.0
        frequency = 1
        
        price = bond_pricer.price_bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Should trade at premium
        assert price > face_value
    
    def test_semiannual_coupon_bond(self, bond_pricer):
        """Test semiannual coupon bond pricing."""
        face_value = 1000
        coupon_rate = 0.05  # 5% annual = 2.5% semiannual
        yield_rate = 0.05   # 5% yield (at par)
        time_to_maturity = 2.0
        frequency = 2  # Semiannual
        
        price = bond_pricer.price_bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # At par, price should equal face value
        assert abs(price - face_value) < 2.0
    
    def test_comprehensive_bond_analysis(self, bond_pricer):
        """Test comprehensive bond analysis with all metrics."""
        face_value = 1000
        coupon_rate = 0.05
        yield_rate = 0.05
        time_to_maturity = 5.0
        frequency = 2
        
        result: BondPricingResult = bond_pricer.comprehensive_bond_analysis(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        assert result.success
        assert result.price > 0
        assert result.price < face_value * 1.5
        assert result.duration > 0
        assert result.modified_duration > 0
        assert result.convexity > 0


class TestBondCashFlows:
    """Tests for bond cash flow generation."""
    
    def test_annual_coupon_cash_flows(self, bond_pricer):
        """Test annual coupon bond cash flows."""
        face_value = 1000
        coupon_rate = 0.05
        time_to_maturity = 2.0
        frequency = 1
        
        cash_flows = bond_pricer.calculate_cash_flows(
            face_value=face_value,
            coupon_rate=coupon_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Should have 2 coupon payments + 1 principal
        assert len(cash_flows) == 3
        
        # Each coupon should be face_value * coupon_rate / frequency
        expected_coupon = face_value * coupon_rate / frequency
        for i, cf in enumerate(cash_flows[:-1]):
            assert cf.amount == expected_coupon
        
        # Principal repayment
        assert cash_flows[-1].amount == face_value
    
    def test_quarterly_coupon_cash_flows(self, bond_pricer):
        """Test quarterly coupon bond cash flows."""
        face_value = 1000
        coupon_rate = 0.08
        time_to_maturity = 1.0
        frequency = 4  # Quarterly
        
        cash_flows = bond_pricer.calculate_cash_flows(
            face_value=face_value,
            coupon_rate=coupon_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Should have 4 coupon payments + 1 principal
        assert len(cash_flows) == 5
        
        expected_coupon = face_value * coupon_rate / frequency
        for i, cf in enumerate(cash_flows[:-1]):
            assert cf.amount == expected_coupon
        
        assert cash_flows[-1].amount == face_value


class TestYieldCurveBootstrapping:
    """Tests for yield curve bootstrapping."""
    
    def test_yield_curve_bootstrap(self, bond_pricer):
        """Test basic yield curve bootstrapping."""
        # Simple case: 3 bonds with different maturities
        bond_prices = [950, 920, 880]
        maturities = [1.0, 2.0, 3.0]
        frequencies = [1, 1, 1]
        
        result = bond_pricer.bootstrap_yield_curve(
            bond_prices=bond_prices,
            maturities=maturities,
            frequencies=frequencies
        )
        
        assert result is not None
        assert result.compute_time_ms > 0


class TestDurationConvexity:
    """Tests for duration and convexity calculations."""
    
    def test_duration_calculation(self, bond_pricer):
        """Test Macaulay duration calculation."""
        price = 1000
        yield_rate = 0.05
        time_to_maturity = 5.0
        frequency = 2
        
        duration = bond_pricer.calculate_duration(
            price=price,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Duration should be less than time to maturity
        assert duration > 0
        assert duration < time_to_maturity
    
    def test_modified_duration(self, bond_pricer):
        """Test modified duration calculation."""
        duration = 4.0
        yield_rate = 0.05
        time_to_maturity = 5.0
        
        modified_duration = bond_pricer.calculate_modified_duration(
            duration=duration,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity
        )
        
        # Modified duration should be less than Macaulay duration
        assert modified_duration > 0
        assert modified_duration < duration
    
    def test_convexity(self, bond_pricer):
        """Test convexity calculation."""
        duration = 4.0
        yield_rate = 0.05
        time_to_maturity = 5.0
        frequency = 2
        
        convexity = bond_pricer.calculate_convexity(
            duration=duration,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Convexity should be positive
        assert convexity > 0


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_perpetual_bond(self, bond_pricer):
        """Test perpetual bond (very long maturity)."""
        face_value = 1000
        coupon_rate = 0.05
        yield_rate = 0.05
        time_to_maturity = 100.0
        frequency = 1
        
        price = bond_pricer.price_bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # Perpetual bond price = Coupon / Yield
        expected_price = face_value * coupon_rate / yield_rate
        
        assert abs(price - expected_price) < 10.0
    
    def test_high_yield_bond(self, bond_pricer):
        """Test high-yield bond pricing."""
        face_value = 1000
        coupon_rate = 0.10
        yield_rate = 0.20  # High yield
        time_to_maturity = 3.0
        frequency = 2
        
        price = bond_pricer.price_bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity,
            frequency=frequency
        )
        
        # High yield should mean significant discount
        assert price < face_value * 0.8
    
    def test_zero_coupon_bond_very_long(self, bond_pricer):
        """Test zero-coupon bond with very long maturity."""
        face_value = 1000
        yield_rate = 0.05
        time_to_maturity = 30.0
        
        price = bond_pricer.price_zero_coupon_bond(
            face_value=face_value,
            yield_rate=yield_rate,
            time_to_maturity=time_to_maturity
        )
        
        # Very long maturity = significantly discounted
        # Price = 1000 / (1 + 0.05*30) = 1000 / 2.5 = 400
        assert price < 500
        assert price > 0
    
    def test_performance_bond_pricing(self, bond_pricer):
        """Test that bond pricing is performant."""
        import time
        
        face_value = 1000
        coupon_rate = 0.05
        yield_rate = 0.05
        time_to_maturity = 5.0
        frequency = 2
        
        # Time batch pricing
        start = time.perf_counter()
        for _ in range(100):
            bond_pricer.price_bond(
                face_value=face_value,
                coupon_rate=coupon_rate,
                yield_rate=yield_rate,
                time_to_maturity=time_to_maturity,
                frequency=frequency
            )
        elapsed = time.perf_counter() - start
        
        # Should complete 100 prices in under 1 second
        assert elapsed < 1.0
