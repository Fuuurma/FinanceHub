"""
Correlation Analyzer Service
Correlation and diversification analysis with interpretable results.

Philosophy:
- Correlation is not just a number - it tells you about portfolio behavior
- Diversification is about reducing correlation, not just adding assets
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import polars as pl
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

from utils.helpers.logger.logger import get_logger
from utils.constants.analytics import (
    CORRELATION_CLUSTER_THRESHOLD,
    CORRELATION_MIN_OBSERVATIONS,
    CORRELATION_METHOD,
    DIVERSIFICATION_EXCELLENT,
    DIVERSIFICATION_MODERATE,
    DIVERSIFICATION_POOR,
    MAX_ASSETS_IN_CORRELATION,
)

logger = get_logger(__name__)


@dataclass
class CorrelationReport:
    """
    Correlation matrix with clustering insights.
    
    What it represents:
    Correlation measures how assets move together (-1 to 1).
    
    Mathematical foundation:
    ρ(X,Y) = Cov(X,Y) / (σx × σy)
    
    Interpretation:
    - "BTC and tech stocks have 0.6 correlation - not the diversifier you think"
    - "Gold provides best diversification (0.1 correlation)"
    """
    symbol: str
    assets: List[str]
    correlation_matrix: List[List[float]]
    diversification_score: float
    clusters: List[List[str]]
    strongest_correlation: Any
    weakest_correlation: Any
    average_correlation: float
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DiversificationReport:
    """
    Portfolio diversification analysis.
    
    What it represents:
    How well-diversified a portfolio is based on correlations and weights.
    
    Interpretation:
    - "Diversification score of 85/100 - well diversified"
    - "Concentration risk of 0.15 - some overweight positions"
    """
    symbol: str
    diversification_score: float
    concentration_risk: float
    top_holdings_weight: float
    correlation_contribution: float
    recommendations: List[str]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CorrelationAnalyzer:
    """
    Correlation and diversification analysis.
    
    Usage:
        analyzer = CorrelationAnalyzer()
        report = analyzer.analyze_correlations(
            returns_dict={"AAPL": aapl_returns, "GOOGL": googl_returns}
        )
        
        div_report = analyzer.analyze_diversification(
            weights={"AAPL": 0.3, "GOOGL": 0.2, "MSFT": 0.2, "BTC": 0.15, "BOND": 0.15}
        )
    """
    
    def analyze_correlations(
        self,
        returns_dict: Dict[str, pl.Series],
        symbol: str = "portfolio"
    ) -> CorrelationReport:
        """
        Calculate correlation matrix with clustering insights.
        
        Args:
            returns_dict: Dict of asset symbol -> return series (Polars)
            symbol: Portfolio symbol for labeling
            
        Returns:
            CorrelationReport with matrix, clusters, and interpretation
            
        Example:
            >>> returns = {"AAPL": aapl_ret, "GOOGL": googl_ret, "BTC": btc_ret}
            >>> report = analyzer.analyze_correlations(returns, "MY_PORTFOLIO")
            >>> print(report.diversification_score)
            72
            >>> print(report.interpretation)
            "Diversification score: 72/100 - Well diversified portfolio"
        """
        assets = list(returns_dict.keys())
        
        if len(assets) < 2:
            return self._empty_correlation_report(symbol, assets)
        
        if len(assets) > MAX_ASSETS_IN_CORRELATION:
            logger.warning(f"Limiting correlation analysis to {MAX_ASSETS_IN_CORRELATION} assets")
            assets = assets[:MAX_ASSETS_IN_CORRELATION]
        
        n = len(assets)
        corr_matrix = np.zeros((n, n))
        
        valid_pairs = 0
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                if i == j:
                    corr_matrix[i][j] = 1.0
                elif i < j:
                    r1 = returns_dict[asset1]
                    r2 = returns_dict[asset2]
                    
                    mask = ~(r1.is_null() | r2.is_null())
                    r1_clean = r1.filter(mask).to_numpy()
                    r2_clean = r2.filter(mask).to_numpy()
                    
                    if len(r1_clean) >= CORRELATION_MIN_OBSERVATIONS:
                        corr = np.corrcoef(r1_clean, r2_clean)[0, 1]
                        if not np.isnan(corr):
                            corr_matrix[i][j] = corr
                            corr_matrix[j][i] = corr
                            valid_pairs += 1
        
        if valid_pairs == 0:
            return self._empty_correlation_report(symbol, assets)
        
        mask = ~np.eye(n, dtype=bool)
        avg_corr = np.mean(np.abs(corr_matrix[mask]))
        diversification_score = max(0, (1 - avg_corr) * 100)
        
        try:
            distance_matrix = 1 - np.abs(corr_matrix)
            condensed = squareform(distance_matrix)
            linkage_matrix = linkage(condensed, method='average')
            clusters_raw = fcluster(linkage_matrix, t=CORRELATION_CLUSTER_THRESHOLD, criterion='distance')
            clusters = []
            for c in set(clusters_raw):
                cluster_assets = [assets[i] for i, x in enumerate(clusters_raw) if x == c]
                clusters.append(cluster_assets)
        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
            clusters = [assets]
        
        max_corr = (-1.0, "", "")
        min_corr = (2.0, "", "")
        for i in range(n):
            for j in range(i+1, n):
                corr = corr_matrix[i][j]
                if corr > max_corr[0]:
                    max_corr = (corr, assets[i], assets[j])
                if corr < min_corr[0]:
                    min_corr = (corr, assets[i], assets[j])
        
        interpretation = self._generate_correlation_interpretation(
            diversification_score, max_corr, min_corr, avg_corr
        )
        
        return CorrelationReport(
            symbol=symbol,
            assets=assets,
            correlation_matrix=corr_matrix.tolist(),
            diversification_score=diversification_score,
            clusters=clusters,
            strongest_correlation=max_corr,
            weakest_correlation=min_corr,
            average_correlation=float(np.mean(corr_matrix[mask])),
            interpretation=interpretation,
        )
    
    def analyze_diversification(
        self,
        weights: Dict[str, float],
        returns_dict: Optional[Dict[str, pl.Series]] = None,
        symbol: str = "portfolio"
    ) -> DiversificationReport:
        """
        Analyze portfolio diversification.
        
        Args:
            weights: Dict of asset symbol -> portfolio weight
            returns_dict: Optional return series for correlation contribution
            symbol: Portfolio symbol
            
        Returns:
            DiversificationReport with score and recommendations
        """
        total_weight = sum(weights.values())
        weights_normalized = {k: v/total_weight for k, v in weights.items()}
        
        hhi = sum(w ** 2 for w in weights_normalized.values())
        concentration_risk = hhi
        
        top_holdings = sorted(weights_normalized.items(), key=lambda x: x[1], reverse=True)[:3]
        top_holdings_weight = sum(w for _, w in top_holdings)
        
        corr_contribution = 0.0
        if returns_dict and len(weights) > 1:
            corr_report = self.analyze_correlations(
                {k: returns_dict[k] for k in weights if k in returns_dict},
                symbol
            )
            corr_contribution = corr_report.diversification_score
        
        diversification_score = self._calculate_diversification_score(
            concentration_risk, top_holdings_weight, corr_contribution
        )
        
        recommendations = self._generate_diversification_recommendations(
            weights_normalized, concentration_risk, top_holdings_weight, corr_contribution
        )
        
        interpretation = self._generate_diversification_interpretation(diversification_score)
        
        return DiversificationReport(
            symbol=symbol,
            diversification_score=diversification_score,
            concentration_risk=concentration_risk,
            top_holdings_weight=top_holdings_weight,
            correlation_contribution=corr_contribution,
            recommendations=recommendations,
            interpretation=interpretation,
        )
    
    def _calculate_diversification_score(
        self,
        concentration: float,
        top_weight: float,
        correlation_score: float
    ) -> float:
        """Calculate overall diversification score (0-100)."""
        conc_score = max(0, (1 - concentration * 2) * 40)
        weight_score = max(0, (1 - top_weight) * 30)
        corr_score = correlation_score * 0.3 if correlation_score > 0 else 30
        
        return min(100, conc_score + weight_score + corr_score)
    
    def _generate_correlation_interpretation(
        self,
        score: float,
        max_corr: Tuple[float, str, str],
        min_corr: Tuple[float, str, str],
        avg_corr: float
    ) -> str:
        """Generate correlation interpretation."""
        interp = f"Diversification score: {score:.0f}/100 - "
        
        if score >= DIVERSIFICATION_EXCELLENT:
            interp += "Well diversified portfolio"
        elif score >= DIVERSIFICATION_MODERATE:
            interp += "Moderately correlated, consider diversification"
        else:
            interp += "Highly correlated holdings"
        
        interp += f". Avg correlation: {avg_corr:.2f}"
        
        if max_corr[0] > 0.7:
            interp += f". Warning: {max_corr[1]} & {max_corr[2]} are highly correlated ({max_corr[0]:.2f})"
        
        if min_corr[0] < 0.2 and min_corr[0] > -0.5:
            interp += f". {min_corr[1]} & {min_corr[2]} provide diversification ({min_corr[0]:.2f})"
        
        return interp
    
    def _generate_diversification_interpretation(self, score: float) -> str:
        """Generate diversification interpretation."""
        if score >= DIVERSIFICATION_EXCELLENT:
            return f"Diversification score: {score:.0f}/100 - Excellent diversification"
        elif score >= DIVERSIFICATION_MODERATE:
            return f"Diversification score: {score:.0f}/100 - Good, with room for improvement"
        elif score >= DIVERSIFICATION_POOR:
            return f"Diversification score: {score:.0f}/100 - Consider adding uncorrelated assets"
        else:
            return f"Diversification score: {score:.0f}/100 - Highly concentrated, high risk"
    
    def _generate_diversification_recommendations(
        self,
        weights: Dict[str, float],
        concentration: float,
        top_weight: float,
        correlation_score: float
    ) -> List[str]:
        """Generate diversification recommendations."""
        recs = []
        
        if top_weight > 0.4:
            recs.append(f"Top holding is {top_weight*100:.0f}% - consider reducing concentration")
        
        if concentration > 0.25:
            recs.append("High concentration risk - spread across more assets")
        
        if correlation_score < DIVERSIFICATION_MODERATE and len(weights) > 3:
            recs.append("Consider adding assets with low correlation to existing holdings")
        
        if len(weights) < 5:
            recs.append("Portfolio has fewer than 5 holdings - limited diversification")
        
        if not recs:
            recs.append("Portfolio is well diversified")
        
        return recs
    
    def _empty_correlation_report(
        self, symbol: str, assets: List[str]
    ) -> CorrelationReport:
        """Return empty correlation report."""
        return CorrelationReport(
            symbol=symbol,
            assets=assets,
            correlation_matrix=[],
            diversification_score=0,
            clusters=[],
            strongest_correlation=("", "", 0),
            weakest_correlation=("", "", 0),
            average_correlation=0,
            interpretation="Insufficient data for correlation analysis",
        )
