from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.optimize import minimize
from datetime import datetime

from utils.helpers.logger.logger import get_logger
from utils.constants.analytics import TRADING_DAYS_PER_YEAR, DEFAULT_RISK_FREE_RATE

logger = get_logger(__name__)


@dataclass
class OptimizationResult:
    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    optimization_method: str
    status: str
    portfolio_value: float
    expected_allocation: Dict[str, float]
    turnover: float
    recommendations: List[str]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())


@dataclass
class RiskParityResult:
    weights: Dict[str, float]
    risk_contribution: Dict[str, float]
    total_volatility: float
    diversification_ratio: float
    interpretation: str
    fetched_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())


class PortfolioOptimizer:
    def __init__(self, returns_dict, current_weights=None, risk_free_rate=DEFAULT_RISK_FREE_RATE):
        self.assets = list(returns_dict.keys())
        self.n_assets = len(self.assets)
        self.returns_array = np.array([returns_dict[a] for a in self.assets])
        self.current_weights = current_weights
        self.risk_free_rate = risk_free_rate
        
        self.mean_returns = np.mean(self.returns_array, axis=1)
        self.cov_matrix = np.cov(self.returns_array)
        self.annual_return = self.mean_returns * TRADING_DAYS_PER_YEAR
        
        logger.info(f"Initialized optimizer with {self.n_assets} assets")
    
    def _portfolio_return(self, weights):
        return np.dot(weights, self.annual_return)
    
    def _portfolio_volatility(self, weights):
        return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * TRADING_DAYS_PER_YEAR, weights)))
    
    def _portfolio_sharpe(self, weights):
        ret = self._portfolio_return(weights)
        vol = self._portfolio_volatility(weights)
        return (ret - self.risk_free_rate) / vol if vol > 0 else 0
    
    def optimize_max_sharpe(self):
        def objective(weights):
            return -self._portfolio_sharpe(weights)
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        initial_weights = np.array([1/self.n_assets] * self.n_assets)
        
        result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
        weights_dict = dict(zip(self.assets, result.x))
        
        exp_return = self._portfolio_return(result.x)
        exp_vol = self._portfolio_volatility(result.x)
        sharpe = (exp_return - self.risk_free_rate) / exp_vol if exp_vol > 0 else 0
        
        interpretation = (
            f"Max Sharpe Portfolio: Expected return {exp_return*100:.1f}%, "
            f"Volatility {exp_vol*100:.1f}%, Sharpe {sharpe:.2f}"
        )
        
        return OptimizationResult(
            weights=weights_dict,
            expected_return=exp_return,
            expected_volatility=exp_vol,
            sharpe_ratio=sharpe,
            optimization_method='Mean-Variance (Max Sharpe)',
            status='success' if result.success else 'failed',
            portfolio_value=sum(self.current_weights.values()) if self.current_weights else 1.0,
            expected_allocation=weights_dict,
            turnover=0,
            recommendations=[],
            interpretation=interpretation
        )
    
    def optimize_min_volatility(self):
        def objective(weights):
            return self._portfolio_volatility(weights)
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        initial_weights = np.array([1/self.n_assets] * self.n_assets)
        
        result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
        weights_dict = dict(zip(self.assets, result.x))
        
        exp_return = self._portfolio_return(result.x)
        exp_vol = self._portfolio_volatility(result.x)
        sharpe = (exp_return - self.risk_free_rate) / exp_vol if exp_vol > 0 else 0
        
        interpretation = (
            f"Min Volatility Portfolio: Expected return {exp_return*100:.1f}%, "
            f"Volatility {exp_vol*100:.1f}%, Sharpe {sharpe:.2f}"
        )
        
        return OptimizationResult(
            weights=weights_dict,
            expected_return=exp_return,
            expected_volatility=exp_vol,
            sharpe_ratio=sharpe,
            optimization_method='Minimum Variance',
            status='success' if result.success else 'failed',
            portfolio_value=sum(self.current_weights.values()) if self.current_weights else 1.0,
            expected_allocation=weights_dict,
            turnover=0,
            recommendations=[],
            interpretation=interpretation
        )
    
    def optimize_risk_parity(self):
        if self.n_assets == 1:
            weights = np.array([1.0])
            rc = np.array([1.0])
            total_vol = self._portfolio_volatility(weights)
            weights_dict = {self.assets[0]: 1.0}
            rc_dict = {self.assets[0]: 1.0}
        else:
            def risk_contribution(weights):
                port_vol = self._portfolio_volatility(weights)
                if port_vol == 0:
                    return np.zeros(self.n_assets)
                marginal_contrib = np.dot(self.cov_matrix * TRADING_DAYS_PER_YEAR, weights)
                return weights * marginal_contrib / port_vol

            def objective(weights):
                rc = risk_contribution(weights)
                target_rc = np.ones(self.n_assets) / self.n_assets
                return np.sum((rc - target_rc) ** 2)

            constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
            bounds = tuple((0.01, 1) for _ in range(self.n_assets))
            initial_weights = np.array([1/self.n_assets] * self.n_assets)

            result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

            rc = risk_contribution(result.x)
            total_vol = self._portfolio_volatility(result.x)

            weights_dict = dict(zip(self.assets, result.x))
            rc_dict = dict(zip(self.assets, rc))

        interpretation = (
            f"Risk Parity Portfolio: {self.n_assets} assets contribute equally to risk. "
            f"Total volatility: {total_vol*100:.1f}%"
        )

        return RiskParityResult(
            weights=weights_dict,
            risk_contribution=rc_dict,
            total_volatility=total_vol,
            diversification_ratio=1.0,
            interpretation=interpretation
        )
        
@dataclass
class BacktestResult:
    strategy_name: str
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    sortino_ratio: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_trade: float
    average_win: float
    average_loss: float
    equity_curve: List[float]
    drawdown_curve: List[float]
    monthly_returns: Dict[str, float]
    daily_returns: List[float]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


class BacktestEngine:
    def __init__(self, prices: Dict[str, List[float]], initial_capital: float = 100000):
        """
        Initialize backtest engine with price data.

        Args:
            prices: Dict mapping symbol to list of prices
            initial_capital: Starting capital for backtest
        """
        self.prices = prices
        self.symbols = list(prices.keys())
        self.initial_capital = initial_capital
        self.n_periods = len(next(iter(prices.values())))

        self.returns = {
            sym: np.diff(prices[sym]) / prices[sym][:-1]
            for sym in self.symbols
        }

        logger.info(f"Initialized backtest with {len(self.symbols)} symbols, {self.n_periods} periods")

    def run_strategy(
        self,
        weights: Dict[str, float],
        strategy_name: str = "Strategy",
        rebalance_freq: Optional[int] = None,
    ) -> BacktestResult:
        """
        Run a backtest with given weights.

        Args:
            weights: Dict mapping symbol to target weight
            strategy_name: Name for reporting
            rebalance_freq: Rebalance every N periods (None = buy & hold)

        Returns:
            BacktestResult with full performance metrics
        """
        weights_array = np.array([weights.get(sym, 0) for sym in self.symbols])
        weights_array = weights_array / weights_array.sum()

        portfolio_returns = np.zeros(self.n_periods - 1)
        for i, sym in enumerate(self.symbols):
            sym_returns = self.returns.get(sym, np.zeros(self.n_periods - 1))
            portfolio_returns += weights_array[i] * sym_returns

        cumulative = (1 + portfolio_returns).cumprod()
        equity_curve = [self.initial_capital]
        for ret in cumulative:
            equity_curve.append(equity_curve[0] * ret)

        daily_returns = np.diff(equity_curve) / np.maximum(equity_curve[:-1], 1e-10)

        total_return = (equity_curve[-1] / self.initial_capital) - 1 if self.initial_capital > 0 else 0
        n_years = len(daily_returns) / TRADING_DAYS_PER_YEAR
        annualized_return = ((1 + total_return) ** (1 / n_years) - 1) if n_years > 0 and total_return > -1 else 0
        annualized_vol = np.std(daily_returns) * np.sqrt(TRADING_DAYS_PER_YEAR) if len(daily_returns) > 0 else 0
        sharpe = (annualized_return - DEFAULT_RISK_FREE_RATE) / annualized_vol if annualized_vol > 0 else 0

        running_max = np.maximum.accumulate(equity_curve)
        drawdowns = [(float(eq) - float(max_val)) / float(max_val) if float(max_val) > 0 else 0 for eq, max_val in zip(equity_curve, running_max)]
        max_drawdown = min(drawdowns) if drawdowns else 0

        downside_returns = daily_returns[daily_returns < 0]
        downside_std = np.std(downside_returns) * np.sqrt(TRADING_DAYS_PER_YEAR) if len(downside_returns) > 0 else 0
        sortino = (annualized_return - DEFAULT_RISK_FREE_RATE) / downside_std if downside_std > 0 else 0

        calmar = abs(annualized_return / max_drawdown) if max_drawdown < 0 else 0

        positive_returns = daily_returns[daily_returns > 0]
        negative_returns = daily_returns[daily_returns < 0]
        win_rate = len(positive_returns) / len(daily_returns) if len(daily_returns) > 0 else 0
        avg_win = np.mean(positive_returns) if len(positive_returns) > 0 else 0
        avg_loss = np.mean(negative_returns) if len(negative_returns) > 0 else 0
        profit_factor = abs(np.sum(positive_returns) / np.sum(negative_returns)) if len(negative_returns) > 0 and np.sum(negative_returns) < 0 else float('inf')

        trades = np.sign(daily_returns)
        n_winning = np.sum((trades[:-1] > 0) & (np.diff(daily_returns) > 0))
        n_losing = np.sum((trades[:-1] < 0) & (np.diff(daily_returns) < 0))

        monthly_returns = self._calculate_monthly_returns(equity_curve)

        interpretation = (
            f"{strategy_name}: Return {total_return*100:.1f}% ({annualized_return*100:.1f}% annualized), "
            f"Sharpe {sharpe:.2f}, Max DD {max_drawdown*100:.1f}%, "
            f"Win Rate {win_rate*100:.1f}%, Profit Factor {profit_factor:.2f}"
        )

        return BacktestResult(
            strategy_name=strategy_name,
            total_return=total_return,
            annualized_return=annualized_return,
            annualized_volatility=annualized_vol,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(daily_returns),
            winning_trades=n_winning,
            losing_trades=n_losing,
            average_trade=np.nanmean(daily_returns),
            average_win=avg_win,
            average_loss=avg_loss,
            equity_curve=equity_curve,
            drawdown_curve=drawdowns,
            monthly_returns=monthly_returns,
            daily_returns=daily_returns.tolist(),
            interpretation=interpretation,
        )

    def _calculate_monthly_returns(self, equity_curve: np.ndarray) -> Dict[str, float]:
        """Calculate monthly returns from equity curve."""
        monthly = {}
        n_months = len(equity_curve) // 21
        for i in range(n_months):
            start_idx = i * 21
            end_idx = min((i + 1) * 21, len(equity_curve))
            month_return = (equity_curve[end_idx - 1] / equity_curve[start_idx]) - 1
            monthly[f"Month_{i+1}"] = month_return
        return monthly

    def compare_strategies(
        self,
        strategies: List[Tuple[Dict[str, float], str]],
    ) -> Dict[str, BacktestResult]:
        """
        Run backtest for multiple strategies and compare.

        Args:
            strategies: List of (weights, name) tuples

        Returns:
            Dict mapping strategy name to BacktestResult
        """
        results = {}
        for weights, name in strategies:
            results[name] = self.run_strategy(weights, name)
        return results
