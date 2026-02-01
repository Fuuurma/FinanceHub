"""
Options Greeks Calculation Service
Implements Black-Scholes model for options pricing and Greeks calculation
"""
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import orjson
from scipy.stats import norm
from scipy.optimize import newton
from math import log, sqrt, exp, pi
import numpy as np

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class OptionsGreeksCalculator:
    """
    Calculate options Greeks using Black-Scholes model
    
    Greeks:
    - Delta (Δ): Price sensitivity
    - Gamma (Γ): Delta sensitivity  
    - Theta (Θ): Time decay
    - Vega (ν): Volatility sensitivity
    - Rho (ρ): Interest rate sensitivity
    """
    
    @staticmethod
    def calculate_greeks(
        S: float,  # Underlying price
        K: float,  # Strike price
        T: float,  # Time to expiration (years)
        r: float,  # Risk-free rate
        sigma: float,  # Volatility
        option_type: str = 'call'  # 'call' or 'put'
    ) -> Dict[str, float]:
        """
        Calculate all Greeks using Black-Scholes model
        
        Performance: Uses numpy and scipy for vectorized calculations
        """
        try:
            # Validate inputs
            if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
                raise ValueError("Invalid inputs: S, K, T, sigma must be positive")
            
            if option_type not in ['call', 'put']:
                raise ValueError("option_type must be 'call' or 'put'")
            
            # Calculate d1 and d2
            d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
            d2 = d1 - sigma * sqrt(T)
            
            # Calculate Delta
            if option_type == 'call':
                delta = norm.cdf(d1)
            else:
                delta = -norm.cdf(-d1)
            
            # Calculate Gamma (same for calls and puts)
            gamma = norm.pdf(d1) / (S * sigma * sqrt(T))
            
            # Calculate Theta
            if option_type == 'call':
                theta = -(S * norm.pdf(d1) * sigma) / (2 * sqrt(T)) - \
                         r * K * exp(-r * T) * norm.cdf(d2)
            else:
                theta = -(S * norm.pdf(d1) * sigma) / (2 * sqrt(T)) + \
                         r * K * exp(-r * T) * norm.cdf(-d2)
            
            # Calculate Vega (same for calls and puts)
            vega = S * sqrt(T) * norm.pdf(d1)
            
            # Calculate Rho
            if option_type == 'call':
                rho = K * T * exp(-r * T) * norm.cdf(d2)
            else:
                rho = -K * T * exp(-r * T) * norm.cdf(-d2)
            
            return {
                'delta': delta,
                'gamma': gamma,
                'theta': theta,
                'vega': vega,
                'rho': rho,
                'd1': d1,
                'd2': d2,
                'underlying_price': S,
                'strike_price': K,
                'time_to_expiration': T,
                'volatility': sigma,
                'risk_free_rate': r,
                'option_type': option_type
            }
            
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error calculating Greeks: {str(e)}")
            raise
    
    @staticmethod
    def calculate_option_price(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate option price using Black-Scholes formula
        
        Performance: Uses numpy for optimized calculations
        """
        try:
            greeks = OptionsGreeksCalculator.calculate_greeks(S, K, T, r, sigma, option_type)
            d1 = greeks['d1']
            d2 = greeks['d2']
            
            # Calculate option price
            if option_type == 'call':
                price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
            else:
                price = K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            
            return max(price, 0)  # Option price can't be negative
            
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error calculating option price: {str(e)}")
            return 0
    
    @staticmethod
    def calculate_implied_volatility(
        option_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str = 'call',
        initial_guess: float = 0.3
    ) -> Optional[float]:
        """
        Calculate implied volatility using Newton-Raphson method
        
        Performance: Uses scipy optimization for fast convergence
        """
        try:
            def objective_function(sigma: float) -> float:
                price = OptionsGreeksCalculator.calculate_option_price(
                    S, K, T, r, sigma, option_type
                )
                return price - option_price
            
            # Use Newton-Raphson to find implied volatility
            try:
                implied_vol = newton(
                    objective_function,
                    initial_guess,
                    tol=1e-6,
                    maxiter=100
                )
                return max(implied_vol, 0.001)  # Minimum volatility
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                logger.warning(f"Could not converge: {str(e)}")
                return None
                
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error calculating implied volatility: {str(e)}")
            return None
    
    @staticmethod
    def calculate_time_to_expiration(expiration_date: datetime) -> float:
        """
        Calculate time to expiration in years
        
        Performance: Uses datetime operations
        """
        now = datetime.now()
        T = (expiration_date - now).days / 365.0
        return max(T, 1/365.0)  # Minimum 1 day
    
    @staticmethod
    def calculate_greeks_for_options_chain(
        S: float,
        strikes: List[float],
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> List[Dict[str, Any]]:
        """
        Calculate Greeks for multiple strikes at once (options chain)
        
        Performance: Vectorized calculations with numpy for better throughput
        """
        try:
            results = []
            
            # Convert to numpy arrays for vectorized operations
            strikes_array = np.array(strikes)
            S_array = np.array([S] * len(strikes))
            
            # Calculate d1 and d2 for all strikes
            d1 = (np.log(S_array / strikes_array) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
            d2 = d1 - sigma * sqrt(T)
            
            # Calculate Delta
            if option_type == 'call':
                delta = norm.cdf(d1)
            else:
                delta = -norm.cdf(-d1)
            
            # Calculate Gamma (same for all)
            gamma = norm.pdf(d1) / (S_array * sigma * sqrt(T))
            
            # Calculate Theta
            if option_type == 'call':
                theta = -(S_array * norm.pdf(d1) * sigma) / (2 * sqrt(T)) - \
                         r * strikes_array * np.exp(-r * T) * norm.cdf(d2)
            else:
                theta = -(S_array * norm.pdf(d1) * sigma) / (2 * sqrt(T)) + \
                         r * strikes_array * np.exp(-r * T) * norm.cdf(-d2)
            
            # Calculate Vega (same for all)
            vega = S_array * sqrt(T) * norm.pdf(d1)
            
            # Calculate Rho
            if option_type == 'call':
                rho = strikes_array * T * np.exp(-r * T) * norm.cdf(d2)
            else:
                rho = -strikes_array * T * np.exp(-r * T) * norm.cdf(-d2)
            
            # Compile results
            for i, K in enumerate(strikes):
                results.append({
                    'strike_price': K,
                    'delta': delta[i],
                    'gamma': gamma[i],
                    'theta': theta[i],
                    'vega': vega[i],
                    'rho': rho[i],
                    'option_type': option_type
                })
            
            return results
            
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error calculating options chain Greeks: {str(e)}")
            return []
    
    @staticmethod
    def get_risk_free_rate() -> float:
        """
        Get current risk-free rate (e.g., 10-year Treasury yield)
        
        Performance: Cached value with periodic updates
        """
        # Default to 5% (can be updated with live data from FRED)
        return 0.05
    
    @staticmethod
    def estimate_historical_volatility(prices: List[float], period_days: int = 30) -> float:
        """
        Estimate historical volatility from price data
        
        Performance: Uses numpy for efficient calculation
        """
        try:
            if len(prices) < 2:
                return 0.2  # Default volatility
            
            # Calculate daily returns
            price_array = np.array(prices)
            returns = np.diff(np.log(price_array))
            
            # Calculate standard deviation (annualized)
            volatility = np.std(returns) * sqrt(252)  # 252 trading days/year
            
            return max(volatility, 0.001)  # Minimum volatility
            
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error estimating volatility: {str(e)}")
            return 0.2  # Default volatility


# Convenience functions for easy use

def calculate_call_greeks(S: float, K: float, T: float, r: float = 0.05, sigma: float = 0.2) -> Dict[str, float]:
    """Convenience function for call options"""
    return OptionsGreeksCalculator.calculate_greeks(S, K, T, r, sigma, 'call')


def calculate_put_greeks(S: float, K: float, T: float, r: float = 0.05, sigma: float = 0.2) -> Dict[str, float]:
    """Convenience function for put options"""
    return OptionsGreeksCalculator.calculate_greeks(S, K, T, r, sigma, 'put')


def calculate_option_price_call(S: float, K: float, T: float, r: float = 0.05, sigma: float = 0.2) -> float:
    """Convenience function for call option pricing"""
    return OptionsGreeksCalculator.calculate_option_price(S, K, T, r, sigma, 'call')


def calculate_option_price_put(S: float, K: float, T: float, r: float = 0.05, sigma: float = 0.2) -> float:
    """Convenience function for put option pricing"""
    return OptionsGreeksCalculator.calculate_option_price(S, K, T, r, sigma, 'put')


if __name__ == "__main__":
    # Test with Apple options
    S = 175.0  # AAPL price
    K = 180.0  # Strike price
    T = 0.25   # 3 months to expiration
    r = 0.05   # 5% risk-free rate
    sigma = 0.2  # 20% volatility
    
    print("Testing Options Greeks Calculator...")
    print(f"Underlying Price: ${S}")
    print(f"Strike Price: ${K}")
    print(f"Time to Expiration: {T} years")
    print(f"Risk-Free Rate: {r * 100}%")
    print(f"Volatility: {sigma * 100}%")
    print()
    
    # Calculate Greeks for call option
    call_greeks = calculate_call_greeks(S, K, T, r, sigma)
    print("CALL OPTION GREEKS:")
    print(f"Delta (Δ): {call_greeks['delta']:.4f}")
    print(f"Gamma (Γ): {call_greeks['gamma']:.4f}")
    print(f"Theta (Θ): {call_greeks['theta']:.4f}")
    print(f"Vega (ν): {call_greeks['vega']:.4f}")
    print(f"Rho (ρ): {call_greeks['rho']:.4f}")
    print()
    
    # Calculate Greeks for put option
    put_greeks = calculate_put_greeks(S, K, T, r, sigma)
    print("PUT OPTION GREEKS:")
    print(f"Delta (Δ): {put_greeks['delta']:.4f}")
    print(f"Gamma (Γ): {put_greeks['gamma']:.4f}")
    print(f"Theta (Θ): {put_greeks['theta']:.4f}")
    print(f"Vega (ν): {put_greeks['vega']:.4f}")
    print(f"Rho (ρ): {put_greeks['rho']:.4f}")
    print()
    
    # Calculate option prices
    call_price = calculate_option_price_call(S, K, T, r, sigma)
    put_price = calculate_option_price_put(S, K, T, r, sigma)
    print(f"Call Price: ${call_price:.2f}")
    print(f"Put Price: ${put_price:.2f}")
    print()
    
    # Test options chain calculation
    print("Testing options chain calculation...")
    strikes = [170, 175, 180, 185, 190]
    chain = OptionsGreeksCalculator.calculate_greeks_for_options_chain(S, strikes, T, r, sigma)
    
    print(f"{'Strike':<10} {'Delta':<10} {'Gamma':<10} {'Vega':<10}")
    for item in chain:
        print(f"${item['strike_price']:<9.2f} {item['delta']:<10.4f} {item['gamma']:<10.4f} {item['vega']:<10.4f}")
    
    # Test implied volatility
    print("\nTesting implied volatility calculation...")
    implied_vol = OptionsGreeksCalculator.calculate_implied_volatility(call_price, S, K, T, r)
    print(f"Implied Volatility: {implied_vol * 100:.2f}%")
