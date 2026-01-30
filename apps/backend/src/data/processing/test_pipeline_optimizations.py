import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


class TestCircuitBreaker:
    def test_circuit_breaker_closed_state(self):
        from utils.services.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(name="test", failure_threshold=3, timeout_seconds=60)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_success_resets_state(self):
        from utils.services.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(name="test", failure_threshold=3, timeout_seconds=60)

        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_opens_after_threshold(self):
        from utils.services.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(name="test", failure_threshold=2, timeout_seconds=60)

        def fail():
            raise ValueError("fail")

        cb.call(fail)
        assert cb.failure_count == 1
        assert cb.state == CircuitState.CLOSED

        cb.call(fail)
        assert cb.failure_count == 2
        assert cb.state == CircuitState.OPEN

    def test_circuit_breaker_blocks_when_open(self):
        from utils.services.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(name="test", failure_threshold=1, timeout_seconds=60)

        def fail():
            raise ValueError("fail")

        cb.call(fail)
        assert cb.state == CircuitState.OPEN

        with pytest.raises(Exception, match="is OPEN"):
            cb.call(lambda: "success")

    def test_circuit_breaker_half_open_recovery(self):
        from utils.services.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker(name="test", failure_threshold=1, timeout_seconds=0)

        def fail():
            raise ValueError("fail")

        cb.call(fail)
        assert cb.state == CircuitState.OPEN

        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_get_circuit_breaker_singleton(self):
        from utils.services.circuit_breaker import get_circuit_breaker

        cb1 = get_circuit_breaker("api1")
        cb2 = get_circuit_breaker("api1")
        cb3 = get_circuit_breaker("api2")

        assert cb1 is cb2
        assert cb1 is not cb3


class TestPipelineMetrics:
    def test_metrics_record_success(self):
        from utils.services.pipeline_monitor import PipelineMetrics

        metrics = PipelineMetrics()
        metrics.record(success=True, elapsed_ms=100.0)

        result = metrics.get_metrics()
        assert result["total_processed"] == 1
        assert result["successful"] == 1
        assert result["failed"] == 0

    def test_metrics_record_failure(self):
        from utils.services.pipeline_monitor import PipelineMetrics

        metrics = PipelineMetrics()
        metrics.record(success=False, elapsed_ms=50.0)

        result = metrics.get_metrics()
        assert result["total_processed"] == 1
        assert result["failed"] == 1

    def test_metrics_calculates_error_rate(self):
        from utils.services.pipeline_monitor import PipelineMetrics

        metrics = PipelineMetrics()
        metrics.record(success=True, elapsed_ms=100.0)
        metrics.record(success=True, elapsed_ms=100.0)
        metrics.record(success=False, elapsed_ms=50.0)

        result = metrics.get_metrics()
        assert result["total_processed"] == 3
        assert result["error_rate"] == pytest.approx(33.33, rel=0.01)
        assert result["success_rate"] == pytest.approx(66.67, rel=0.01)

    def test_metrics_reset(self):
        from utils.services.pipeline_monitor import PipelineMetrics

        metrics = PipelineMetrics()
        metrics.record(success=True, elapsed_ms=100.0)
        metrics.reset()

        result = metrics.get_metrics()
        assert result["total_processed"] == 0


class TestSupportResistance:
    def test_support_resistance_calculation(self):
        from data.processing.pipeline import TechnicalIndicatorsCalculator
        import polars as pl

        calculator = TechnicalIndicatorsCalculator()

        df = pl.DataFrame(
            {
                "timestamp": [datetime.now() - timedelta(days=i) for i in range(60)],
                "open": [150.0 + i for i in range(60)],
                "high": [155.0 + i for i in range(60)],
                "low": [145.0 + i for i in range(60)],
                "close": [152.0 + i for i in range(60)],
                "volume": [1000000 for _ in range(60)],
            }
        )

        result = calculator._calculate_support_resistance(df, lookback=50)

        assert "pivot_point" in result
        assert "support_levels" in result
        assert "resistance_levels" in result
        assert "current_support" in result
        assert "current_resistance" in result

        assert result["pivot_point"] > 0
        assert len(result["support_levels"]) == 3
        assert len(result["resistance_levels"]) == 3

    def test_support_resistance_insufficient_data(self):
        from data.processing.pipeline import TechnicalIndicatorsCalculator
        import polars as pl

        calculator = TechnicalIndicatorsCalculator()

        df = pl.DataFrame(
            {
                "timestamp": [datetime.now()],
                "open": [150.0],
                "high": [155.0],
                "low": [145.0],
                "close": [152.0],
                "volume": [1000000],
            }
        )

        result = calculator._calculate_support_resistance(df, lookback=50)
        assert result == {}


class TestBatchOperations:
    def test_processed_asset_data_dataclass(self):
        from data.processing.pipeline import ProcessedAssetData

        data = ProcessedAssetData(
            symbol="AAPL",
            source="yahoo",
            raw_data={"close": 150.0},
            normalized_data={"close": 150.0},
            is_valid=True,
        )

        assert data.symbol == "AAPL"
        assert data.is_valid is True
        assert data.validation_errors == []

    def test_normalize_symbol(self):
        from data.processing.pipeline import DataProcessor

        assert DataProcessor.normalize_symbol("aapl") == "AAPL"
        assert DataProcessor.normalize_symbol("BTC-USD") == "BTC.USD"
        assert DataProcessor.normalize_symbol("  eth  ") == "ETH"

    def test_calculate_change_percent(self):
        from data.processing.pipeline import DataProcessor

        assert DataProcessor.calculate_change_percent(110.0, 100.0) == 10.0
        assert DataProcessor.calculate_change_percent(90.0, 100.0) == -10.0
        assert DataProcessor.calculate_change_percent(100.0, 0.0) == 0.0
        assert DataProcessor.calculate_change_percent(100.0, 100.0) == 0.0
