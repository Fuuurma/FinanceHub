"""
Risk Analyzer Service
Comprehensive risk analysis with interpretable results.

Philosophy:
- Risk is more than volatility - it's about understanding downside potential
- VaR and CVaR tell you what you might lose, not just how volatile you are
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
import polars as pl
from scipy import stats

from utils.helpers.logger.logger import get_logger
from utils.constants.analytics import (
    TRADING_DAYS_PER_YEAR,
    DEFAULT_CONFIDENCE_LEVEL,
    VAR_CONFIDENCE_LEVELS,
    DEFAULT_RISK_FREE_RATE,
    HISTOGRAM_BINS,
    VOLATILITY_LOW,
    VOLATILITY_MODERATE,
    VOLATILITY_HIGH,
)

logger = get_logger(__name__)


@dataclass
class VolatilityReport:
    """
    Volatility analysis with interpretation.
    
    What it represents:
    Volatility measures the dispersion of returns. Higher = more risk.
    
    Mathematical foundation:
    - Daily σ = std(returns)
    - Annualized σ = Daily σ × √252
    - Semivariance = avg(negative returns below target)²
    
    Interpretation:
    - "20% annualized volatility means daily moves average 1.25%"
    - "Semivariance of 15% indicates downside risk is lower than upside"
    """
    symbol: str
    daily_volatility: float
    annualized_volatility: float
    semivariance: float
    skewness: float
    kurtosis: float
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DrawdownReport:
    """
    Drawdown analysis with peak/valley tracking.
    
    What it represents:
    Drawdown measures decline from peak to trough. Shows pain periods.
    
    Interpretation:
    - "Max drawdown of 20% occurred in 2022, took 180 days to recover"
    - "Currently 5% below peak - early warning sign"
    """
    symbol: str
    max_drawdown: float
    max_drawdown_date: str
    recovery_date: Optional[str]
    current_drawdown: float
    drawdown_duration: int
    drawdown_percentiles: Dict[str, float]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VaRReport:
    """
    Value at Risk with practical interpretation.
    
    What it represents:
    VaR answers: "What's my worst-case loss with X% confidence?"
    
    Mathematical foundation (historical):
    VaR_α = -percentile(returns, 1 - α)
    
    Interpretation:
    - "95% confident daily loss won't exceed $5,000"
    - "This means 19 out of 20 days, loss < $5,000"
    """
    symbol: str
    var_daily: float
    var_weekly: Optional[float]
    var_monthly: Optional[float]
    confidence_level: float
    method: str
    exceedances: int
    interpretation: str
    return_distribution_bins: List[float]
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CVaRReport:
    """
    Conditional Value at Risk (Expected Shortfall).
    
    What it represents:
    CVaR measures the average loss when VaR is exceeded. More coherent than VaR.
    
    Mathematical foundation:
    CVaR = E[Loss | Loss > VaR]
    
    Interpretation:
    - "When losses exceed VaR ($5K), average loss is $7.5K"
    - "CVaR captures tail risk better than VaR alone"
    """
    symbol: str
    cvar_daily: float
    confidence_level: float
    var_at_level: float
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RiskAnalyzer:
    """
    Comprehensive risk analysis with interpretable results.
    
    Usage:
        analyzer = RiskAnalyzer()
        vol_report = analyzer.analyze_volatility(returns, symbol="AAPL")
        var_report = analyzer.calculate_var(returns, symbol="AAPL", confidence=0.95)
        dd_report = analyzer.analyze_drawdown(prices, symbol="AAPL")
    """
    
    def analyze_volatility(
        self,
        returns: pl.Series,
        symbol: str,
        annualized: bool = True
    ) -> VolatilityReport:
        """
        Calculate volatility with context.
        
        Args:
            returns: Return series (Polars)
            symbol: Asset symbol
            annualized: Return annualized volatility (default: True)
        
        Returns:
            VolatilityReport with all metrics and interpretation
        """
        if len(returns) < 2:
            return self._empty_volatility_report(symbol)
        
        ret_array = returns.to_numpy()
        ret_array = ret_array[~np.isnan(ret_array)]
        
        daily_vol = np.std(ret_array, ddof=1)
        annualized_vol = daily_vol * np.sqrt(TRADING_DAYS_PER_YEAR)
        
        negative_returns = ret_array[ret_array < 0]
        semivariance = np.mean(negative_returns ** 2) if len(negative_returns) > 0 else 0
        
        skewness = stats.skew(ret_array)
        kurtosis = stats.kurtosis(ret_array)
        
        interpretation = self._generate_volatility_interpretation(annualized_vol, semivariance)
        
        return VolatilityReport(
            symbol=symbol,
            daily_volatility=daily_vol,
            annualized_volatility=annualized_vol,
            semivariance=semivariance,
            skewness=skewness,
            kurtosis=kurtosis,
            interpretation=interpretation,
        )
    
    def analyze_drawdown(
        self,
        equity_curve: pl.Series,
        symbol: str
    ) -> DrawdownReport:
        """
        Analyze drawdowns with peak/valley tracking.
        
        Args:
            equity_curve: Portfolio value over time (Polars)
            symbol: Portfolio symbol
            
        Returns:
            DrawdownReport with all metrics and interpretation
        """
        if len(equity_curve) < 2:
            return self._empty_drawdown_report(symbol)
        
        prices = equity_curve.to_numpy()
        running_max = np.maximum.accumulate(prices)
        drawdown = (prices - running_max) / running_max
        
        max_dd = np.min(drawdown)
        max_dd_idx = np.argmin(drawdown)
        
        recovery_idx = None
        for i in range(max_dd_idx + 1, len(drawdown)):
            if prices[i] >= running_max[max_dd_idx]:
                recovery_idx = i
                break
        
        current_dd = drawdown[-1]
        duration = (recovery_idx - max_dd_idx) if recovery_idx else None
        
        percentiles = {
            "p10": float(np.percentile(drawdown, 10)),
            "p25": float(np.percentile(drawdown, 25)),
            "p50": float(np.percentile(drawdown, 50)),
            "p75": float(np.percentile(drawdown, 75)),
            "p90": float(np.percentile(drawdown, 90)),
        }
        
        interpretation = self._generate_drawdown_interpretation(
            max_dd, max_dd_idx, recovery_idx, duration, current_dd
        )
        
        return DrawdownReport(
            symbol=symbol,
            max_drawdown=max_dd,
            max_drawdown_date=f"Day {max_dd_idx}",
            recovery_date=f"Day {recovery_idx}" if recovery_idx else None,
            current_drawdown=current_dd,
            drawdown_duration=duration or 0,
            drawdown_percentiles=percentiles,
            interpretation=interpretation,
        )
    
    def calculate_var(
        self,
        returns: pl.Series,
        symbol: str,
        confidence: float = DEFAULT_CONFIDENCE_LEVEL,
        method: str = "historical"
    ) -> VaRReport:
        """
        Calculate Value at Risk with interpretation.
        
        Args:
            returns: Return series (Polars)
            symbol: Asset symbol
            confidence: Confidence level (0.90, 0.95, 0.99)
            method: "historical", "parametric", or "monte_carlo"
        
        Returns:
            VaRReport with all metrics and interpretation
        """
        if len(returns) < 30:
            return self._empty_var_report(symbol, confidence)
        
        ret_array = returns.to_numpy()
        ret_array = ret_array[~np.isnan(ret_array)]
        
        if method == "historical":
            var = -np.percentile(ret_array, (1 - confidence) * 100)
        elif method == "parametric":
            mu = np.mean(ret_array)
            sigma = np.std(ret_array, ddof=1)
            var = -(mu + stats.norm.ppf(1 - confidence) * sigma)
        else:
            mu = np.mean(ret_array)
            sigma = np.std(ret_array, ddof=1)
            sim_returns = np.random.normal(mu, sigma, 10000)
            var = -np.percentile(sim_returns, (1 - confidence) * 100)
        
        exceedances = np.sum(ret_array < -var)
        
        bins = np.linspace(ret_array.min(), ret_array.max(), HISTOGRAM_BINS).tolist()
        
        interpretation = self._generate_var_interpretation(
            symbol, var, confidence, method, exceedances, len(ret_array)
        )
        
        return VaRReport(
            symbol=symbol,
            var_daily=var,
            var_weekly=var * np.sqrt(5) if var else None,
            var_monthly=var * np.sqrt(21) if var else None,
            confidence_level=confidence,
            method=method,
            exceedances=exceedances,
            interpretation=interpretation,
            return_distribution_bins=bins,
        )
    
    def calculate_cvar(
        self,
        returns: pl.Series,
        symbol: str,
        confidence: float = DEFAULT_CONFIDENCE_LEVEL
    ) -> CVaRReport:
        """
        Calculate Conditional Value at Risk (Expected Shortfall).
        
        Args:
            returns: Return series (Polars)
            symbol: Asset symbol
            confidence: Confidence level
            
        Returns:
            CVaRReport with all metrics and interpretation
        """
        if len(returns) < 30:
            return self._empty_cvar_report(symbol, confidence)
        
        ret_array = returns.to_numpy()
        ret_array = ret_array[~np.isnan(ret_array)]
        
        var_threshold = np.percentile(ret_array, (1 - confidence) * 100)
        tail_losses = ret_array[ret_array <= var_threshold]
        cvar = -np.mean(tail_losses) if len(tail_losses) > 0 else 0
        
        interpretation = self._generate_cvar_interpretation(
            symbol, cvar, var_threshold, confidence
        )
        
        return CVaRReport(
            symbol=symbol,
            cvar_daily=cvar,
            confidence_level=confidence,
            var_at_level=var_threshold,
            interpretation=interpretation,
        )
    
    def _generate_volatility_interpretation(
        self,
        annualized_vol: float,
        semivariance: float
    ) -> str:
        """Generate volatility interpretation."""
        daily_vol = annualized_vol / np.sqrt(TRADING_DAYS_PER_YEAR)
        
        interp = f"Daily moves average {daily_vol*100:.2f}% "
        interp += f"({annualized_vol*100:.1f}% annualized)"
        
        if annualized_vol < VOLATILITY_LOW:
            interp += " - Low volatility, suitable for risk-averse investors"
        elif annualized_vol < VOLATILITY_MODERATE:
            interp += " - Moderate volatility, typical for equities"
        elif annualized_vol < VOLATILITY_HIGH:
            interp += " - High volatility, expect significant swings"
        else:
            interp += " - Very high volatility, speculative territory"
        
        return interp
    
    def _generate_drawdown_interpretation(
        self,
        max_dd: float,
        max_dd_idx: int,
        recovery_idx: Optional[int],
        duration: Optional[int],
        current_dd: float
    ) -> str:
        """Generate drawdown interpretation."""
        interp = f"Maximum drawdown of {abs(max_dd)*100:.1f}%"
        
        if recovery_idx:
            interp += f", recovered in {duration} days"
        else:
            interp += ", still in drawdown"
        
        if current_dd < -0.05:
            interp += f". Currently {abs(current_dd)*100:.1f}% below peak - monitor closely"
        elif current_dd < 0:
            interp += f". Currently {abs(current_dd)*100:.1f}% below peak"
        
        return interp
    
    def _generate_var_interpretation(
        self,
        symbol: str,
        var: float,
        confidence: float,
        method: str,
        exceedances: int,
        total_days: int
    ) -> str:
        """Generate VaR interpretation."""
        interp = f"At {confidence*100:.0f}% confidence, daily VaR is {abs(var)*100:.2f}%"
        
        expected_exceed = (1 - confidence) * total_days
        if exceedances > expected_exceed * 1.5:
            interp += f" - WARNING: Exceeded {exceedances} times (expected ~{expected_exceed:.0f})"
        elif exceedances < expected_exceed * 0.5:
            interp += f" - Conservative: Only exceeded {exceedances} times"
        
        interp += f" ({method} method)"
        
        return interp
    
    def _generate_cvar_interpretation(
        self,
        symbol: str,
        cvar: float,
        var_at_level: float,
        confidence: float
    ) -> str:
        """Generate CVaR interpretation."""
        interp = f"When losses exceed VaR ({abs(var_at_level)*100:.2f}%), "
        interp += f"average loss is {abs(cvar)*100:.2f}%"
        
        interp += f" ({confidence*100:.0f}% confidence)"
        
        interp += " - CVaR captures tail risk better than VaR alone"
        
        return interp
    
    def _empty_volatility_report(self, symbol: str) -> VolatilityReport:
        """Return empty volatility report."""
        return VolatilityReport(
            symbol=symbol,
            daily_volatility=0,
            annualized_volatility=0,
            semivariance=0,
            skewness=0,
            kurtosis=0,
            interpretation="Insufficient data for volatility analysis",
        )
    
    def _empty_drawdown_report(self, symbol: str) -> DrawdownReport:
        """Return empty drawdown report."""
        return DrawdownReport(
            symbol=symbol,
            max_drawdown=0,
            max_drawdown_date="N/A",
            recovery_date=None,
            current_drawdown=0,
            drawdown_duration=0,
            drawdown_percentiles={},
            interpretation="Insufficient data for drawdown analysis",
        )
    
    def _empty_var_report(
        self, symbol: str, confidence: float
    ) -> VaRReport:
        """Return empty VaR report."""
        return VaRReport(
            symbol=symbol,
            var_daily=0,
            var_weekly=None,
            var_monthly=None,
            confidence_level=confidence,
            method="historical",
            exceedances=0,
            interpretation="Insufficient data for VaR calculation",
            return_distribution_bins=[],
        )
    
    def _empty_cvar_report(
        self, symbol: str, confidence: float
    ) -> CVaRReport:
        """Return empty CVaR report."""
        return CVaRReport(
            symbol=symbol,
            cvar_daily=0,
            confidence_level=confidence,
            var_at_level=0,
            interpretation="Insufficient data for CVaR calculation",
        )
