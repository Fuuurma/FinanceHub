import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from decimal import Decimal

from utils.services.performance.analyzer import PerformanceAnalyzer, PerformanceReport, RiskAdjustedReport, FactorReport
from utils.services.risk.analyzer import RiskAnalyzer
from utils.services.correlation.analyzer import CorrelationAnalyzer, CorrelationReport, DiversificationReport
from utils.services.options.analyzer import OptionsAnalyzer


@pytest.fixture
def sample_polars_prices():
    """Generate sample price data as polars Series."""
    import numpy as np
    import polars as pl
    from datetime import datetime
    
    np.random.seed(42)
    n = 252
    dates = [datetime(2024, 1, 1) for _ in range(n)]
    returns = np.random.normal(0.0005, 0.01, n)
    prices = 100 * (1 + returns).cumprod()
    
    return pl.Series(name='price', values=prices)


@pytest.fixture
def sample_polars_returns():
    """Generate sample returns as polars Series."""
    import numpy as np
    import polars as pl
    from datetime import datetime
    
    np.random.seed(42)
    n = 252
    dates = [datetime(2024, 1, 1) for _ in range(n)]
    returns = np.random.normal(0.0005, 0.01, n)
    
    return pl.Series(name='returns', values=returns)


@pytest.fixture
def sample_returns_dict():
    """Generate sample returns as dict for correlation analysis."""
    import numpy as np
    import polars as pl
    from datetime import datetime
    
    np.random.seed(42)
    n = 252
    dates = [datetime(2024, 1, 1) for _ in range(n)]
    
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    returns_dict = {}
    
    for asset in assets:
        returns = np.random.normal(0.0005, 0.015, n)
        returns_dict[asset] = pl.Series(name=asset, values=returns)
    
    return returns_dict


class TestPerformanceAnalyzer:
    """Tests for PerformanceAnalyzer service."""
    
    def test_analyze_returns(self, sample_polars_prices):
        """Test return analysis."""
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze_returns(
            prices=sample_polars_prices,
            symbol="TEST"
        )
        
        assert isinstance(report, PerformanceReport)
        assert hasattr(report, 'total_return')
        assert hasattr(report, 'annualized_return')
        assert hasattr(report, 'interpretation')
    
    def test_analyze_risk_adjusted(self, sample_polars_returns):
        """Test risk-adjusted return analysis."""
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze_risk_adjusted(
            portfolio_returns=sample_polars_returns,
            risk_free_rate=0.05
        )
        
        assert isinstance(report, RiskAdjustedReport)
        assert hasattr(report, 'sharpe_ratio')
        assert hasattr(report, 'sortino_ratio')
        assert hasattr(report, 'interpretation')
    
    def test_analyze_factor_exposures(self, sample_polars_returns):
        """Test factor analysis."""
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze_factor_exposures(
            portfolio_returns=sample_polars_returns,
            symbol="TEST"
        )
        
        assert isinstance(report, FactorReport)
        assert hasattr(report, 'factor_betas')
        assert hasattr(report, 'alpha')
        assert hasattr(report, 'interpretation')


class TestRiskAnalyzer:
    """Tests for RiskAnalyzer service."""
    
    def test_analyze_volatility(self, sample_polars_returns):
        """Test volatility analysis."""
        analyzer = RiskAnalyzer()
        report = analyzer.analyze_volatility(
            returns=sample_polars_returns,
            symbol="TEST"
        )
        
        assert hasattr(report, 'daily_volatility')
        assert hasattr(report, 'annualized_volatility')
        assert report.annualized_volatility > 0
    
    def test_analyze_drawdown(self, sample_polars_prices):
        """Test drawdown analysis."""
        analyzer = RiskAnalyzer()
        report = analyzer.analyze_drawdown(
            equity_curve=sample_polars_prices,
            symbol="TEST"
        )
        
        assert hasattr(report, 'max_drawdown')
        assert report.max_drawdown <= 0
        assert hasattr(report, 'current_drawdown')
    
    def test_calculate_var(self, sample_polars_returns):
        """Test VaR calculation."""
        analyzer = RiskAnalyzer()
        report = analyzer.calculate_var(
            returns=sample_polars_returns,
            symbol="TEST",
            confidence=0.95
        )
        
        assert hasattr(report, 'var_daily')
        assert report.var_daily >= 0  # VaR is positive representing potential loss
    
    def test_calculate_cvar(self, sample_polars_returns):
        """Test CVaR calculation."""
        analyzer = RiskAnalyzer()
        report = analyzer.calculate_cvar(
            returns=sample_polars_returns,
            symbol="TEST",
            confidence=0.95
        )
        
        assert hasattr(report, 'cvar_daily')
        assert hasattr(report, 'var_at_level')


class TestCorrelationAnalyzer:
    """Tests for CorrelationAnalyzer service."""
    
    def test_analyze_correlations(self, sample_returns_dict):
        """Test correlation analysis."""
        analyzer = CorrelationAnalyzer()
        report = analyzer.analyze_correlations(
            returns_dict=sample_returns_dict,
            symbol="portfolio"
        )
        
        assert isinstance(report, CorrelationReport)
        assert hasattr(report, 'correlation_matrix')
        assert hasattr(report, 'diversification_score')
        assert hasattr(report, 'clusters')
        assert hasattr(report, 'interpretation')
    
    def test_analyze_diversification(self, sample_returns_dict):
        """Test diversification analysis."""
        analyzer = CorrelationAnalyzer()
        
        weights = {
            'AAPL': 0.25,
            'GOOGL': 0.20,
            'MSFT': 0.20,
            'AMZN': 0.20,
            'TSLA': 0.15
        }
        
        report = analyzer.analyze_diversification(
            weights=weights,
            returns_dict=sample_returns_dict
        )
        
        assert isinstance(report, DiversificationReport)
        assert hasattr(report, 'diversification_score')
        assert hasattr(report, 'concentration_risk')
        assert hasattr(report, 'recommendations')


class TestOptionsAnalyzer:
    """Tests for OptionsAnalyzer service."""
    
    def test_analyze_option(self):
        """Test single option analysis."""
        analyzer = OptionsAnalyzer()
        report = analyzer.analyze_option(
            S=175.0,
            K=180.0,
            T=0.25,
            r=0.05,
            sigma=0.2,
            option_type='call'
        )
        
        assert hasattr(report, 'fair_price')
        assert hasattr(report, 'greeks')
        assert hasattr(report, 'interpretation')
        assert 0 <= report.greeks['delta'] <= 1
    
    def test_analyze_put_option(self):
        """Test put option analysis."""
        analyzer = OptionsAnalyzer()
        report = analyzer.analyze_option(
            S=175.0,
            K=170.0,
            T=0.25,
            r=0.05,
            sigma=0.2,
            option_type='put'
        )
        
        assert report.greeks['delta'] <= 0
        assert report.greeks['delta'] >= -1
    
    def test_analyze_options_chain(self):
        """Test options chain analysis."""
        analyzer = OptionsAnalyzer()
        strikes = [165.0, 170.0, 175.0, 180.0, 185.0]
        report = analyzer.analyze_options_chain(
            underlying_price=175.0,
            strikes=strikes,
            T=0.25,
            r=0.05,
            iv_map=None,
            option_type='call'
        )
        
        assert hasattr(report, 'greeks_by_strike')
        assert hasattr(report, 'strikes')
        assert len(report.greeks_by_strike) == len(strikes)
    
    def test_analyze_vol_surface(self):
        """Test volatility surface analysis."""
        analyzer = OptionsAnalyzer()
        
        strikes = [160.0, 165.0, 170.0, 175.0, 180.0, 185.0, 190.0]
        expirations = [0.083, 0.25, 0.5]
        iv_data = {}
        
        for strike in strikes:
            for tte in expirations:
                iv_data[(strike, tte)] = 0.15 + 0.02 * abs(strike - 175) / 175 + 0.03 * tte
        
        report = analyzer.analyze_vol_surface(
            underlying_symbol="AAPL",
            strikes=strikes,
            expirations=expirations,
            iv_data=iv_data,
            underlying_price=175.0
        )
        
        assert hasattr(report, 'implied_vols')
        assert hasattr(report, 'atm_vol')
        assert hasattr(report, 'vol_skew')


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_constant_price_series(self):
        """Test handling of constant price series."""
        import polars as pl
        prices = pl.Series(name='price', values=[100.0] * 252)
        
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze_returns(prices=prices, symbol="CONST")
        
        assert report.total_return == 0.0
    
    def test_single_price_point(self):
        """Test handling of single price point."""
        import polars as pl
        prices = pl.Series(name='price', values=[100.0])
        
        analyzer = PerformanceAnalyzer()
        try:
            report = analyzer.analyze_returns(prices=prices, symbol="SINGLE")
            assert report.total_return == 0.0
        except (ValueError, IndexError):
            pass
    
    def test_zero_volatility_option(self):
        """Test option pricing with zero volatility."""
        analyzer = OptionsAnalyzer()
        
        report = analyzer.analyze_option(
            S=100.0,
            K=100.0,
            T=0.25,
            r=0.05,
            sigma=0.0,
            option_type='call'
        )
        
        assert report.fair_price >= 0
        assert report.greeks['gamma'] == 0
        assert report.greeks['vega'] == 0
