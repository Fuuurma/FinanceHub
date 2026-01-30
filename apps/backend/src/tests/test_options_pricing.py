"""
Tests for Options Pricing API (Black-Scholes)
"""
import pytest
import numpy as np
from utils.services.pricing.black_scholes import BlackScholesPricer, BlackScholesResult


@pytest.fixture
def bs_pricer():
    """Create Black-Scholes pricer instance."""
    return BlackScholesPricer()


class TestBlackScholesPricer:
    """Tests for Black-Scholes pricing algorithm."""
    
    def test_atm_call_price(self, bs_pricer):
        """Test ATM call option pricing."""
        S = 100.0  # Underlying price
        K = 100.0  # Strike price
        T = 0.5    # 6 months
        r = 0.05    # 5% risk-free rate
        sigma = 0.2  # 20% volatility
        
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        
        # ATM call should have positive value
        assert price > 0
        # Should be reasonable (not negative or extreme)
        assert price < S  # Price can't be greater than underlying
        
    def test_itm_call_price(self, bs_pricer):
        """Test ITM call option pricing."""
        S = 110.0  # Above strike
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        
        # ITM call should have significant intrinsic value
        intrinsic_value = max(S - K, 0)
        assert price >= intrinsic_value - 1.0  # Allow for rounding
    
    def test_otm_call_price(self, bs_pricer):
        """Test OTM call option pricing."""
        S = 90.0   # Below strike
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        
        # OTM call should be mostly time value
        assert price < K  # Price less than strike
        assert price > 0  # But still positive due to time value
        
    def test_atm_put_price(self, bs_pricer):
        """Test ATM put option pricing."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        price = bs_pricer.price(S, K, T, r, sigma, 'put')
        
        # ATM put should have positive value
        assert price > 0
        assert price < K
        
    def test_itm_put_price(self, bs_pricer):
        """Test ITM put option pricing."""
        S = 90.0   # Below strike
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        price = bs_pricer.price(S, K, T, r, sigma, 'put')
        
        # ITM put should have significant intrinsic value
        intrinsic_value = max(K - S, 0)
        assert price >= intrinsic_value - 1.0
    
    def test_greeks_call(self, bs_pricer):
        """Test Greeks calculation for call option."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        result = bs_pricer.calculate_greeks(S, K, T, r, sigma, 'call')
        
        assert result is not None
        assert hasattr(result, 'prices')
        assert hasattr(result, 'deltas')
        assert hasattr(result, 'gammas')
        assert hasattr(result, 'vegas')
        assert hasattr(result, 'thetas')
        assert hasattr(result, 'rhos')
        
        # Delta should be positive for call (0 to 1)
        delta_value = float(result.deltas) if np.isscalar(result.deltas) else result.deltas[0]
        assert delta_value > 0 and delta_value <= 1
        
        # Gamma should be positive
        gamma_value = float(result.gammas) if np.isscalar(result.gammas) else result.gammas[0]
        assert gamma_value > 0
        
        # Vega should be positive (sensitivity to volatility)
        vega_value = float(result.vegas) if np.isscalar(result.vegas) else result.vegas[0]
        assert vega_value > 0
        
        # Theta should be negative (time decay)
        theta_value = float(result.thetas) if np.isscalar(result.thetas) else result.thetas[0]
        assert theta_value < 0
        
        # Rho should be positive for call
        rho_value = float(result.rhos) if np.isscalar(result.rhos) else result.rhos[0]
        assert rho_value > 0
        
        # Performance check
        assert result.compute_time_ms < 100  # Should be fast
    
    def test_greeks_put(self, bs_pricer):
        """Test Greeks calculation for put option."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        result = bs_pricer.calculate_greeks(S, K, T, r, sigma, 'put')
        
        # Delta should be negative for put (-1 to 0)
        delta_value = result.deltas.item() if result.deltas.ndim > 0 else result.deltas
        assert delta_value < 0 and delta_value >= -1
        
        # Rho should be negative for put
        rho_value = result.rhos.item() if result.rhos.ndim > 0 else result.rhos
        assert rho_value < 0
    
    def test_put_call_parity(self, bs_pricer):
        """Test put-call parity relationship."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.2
        
        call_price = bs_pricer.price(S, K, T, r, sigma, 'call')
        put_price = bs_pricer.price(S, K, T, r, sigma, 'put')
        
        # Put-call parity: C - P = S - K * exp(-rT)
        lhs = call_price - put_price
        rhs = S - K * np.exp(-r * T)
        
        assert abs(lhs - rhs) < 0.01  # Within 1 cent
    
    def test_batch_pricing(self, bs_pricer):
        """Test batch pricing with multiple options."""
        underlying_prices = np.array([90.0, 100.0, 110.0])
        strikes = np.array([95.0, 100.0, 105.0])
        expirations = np.array([0.25, 0.5, 1.0])
        volatilities = np.array([0.15, 0.20, 0.25])
        
        result = bs_pricer.price_batch(
            underlying_prices=underlying_prices,
            strikes=strikes,
            expirations=expirations,
            r=0.05,
            volatilities=volatilities,
            option_type='call'
        )
        
        # Should return 3x3x3x3 = 27 prices
        assert result.prices.shape == (3, 3, 3, 3)
        assert result.compute_time_ms < 100  # Should still be fast
        
        # All prices should be positive
        assert np.all(result.prices >= 0)
        assert np.all(result.prices <= 150)  # Reasonable upper bound
    
    def test_implied_volatility(self, bs_pricer):
        """Test implied volatility calculation."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        
        # Get price at known volatility
        known_sigma = 0.20
        market_price = bs_pricer.price(S, K, T, r, known_sigma, 'call')
        
        # Calculate implied volatility from market price
        iv = bs_pricer.implied_volatility(
            market_price=market_price,
            S=S,
            K=K,
            T=T,
            r=r,
            option_type='call',
            max_iterations=100,
            tolerance=1e-6
        )
        
        # Should converge to close to known volatility
        assert abs(iv - known_sigma) < 0.01  # Within 1%


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_zero_time_to_expiration(self, bs_pricer):
        """Test option at expiration (time decay)."""
        S = 100.0
        K = 100.0
        T = 0.0
        r = 0.05
        sigma = 0.2
        
        # At expiration, price should equal intrinsic value
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        intrinsic_value = max(S - K, 0)
        
        assert abs(price - intrinsic_value) < 0.01
    
    def test_zero_volatility(self, bs_pricer):
        """Test option with zero volatility (certain outcome)."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 0.0
        
        # With zero volatility, option should be worth intrinsic value
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        forward_price = S * np.exp(r * T)
        expected_price = max(forward_price - K, 0) * np.exp(-r * T)
        
        assert abs(price - expected_price) < 0.01
    
    def test_very_high_volatility(self, bs_pricer):
        """Test option with very high volatility."""
        S = 100.0
        K = 100.0
        T = 0.5
        r = 0.05
        sigma = 2.0  # 200% volatility
        
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        
        # High volatility should increase option value
        # But still bounded by underlying price
        assert price > 0
        assert price < S * 1.5  # Not more than 1.5x underlying
    
    def test_long_dated_option(self, bs_pricer):
        """Test long-dated option (5 years)."""
        S = 100.0
        K = 100.0
        T = 5.0
        r = 0.05
        sigma = 0.2
        
        price = bs_pricer.price(S, K, T, r, sigma, 'call')
        
        # Long-dated options should have significant time value
        assert price > 0
        # But still reasonable
        assert price < S * 2.0
    
    def test_batch_performance(self, bs_pricer):
        """Test that batch pricing is fast."""
        import time
        
        underlying_prices = np.random.uniform(90, 110, 100)
        strikes = np.random.uniform(95, 105, 50)
        expirations = np.random.uniform(0.1, 1.0, 20)
        
        # Batch pricing
        start = time.perf_counter()
        batch_result = bs_pricer.price_batch(
            underlying_prices=underlying_prices,
            strikes=strikes,
            expirations=expirations,
            r=0.05,
            volatilities=np.array([0.2]),
            option_type='call'
        )
        batch_time = time.perf_counter() - start
        
        assert batch_result.prices.shape == (100, 50, 20, 1)
        assert batch_time < 1.0  # Should complete in < 1 second
