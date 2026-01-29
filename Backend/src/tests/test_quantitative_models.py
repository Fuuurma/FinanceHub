"""
Tests for Quantitative Models API
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from api.quantitative_models import router
from utils.services.quantitative.time_series_models import (
    TimeSeriesModels, ARIMAResult, GARCHResult, KalmanFilterResult
)


@pytest.fixture
def time_series_models():
    """Create time series models instance."""
    return TimeSeriesModels()


@pytest.fixture
def sample_data():
    """Generate sample time series data."""
    np.random.seed(42)
    return np.cumsum(np.random.randn(100))


@pytest.fixture
def sample_returns():
    """Generate sample returns."""
    np.random.seed(42)
    return np.random.randn(100) * 0.02


class TestARIMAForecast:
    """Tests for ARIMA forecasting."""
    
    def test_arima_basic(self, time_series_models, sample_data):
        """Test basic ARIMA forecast."""
        result = time_series_models.arima_forecast(
            data=sample_data,
            order=(1, 0, 1),
            steps=10
        )
        
        assert isinstance(result, ARIMAResult)
        assert len(result.forecast) == 10
        assert len(result.confidence_interval_lower) == 10
        assert len(result.confidence_interval_upper) == 10
        assert result.order == (1, 0, 1)
        assert result.aic > 0
        assert result.compute_time_ms > 0
    
    def test_arima_with_differencing(self, time_series_models):
        """Test ARIMA with differencing."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(100))
        
        result = time_series_models.arima_forecast(
            data=data,
            order=(1, 1, 1),
            steps=5
        )
        
        assert len(result.forecast) == 5
        assert result.order == (1, 1, 1)
    
    def test_arima_confidence_intervals(self, time_series_models, sample_data):
        """Test that confidence intervals widen with horizon."""
        result = time_series_models.arima_forecast(
            data=sample_data,
            order=(1, 0, 1),
            steps=20,
            confidence_level=0.95
        )
        
        # Later intervals should be wider
        early_width = result.confidence_interval_upper[4] - result.confidence_interval_lower[4]
        late_width = result.confidence_interval_upper[19] - result.confidence_interval_lower[19]
        
        assert late_width >= early_width


class TestGARCHForecast:
    """Tests for GARCH volatility forecasting."""
    
    def test_garch_basic(self, time_series_models, sample_returns):
        """Test basic GARCH forecast."""
        result = time_series_models.garch11_forecast(
            data=sample_returns,
            steps=10
        )
        
        assert isinstance(result, GARCHResult)
        assert len(result.conditional_volatility) == len(sample_returns)
        assert result.forecast_volatility > 0
        assert result.omega > 0
        assert result.alpha > 0
        assert result.beta > 0
        assert result.total_volatility > 0
        assert result.compute_time_ms > 0
    
    def test_garch_parameters(self, time_series_models, sample_returns):
        """Test GARCH with custom parameters."""
        result = time_series_models.garch11_forecast(
            data=sample_returns,
            omega=0.0001,
            alpha=0.05,
            beta=0.90,
            steps=10
        )
        
        assert result.omega == 0.0001
        assert result.alpha == 0.05
        assert result.beta == 0.90
    
    def test_garch_volatility_positive(self, time_series_models, sample_returns):
        """Test that GARCH volatility is always positive."""
        result = time_series_models.garch11_forecast(data=sample_returns)
        
        assert np.all(result.conditional_volatility >= 0)
        assert result.forecast_volatility >= 0


class TestKalmanFilter:
    """Tests for Kalman filter."""
    
    def test_kalman_basic(self, time_series_models):
        """Test basic Kalman filter."""
        np.random.seed(42)
        observations = np.cumsum(np.random.randn(50)) + np.random.randn(50) * 0.1
        
        result = time_series_models.kalman_filter(
            observations=observations,
            state_dim=1
        )
        
        assert isinstance(result, KalmanFilterResult)
        assert len(result.filtered_state) == len(observations)
        assert len(result.predicted_state) == len(observations)
        assert result.likelihood != 0
        assert result.compute_time_ms > 0
    
    def test_kalman_filtering(self, time_series_models):
        """Test that Kalman filter smooths observations."""
        np.random.seed(42)
        true_signal = np.sin(np.linspace(0, 4*np.pi, 100))
        observations = true_signal + np.random.randn(100) * 0.5
        
        result = time_series_models.kalman_filter(
            observations=observations,
            process_noise=0.01,
            observation_noise=0.5
        )
        
        # Filtered state should be smoother than observations
        obs_variance = np.var(observations)
        state_variance = np.var(result.filtered_state)
        
        assert state_variance < obs_variance


class TestHalfLife:
    """Tests for half-life calculation."""
    
    def test_half_life_mean_reverting(self, time_series_models):
        """Test half-life for mean-reverting series."""
        # Mean-reverting: Ornstein-Uhlenbeck process
        np.random.seed(42)
        n = 200
        phi = 0.95
        data = np.zeros(n)
        data[0] = 1.0
        for t in range(1, n):
            data[t] = phi * data[t-1] + np.random.randn() * 0.1
        
        result = time_series_models.calculate_half_life(data)
        
        assert isinstance(result.half_life, float)
        assert result.half_life > 0
        assert result.half_life < float('inf')
        assert result.hurst_exponent > 0
        assert result.hurst_exponent < 1
    
    def test_half_life_random_walk(self, time_series_models):
        """Test half-life for random walk (should be infinite)."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        
        result = time_series_models.calculate_half_life(data)
        
        # Random walk has no mean reversion
        assert result.half_life == float('inf') or result.half_life > 1000
    
    def test_half_life_with_lookback(self, time_series_models):
        """Test half-life with custom lookback."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(300))
        
        result = time_series_models.calculate_half_life(data, lookback=100)
        
        assert isinstance(result.half_life, float)


class TestHurstExponent:
    """Tests for Hurst exponent estimation."""
    
    def test_hurst_random_walk(self, time_series_models):
        """Test Hurst for random walk (should be ~0.5)."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        
        result = time_series_models.estimate_hurst_exponent(data, max_scale=10)
        
        assert 0.4 < result.hurst_exponent < 0.6
        assert result.trend_type == "random_walk"
    
    def test_hurst_trending(self, time_series_models):
        """Test Hurst for trending series (should be > 0.5)."""
        np.random.seed(42)
        n = 200
        trend = np.linspace(0, 2, n)
        noise = np.random.randn(n) * 0.1
        data = trend + noise
        
        result = time_series_models.estimate_hurst_exponent(data, max_scale=10)
        
        assert result.hurst_exponent > 0.5
        assert result.trend_type == "trending"
    
    def test_hurst_mean_reverting(self, time_series_models):
        """Test Hurst for mean-reverting series (should be < 0.5)."""
        np.random.seed(42)
        n = 200
        data = np.zeros(n)
        data[0] = 1.0
        for t in range(1, n):
            data[t] = 0.9 * data[t-1] + np.random.randn() * 0.1
        
        result = time_series_models.estimate_hurst_exponent(data, max_scale=10)
        
        assert result.hurst_exponent < 0.5
        assert result.trend_type == "mean_reverting"
    
    def test_hurst_interpretation(self, time_series_models):
        """Test Hurst interpretation text."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        
        result = time_series_models.estimate_hurst_exponent(data, max_scale=10)
        
        assert "H" in result.interpretation or "persistent" in result.interpretation.lower() or "random" in result.interpretation.lower()


class TestAPIEndpoints:
    """Tests for API endpoints (mocked)."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from ninja.testing import TestAsyncClient
        return TestAsyncClient(router)
    
    @patch('api.quantitative_models.TimeSeriesModels')
    def test_arima_endpoint(self, mock_models, client):
        """Test ARIMA endpoint."""
        mock_instance = Mock()
        mock_instance.arima_forecast.return_value = ARIMAResult(
            forecast=np.array([100, 101, 102]),
            confidence_interval_lower=np.array([99, 100, 101]),
            confidence_interval_upper=np.array([101, 102, 103]),
            aic=250.5,
            bic=260.3,
            order=(1, 0, 1),
            residuals=np.array([0.1, -0.2, 0.1]),
            compute_time_ms=50.0
        )
        mock_models.return_value = mock_instance
        
        response = client.post("/arima-forecast", {
            "data": list(range(50)),
            "order_p": 1,
            "order_d": 0,
            "order_q": 1,
            "steps": 3,
            "confidence_level": 0.95
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["forecast"]) == 3
        assert data["order"] == [1, 0, 1]
    
    @patch('api.quantitative_models.TimeSeriesModels')
    def test_garch_endpoint(self, mock_models, client):
        """Test GARCH endpoint."""
        mock_instance = Mock()
        mock_instance.garch11_forecast.return_value = GARCHResult(
            conditional_volatility=np.array([0.2, 0.21, 0.19]),
            forecast_volatility=0.20,
            omega=0.0001,
            alpha=0.05,
            beta=0.90,
            total_volatility=0.25,
            compute_time_ms=30.0
        )
        mock_models.return_value = mock_instance
        
        response = client.post("/garch-volatility", {
            "returns": [0.01, -0.02, 0.015, -0.01, 0.02] * 20,
            "steps": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "forecast_volatility" in data
        assert data["alpha"] == 0.05
    
    @patch('api.quantitative_models.TimeSeriesModels')
    def test_kalman_endpoint(self, mock_models, client):
        """Test Kalman filter endpoint."""
        mock_instance = Mock()
        mock_instance.kalman_filter.return_value = KalmanFilterResult(
            filtered_state=np.array([1.0, 1.1, 1.2]),
            filtered_covariance=np.array([[0.1], [0.1], [0.1]]),
            predicted_state=np.array([0.9, 1.0, 1.1]),
            predicted_covariance=np.array([[0.1], [0.1], [0.1]]),
            likelihood=-50.5,
            compute_time_ms=25.0
        )
        mock_models.return_value = mock_instance
        
        response = client.post("/kalman-filter", {
            "observations": [1.0, 1.1, 1.2, 1.3, 1.4],
            "state_dim": 1
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "filtered_state" in data


class TestVolatilityRegimes:
    """Tests for volatility regime detection."""
    
    def test_volatility_regimes_classification(self):
        """Test volatility regime classification."""
        from api.quantitative_models import detect_volatility_regimes
        
        # Create test returns with known patterns
        returns = [0.01] * 50 + [0.05] * 20 + [0.01] * 50
        
        result = detect_volatility_regimes(
            None,  # request
            returns=",".join(map(str, returns)),
            threshold_low=0.5,
            threshold_high=1.5
        )
        
        assert "regimes" in result
        assert "summary" in result
        assert result["current_regime"] in ["low", "normal", "high"]
    
    def test_volatility_regimes_thresholds(self):
        """Test volatility regime with different thresholds."""
        from api.quantitative_models import detect_volatility_regimes
        
        returns = [0.02] * 100
        
        result = detect_volatility_regimes(
            None,
            returns=",".join(map(str, returns)),
            threshold_low=0.5,
            threshold_high=1.5
        )
        
        # With threshold 0.5/1.5, 2% vol should be "normal"
        assert result["summary"]["normal"] > 0


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_arima_short_data(self, time_series_models):
        """Test ARIMA with minimum data length."""
        data = np.random.randn(10)
        
        result = time_series_models.arima_forecast(
            data=data,
            order=(1, 0, 0),
            steps=5
        )
        
        assert len(result.forecast) == 5
    
    def test_garch_high_alpha(self, time_series_models):
        """Test GARCH with high alpha (volatile)."""
        np.random.seed(42)
        returns = np.random.randn(100) * 0.05
        
        result = time_series_models.garch11_forecast(
            data=returns,
            alpha=0.10,
            beta=0.85
        )
        
        assert result.alpha == 0.10
        assert result.beta == 0.85
    
    def test_hurst_minimal_data(self, time_series_models):
        """Test Hurst with minimal data."""
        data = np.random.randn(100)
        
        result = time_series_models.estimate_hurst_exponent(data, max_scale=5)
        
        assert 0 <= result.hurst_exponent <= 1
