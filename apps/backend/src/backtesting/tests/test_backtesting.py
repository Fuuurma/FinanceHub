from decimal import Decimal
from datetime import date, datetime
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtesting.strategies.base_strategy import BaseStrategy
from backtesting.strategies.sma_crossover import SMACrossoverStrategy
from backtesting.strategies.rsi_mean_reversion import RSIMeanReversionStrategy
from backtesting.engine import BacktestingEngine
from backtesting.metrics import PerformanceMetrics


class TestBaseStrategy:
    """Tests for BaseStrategy abstract class."""

    def test_strategy_initialization(self):
        """Test strategy initializes with config."""

        class TestStrategy(BaseStrategy):
            def generate_signals(self, data, timestamp):
                return []

        strategy = TestStrategy({"param": "value"})
        assert strategy.name == "TestStrategy"
        assert strategy.config == {"param": "value"}

    def test_get_asset_data(self):
        """Test getting asset data from DataFrame."""
        strategy = SMACrossoverStrategy()
        data = pd.DataFrame(
            {
                "asset_symbol": ["AAPL", "AAPL", "MSFT", "MSFT"],
                "close": [100, 101, 200, 201],
            }
        )

        aapl_data = strategy.get_asset_data(data, "AAPL")
        assert len(aapl_data) == 2
        assert aapl_data["asset_symbol"].iloc[0] == "AAPL"

    def test_validate_data_valid(self):
        """Test data validation with valid data."""
        strategy = SMACrossoverStrategy()
        data = pd.DataFrame(
            {
                "close": [100, 101],
                "open": [99, 100],
                "high": [102, 103],
                "low": [98, 99],
            }
        )
        assert strategy.validate_data(data) == True

    def test_validate_data_invalid(self):
        """Test data validation with invalid data."""
        strategy = SMACrossoverStrategy()
        data = pd.DataFrame({"close": [100, 101]})
        assert strategy.validate_data(data) == False


class TestSMACrossoverStrategy:
    """Tests for SMA Crossover Strategy."""

    def test_sma_initialization(self):
        """Test SMA strategy initializes with defaults."""
        strategy = SMACrossoverStrategy()
        assert strategy.fast_period == 10
        assert strategy.slow_period == 20
        assert strategy.position_size == 0.1

    def test_sma_custom_config(self):
        """Test SMA strategy with custom config."""
        strategy = SMACrossoverStrategy(
            {"fast_period": 5, "slow_period": 15, "position_size": 0.2}
        )
        assert strategy.fast_period == 5
        assert strategy.slow_period == 15
        assert strategy.position_size == 0.2

    def test_sma_no_signal_insufficient_data(self):
        """Test SMA doesn't generate signal with insufficient data."""
        strategy = SMACrossoverStrategy({"fast_period": 10, "slow_period": 20})
        data = pd.DataFrame({"asset_symbol": ["AAPL"], "close": [100]})
        timestamp = datetime.now()

        signals = strategy.generate_signals(data, timestamp)
        assert len(signals) == 0

    def test_sma_buy_signal_crossover(self):
        """Test SMA strategy runs without errors."""
        strategy = SMACrossoverStrategy({"fast_period": 3, "slow_period": 5})

        prices = [100, 101, 102, 103, 104, 105, 110, 115, 120, 125, 130]
        data = pd.DataFrame({"asset_symbol": ["AAPL"] * 11, "close": prices})
        timestamp = datetime.now()

        signals = strategy.generate_signals(data, timestamp)
        assert isinstance(signals, list)

    def test_sma_reset(self):
        """Test SMA strategy reset clears state."""
        strategy = SMACrossoverStrategy()
        strategy._price_history = {"AAPL": [100, 101]}
        strategy._last_signal = {"AAPL": "BUY"}

        strategy.reset()

        assert strategy._price_history == {}
        assert strategy._last_signal == {}


class TestRSIMeanReversionStrategy:
    """Tests for RSI Mean Reversion Strategy."""

    def test_rsi_initialization(self):
        """Test RSI strategy initializes with defaults."""
        strategy = RSIMeanReversionStrategy()
        assert strategy.period == 14
        assert strategy.oversold == 30
        assert strategy.overbought == 70
        assert strategy.position_size == 0.1

    def test_rsi_buy_signal_oversold(self):
        """Test RSI strategy runs without errors."""
        strategy = RSIMeanReversionStrategy(
            {"period": 5, "oversold": 30, "overbought": 70}
        )

        prices = [80, 75, 70, 65, 60, 65, 70, 75, 80, 85]
        data = pd.DataFrame({"asset_symbol": ["AAPL"] * 10, "close": prices})
        timestamp = datetime.now()

        signals = strategy.generate_signals(data, timestamp)
        assert isinstance(signals, list)

    def test_rsi_sell_signal_overbought(self):
        """Test RSI strategy handles overbought signals."""
        strategy = RSIMeanReversionStrategy(
            {"period": 5, "oversold": 30, "overbought": 70}
        )

        prices = [80, 85, 90, 95, 100, 95, 90, 85, 80, 75]
        data = pd.DataFrame({"asset_symbol": ["AAPL"] * 10, "close": prices})
        timestamp = datetime.now()

        strategy._last_signal = {"AAPL": "BUY"}
        signals = strategy.generate_signals(data, timestamp)
        assert isinstance(signals, list)


class TestPerformanceMetrics:
    """Tests for Performance Metrics calculator."""

    def test_total_return_positive(self):
        """Test total return calculation with profit."""
        result = PerformanceMetrics.calculate_total_return(
            Decimal("10000"), Decimal("12000")
        )
        assert result == Decimal("20.00")

    def test_total_return_negative(self):
        """Test total return calculation with loss."""
        result = PerformanceMetrics.calculate_total_return(
            Decimal("10000"), Decimal("8000")
        )
        assert result == Decimal("-20.00")

    def test_total_return_zero(self):
        """Test total return calculation with break-even."""
        result = PerformanceMetrics.calculate_total_return(
            Decimal("10000"), Decimal("10000")
        )
        assert result == Decimal("0")

    def test_sharpe_ratio_empty(self):
        """Test Sharpe ratio returns None for empty data."""
        result = PerformanceMetrics.calculate_sharpe_ratio([])
        assert result is None

    def test_sharpe_ratio_single_value(self):
        """Test Sharpe ratio returns None for single value."""
        result = PerformanceMetrics.calculate_sharpe_ratio([Decimal("0.01")])
        assert result is None

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        returns = [
            Decimal("0.01"),
            Decimal("-0.005"),
            Decimal("0.02"),
            Decimal("0.015"),
            Decimal("-0.01"),
        ]
        result = PerformanceMetrics.calculate_sharpe_ratio(returns)
        assert result is not None
        assert isinstance(result, float)

    def test_max_drawdown_calculation(self):
        """Test max drawdown calculation."""
        equity = [10000, 10500, 10200, 10800, 10300, 11000]
        result = PerformanceMetrics.calculate_max_drawdown(equity)
        assert result is not None
        assert result >= 0

    def test_win_rate_all_winners(self):
        """Test win rate with all winning trades."""
        trades = [{"pnl": 100}, {"pnl": 200}, {"pnl": 150}]
        result = PerformanceMetrics.calculate_win_rate(trades)
        assert result == 100.0

    def test_win_rate_all_losers(self):
        """Test win rate with all losing trades."""
        trades = [{"pnl": -100}, {"pnl": -200}, {"pnl": -150}]
        result = PerformanceMetrics.calculate_win_rate(trades)
        assert result == 0.0

    def test_win_rate_mixed(self):
        """Test win rate with mixed trades."""
        trades = [{"pnl": 100}, {"pnl": -50}, {"pnl": 200}, {"pnl": -100}]
        result = PerformanceMetrics.calculate_win_rate(trades)
        assert result == 50.0

    def test_profit_factor_calculation(self):
        """Test profit factor calculation."""
        trades = [{"pnl": 500}, {"pnl": 300}, {"pnl": -200}, {"pnl": -100}]
        result = PerformanceMetrics.calculate_profit_factor(trades)
        assert result is not None
        assert round(result, 1) == 2.7

    def test_calculate_all_metrics(self):
        """Test calculating all metrics at once."""
        equity_curve = [
            {"value": 10000},
            {"value": 10200},
            {"value": 10100},
            {"value": 10500},
            {"value": 10300},
            {"value": 10800},
        ]
        trades = [{"pnl": 100}, {"pnl": -50}, {"pnl": 200}]

        metrics = PerformanceMetrics.calculate_all_metrics(
            equity_curve, trades, Decimal("10000")
        )

        assert "total_return" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown" in metrics
        assert "win_rate" in metrics
        assert "profit_factor" in metrics
        assert "total_trades" in metrics


class TestBacktestingEngine:
    """Tests for Backtesting Engine."""

    def test_engine_initialization(self):
        """Test engine initializes with capital."""
        engine = BacktestingEngine(Decimal("10000"))
        assert engine.initial_capital == Decimal("10000")
        assert engine.cash == Decimal("10000")
        assert engine.current_value == Decimal("10000")

    def test_engine_custom_commission(self):
        """Test engine with custom commission rate."""
        engine = BacktestingEngine(Decimal("10000"), commission_rate=Decimal("0.002"))
        assert engine.commission_rate == Decimal("0.002")

    def test_engine_reset(self):
        """Test engine reset clears state."""
        engine = BacktestingEngine(Decimal("10000"))
        engine.cash = Decimal("5000")
        engine.positions = {"AAPL": {"quantity": 10}}
        engine.trades = [{"action": "BUY"}]

        engine.reset()

        assert engine.cash == Decimal("10000")
        assert engine.positions == {}
        assert engine.trades == []

    def test_run_with_sma_strategy(self):
        """Test running backtest with SMA strategy."""
        engine = BacktestingEngine(Decimal("10000"))

        prices = [
            100,
            101,
            102,
            103,
            104,
            105,
            110,
            115,
            120,
            125,
            130,
            135,
            140,
            145,
            150,
        ]
        data = pd.DataFrame(
            {
                "date": pd.date_range(start="2023-01-01", periods=15),
                "asset_symbol": ["AAPL"] * 15,
                "close": prices,
                "open": [p - 1 for p in prices],
                "high": [p + 2 for p in prices],
                "low": [p - 2 for p in prices],
                "volume": [1000000] * 15,
            }
        )

        result = engine.run(
            strategy_type="sma_crossover", config={"fast_period": 3, "slow_period": 5}
        )

        assert "equity_curve" in result
        assert "trades" in result
        assert "metrics" in result
        assert isinstance(result["equity_curve"], list)

    def test_run_with_rsi_strategy(self):
        """Test running backtest with RSI strategy."""
        engine = BacktestingEngine(Decimal("10000"))

        prices = [100 + i for i in range(50)]
        data = pd.DataFrame(
            {
                "date": pd.date_range(start="2023-01-01", periods=50),
                "asset_symbol": ["AAPL"] * 50,
                "close": prices,
                "open": [p - 1 for p in prices],
                "high": [p + 2 for p in prices],
                "low": [p - 2 for p in prices],
                "volume": [1000000] * 50,
            }
        )

        result = engine.run(
            strategy_type="rsi_mean_reversion",
            config={"period": 5, "oversold": 30, "overbought": 70},
        )

        assert "equity_curve" in result
        assert "trades" in result
        assert "metrics" in result

    def test_run_unknown_strategy(self):
        """Test running backtest with unknown strategy raises error."""
        engine = BacktestingEngine(Decimal("10000"))

        data = pd.DataFrame(
            {
                "close": [100, 101],
                "open": [99, 100],
                "high": [102, 103],
                "low": [98, 99],
            }
        )

        try:
            engine.run(strategy_type="unknown_strategy")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown strategy type" in str(e)

    def test_run_empty_data(self):
        """Test running backtest with empty data."""
        engine = BacktestingEngine(Decimal("10000"))
        data = pd.DataFrame()

        result = engine.run(strategy_type="sma_crossover")

        assert "error" in result
        assert result["error"] == "No data available for specified date range"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
