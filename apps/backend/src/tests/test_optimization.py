"""
Tests for Portfolio Optimization Services
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from utils.services.optimization.optimizer import (
    PortfolioOptimizer,
    OptimizationResult,
    RiskParityResult,
    BacktestEngine,
    BacktestResult,
)


class TestPortfolioOptimizer:
    """Tests for PortfolioOptimizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.returns_dict = {
            'AAPL': list(np.random.randn(100) * 0.02 + 0.001),
            'GOOGL': list(np.random.randn(100) * 0.02 + 0.001),
            'MSFT': list(np.random.randn(100) * 0.02 + 0.001),
        }
        self.current_weights = {'AAPL': 0.4, 'GOOGL': 0.3, 'MSFT': 0.3}

    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly."""
        optimizer = PortfolioOptimizer(self.returns_dict)

        assert optimizer.n_assets == 3
        assert len(optimizer.assets) == 3
        assert optimizer.returns_array.shape[1] == 100

    def test_optimizer_with_current_weights(self):
        """Test optimizer with current portfolio weights."""
        optimizer = PortfolioOptimizer(
            self.returns_dict,
            current_weights=self.current_weights
        )

        assert optimizer.current_weights == self.current_weights

    def test_optimize_max_sharpe(self):
        """Test maximum Sharpe ratio optimization."""
        optimizer = PortfolioOptimizer(self.returns_dict)
        result = optimizer.optimize_max_sharpe()

        assert isinstance(result, OptimizationResult)
        assert result.status in ['success', 'failed']
        assert len(result.weights) == 3
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert result.expected_return >= -1.0
        assert result.sharpe_ratio >= 0

    def test_optimize_min_volatility(self):
        """Test minimum volatility optimization."""
        optimizer = PortfolioOptimizer(self.returns_dict)
        result = optimizer.optimize_min_volatility()

        assert isinstance(result, OptimizationResult)
        assert len(result.weights) == 3
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert result.expected_volatility >= 0

    def test_optimize_risk_parity(self):
        """Test risk parity optimization."""
        optimizer = PortfolioOptimizer(self.returns_dict)
        result = optimizer.optimize_risk_parity()

        assert isinstance(result, RiskParityResult)
        assert len(result.weights) == 3
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert len(result.risk_contribution) == 3
        assert result.total_volatility >= 0

    def test_optimization_uses_all_assets(self):
        """Test that optimization uses all available assets."""
        optimizer = PortfolioOptimizer(self.returns_dict)
        max_sharpe = optimizer.optimize_max_sharpe()
        min_vol = optimizer.optimize_min_volatility()
        risk_parity = optimizer.optimize_risk_parity()

        assert set(max_sharpe.weights.keys()) == set(self.returns_dict.keys())
        assert set(min_vol.weights.keys()) == set(self.returns_dict.keys())
        assert set(risk_parity.weights.keys()) == set(self.returns_dict.keys())

    def test_weights_sum_to_one(self):
        """Test that portfolio weights sum to 1."""
        optimizer = PortfolioOptimizer(self.returns_dict)

        for result in [optimizer.optimize_max_sharpe(),
                       optimizer.optimize_min_volatility(),
                       optimizer.optimize_risk_parity()]:
            total = sum(result.weights.values())
            assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"

    def test_negative_returns_handling(self):
        """Test optimization with negative returns."""
        negative_returns = {
            'RISKY': list(np.random.randn(50) * 0.05 - 0.002),
            'SAFE': list(np.random.randn(50) * 0.01 + 0.0001),
        }
        optimizer = PortfolioOptimizer(negative_returns)
        result = optimizer.optimize_max_sharpe()

        assert isinstance(result, OptimizationResult)
        assert result.sharpe_ratio is not None


class TestBacktestEngine:
    """Tests for BacktestEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.prices = {
            'AAPL': list(100 * np.cumprod(1 + np.random.randn(252) * 0.02 + 0.001)),
            'GOOGL': list(100 * np.cumprod(1 + np.random.randn(252) * 0.02 + 0.001)),
        }
        self.initial_capital = 100000

    def test_backtest_initialization(self):
        """Test backtest engine initializes correctly."""
        engine = BacktestEngine(self.prices, self.initial_capital)

        assert engine.n_periods == 252
        assert len(engine.symbols) == 2
        assert engine.initial_capital == self.initial_capital

    def test_run_strategy_basic(self):
        """Test running a basic strategy backtest."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 0.6, 'GOOGL': 0.4}

        result = engine.run_strategy(weights, "Test Strategy")

        assert isinstance(result, BacktestResult)
        assert result.strategy_name == "Test Strategy"
        assert result.total_return >= -1.0
        assert len(result.equity_curve) == 252
        assert len(result.drawdown_curve) == 252

    def test_equity_curve_growth(self):
        """Test that equity curve reflects portfolio growth."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 1.0, 'GOOGL': 0.0}

        result = engine.run_strategy(weights, "Long AAPL")

        assert result.equity_curve[0] == self.initial_capital
        assert len(result.equity_curve) > 0

    def test_max_drawdown_calculation(self):
        """Test max drawdown is correctly calculated."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 1.0, 'GOOGL': 0.0}

        result = engine.run_strategy(weights, "Test")

        assert result.max_drawdown <= 0
        assert result.max_drawdown >= -1.0

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio is calculated."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 0.5, 'GOOGL': 0.5}

        result = engine.run_strategy(weights, "Test")

        assert result.sharpe_ratio is not None
        assert isinstance(result.sharpe_ratio, (int, float))

    def test_compare_strategies(self):
        """Test comparing multiple strategies."""
        engine = BacktestEngine(self.prices, self.initial_capital)

        strategies = [
            ({'AAPL': 1.0, 'GOOGL': 0.0}, "All AAPL"),
            ({'AAPL': 0.0, 'GOOGL': 1.0}, "All GOOGL"),
            ({'AAPL': 0.5, 'GOOGL': 0.5}, "Balanced"),
        ]

        results = engine.compare_strategies(strategies)

        assert len(results) == 3
        assert "All AAPL" in results
        assert "All GOOGL" in results
        assert "Balanced" in results

        for name, result in results.items():
            assert isinstance(result, BacktestResult)
            assert result.strategy_name == name

    def test_rebalance_frequency(self):
        """Test rebalancing with different frequencies."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 0.5, 'GOOGL': 0.5}

        result_no_rebalance = engine.run_strategy(
            weights, "No Rebalance", rebalance_freq=None
        )
        result_with_rebalance = engine.run_strategy(
            weights, "Monthly Rebalance", rebalance_freq=21
        )

        assert isinstance(result_no_rebalance, BacktestResult)
        assert isinstance(result_with_rebalance, BacktestResult)

    def test_daily_returns_length(self):
        """Test daily returns array length matches equity curve."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 1.0, 'GOOGL': 0.0}

        result = engine.run_strategy(weights, "Test")

        assert len(result.daily_returns) == len(result.equity_curve) - 1

    def test_monthly_returns_dict(self):
        """Test monthly returns are returned as dictionary."""
        engine = BacktestEngine(self.prices, self.initial_capital)
        weights = {'AAPL': 1.0, 'GOOGL': 0.0}

        result = engine.run_strategy(weights, "Test")

        assert isinstance(result.monthly_returns, dict)
        for key, value in result.monthly_returns.items():
            assert isinstance(key, str)
            assert isinstance(value, (int, float))


class TestOptimizationResult:
    """Tests for OptimizationResult dataclass."""

    def test_optimization_result_creation(self):
        """Test creating an OptimizationResult."""
        result = OptimizationResult(
            weights={'AAPL': 0.5, 'GOOGL': 0.5},
            expected_return=0.12,
            expected_volatility=0.15,
            sharpe_ratio=0.8,
            optimization_method='Mean-Variance (Max Sharpe)',
            status='success',
            portfolio_value=100000,
            expected_allocation={'AAPL': 0.5, 'GOOGL': 0.5},
            turnover=0.05,
            recommendations=['Diversify more'],
            interpretation='Test interpretation'
        )

        assert result.weights == {'AAPL': 0.5, 'GOOGL': 0.5}
        assert result.expected_return == 0.12
        assert result.sharpe_ratio == 0.8
        assert result.status == 'success'
        assert result.fetched_at is not None


class TestRiskParityResult:
    """Tests for RiskParityResult dataclass."""

    def test_risk_parity_result_creation(self):
        """Test creating a RiskParityResult."""
        result = RiskParityResult(
            weights={'AAPL': 0.5, 'GOOGL': 0.5},
            risk_contribution={'AAPL': 0.5, 'GOOGL': 0.5},
            total_volatility=0.15,
            diversification_ratio=1.5,
            interpretation='Equal risk contribution'
        )

        assert result.weights == {'AAPL': 0.5, 'GOOGL': 0.5}
        assert result.risk_contribution == {'AAPL': 0.5, 'GOOGL': 0.5}
        assert result.total_volatility == 0.15
        assert result.fetched_at is not None


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_single_asset_optimization(self):
        """Test optimization with single asset."""
        returns_dict = {'AAPL': list(np.random.randn(100) * 0.02)}
        optimizer = PortfolioOptimizer(returns_dict)

        result = optimizer.optimize_max_sharpe()
        assert result.status in ['success', 'failed']
        assert 'AAPL' in result.weights

    def test_single_asset_backtest(self):
        """Test backtest with single asset."""
        prices = {
            'AAPL': list(100 * np.cumprod(1 + np.random.randn(100) * 0.02)),
        }
        engine = BacktestEngine(prices, 100000)
        result = engine.run_strategy({'AAPL': 1.0}, "Single Asset")

        assert isinstance(result, BacktestResult)

    def test_equal_weight_portfolio(self):
        """Test equal weight portfolio optimization."""
        n_assets = 5
        returns_dict = {
            f'Asset{i}': list(np.random.randn(100) * 0.02) for i in range(n_assets)
        }
        optimizer = PortfolioOptimizer(returns_dict)
        result = optimizer.optimize_max_sharpe()

        assert len(result.weights) == n_assets

    def test_backtest_with_zero_initial_capital(self):
        """Test backtest edge case with zero initial capital."""
        prices = {
            'AAPL': [100, 101, 102],
        }
        engine = BacktestEngine(prices, 0)
        result = engine.run_strategy({'AAPL': 1.0}, "Zero Capital")

        assert result.total_return == 0
