from typing import Dict, List, Optional
from decimal import Decimal
import time

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    import warnings

    warnings.warn("NumPy not available, using fallback calculations")

try:
    from scipy import stats

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from utils.financial import (
    to_decimal,
    safe_divide,
    round_decimal,
)


class ValueAtRiskService:
    HISTORICAL_SCENARIOS = {
        "2008_financial_crisis": {
            "name": "2008 Financial Crisis",
            "start_date": "2008-09-01",
            "end_date": "2009-03-31",
            "market_drop": -0.50,
            "sector_shocks": {
                "Financials": -0.60,
                "Technology": -0.45,
                "Healthcare": -0.30,
            },
        },
        "covid_crash": {
            "name": "COVID-19 Crash (2020)",
            "start_date": "2020-02-19",
            "end_date": "2020-03-23",
            "market_drop": -0.34,
            "sector_shocks": {
                "Energy": -0.50,
                "Industrials": -0.40,
                "Financials": -0.35,
            },
        },
        "dot_com_bubble": {
            "name": "Dot-Com Bubble (2000-2002)",
            "start_date": "2000-03-10",
            "end_date": "2002-10-09",
            "market_drop": -0.49,
            "sector_shocks": {"Technology": -0.78, "Telecommunications": -0.65},
        },
    }

    def __init__(self, price_service=None):
        self.price_service = price_service

    def calculate_var(
        self,
        portfolio_id: int,
        portfolio_name: str,
        user_id: int,
        positions: List[Dict],
        method: str = "parametric",
        confidence_level: int = 95,
        time_horizon: int = 1,
        lookback_days: int = 252,
    ) -> Dict:
        start_time = time.time()

        portfolio_value = self._calculate_portfolio_value(positions)

        if method == "parametric":
            result = self._calculate_parametric_var(
                positions, portfolio_value, confidence_level, time_horizon
            )
        elif method == "historical":
            result = self._calculate_historical_var(
                positions,
                portfolio_value,
                confidence_level,
                time_horizon,
                lookback_days,
            )
        elif method == "monte_carlo":
            result = self._calculate_monte_carlo_var(
                positions, portfolio_value, confidence_level, time_horizon
            )
        else:
            raise ValueError(f"Unknown VaR method: {method}")

        calculation_time_ms = int((time.time() - start_time) * 1000)

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio_name,
            "method": method,
            "confidence_level": confidence_level,
            "time_horizon": time_horizon,
            "var_amount": round_decimal(result["var_amount"], 2),
            "var_percentage": round_decimal(
                result["var_percentage"] * Decimal("100"), 4
            ),
            "expected_shortfall": round_decimal(
                result.get("expected_shortfall", Decimal("0")), 2
            ),
            "portfolio_value": round_decimal(portfolio_value, 2),
            "calculation_time_ms": calculation_time_ms,
            "portfolio_volatility": result.get("portfolio_volatility"),
            "z_score": result.get("z_score"),
        }

    def _calculate_portfolio_value(self, positions: List[Dict]) -> Decimal:
        total = Decimal("0")
        for position in positions:
            value = Decimal(str(position.get("quantity", 0))) * Decimal(
                str(position.get("current_price", 0))
            )
            total += value
        return total if total > 0 else Decimal("1")

    def _calculate_parametric_var(
        self,
        positions: List[Dict],
        portfolio_value: Decimal,
        confidence_level: int,
        time_horizon: int,
    ) -> Dict:
        if not HAS_NUMPY:
            return self._fallback_var_calculation(portfolio_value, confidence_level)

        weights = np.array(
            [
                float(
                    Decimal(str(p.get("quantity", 0)))
                    * Decimal(str(p.get("current_price", 0)))
                    / portfolio_value
                )
                for p in positions
            ]
        )

        returns_matrix = self._get_returns_matrix(positions, lookback_days=252)
        if returns_matrix.size == 0:
            return self._fallback_var_calculation(portfolio_value, confidence_level)

        cov_matrix = np.cov(returns_matrix)
        portfolio_variance = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
        portfolio_volatility = np.sqrt(portfolio_variance)
        z_score = self._get_z_score(confidence_level)

        var_percentage = z_score * portfolio_volatility * np.sqrt(time_horizon)
        var_amount = float(portfolio_value) * var_percentage
        expected_shortfall = (
            var_amount * 1.5
            if not HAS_SCIPY
            else var_amount * stats.norm.pdf(z_score) / (1 - confidence_level / 100)
        )

        return {
            "var_amount": var_amount,
            "var_percentage": var_percentage,
            "expected_shortfall": expected_shortfall,
            "portfolio_volatility": portfolio_volatility,
            "z_score": z_score,
        }

    def _calculate_historical_var(
        self,
        positions: List[Dict],
        portfolio_value: Decimal,
        confidence_level: int,
        time_horizon: int,
        lookback_days: int,
    ) -> Dict:
        if not HAS_NUMPY:
            return self._fallback_var_calculation(portfolio_value, confidence_level)

        returns_matrix = self._get_returns_matrix(positions, lookback_days)
        if returns_matrix.size == 0:
            return self._fallback_var_calculation(portfolio_value, confidence_level)

        weights = np.array(
            [
                float(
                    to_decimal(p.get("quantity", 0))
                    * to_decimal(p.get("current_price", 0))
                    / to_decimal(portfolio_value)
                )
                for p in positions
            ]
        )
        portfolio_returns = np.dot(returns_matrix.T, weights)

        if time_horizon > 1:
            portfolio_returns = self._aggregate_returns(portfolio_returns, time_horizon)

        var_percentile = (100 - confidence_level) / 100
        var_percentage = np.percentile(portfolio_returns, var_percentile * 100)
        var_amount = float(to_decimal(portfolio_value)) * abs(var_percentage)

        tail_losses = portfolio_returns[portfolio_returns <= var_percentage]
        expected_shortfall = (
            float(to_decimal(portfolio_value)) * abs(np.mean(tail_losses))
            if len(tail_losses) > 0
            else var_amount
        )

        return {
            "var_amount": var_amount,
            "var_percentage": abs(var_percentage),
            "expected_shortfall": expected_shortfall,
            "historical_scenarios": len(portfolio_returns),
        }

    def _calculate_monte_carlo_var(
        self,
        positions: List[Dict],
        portfolio_value: Decimal,
        confidence_level: int,
        time_horizon: int,
        num_simulations: int = 10000,
    ) -> Dict:
        if not HAS_NUMPY:
            return self._fallback_var_calculation(portfolio_value, confidence_level)

        returns_matrix = self._get_returns_matrix(positions, lookback_days=252)
        if returns_matrix.size == 0:
            return self._fallback_var_calculation(portfolio_value, confidence_level)

        weights = np.array(
            [
                float(
                    Decimal(str(p.get("quantity", 0)))
                    * Decimal(str(p.get("current_price", 0)))
                    / portfolio_value
                )
                for p in positions
            ]
        )
        mean_returns = np.mean(returns_matrix, axis=1)
        cov_matrix = np.cov(returns_matrix)

        np.random.seed(42)
        simulated_returns = np.random.multivariate_normal(
            mean_returns, cov_matrix, size=(num_simulations, time_horizon)
        )

        portfolio_simulations = [
            np.dot(sim.sum(axis=0), weights) for sim in simulated_returns
        ]
        portfolio_simulations = np.array(portfolio_simulations)

        var_percentile = (100 - confidence_level) / 100
        var_percentage = np.percentile(portfolio_simulations, var_percentile * 100)
        var_amount = float(portfolio_value) * abs(var_percentage)

        tail_losses = portfolio_simulations[portfolio_simulations <= var_percentage]
        expected_shortfall = (
            float(portfolio_value) * abs(np.mean(tail_losses))
            if len(tail_losses) > 0
            else var_amount
        )

        return {
            "var_amount": var_amount,
            "var_percentage": abs(var_percentage),
            "expected_shortfall": expected_shortfall,
            "num_simulations": num_simulations,
        }

    def _aggregate_returns(self, returns: np.ndarray, time_horizon: int) -> np.ndarray:
        if time_horizon <= 1:
            return returns
        aggregated = []
        for i in range(len(returns) - time_horizon + 1):
            aggregated.append(np.sum(returns[i : i + time_horizon]))
        return np.array(aggregated) if aggregated else returns

    def _get_returns_matrix(
        self, positions: List[Dict], lookback_days: int
    ) -> np.ndarray:
        if not HAS_NUMPY:
            return np.array([])

        returns_list = []
        for position in positions:
            price_history = position.get("price_history", [])
            if len(price_history) < 2:
                returns_list.append(np.zeros(lookback_days))
                continue
            try:
                price_array = np.array(
                    [float(p.get("close", p)) for p in price_history[-lookback_days:]]
                )
                if len(price_array) < 2:
                    returns_list.append(np.zeros(lookback_days))
                    continue
                returns = np.diff(price_array) / price_array[:-1]
                returns_list.append(returns)
            except (ValueError, IndexError):
                returns_list.append(np.zeros(lookback_days))

        if not returns_list:
            return np.array([])

        max_length = max(len(r) for r in returns_list)
        padded_returns = [
            np.pad(r, (max_length - len(r), 0), constant_values=0)
            if len(r) < max_length
            else r
            for r in returns_list
        ]
        return np.array(padded_returns)

    def _get_z_score(self, confidence_level: int) -> float:
        if HAS_SCIPY:
            return stats.norm.ppf(1 - (100 - confidence_level) / 100)
        z_scores = {90: 1.282, 95: 1.645, 99: 2.326, 99.9: 3.090}
        return z_scores.get(confidence_level, 1.645)

    def _fallback_var_calculation(
        self, portfolio_value: Decimal, confidence_level: int
    ) -> Dict:
        base_volatility = 0.02
        z_score = self._get_z_score(confidence_level)
        var_percentage = z_score * base_volatility
        var_amount = float(portfolio_value) * var_percentage
        return {
            "var_amount": var_amount,
            "var_percentage": var_percentage,
            "expected_shortfall": var_amount * 1.3,
            "portfolio_volatility": base_volatility,
            "z_score": z_score,
        }

    def run_historical_stress_test(
        self,
        portfolio_id: int,
        portfolio_name: str,
        user_id: int,
        positions: List[Dict],
        scenario_key: str,
    ) -> Dict:
        if scenario_key not in self.HISTORICAL_SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_key}")

        scenario = self.HISTORICAL_SCENARIOS[scenario_key]
        portfolio_value_before = self._calculate_portfolio_value(positions)
        portfolio_value_after = Decimal("0")
        worst_performers = []

        for position in positions:
            sector = position.get("sector", "Unknown")
            sector_shock = scenario["sector_shocks"].get(
                sector, scenario["market_drop"]
            )
            current_value = Decimal(str(position.get("quantity", 0))) * Decimal(
                str(position.get("current_price", 0))
            )
            shocked_value = current_value * (1 + Decimal(str(sector_shock)))
            portfolio_value_after += shocked_value
            worst_performers.append(
                {
                    "symbol": position.get("symbol", "UNKNOWN"),
                    "name": position.get("name", ""),
                    "loss": float(sector_shock),
                    "loss_amount": float(current_value - shocked_value),
                }
            )

        worst_performers.sort(key=lambda x: x["loss"])
        portfolio_loss = portfolio_value_before - portfolio_value_after
        portfolio_loss_pct = (
            float(portfolio_loss / portfolio_value_before * 100)
            if portfolio_value_before > 0
            else 0
        )

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio_name,
            "scenario_type": "historical",
            "scenario_name": scenario["name"],
            "market_shock_pct": scenario["market_drop"],
            "sector_shocks": scenario["sector_shocks"],
            "portfolio_value_before": round(float(portfolio_value_before), 2),
            "portfolio_value_after": round(float(portfolio_value_after), 2),
            "portfolio_loss": round(float(portfolio_loss), 2),
            "portfolio_loss_pct": round(portfolio_loss_pct, 4),
            "worst_performing_assets": worst_performers[:5],
        }

    def run_custom_stress_test(
        self,
        portfolio_id: int,
        portfolio_name: str,
        user_id: int,
        positions: List[Dict],
        market_shock_pct: float,
        sector_shocks: Dict[str, float] = None,
        fx_shocks: Dict[str, float] = None,
    ) -> Dict:
        portfolio_value_before = self._calculate_portfolio_value(positions)
        portfolio_value_after = Decimal("0")
        worst_performers = []

        for position in positions:
            sector = position.get("sector", "Unknown")
            shock = Decimal(str(sector_shocks.get(sector, market_shock_pct)))
            current_value = Decimal(str(position.get("quantity", 0))) * Decimal(
                str(position.get("current_price", 0))
            )
            shocked_value = current_value * (1 + shock)
            portfolio_value_after += shocked_value
            worst_performers.append(
                {
                    "symbol": position.get("symbol", "UNKNOWN"),
                    "loss": float(shock),
                    "loss_amount": float(current_value - shocked_value),
                }
            )

        worst_performers.sort(key=lambda x: x["loss"])
        portfolio_loss = portfolio_value_before - portfolio_value_after
        portfolio_loss_pct = (
            float(portfolio_loss / portfolio_value_before * 100)
            if portfolio_value_before > 0
            else 0
        )

        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio_name,
            "scenario_type": "custom",
            "scenario_name": "Custom Scenario",
            "market_shock_pct": market_shock_pct,
            "sector_shocks": sector_shocks or {},
            "portfolio_value_before": round(float(portfolio_value_before), 2),
            "portfolio_value_after": round(float(portfolio_value_after), 2),
            "portfolio_loss": round(float(portfolio_loss), 2),
            "portfolio_loss_pct": round(portfolio_loss_pct, 4),
            "worst_performing_assets": worst_performers[:5],
        }

    def get_available_scenarios(self) -> List[Dict]:
        return [
            {
                "key": k,
                "name": v["name"],
                "market_drop": v["market_drop"],
                "sectors_affected": list(v["sector_shocks"].keys()),
            }
            for k, v in self.HISTORICAL_SCENARIOS.items()
        ]
