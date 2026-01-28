"""
Performance Analyzer Service
Comprehensive portfolio performance analysis with interpretable results.

Philosophy:
- Return not just numbers, but what they mean for your portfolio
- Enable composition and chaining of analyses
- Document the "why" behind each metric
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import polars as pl
from scipy import stats

from utils.helpers.logger.logger import get_logger
from utils.constants.analytics import (
    TRADING_DAYS_PER_YEAR,
    DEFAULT_RISK_FREE_RATE,
    SHARPE_EXCELLENT,
    SHARPE_GOOD,
    SHARPE_ACCEPTABLE,
    DEFAULT_FACTORS,
)

logger = get_logger(__name__)


@dataclass
class PerformanceReport:
    """
    Comprehensive performance analysis report.
    
    What it represents:
    Complete return analysis with benchmarks and interpretable metrics.
    
    Mathematical foundation:
    - Total Return = (End Price - Start Price) / Start Price
    - Annualized Return = (1 + Total Return)^(252/trading_days) - 1
    """
    symbol: str
    total_return: float
    annualized_return: float
    best_period: Tuple[str, float]
    worst_period: Tuple[str, float]
    monthly_distribution: Dict[str, float]
    positive_months: int
    negative_months: int
    hit_rate: Optional[float]
    benchmark_return: Optional[float]
    excess_return: Optional[float]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RiskAdjustedReport:
    """
    Risk-adjusted performance metrics.
    
    What it represents:
    How efficiently the portfolio generates returns relative to risk taken.
    
    Mathematical foundation:
    - Sharpe Ratio = (Rp - Rf) / σp
    - Sortino Ratio = (Rp - Rf) / σdownside
    - Treynor Ratio = (Rp - Rf) / β
    - Information Ratio = (Rp - Rb) / Tracking Error
    - Alpha = Rp - (Rf + β × (Rm - Rf))
    """
    symbol: str
    sharpe_ratio: float
    sortino_ratio: float
    treynor_ratio: Optional[float]
    information_ratio: Optional[float]
    beta: Optional[float]
    alpha: Optional[float]
    r_squared: Optional[float]
    tracking_error: Optional[float]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FactorReport:
    """
    Factor exposure analysis.
    
    What it represents:
    Where portfolio returns are coming from (market, size, value, momentum, etc.).
    
    Mathematical foundation:
    Portfolio = α + β₁·Market + β₂·Size + β₃·Value + β₄·Momentum + ε
    
    Interpretation:
    - "Portfolio has 1.2x market exposure, small-cap tilt of 0.3"
    - "Momentum factor contributes 40% of returns"
    """
    symbol: str
    factor_betas: Dict[str, float]
    factor_returns: Dict[str, float]
    alpha: float
    r_squared: float
    top_contributors: List[Tuple[str, float]]
    bottom_contributors: List[Tuple[str, float]]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PerformanceAnalyzer:
    """
    Analyze portfolio performance with benchmarks and interpretations.
    
    Usage:
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze_returns(
            prices=price_series,
            symbol="AAPL",
            benchmark=benchmark_series
        )
        
        risk_report = analyzer.analyze_risk_adjusted(
            portfolio_returns=returns,
            benchmark_returns=benchmark,
            risk_free_rate=0.05
        )
    """
    
    def analyze_returns(
        self,
        prices: pl.Series,
        symbol: str,
        benchmark: Optional[pl.Series] = None,
        period: str = "1y"
    ) -> PerformanceReport:
        """
        Calculate comprehensive return metrics.
        
        Args:
            prices: Price series (Polars)
            symbol: Asset symbol for labeling
            benchmark: Benchmark price series for comparison
            period: Time period string (e.g., "1y", "6m", "1d")
        
        Returns:
            PerformanceReport with all metrics and interpretation
            
        Example:
            >>> analyzer = PerformanceAnalyzer()
            >>> report = analyzer.analyze_returns(prices, "AAPL")
            >>> print(report.interpretation)
            "Portfolio returned 15.2% over the past year, outperforming benchmark by 3.1%"
        """
        if len(prices) < 2:
            return self._empty_performance_report(symbol)
        
        prices_np = prices.to_numpy()
        
        total_return = (prices_np[-1] / prices_np[0]) - 1
        
        n_years = len(prices_np) / TRADING_DAYS_PER_YEAR
        annualized_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0
        
        returns = np.diff(prices_np) / prices_np[:-1]
        
        best_idx = np.argmax(returns)
        worst_idx = np.argmin(returns)
        best_period = (f"Day {best_idx}", float(returns[best_idx]))
        worst_period = (f"Day {worst_idx}", float(returns[worst_idx]))
        
        monthly_dist = self._calculate_monthly_distribution(prices_np)
        
        positive = np.sum(returns > 0)
        negative = np.sum(returns < 0)
        total = len(returns)
        hit_rate = positive / total if total > 0 else 0
        
        benchmark_return = None
        excess_return = None
        if benchmark is not None and len(benchmark) >= 2:
            bench_np = benchmark.to_numpy()
            benchmark_return = (bench_np[-1] / bench_np[0]) - 1
            excess_return = annualized_return - benchmark_return
        
        interpretation = self._generate_return_interpretation(
            symbol, annualized_return, benchmark_return, excess_return
        )
        
        return PerformanceReport(
            symbol=symbol,
            total_return=total_return,
            annualized_return=annualized_return,
            best_period=best_period,
            worst_period=worst_period,
            monthly_distribution=monthly_dist,
            positive_months=positive,
            negative_months=negative,
            hit_rate=hit_rate,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            interpretation=interpretation,
        )
    
    def analyze_risk_adjusted(
        self,
        portfolio_returns: pl.Series,
        symbol: str = "",
        benchmark_returns: Optional[pl.Series] = None,
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    ) -> RiskAdjustedReport:
        """
        Calculate risk-adjusted return metrics.
        
        Args:
            portfolio_returns: Portfolio return series (Polars)
            symbol: Asset/portfolio symbol
            benchmark_returns: Benchmark return series
            risk_free_rate: Annual risk-free rate (default: 5%)
        
        Returns:
            RiskAdjustedReport with all metrics and interpretation
            
        Example:
            >>> report = analyzer.analyze_risk_adjusted(returns, "PORTFOLIO")
            >>> print(report.sharpe_ratio)
            1.25
            >>> print(report.interpretation)
            "Sharpe of 1.25 indicates good risk-adjusted performance"
        """
        if len(portfolio_returns) < 10:
            return self._empty_risk_adjusted_report(symbol)
        
        ret_array = portfolio_returns.to_numpy()
        daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR
        excess_returns = ret_array - daily_rf
        
        mean_excess = np.mean(excess_returns)
        std_portfolio = np.std(ret_array, ddof=1)
        
        sharpe = (mean_excess / std_portfolio) * np.sqrt(TRADING_DAYS_PER_YEAR) if std_portfolio > 0 else 0
        
        negative_returns = ret_array[ret_array < 0]
        downside_std = np.std(negative_returns, ddof=1) if len(negative_returns) > 0 else 0
        sortino = (mean_excess / downside_std) * np.sqrt(TRADING_DAYS_PER_YEAR) if downside_std > 0 else 0
        
        beta = None
        treynor = None
        alpha = None
        r_squared = None
        tracking_error = None
        information_ratio = None
        
        if benchmark_returns is not None:
            bench_array = benchmark_returns.to_numpy()
            if len(bench_array) == len(ret_array):
                covariance = np.cov(ret_array, bench_array)[0][ 1]
                bench_variance = np.var(bench_array)
                if bench_variance > 0:
                    beta = covariance / bench_variance
                
                if beta is not None and beta > 0:
                    treynor = (mean_excess / beta) * TRADING_DAYS_PER_YEAR
                
                if beta is not None:
                    expected_return = daily_rf + beta * (np.mean(bench_array) - daily_rf)
                    alpha = mean_excess - expected_return
                    r_squared = covariance ** 2 / (std_portfolio ** 2 * bench_variance) if std_portfolio > 0 and bench_variance > 0 else 0
                
                tracking_errors = ret_array - bench_array
                tracking_error = np.std(tracking_errors, ddof=1) if len(tracking_errors) > 0 else 0
                if tracking_error > 0:
                    information_ratio = mean_excess / tracking_error * np.sqrt(TRADING_DAYS_PER_YEAR)
        
        interpretation = self._generate_sharpe_interpretation(sharpe, sortino, beta, alpha)
        
        return RiskAdjustedReport(
            symbol=symbol,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            treynor_ratio=treynor,
            information_ratio=information_ratio,
            beta=beta,
            alpha=alpha,
            r_squared=r_squared,
            tracking_error=tracking_error,
            interpretation=interpretation,
        )
    
    def analyze_factor_exposures(
        self,
        portfolio_returns: pl.Series,
        symbol: str = "",
        factor_returns: Optional[Dict[str, pl.Series]] = None
    ) -> FactorReport:
        """
        Calculate factor exposures using OLS regression.
        
        Args:
            portfolio_returns: Portfolio return series
            symbol: Portfolio symbol
            factor_returns: Dict of factor name -> return series
            
        Returns:
            FactorReport with exposures and interpretation
            
        Example:
            >>> factors = {"market": market_returns, "size": size_returns}
            >>> report = analyzer.analyze_factor_exposures(returns, "PORT", factors)
            >>> print(report.factor_betas)
            {"market": 1.2, "size": 0.3, "value": -0.1}
        """
        if factor_returns is None:
            factor_returns = {f: pl.Series([0]) for f in DEFAULT_FACTORS}
        
        ret_array = portfolio_returns.to_numpy()
        
        if len(ret_array) < len(factor_returns) + 5:
            return self._empty_factor_report(symbol)
        
        factor_names = list(factor_returns.keys())
        n_factors = len(factor_names)
        
        if n_factors == 0:
            return self._empty_factor_report(symbol)
        
        X = np.column_stack([factor_returns[name].to_numpy() for name in factor_names])
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(ret_array))
        X_clean = X[mask]
        y_clean = ret_array[mask]
        
        if len(y_clean) < n_factors + 5:
            return self._empty_factor_report(symbol)
        
        try:
            X_with_const = np.column_stack([np.ones(len(X_clean)), X_clean])
            coeffs = np.linalg.lstsq(X_with_const, y_clean, rcond=None)[0]
            
            alpha = coeffs[0]
            betas = coeffs[1:]
            
            residuals = y_clean - X_with_const @ coeffs
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            factor_betas = dict(zip(factor_names, betas))
            
            factor_contrib = X_clean @ betas
            contributions = {name: float(np.mean(X_clean[:, i] * betas[i])) for i, name in enumerate(factor_names)}
            
            sorted_contrib = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
            top_contributors = sorted_contrib[:3]
            bottom_contributors = sorted_contrib[-3:]
            
            interpretation = self._generate_factor_interpretation(factor_betas, alpha, r_squared)
            
            return FactorReport(
                symbol=symbol,
                factor_betas=factor_betas,
                factor_returns=contributions,
                alpha=alpha,
                r_squared=r_squared,
                top_contributors=top_contributors,
                bottom_contributors=bottom_contributors,
                interpretation=interpretation,
            )
            
        except Exception as e:
            logger.error(f"Error in factor analysis: {e}")
            return self._empty_factor_report(symbol)
    
    def _calculate_monthly_distribution(
        self, prices: np.ndarray
    ) -> Dict[str, float]:
        """Calculate average monthly returns."""
        return {"data": float(np.mean(np.diff(prices) / prices[:-1]))}
    
    def _generate_return_interpretation(
        self,
        symbol: str,
        annualized: float,
        benchmark: Optional[float],
        excess: Optional[float]
    ) -> str:
        """Generate human-readable interpretation."""
        interp = f"{symbol} returned {annualized*100:.1f}% annualized"
        
        if benchmark is not None:
            diff = annualized - benchmark
            if diff > 0:
                interp += f", outperforming benchmark by {diff*100:.1f}%"
            else:
                interp += f", underperforming benchmark by {abs(diff)*100:.1f}%"
        
        if annualized > 0.20:
            interp += " - Excellent performance"
        elif annualized > 0.10:
            interp += " - Strong performance"
        elif annualized > 0:
            interp += " - Positive but modest returns"
        else:
            interp += " - Negative returns"
        
        return interp
    
    def _generate_sharpe_interpretation(
        self,
        sharpe: float,
        sortino: float,
        beta: Optional[float],
        alpha: Optional[float]
    ) -> str:
        """Generate Sharpe ratio interpretation."""
        if sharpe >= SHARPE_EXCELLENT:
            interp = f"Sharpe of {sharpe:.2f} indicates excellent risk-adjusted performance"
        elif sharpe >= SHARPE_GOOD:
            interp = f"Sharpe of {sharpe:.2f} indicates good risk-adjusted performance"
        elif sharpe >= SHARPE_ACCEPTABLE:
            interp = f"Sharpe of {sharpe:.2f} is acceptable but has room for improvement"
        else:
            interp = f"Sharpe of {sharpe:.2f} suggests poor risk-adjusted returns"
        
        if beta is not None:
            if beta > 1.2:
                interp += f", with high market beta ({beta:.2f})"
            elif beta < 0.8:
                interp += f", with defensive beta ({beta:.2f})"
        
        if alpha is not None and alpha > 0:
            interp += f", generating {alpha*100:.2f}% alpha"
        elif alpha is not None and alpha < 0:
            interp += f", underperforming by {abs(alpha)*100:.2f}% alpha"
        
        return interp
    
    def _generate_factor_interpretation(
        self,
        betas: Dict[str, float],
        alpha: float,
        r_squared: float
    ) -> str:
        """Generate factor exposure interpretation."""
        interp = f"Factor analysis (R²={r_squared:.2f}): "
        
        factors = []
        for name, beta in betas.items():
            if abs(beta) > 0.1:
                if name == "market":
                    factors.append(f"{'high' if beta > 1 else 'low'} market ({beta:.2f})")
                elif name == "size":
                    factors.append(f"{'small-cap' if beta > 0 else 'large-cap'} tilt ({beta:.2f})")
                elif name == "value":
                    factors.append(f"{'value' if beta > 0 else 'growth'} ({beta:.2f})")
                elif name == "momentum":
                    factors.append(f"{'momentum' if beta > 0 else 'contrarian'} ({beta:.2f})")
        
        if factors:
            interp += ", ".join(factors)
        else:
            interp += "market-neutral positioning"
        
        if alpha > 0.001:
            interp += f", {alpha*100:.2f}% alpha generation"
        
        return interp
    
    def _empty_performance_report(self, symbol: str) -> PerformanceReport:
        """Return empty report for insufficient data."""
        return PerformanceReport(
            symbol=symbol,
            total_return=0,
            annualized_return=0,
            best_period=("N/A", 0),
            worst_period=("N/A", 0),
            monthly_distribution={},
            positive_months=0,
            negative_months=0,
            hit_rate=None,
            benchmark_return=None,
            excess_return=None,
            interpretation="Insufficient data for analysis",
        )
    
    def _empty_risk_adjusted_report(self, symbol: str) -> RiskAdjustedReport:
        """Return empty risk-adjusted report."""
        return RiskAdjustedReport(
            symbol=symbol,
            sharpe_ratio=0,
            sortino_ratio=0,
            treynor_ratio=None,
            information_ratio=None,
            beta=None,
            alpha=None,
            r_squared=None,
            tracking_error=None,
            interpretation="Insufficient data for analysis",
        )
    
    def _empty_factor_report(self, symbol: str) -> FactorReport:
        """Return empty factor report."""
        return FactorReport(
            symbol=symbol,
            factor_betas={},
            factor_returns={},
            alpha=0,
            r_squared=0,
            top_contributors=[],
            bottom_contributors=[],
            interpretation="Insufficient data for factor analysis",
        )
