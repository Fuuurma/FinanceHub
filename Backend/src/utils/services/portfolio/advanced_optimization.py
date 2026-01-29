"""
Advanced Portfolio Optimization Models
High-performance implementation of portfolio optimization algorithms.
"""
import numpy as np
from typing import Tuple, Optional, Dict, List, Union
from dataclasses import dataclass
from scipy.optimize import minimize


@dataclass
class OptimizationResult:
    """Result container for portfolio optimization."""
    weights: np.ndarray
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    success: bool
    message: str
    iterations: int = 0
    compute_time_ms: float = 0.0


@dataclass
class BlackLittermanResult:
    """Result container for Black-Litterman model."""
    weights: np.ndarray
    expected_returns: np.ndarray
    expected_risk: float
    shrinkage_factor: float
    tau: float
    success: bool
    message: str
    compute_time_ms: float = 0.0


@dataclass
class RiskParityResult:
    """Result container for risk parity optimization."""
    weights: np.ndarray
    risk_contributions: np.ndarray
    marginal_risk_contributions: np.ndarray
    risk_budget: float
    success: bool
    message: str
    compute_time_ms: float = 0.0


class PortfolioOptimizer:
    """
    Advanced portfolio optimization with multiple strategies.
    
    Supports:
    - Mean-variance optimization (efficient frontier)
    - Black-Litterman model (Bayesian shrinkage)
    - Risk parity (equal risk contribution)
    - CVaR optimization (expected shortfall)
    """
    
    def __init__(self, returns: np.ndarray, risk_free_rate: float = 0.03):
        """
        Initialize optimizer with historical returns.
        
        Parameters:
        -----------
        returns : np.ndarray
            Historical returns matrix (assets x periods)
        risk_free_rate : float
            Annualized risk-free rate
        """
        self.returns = np.asarray(returns)
        self.risk_free_rate = risk_free_rate
        self.n_assets = returns.shape[0] if returns.ndim > 1 else 1
        self.n_periods = returns.shape[1] if returns.ndim > 1 else 1
        
    def mean_variance_optimization(
        self,
        target_return: Optional[float] = None,
        method: str = 'max_sharpe'
    ) -> OptimizationResult:
        """
        Mean-variance optimization for efficient frontier.
        
        Parameters:
        -----------
        target_return : float, optional
            Target expected return (for efficient frontier)
        method : str
            'max_sharpe' or 'min_variance'
        
        Returns:
        --------
        OptimizationResult
            Optimal weights and metrics
        """
        import time
        start_time = time.perf_counter()
        
        # Calculate expected returns and covariance
        mu = np.mean(self.returns, axis=1)
        cov = np.cov(self.returns)
        
        # Objective function
        def portfolio_variance(weights):
            return weights.T @ cov @ weights
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},  # Weights sum to 1
        ]
        
        bounds = [(0.0, 1.0) for _ in range(self.n_assets)]  # Long-only, max 100%
        
        # Initial guess (equal weights)
        x0 = np.ones(self.n_assets) / self.n_assets
        
        if method == 'max_sharpe':
            # Maximize Sharpe ratio
            def neg_sharpe(weights):
                portfolio_return = weights @ mu
                portfolio_risk = np.sqrt(portfolio_variance(weights) + 1e-10)
                return -(portfolio_return - self.risk_free_rate) / portfolio_risk
            
            result = minimize(neg_sharpe, x0, bounds=bounds, constraints=constraints, method='SLSQP')
            message = "Maximized Sharpe ratio"
            
        elif method == 'min_variance':
            # Minimize portfolio variance
            result = minimize(portfolio_variance, x0, bounds=bounds, constraints=constraints, method='SLSQP')
            message = "Minimized portfolio variance"
        else:
            raise ValueError(f"Unknown method: {method}")
        
        weights = result.x
        expected_return = weights @ mu
        expected_risk = np.sqrt(portfolio_variance(weights))
        sharpe_ratio = (expected_return - self.risk_free_rate) / expected_risk if expected_risk > 0 else 0
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return OptimizationResult(
            weights=weights,
            expected_return=expected_return,
            expected_risk=expected_risk,
            sharpe_ratio=sharpe_ratio,
            success=result.success,
            message=message,
            iterations=result.nit,
            compute_time_ms=compute_time_ms
        )
    
    def black_litterman_model(
        self,
        market_caps: np.ndarray,
        tau: float = 0.25,
        view_matrix: Optional[np.ndarray] = None,
        view_picking: Optional[np.ndarray] = None,
        omega: Optional[np.ndarray] = None
    ) -> BlackLittermanResult:
        """
        Black-Litterman model with Bayesian shrinkage.
        
        Combines investor views with market equilibrium.
        
        Parameters:
        -----------
        market_caps : np.ndarray
            Market capitalizations for shrinkage
        tau : float
            Shrinkage intensity (lower = more shrinkage)
        view_matrix : np.ndarray, optional
            Investor views (P x N matrix)
        view_picking : np.ndarray, optional
            P x P matrix for view selection
        omega : np.ndarray, optional
            Uncertainty in views (P x P)
        
        Returns:
        --------
        BlackLittermanResult
            Shrinked expected returns and optimal weights
        """
        import time
        start_time = time.perf_counter()
        
        # Calculate equilibrium returns (market-weighted)
        mu_eq = np.mean(self.returns, axis=1)
        
        # Calculate shrinkage factor based on market cap
        market_cap_weights = market_caps / np.sum(market_caps)
        shrinkage_factor = (tau * np.cov(self.returns)) @ market_cap_weights
        
        # Shrink towards market equilibrium
        mu_bl = (np.linalg.inv(tau * np.cov(self.returns)) + shrinkage_factor) @ (
            tau * np.linalg.inv(tau * np.cov(self.returns)) @ mu_eq
        )
        
        # If investor views provided, incorporate them
        if view_matrix is not None and view_picking is not None:
            P, Q = view_picking.shape
            omega = omega if omega is not None else np.eye(P)
            
            # Black-Litterman formula
            M = np.linalg.inv(np.linalg.inv(tau * np.cov(self.returns)) + P.T @ omega @ P)
            mu_adjusted = mu_bl + (P.T @ M @ (view_matrix - P @ mu_bl))
        else:
            mu_adjusted = mu_bl
            tau = tau
            shrinkage_factor = np.mean(shrinkage_factor)
        
        # Optimize with adjusted returns
        cov = np.cov(self.returns)
        
        def portfolio_variance(weights):
            return weights.T @ cov @ weights
        
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
        ]
        bounds = [(0.0, 1.0) for _ in range(self.n_assets)]
        x0 = np.ones(self.n_assets) / self.n_assets
        
        result = minimize(portfolio_variance, x0, bounds=bounds, constraints=constraints, method='SLSQP')
        
        weights = result.x
        expected_return = weights @ mu_adjusted
        expected_risk = np.sqrt(portfolio_variance(weights))
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return BlackLittermanResult(
            weights=weights,
            expected_returns=mu_adjusted,
            expected_risk=expected_risk,
            shrinkage_factor=np.mean(shrinkage_factor),
            tau=tau,
            success=result.success,
            message="Black-Litterman optimization complete",
            compute_time_ms=compute_time_ms
        )
    
    def risk_parity_optimization(
        self,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> RiskParityResult:
        """
        Risk parity optimization - equalize risk contributions.
        
        Each asset contributes equal risk to the portfolio.
        
        Parameters:
        -----------
        max_iterations : int
            Maximum iterations for convergence
        tolerance : float
            Convergence tolerance
        
        Returns:
        --------
        RiskParityResult
            Weights, risk contributions, and marginal risk contributions
        """
        import time
        start_time = time.perf_counter()
        
        # Calculate covariance
        cov = np.cov(self.returns)
        asset_stds = np.sqrt(np.diag(cov))
        
        # Risk budget (equal contribution per asset)
        risk_budget = np.ones(self.n_assets) / self.n_assets
        
        # Initial weights (inverse volatility)
        weights = 1.0 / asset_stds
        weights = weights / np.sum(weights)
        
        # Iterative solution using cyclical coordinate descent
        for iteration in range(max_iterations):
            weights_old = weights.copy()
            
            # Update weights based on risk contributions
            marginal_risk_contributions = cov @ weights
            risk_contributions = weights * marginal_risk_contributions
            
            # Scale weights to match risk budget
            scaling_factors = risk_budget / (risk_contributions + 1e-10)
            weights = weights * scaling_factors
            
            # Re-normalize weights
            weights = weights / np.sum(weights)
            
            # Check convergence
            weight_change = np.max(np.abs(weights - weights_old))
            if weight_change < tolerance:
                break
        
        final_risk_contributions = weights * (cov @ weights)
        final_marginal_risk_contributions = cov @ weights
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return RiskParityResult(
            weights=weights,
            risk_contributions=final_risk_contributions,
            marginal_risk_contributions=final_marginal_risk_contributions,
            risk_budget=risk_budget[0],
            success=True,
            message=f"Risk parity converged in {iteration + 1} iterations",
            compute_time_ms=compute_time_ms
        )
    
    def cvar_optimization(
        self,
        confidence_level: float = 0.95,
        n_simulations: int = 10000,
        target_return: Optional[float] = None
    ) -> OptimizationResult:
        """
        CVaR optimization - minimize expected shortfall.
        
        Parameters:
        -----------
        confidence_level : float
            CVaR confidence level (e.g., 0.95 for 95%)
        n_simulations : int
            Number of Monte Carlo simulations
        target_return : float, optional
            Target expected return constraint
        
        Returns:
        --------
        OptimizationResult
            CVaR-optimal weights
        """
        import time
        start_time = time.perf_counter()
        
        # Calculate expected returns
        mu = np.mean(self.returns, axis=1)
        cov = np.cov(self.returns)
        
        # Generate scenarios via Cholesky decomposition
        L = np.linalg.cholesky(cov)
        n_periods = self.n_periods
        scenario_returns = np.random.randn(n_simulations, self.n_assets)
        scenario_returns = scenario_returns @ L.T
        scenario_returns = scenario_returns + mu
        
        # CVaR objective function
        def cvar_objective(weights):
            portfolio_returns = scenario_returns @ weights
            
            # VaR
            var_index = int((1 - confidence_level) * n_simulations)
            var = portfolio_returns[var_index]
            
            # CVaR: expected shortfall beyond VaR
            shortfall_mask = portfolio_returns < var
            cvar = var + np.mean(portfolio_returns[shortfall_mask] - var)
            
            # Minimize CVaR
            return cvar
        
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
        ]
        
        if target_return is not None:
            constraints.append({
                'type': 'ineq',
                'fun': lambda w: (w @ mu) - target_return
            })
        
        bounds = [(0.0, 1.0) for _ in range(self.n_assets)]
        x0 = np.ones(self.n_assets) / self.n_assets
        
        result = minimize(cvar_objective, x0, bounds=bounds, constraints=constraints, method='SLSQP')
        
        weights = result.x
        expected_return = weights @ mu
        expected_risk = np.sqrt(weights.T @ cov @ weights)
        sharpe_ratio = (expected_return - self.risk_free_rate) / expected_risk if expected_risk > 0 else 0
        
        compute_time_ms = (time.perf_counter() - start_time) * 1000
        
        return OptimizationResult(
            weights=weights,
            expected_return=expected_return,
            expected_risk=expected_risk,
            sharpe_ratio=sharpe_ratio,
            success=result.success,
            message=f"CVaR optimization at {confidence_level:.0%} confidence level",
            iterations=result.nit,
            compute_time_ms=compute_time_ms
        )
    
    def efficient_frontier(
        self,
        n_portfolios: int = 20,
        method: str = 'max_sharpe'
    ) -> List[OptimizationResult]:
        """
        Calculate efficient frontier of optimal portfolios.
        
        Parameters:
        -----------
        n_portfolios : int
            Number of portfolios on frontier
        method : str
            Optimization method ('max_sharpe', 'min_variance')
        
        Returns:
        --------
        List[OptimizationResult]
            Efficient frontier portfolios
        """
        mu = np.mean(self.returns, axis=1)
        min_return = np.min(mu)
        max_return = np.max(mu)
        
        target_returns = np.linspace(min_return, max_return, n_portfolios)
        
        frontier = []
        for target in target_returns:
            result = self.mean_variance_optimization(target_return=target, method=method)
            frontier.append(result)
        
        return frontier


def get_portfolio_optimizer(returns: np.ndarray, risk_free_rate: float = 0.03) -> PortfolioOptimizer:
    """
    Get singleton instance of portfolio optimizer.
    """
    return PortfolioOptimizer(returns, risk_free_rate)
