"""
Tests for Data Pipeline Optimizations
Tests batch operations, circuit breaker, pipeline metrics, and data deduplication
"""

import pytest
import time
from datetime import datetime, timedelta
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import django

django.setup()

from data.processing.pipeline import (
    DataPipeline,
    ProcessedAssetData,
    PriceDataProcessor,
    TechnicalIndicatorsCalculator,
)
from utils.services.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    get_circuit_breaker,
)
from utils.services.pipeline_monitor import PipelineMetrics, get_metrics


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    def test_circuit_initial_state(self):
        """Test circuit breaker starts in closed state"""
        breaker = CircuitBreaker("test", failure_threshold=3, timeout_seconds=60)
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_success_call(self):
        """Test successful call doesn't open circuit"""
        breaker = CircuitBreaker("test", failure_threshold=3, timeout_seconds=60)
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_circuit_opens_on_threshold(self):
        """Test circuit opens after failure threshold"""
        breaker = CircuitBreaker("test", failure_threshold=3, timeout_seconds=60)
        for i in range(3):
            with pytest.raises(Exception):
                breaker.call(lambda: (_ for _ in ()).throw(Exception("Test failure")))
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 3

    def test_circuit_blocks_calls_when_open(self):
        """Test circuit blocks calls when open"""
        breaker = CircuitBreaker("test", failure_threshold=2, timeout_seconds=60)
        with pytest.raises(Exception):
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Test failure")))
        with pytest.raises(Exception):
            breaker.call(lambda: (_ for _ in ()).throw(Exception("Test failure")))
        assert breaker.state == CircuitState.OPEN
        with pytest.raises(Exception) as exc_info:
            breaker.call(lambda: "test")
        assert "is OPEN - calls blocked" in str(exc_info.value)

    def test_get_circuit_breaker_singleton(self):
        """Test get_circuit_breaker returns same instance"""
        breaker1 = get_circuit_breaker("singleton_test", failure_threshold=5)
        breaker2 = get_circuit_breaker("singleton_test", failure_threshold=5)
        assert breaker1 is breaker2

    def test_get_circuit_breaker_different_names(self):
        """Test different circuit breaker names create different instances"""
        breaker1 = get_circuit_breaker("breaker1")
        breaker2 = get_circuit_breaker("breaker2")
        assert breaker1 is not breaker2


class TestPipelineMetrics:
    """Test pipeline monitoring and metrics"""

    @pytest.fixture
    def metrics(self):
        return PipelineMetrics()

    def test_metrics_initial_state(self, metrics):
        """Test metrics start at zero"""
        assert metrics._total_processed == 0
        assert metrics._successful == 0
        assert metrics._failed == 0

    def test_metrics_record_success(self, metrics):
        """Test recording successful operation"""
        metrics.record(success=True, elapsed_ms=100.0)
        assert metrics._total_processed == 1
        assert metrics._successful == 1
        assert metrics._failed == 0

    def test_metrics_record_failure(self, metrics):
        """Test recording failed operation"""
        metrics.record(success=False, elapsed_ms=50.0)
        assert metrics._total_processed == 1
        assert metrics._successful == 0
        assert metrics._failed == 1

    def test_metrics_get_metrics_structure(self, metrics):
        """Test get_metrics returns proper structure"""
        metrics.record(success=True, elapsed_ms=100.0)
        result = metrics.get_metrics()
        assert "total_processed" in result
        assert "successful" in result
        assert "failed" in result
        assert "avg_time_ms" in result
        assert "error_rate" in result
        assert "success_rate" in result

    def test_metrics_error_rate_calculation(self, metrics):
        """Test error rate is calculated correctly"""
        metrics.record(success=True, elapsed_ms=100.0)
        metrics.record(success=True, elapsed_ms=200.0)
        metrics.record(success=False, elapsed_ms=50.0)
        result = metrics.get_metrics()
        assert result["error_rate"] == pytest.approx(33.33, rel=1)
        assert result["success_rate"] == pytest.approx(66.67, rel=1)

    def test_metrics_reset(self, metrics):
        """Test metrics reset functionality"""
        metrics.record(success=True, elapsed_ms=100.0)
        metrics.reset()
        assert metrics._total_processed == 0
        assert metrics._successful == 0
        assert metrics._failed == 0

    def test_get_metrics_singleton(self):
        """Test get_metrics returns singleton instance"""
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is metrics2


class TestDataPipeline:
    """Test DataPipeline class"""

    @pytest.fixture
    def pipeline(self):
        return DataPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes with required components"""
        assert pipeline.price_processor is not None
        assert pipeline.indicators_calculator is not None
        assert pipeline.api_breaker is not None

    def test_pipeline_has_metrics(self, pipeline):
        """Test pipeline has metrics dictionary"""
        assert "total_processed" in pipeline._metrics
        assert "total_saved" in pipeline._metrics
        assert "total_errors" in pipeline._metrics

    def test_get_metrics_returns_dict(self, pipeline):
        """Test get_metrics returns proper structure"""
        metrics = pipeline.get_metrics()
        assert isinstance(metrics, dict)
        assert "total_processed" in metrics
        assert "success_rate" in metrics

    def test_process_raw_data_valid_input(self, pipeline):
        """Test processing valid raw data"""
        raw_data = {
            "symbol": "AAPL",
            "timestamp": datetime.now().isoformat(),
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.5,
            "volume": 50000000,
        }
        processed = pipeline.process_raw_data(raw_data, "yahoo", "stock")
        assert processed.symbol == "AAPL"
        assert processed.is_valid is True
        assert processed.normalized_data is not None
        assert processed.normalized_data["close"] == 151.5

    def test_process_raw_data_invalid_price(self, pipeline):
        """Test processing data with invalid price"""
        raw_data = {
            "symbol": "TEST",
            "timestamp": datetime.now().isoformat(),
            "open": -100.0,
            "high": -50.0,
            "low": -75.0,
            "close": -100.0,
            "volume": 1000000,
        }
        processed = pipeline.process_raw_data(raw_data, "test", "stock")
        assert processed.is_valid is False

    def test_batch_save_empty_list(self, pipeline):
        """Test batch save with empty list returns zero counts"""
        result = pipeline.save_to_database_batch([])
        assert result["saved"] == 0
        assert result["skipped"] == 0
        assert result["total"] == 0


class TestPriceDataProcessor:
    """Test PriceDataProcessor class"""

    @pytest.fixture
    def processor(self):
        return PriceDataProcessor()

    def test_normalize_symbol(self, processor):
        """Test symbol normalization"""
        assert processor.normalize_symbol("aapl") == "AAPL"
        assert processor.normalize_symbol(" AAPL ") == "AAPL"
        assert processor.normalize_symbol("BTC-USD") == "BTC.USD"

    def test_validate_price_valid(self, processor):
        """Test valid price validation"""
        assert processor.validate_price_data(150.0) is True
        assert processor.validate_price_data(0.01) is True

    def test_validate_price_invalid(self, processor):
        """Test invalid price validation"""
        assert processor.validate_price_data(0) is False
        assert processor.validate_price_data(-100.0) is False
        assert processor.validate_price_data(20000000) is False

    def test_validate_volume(self, processor):
        """Test volume validation"""
        assert processor.validate_volume(1000000) is True
        assert processor.validate_volume(500) is False

    def test_calculate_change_percent(self, processor):
        """Test percentage change calculation"""
        assert processor.calculate_change_percent(110.0, 100.0) == 10.0
        assert processor.calculate_change_percent(90.0, 100.0) == -10.0
        assert processor.calculate_change_percent(100.0, 0.0) == 0.0

    def test_detect_anomalies_no_anomalies(self, processor):
        """Test anomaly detection with normal data"""
        prices = [100.0, 101.0, 100.5, 102.0, 99.5, 101.5, 100.0]
        anomalies = processor.detect_anomalies(prices)
        assert len(anomalies) == 0

    def test_normalize_price_data_yahoo(self, processor):
        """Test Yahoo Finance data normalization"""
        raw = {
            "symbol": "AAPL",
            "timestamp": "2024-01-15T10:00:00Z",
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.5,
            "volume": 50000000,
        }
        normalized = processor.normalize_price_data(raw, "yahoo")
        assert normalized is not None
        assert normalized["symbol"] == "AAPL"
        assert normalized["close"] == 151.5


class TestTechnicalIndicatorsCalculator:
    """Test TechnicalIndicatorsCalculator class"""

    @pytest.fixture
    def calculator(self):
        return TechnicalIndicatorsCalculator()

    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data for indicator calculation"""
        data = []
        base_price = 100.0
        for i in range(100):
            close = base_price + i + (i % 10) * 0.5
            data.append(
                {
                    "timestamp": datetime.now() - timedelta(days=100 - i),
                    "open": close - 1.0,
                    "high": close + 2.0,
                    "low": close - 2.0,
                    "close": close,
                    "volume": 1000000 + i * 1000,
                }
            )
        return data

    def test_calculate_all_indicators(self, calculator, sample_price_data):
        """Test calculating all indicators"""
        indicators = calculator.calculate_all_indicators(sample_price_data)
        assert "ma" in indicators
        assert "ema" in indicators
        assert "rsi" in indicators
        assert "macd" in indicators
        assert "bollinger" in indicators
        assert "atr" in indicators
        assert "volume_ma" in indicators
        assert "support_resistance" in indicators

    def test_calculate_all_indicators_insufficient_data(self, calculator):
        """Test indicator calculation with insufficient data"""
        insufficient_data = [{"close": 100.0, "volume": 1000000}] * 10
        indicators = calculator.calculate_all_indicators(insufficient_data)
        assert indicators == {}

    def test_support_resistance_returns_structure(self, calculator, sample_price_data):
        """Test support/resistance returns proper structure"""
        import polars as pl

        df = pl.DataFrame(sample_price_data)
        result = calculator._calculate_support_resistance(df, lookback=50)
        assert "pivot_point" in result
        assert "support_levels" in result
        assert "resistance_levels" in result


class TestProcessedAssetData:
    """Test ProcessedAssetData dataclass"""

    def test_valid_processed_data(self):
        """Test creating valid ProcessedAssetData"""
        processed = ProcessedAssetData(
            symbol="AAPL",
            source="yahoo",
            raw_data={"symbol": "AAPL"},
            normalized_data={"close": 150.0},
            is_valid=True,
        )
        assert processed.symbol == "AAPL"
        assert processed.source == "yahoo"
        assert processed.is_valid is True
        assert processed.normalized_data["close"] == 150.0

    def test_invalid_processed_data(self):
        """Test creating invalid ProcessedAssetData"""
        processed = ProcessedAssetData(
            symbol="INVALID",
            source="test",
            raw_data={"symbol": "INVALID"},
            is_valid=False,
            validation_errors=["Invalid price data"],
        )
        assert processed.is_valid is False
        assert "Invalid price data" in processed.validation_errors
