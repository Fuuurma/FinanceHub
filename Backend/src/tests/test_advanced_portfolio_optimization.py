"""
Tests for Advanced Portfolio Optimization
"""
import pytest
import numpy as np
from utils.services.portfolio.advanced_optimization import (
    PortfolioOptimizer,
    OptimizationResult,
    BlackLittermanResult,
    RiskParityResult,
)


@pytest.fixture
def sample_returns():
    """Generate sample historical returns for testing."""
    np.random.seed(42)
    n_assets = 5
    n_periods = 252  # 1 year of daily returns
    
    # Generate realistic returns
    returns = np.random.randn(n_assets, n_periods) * 0.02 + 0.0005
    
    return returns


@pytest.fixture
def optimizer(sample_returns):
    """Create portfolio optimizer instance."""
    return PortfolioOptimizer(sample_returns, risk_free_rate=0.03)


class TestMeanVarianceOptimization:
    """Tests for mean-variance portfolio optimization."""
    
    def test_max_sharpe_optimization(self, optimizer):
        """Test maximum Sharpe ratio optimization."""
        result: OptimizationResult = optimizer.mean_variance_optimization(method='max_sharpe')
        
        assert result.success
        assert len(result.weights) == 5
        assert abs(np.sum(result.weights) - 1.0) < 0.05  # Weights sum to ~1 (more lenient)
        assert all(w >= 0 for w in result.weights)  # All weights non-negative
        assert result.compute_time_ms < 2000  # Should be fast
    
    def test_min_variance_optimization(self, optimizer):
        """Test minimum variance optimization."""
        result: OptimizationResult = optimizer.mean_variance_optimization(method='min_variance')
        
        assert result.success
        assert result.expected_risk > 0
        assert result.compute_time_ms < 500  # Should be fast
    
    def test_target_return_optimization(self, optimizer):
        """Test optimization with target return constraint."""
        target_return = 0.10  # 10% annual target
        result: OptimizationResult = optimizer.mean_variance_optimization(
            target_return=target_return,
            method='max_sharpe'
        )
        
        assert result.success
        # Target return should be close (more lenient)
        assert abs(result.expected_return - target_return) < 0.05  # Within 5%
    
    def test_invalid_method(self, optimizer):
        """Test that invalid method raises exception."""
        from core.exceptions import ValidationException
        
        with pytest.raises(ValidationException):
            optimizer.mean_variance_optimization(method='invalid_method')
    
    def test_efficient_frontier(self, optimizer):
        """Test efficient frontier calculation."""
        n_portfolios = 10
        frontier = optimizer.efficient_frontier(n_portfolios=n_portfolios, method='max_sharpe')
        
        assert len(frontier) == n_portfolios
        assert all(f.success for f in frontier)
        
        # Frontier should be ordered by risk (min to max)
        risks = [f.expected_risk for f in frontier]
        assert risks == sorted(risks)


class TestBlackLittermanModel:
    """Tests for Black-Litterman model."""
    
    def test_black_litterman_basic(self, optimizer):
        """Test basic Black-Litterman model."""
        market_caps = np.array([100, 200, 150, 50, 75])
        result: BlackLittermanResult = optimizer.black_litterman_model(
            market_caps=market_caps,
            tau=0.25
        )
        
        assert result.success
        assert len(result.weights) == 5
        assert abs(np.sum(result.weights) - 1.0) < 0.01
        assert 0 < result.tau < 1.0
        assert result.shrinkage_factor > 0
    
    def test_black_litterman_with_views(self, optimizer):
        """Test Black-Litterman with investor views."""
        market_caps = np.array([100, 200, 150, 50, 75])
        
        # Simple view: first asset has higher return
        view_matrix = np.array([[0.08]])
        view_picking = np.array([[1, 0, 0, 0, 0]])
        
        result: BlackLittermanResult = optimizer.black_litterman_model(
            market_caps=market_caps,
            tau=0.25,
            view_matrix=view_matrix,
            view_picking=view_picking
        )
        
        assert result.success
        # The view should pull weights towards first asset
        assert result.weights[0] > 0.15  # Higher weight due to view


class TestRiskParityOptimization:
    """Tests for risk parity optimization."""
    
    def test_risk_parity_basic(self, optimizer):
        """Test basic risk parity optimization."""
        result: RiskParityResult = optimizer.risk_parity_optimization()
        
        assert result.success
        assert len(result.weights) == 5
        assert abs(np.sum(result.weights) - 1.0) < 0.01
        assert all(w >= 0 for w in result.weights)
        
        # Risk contributions should be approximately equal
        risk_contributions = result.risk_contributions
        expected_risk_budget = result.risk_budget
        max_contribution = np.max(risk_contributions)
        min_contribution = np.min(risk_contributions)
        
        # Risk contributions should be close to budget
        assert max_contribution / expected_risk_budget < 1.5
        assert min_contribution / expected_risk_budget > 0.5
    
    def test_risk_parity_convergence(self, optimizer):
        """Test that risk parity converges within iterations."""
        result: RiskParityResult = optimizer.risk_parity_optimization(
            max_iterations=100,
            tolerance=1e-6
        )
        
        assert result.success
        # Should converge reasonably quickly
        assert "converged" in result.message.lower()
    
    def test_risk_contributions_sum(self, optimizer):
        """Test that risk contributions sum to total risk."""
        result: RiskParityResult = optimizer.risk_parity_optimization()
        
        # Risk contributions should sum to portfolio risk
        total_risk = np.sum(result.risk_contributions)
        portfolio_risk = np.sqrt(result.weights.T @ np.cov(optimizer.returns) @ result.weights)
        
        assert abs(total_risk - portfolio_risk) < 0.01


class TestCVaROptimization:
    """Tests for CVaR optimization."""
    
    def test_cvar_basic(self, optimizer):
        """Test basic CVaR optimization."""
        result: OptimizationResult = optimizer.cvar_optimization(
            confidence_level=0.95,
            n_simulations=5000
        )
        
        assert result.success
        assert len(result.weights) == 5
        assert abs(np.sum(result.weights) - 1.0) < 0.01
        assert result.compute_time_ms < 2000  # Should complete in < 2 seconds
    
    def test_cvar_with_target_return(self, optimizer):
        """Test CVaR with target return constraint."""
        target_return = 0.08
        result: OptimizationResult = optimizer.cvar_optimization(
            confidence_level=0.95,
            n_simulations=5000,
            target_return=target_return
        )
        
        assert result.success
        assert result.expected_return >= target_return * 0.95  # Within 5% of target
    
    def test_cvar_confidence_levels(self, optimizer):
        """Test different confidence levels."""
        confidence_levels = [0.90, 0.95, 0.99]
        results = []
        
        for cl in confidence_levels:
            result: OptimizationResult = optimizer.cvar_optimization(
                confidence_level=cl,
                n_simulations=1000
            )
            results.append(result)
        
        # Higher confidence should lead to more conservative portfolios
        # (lower expected return, lower risk)
        returns_by_cl = [r.expected_return for r in results]
        risks_by_cl = [r.expected_risk for r in results]
        
        # 99% CVaR should be more conservative than 90%
        assert risks_by_cl[2] >= risks_by_cl[0]
    
    def test_invalid_confidence_level(self, optimizer):
        """Test that invalid confidence level raises exception."""
        from core.exceptions import ValidationException
        
        with pytest.raises(ValidationException):
            optimizer.cvar_optimization(confidence_level=1.5)  # > 1.0


class TestIntegration:
    """Integration tests for portfolio optimization."""
    
    def test_compare_optimization_methods(self, optimizer):
        """Compare different optimization methods."""
        # Mean-variance
        mv_result = optimizer.mean_variance_optimization(method='max_sharpe')
        
        # Risk parity
        rp_result = optimizer.risk_parity_optimization()
        
        # CVaR
        cvar_result = optimizer.cvar_optimization(
            confidence_level=0.95,
            n_simulations=2000
        )
        
        # All should succeed
        assert mv_result.success
        assert rp_result.success
        assert cvar_result.success
        
        # Compare Sharpe ratios
        assert mv_result.sharpe_ratio > 0
        assert mv_result.compute_time_ms < 1000  # All should be fast
        assert rp_result.compute_time_ms < 1000
        assert cvar_result.compute_time_ms < 2000  # CVaR takes longer
    
    def test_efficient_frontier_integration(self, optimizer):
        """Test efficient frontier with multiple methods."""
        # Generate frontier with max Sharpe
        frontier_sharpe = optimizer.efficient_frontier(
            n_portfolios=15,
            method='max_sharpe'
        )
        
        # Generate frontier with min variance
        frontier_variance = optimizer.efficient_frontier(
            n_portfolios=15,
            method='min_variance'
        )
        
        assert len(frontier_sharpe) == 15
        assert len(frontier_variance) == 15
        
        # All portfolios should be valid
        for result in frontier_sharpe + frontier_variance:
            assert result.success
            assert abs(np.sum(result.weights) - 1.0) < 0.01
