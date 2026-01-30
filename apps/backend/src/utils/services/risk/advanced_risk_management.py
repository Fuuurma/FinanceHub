"""
Advanced Risk Management Module
High-performance risk calculations for portfolios.
"""

import numpy as np
from typing import List, Optional, Dict, Union, Tuple
from dataclasses import dataclass
from scipy.stats import norm


@dataclass
class VaRResult:
    """Result container for Value at Risk calculation."""

    var_95: float
    var_99: float
    expected_shortfall_95: float
    expected_shortfall_99: float
    method: str
    confidence_level: float
    n_scenarios: int
    compute_time_ms: float


@dataclass
class StressTestResult:
    """Result container for stress testing."""

    stress_scenarios: Dict[str, Dict[str, float]]
    worst_case_scenario: str
    worst_case_loss: float
    recovery_scenarios: List[Dict[str, str]]
    compute_time_ms: float


@dataclass
class FactorStressTestResult:
    """Result container for factor-based stress testing."""

    factor_shocks: Dict[str, float]
    portfolio_impact: Dict[str, float]
    worst_factor: str
    worst_impact: float
    compute_time_ms: float


class RiskManager:
    """
    Advanced risk management with multiple methodologies.

    Supports:
    - Historical VaR (parametric, historical simulation)
    - Monte Carlo VaR with full distribution
    - Expected Shortfall (CVaR)
    - Stress testing with historical scenarios
    - Factor-based stress testing
    """

    def __init__(
        self, returns: np.ndarray, weights: np.ndarray, risk_free_rate: float = 0.03
    ):
        """
        Initialize risk manager with returns and weights.

        Parameters:
        -----------
        returns : np.ndarray
            Historical returns matrix (assets x periods)
        weights : np.ndarray
            Portfolio weights
        risk_free_rate : float
            Annualized risk-free rate
        """
        self.returns = np.asarray(returns)
        self.weights = np.asarray(weights)
        self.risk_free_rate = risk_free_rate
        self.n_assets = returns.shape[0] if returns.ndim > 1 else 1
        self.n_periods = returns.shape[1] if returns.ndim > 1 else 1

        # Calculate portfolio returns
        self.portfolio_returns = np.sum(
            self.returns * self.weights[:, np.newaxis], axis=0
        )

    def parametric_var(self, confidence_level: float = 0.95) -> float:
        """
        Parametric VaR using normal distribution assumption.

        Assumes returns are normally distributed.
        """
        mu = np.mean(self.portfolio_returns)
        sigma = np.std(self.portfolio_returns)

        # VaR = mean + z_alpha * sigma
        z_alpha = norm.ppf(1 - confidence_level)
        var = mu + z_alpha * sigma

        return var

    def historical_var(self, confidence_level: float = 0.95) -> float:
        """
        Historical VaR using empirical distribution.

        Uses actual historical returns without distributional assumptions.
        """
        # Sort returns
        sorted_returns = np.sort(self.portfolio_returns)
        n = len(sorted_returns)

        # VaR index
        var_index = int(n * (1 - confidence_level))
        var = sorted_returns[var_index]

        return var

    def monte_carlo_var(
        self,
        confidence_levels: List[float] = [0.95, 0.99],
        n_simulations: int = 10000,
        time_horizon: int = 10,  # days
    ) -> VaRResult:
        """
        Monte Carlo VaR with multiple confidence levels.

        Generates scenarios and calculates VaR and CVaR.
        """
        import time

        start_time = time.perf_counter()

        # Generate random normal returns
        np.random.seed(42)
        random_returns = np.random.randn(n_simulations, self.n_periods)

        # Simulate portfolio returns
        portfolio_simulated = random_returns @ self.weights

        # Calculate cumulative returns over time horizon
        cumulative_returns = np.cumprod(
            1 + portfolio_simulated[:, :time_horizon], axis=1
        )
        final_returns = cumulative_returns[:, -1] - 1

        # Calculate VaR at different confidence levels
        var_results = {}
        cvar_results = {}

        for cl in confidence_levels:
            # VaR: quantile at (1 - cl)
            var_cl = np.percentile(final_returns, (1 - cl) * 100)
            var_results[f"var_{int(cl * 100)}"] = var_cl

            # CVaR: expected shortfall beyond VaR
            shortfall_mask = final_returns < var_cl
            cvar_cl = var_cl + np.mean(final_returns[shortfall_mask] - var_cl)
            cvar_results[f"cvar_{int(cl * 100)}"] = cvar_cl

        compute_time_ms = (time.perf_counter() - start_time) * 1000

        return VaRResult(
            var_95=var_results.get("var_95", 0.0),
            var_99=var_results.get("var_99", 0.0),
            expected_shortfall_95=cvar_results.get("cvar_95", 0.0),
            expected_shortfall_99=cvar_results.get("cvar_99", 0.0),
            method="monte_carlo",
            confidence_level=confidence_levels[0],
            n_scenarios=n_simulations,
            compute_time_ms=compute_time_ms,
        )

    def expected_shortfall(
        self, confidence_level: float = 0.95, n_simulations: int = 10000
    ) -> float:
        """
        Calculate Expected Shortfall (CVaR).

        Average loss beyond VaR.
        """
        var = self.monte_carlo_var(
            confidence_levels=[confidence_level], n_simulations=n_simulations
        )

        if confidence_level == 0.95:
            return var.expected_shortfall_95
        else:
            return var.expected_shortfall_99

    def stress_test_historical(
        self,
        stress_scenarios: List[Dict[str, float]],
        scenario_names: Optional[List[str]] = None,
    ) -> StressTestResult:
        """
        Stress test portfolio against historical scenarios.

        Parameters:
        -----------
        stress_scenarios : List[Dict[str, float]]
            List of asset return shocks
        scenario_names : List[str], optional
            Names for the scenarios

        Returns:
        --------
        StressTestResult
            Impact of each scenario and worst case
        """
        import time

        start_time = time.perf_counter()

        if scenario_names is None:
            scenario_names = [f"Scenario_{i + 1}" for i in range(len(stress_scenarios))]

        # Calculate portfolio impact for each scenario
        impacts = {}
        for i, scenario in enumerate(stress_scenarios):
            # Apply scenario returns
            scenario_returns = {}
            for asset_idx, asset_name in enumerate(scenario.keys()):
                scenario_returns[asset_name] = scenario[asset_name]

            # Calculate portfolio return for scenario
            scenario_portfolio_return = np.sum(
                np.array(list(scenario_returns.values())) * self.weights
            )

            # Portfolio value change
            scenario_value_change = np.exp(scenario_portfolio_return) - 1

            impacts[scenario_names[i]] = {
                "portfolio_return": scenario_portfolio_return,
                "value_change": scenario_value_change,
                "percent_change": scenario_value_change * 100,
            }

        # Find worst case
        worst_scenario = max(impacts.keys(), key=lambda k: impacts[k]["value_change"])
        worst_loss = impacts[worst_scenario]["value_change"]

        # Recovery scenarios (best performing assets in each scenario)
        recovery_scenarios = []
        for scenario_name, scenario_data in impacts.items():
            best_asset = scenario_name  # Placeholder

        compute_time_ms = (time.perf_counter() - start_time) * 1000

        return StressTestResult(
            stress_scenarios=impacts,
            worst_case_scenario=worst_scenario,
            worst_case_loss=worst_loss,
            recovery_scenarios=recovery_scenarios,
            compute_time_ms=compute_time_ms,
        )

    def factor_stress_test(
        self,
        factor_loadings: Optional[Dict[str, float]] = None,
        factor_shocks: Dict[str, float] = None,
    ) -> FactorStressTestResult:
        """
        Factor-based stress testing.

        Test portfolio sensitivity to factor shocks.
        """
        import time

        start_time = time.perf_counter()

        if factor_loadings is None:
            factor_loadings = {
                "equity": 1.0,
                "size": 1.0,
                "value": 1.0,
                "quality": 1.0,
                "momentum": 1.0,
            }

        if factor_shocks is None:
            factor_shocks = {
                "equity": -0.20,  # 20% market drop
                "size": -0.10,  # 10% size factor underperformance
                "value": -0.15,  # 15% value factor drop
                "quality": -0.10,  # 10% quality spread compression
                "momentum": -0.05,  # 5% momentum reversal
            }

        # Calculate factor sensitivities
        # Assuming simple factor exposure model
        sensitivities = {}
        for factor, shock in factor_shocks.items():
            # Portfolio sensitivity to factor (simplified)
            sensitivity = np.sum(self.weights)  # Equal sensitivity for all factors

            # Portfolio impact
            impact = sensitivity * shock
            sensitivities[factor] = {
                "sensitivity": sensitivity,
                "shock": shock,
                "impact": impact,
            }

        # Portfolio impacts by factor
        portfolio_impacts = {}
        for factor, data in sensitivities.items():
            portfolio_impacts[factor] = data["impact"]

        # Find worst factor
        worst_factor = max(
            portfolio_impacts.keys(), key=lambda k: abs(portfolio_impacts[k])
        )
        worst_impact = portfolio_impacts[worst_factor]

        compute_time_ms = (time.perf_counter() - start_time) * 1000

        return FactorStressTestResult(
            factor_shocks=factor_shocks,
            portfolio_impact=portfolio_impacts,
            worst_factor=worst_factor,
            worst_impact=worst_impact,
            compute_time_ms=compute_time_ms,
        )

    def comprehensive_risk_analysis(
        self,
        confidence_level: float = 0.95,
        n_simulations: int = 10000,
        stress_scenarios: Optional[List[Dict[str, float]]] = None,
    ) -> Dict:
        """
        Comprehensive risk analysis combining all methodologies.

        Returns VaR, CVaR, and stress test results.
        """
        # VaR calculations
        param_var = self.parametric_var(confidence_level)
        hist_var = self.historical_var(confidence_level)
        mc_result = self.monte_carlo_var(
            confidence_levels=[confidence_level], n_simulations=n_simulations
        )

        # Stress testing
        if stress_scenarios:
            stress_result = self.stress_test_historical(stress_scenarios)
        else:
            stress_result = None

        # Factor stress test
        factor_result = self.factor_stress_test()

        return {
            "parametric_var": param_var,
            "historical_var": hist_var,
            "monte_carlo_var": mc_result,
            "stress_test": stress_result,
            "factor_stress_test": factor_result,
        }


def get_risk_manager(
    returns: np.ndarray, weights: np.ndarray, risk_free_rate: float = 0.03
) -> RiskManager:
    """
    Get singleton instance of risk manager.
    """
    return RiskManager(returns, weights, risk_free_rate)
