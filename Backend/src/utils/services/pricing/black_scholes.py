"""
High-Performance Black-Scholes Options Pricing
Vectorized implementation using NumPy for batch processing.

This module provides fast options pricing and Greeks calculation
with NumPy vectorization for performance optimization.
"""
import numpy as np
from typing import Tuple, Optional, Union
from dataclasses import dataclass
from scipy.stats import norm


@dataclass
class BlackScholesResult:
    """Result container for Black-Scholes pricing."""
    prices: np.ndarray
    deltas: np.ndarray
    gammas: np.ndarray
    vegas: np.ndarray
    thetas: np.ndarray
    rhos: np.ndarray
    compute_time_ms: float


class BlackScholesPricer:
    """
    Black-Scholes option pricing model with vectorized calculations.
    
    Supports batch processing for high-performance calculations.
    Uses NumPy broadcasting and vectorized operations.
    """
    
    @staticmethod
    def _cdf(x: np.ndarray) -> np.ndarray:
        """
        Cumulative distribution function for standard normal distribution.
        Vectorized implementation using scipy.stats.norm.
        """
        return norm.cdf(x)
    
    @staticmethod
    def _pdf(x: np.ndarray) -> np.ndarray:
        """
        Probability density function for standard normal distribution.
        """
        return norm.pdf(x)
    
    @staticmethod
    def _d1(
        S: Union[float, np.ndarray],
        K: Union[float, np.ndarray],
        T: Union[float, np.ndarray],
        r: float,
        sigma: Union[float, np.ndarray]
    ) -> np.ndarray:
        """
        Calculate d1 parameter for Black-Scholes formula.
        """
        S = np.asarray(S)
        K = np.asarray(K)
        T = np.asarray(T)
        sigma = np.asarray(sigma)
        
        numerator = np.log(S / K) + (r + 0.5 * sigma**2) * T
        denominator = sigma * np.sqrt(T)
        
        return numerator / denominator
    
    @staticmethod
    def _d2(
        d1: np.ndarray,
        T: Union[float, np.ndarray],
        sigma: Union[float, np.ndarray]
    ) -> np.ndarray:
        """
        Calculate d2 parameter for Black-Scholes formula.
        """
        T = np.asarray(T)
        sigma = np.asarray(sigma)
        
        return d1 - sigma * np.sqrt(T)
    
    def price(
        self,
        S: Union[float, np.ndarray],
        K: Union[float, np.ndarray],
        T: Union[float, np.ndarray],
        r: float,
        sigma: Union[float, np.ndarray],
        option_type: str = 'call'
    ) -> np.ndarray:
        """
        Calculate option prices using Black-Scholes formula.
        
        Parameters:
        -----------
        S : float or np.ndarray
            Underlying asset price(s)
        K : float or np.ndarray
            Strike price(s)
        T : float or np.ndarray
            Time to expiration in years
        r : float
            Risk-free interest rate (annualized)
        sigma : float or np.ndarray
            Volatility (annualized)
        option_type : str
            'call' or 'put'
        
        Returns:
        --------
        np.ndarray
            Option prices
        """
        start_time = np.datetime64('now').astype(np.int64)
        
        S = np.asarray(S)
        K = np.asarray(K)
        T = np.asarray(T)
        sigma = np.asarray(sigma)
        
        # Ensure T > 0 to avoid division by zero
        T = np.maximum(T, 1e-10)
        
        d1 = self._d1(S, K, T, r, sigma)
        d2 = self._d2(d1, T, sigma)
        
        if option_type.lower() == 'call':
            prices = S * self._cdf(d1) - K * np.exp(-r * T) * self._cdf(d2)
        else:
            prices = K * np.exp(-r * T) * self._cdf(-d2) - S * self._cdf(-d1)
        
        compute_time = (np.datetime64('now').astype(np.int64) - start_time) / 1_000_000
        
        return np.maximum(prices, 0)  # Ensure non-negative prices
    
    def calculate_greeks(
        self,
        S: Union[float, np.ndarray],
        K: Union[float, np.ndarray],
        T: Union[float, np.ndarray],
        r: float,
        sigma: Union[float, np.ndarray],
        option_type: str = 'call'
    ) -> BlackScholesResult:
        """
        Calculate option prices and all Greeks in a single pass.
        
        Parameters:
        -----------
        Same as price() method
        
        Returns:
        --------
        BlackScholesResult
            Contains prices, deltas, gammas, vegas, thetas, rhos
        """
        import time
        start_time = time.perf_counter()
        
        S = np.asarray(S)
        K = np.asarray(K)
        T = np.asarray(T)
        sigma = np.asarray(sigma)
        
        # Ensure T > 0 to avoid division by zero
        T = np.maximum(T, 1e-10)
        
        d1 = self._d1(S, K, T, r, sigma)
        d2 = self._d2(d1, T, sigma)
        
        sqrt_T = np.sqrt(T)
        pdf_d1 = self._pdf(d1)
        cdf_d1 = self._cdf(d1)
        cfd_d2 = self._cdf(d2)  # CDF of d2
        
        exp_minus_rT = np.exp(-r * T)
        
        # Price
        if option_type.lower() == 'call':
            prices = S * cdf_d1 - K * exp_minus_rT * cfd_d2
        else:
            prices = K * exp_minus_rT * self._cdf(-d2) - S * self._cdf(-d1)
        
        prices = np.maximum(prices, 0)
        
        # Delta
        if option_type.lower() == 'call':
            deltas = cdf_d1
        else:
            deltas = cdf_d1 - 1
        
        # Gamma (same for calls and puts)
        gammas = pdf_d1 / (S * sigma * sqrt_T)
        
        # Vega (same for calls and puts)
        vegas = S * sqrt_T * pdf_d1 / 100  # Per 1% volatility change
        
        # Theta
        if option_type.lower() == 'call':
            theta1 = -S * pdf_d1 * sigma / (2 * sqrt_T)
            theta2 = -r * K * exp_minus_rT * cfd_d2
            thetas = (theta1 + theta2) / 365  # Per day
        else:
            theta1 = -S * pdf_d1 * sigma / (2 * sqrt_T)
            theta2 = r * K * exp_minus_rT * self._cdf(-d2)
            thetas = (theta1 + theta2) / 365  # Per day
        
        # Rho
        if option_type.lower() == 'call':
            rhos = K * T * exp_minus_rT * cfd_d2 / 100  # Per 1% rate change
        else:
            rhos = -K * T * exp_minus_rT * self._cdf(-d2) / 100  # Per 1% rate change
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return BlackScholesResult(
            prices=prices,
            deltas=deltas,
            gammas=gammas,
            vegas=vegas,
            thetas=thetas,
            rhos=rhos,
            compute_time_ms=compute_time_ms
        )
    
    def price_batch(
        self,
        underlying_prices: np.ndarray,
        strikes: np.ndarray,
        expirations: np.ndarray,
        r: float,
        volatilities: np.ndarray,
        option_type: str = 'call'
    ) -> BlackScholesResult:
        """
        Batch price options across multiple strikes, expirations, and volatilities.
        
        Uses broadcasting for efficient batch processing.
        
        Parameters:
        -----------
        underlying_prices : np.ndarray
            Array of underlying prices (shape: [n_prices,])
        strikes : np.ndarray
            Array of strike prices (shape: [n_strikes,])
        expirations : np.ndarray
            Array of times to expiration (shape: [n_expirations,])
        r : float
            Risk-free rate
        volatilities : np.ndarray
            Array of volatilities (shape: [n_vols,])
        option_type : str
            'call' or 'put'
        
        Returns:
        --------
        BlackScholesResult
            Arrays of shape [n_prices, n_strikes, n_expirations, n_vols]
        """
        # Reshape for broadcasting
        S = underlying_prices[:, np.newaxis, np.newaxis, np.newaxis]
        K = strikes[np.newaxis, :, np.newaxis, np.newaxis]
        T = expirations[np.newaxis, np.newaxis, :, np.newaxis]
        sigma = volatilities[np.newaxis, np.newaxis, np.newaxis, :]
        
        return self.calculate_greeks(S, K, T, r, sigma, option_type)
    
    def implied_volatility(
        self,
        market_price: Union[float, np.ndarray],
        S: Union[float, np.ndarray],
        K: Union[float, np.ndarray],
        T: Union[float, np.ndarray],
        r: float,
        option_type: str = 'call',
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> np.ndarray:
        """
        Calculate implied volatility using Newton-Raphson method.
        
        Parameters:
        -----------
        market_price : float or np.ndarray
            Observed market price(s)
        S : float or np.ndarray
            Underlying price(s)
        K : float or np.ndarray
            Strike price(s)
        T : float or np.ndarray
            Time to expiration
        r : float
            Risk-free rate
        option_type : str
            'call' or 'put'
        max_iterations : int
            Maximum iterations for Newton-Raphson
        tolerance : float
            Convergence tolerance
        
        Returns:
        --------
        np.ndarray
            Implied volatilities
        """
        market_price = np.asarray(market_price)
        S = np.asarray(S)
        K = np.asarray(K)
        T = np.asarray(T)
        
        # Initial guess (use at-the-money volatility as starting point)
        sigma = np.full_like(market_price, 0.3)  # 30% volatility
        
        for _ in range(max_iterations):
            # Price with current volatility guess
            greeks = self.calculate_greeks(S, K, T, r, sigma, option_type)
            model_price = greeks.prices
            vega = greeks.vegas * 100  # Convert back from per 1%
            
            # Check for convergence
            price_diff = model_price - market_price
            if np.all(np.abs(price_diff) < tolerance):
                break
            
            # Newton-Raphson update
            # Avoid division by zero
            vega = np.where(np.abs(vega) < 1e-10, 1e-10, vega)
            sigma = sigma - price_diff / vega
            
            # Ensure positive volatility
            sigma = np.maximum(sigma, 0.001)  # Minimum 0.1%
        
        return sigma


def get_black_scholes_pricer() -> BlackScholesPricer:
    """
    Get singleton instance of Black-Scholes pricer.
    """
    return BlackScholesPricer()
