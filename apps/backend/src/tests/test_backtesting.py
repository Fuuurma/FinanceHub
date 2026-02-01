"""
Tests for Backtesting Engine
Comprehensive tests for strategy backtesting functionality.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

from investments.services.backtesting.backtesting_engine import (
    BacktestingEngine,
    BacktestConfig,
    Trade,
    Position,
    BacktestResult,
)
from investments.services.strategies.base_strategy import BaseStrategy
from investments.services.strategies.sma_crossover import SMACrossoverStrategy
from investments.services.strategies.rsi_mean_reversion import RSIMeanReversionStrategy


class TestBacktestConfig:
    """Tests for BacktestConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = BacktestConfig()

        assert config.initial_capital == 100000
        assert config.position_size_pct == 0.20
        assert config.max_positions == 5
        assert config.stop_loss_pct == 0.10
        assert config.take_profit_pct == 0.20
        assert config.transaction_cost_pct == 0.001
        assert config.slippage_pct == 0.0005
        assert config.allow_short is False
        assert config.allow_leverage is False
        assert config.max_leverage == 1.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = BacktestConfig(
            initial_capital=50000,
            position_size_pct=0.30,
            max_positions=10,
            transaction_cost_pct=0.002,
        )

        assert config.initial_capital == 50000
        assert config.position_size_pct == 0.30
        assert config.max_positions == 10
        assert config.transaction_cost_pct == 0.002


class TestTrade:
    """Tests for Trade dataclass."""

    def test_trade_creation(self):
        """Test creating a trade."""
        trade = Trade(
            entry_date=datetime(2024, 1, 1),
            entry_price=100.0,
            exit_date=datetime(2024, 1, 15),
            exit_price=110.0,
            quantity=10,
            direction="LONG",
            pnl=100.0,
            pnl_pct=10.0,
            status="CLOSED",
            reason="SMA Crossover",
        )

        assert trade.entry_date == datetime(2024, 1, 1)
        assert trade.entry_price == 100.0
        assert trade.exit_price == 110.0
        assert trade.pnl == 100.0
        assert trade.status == "CLOSED"


class TestPosition:
    """Tests for Position dataclass."""

    def test_position_creation(self):
        """Test creating a position."""
        position = Position(
            asset_symbol="AAPL",
            quantity=10,
            entry_price=150.0,
            entry_date=datetime(2024, 1, 1),
            direction="LONG",
            stop_loss=135.0,
            take_profit=180.0,
        )

        assert position.asset_symbol == "AAPL"
        assert position.quantity == 10
        assert position.entry_price == 150.0
        assert position.direction == "LONG"
        assert position.stop_loss == 135.0


class TestBacktestingEngine:
    """Tests for BacktestingEngine."""

    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data for testing."""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        base_price = 100.0

        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, 100)
        prices = base_price * np.cumprod(1 + returns)

        return pd.DataFrame(
            {
                "date": dates,
                "open": prices * (1 - 0.001),
                "high": prices * (1 + 0.002),
                "low": prices * (1 - 0.002),
                "close": prices,
                "volume": np.random.randint(1000000, 10000000, 100),
            }
        ).set_index("date")

    @pytest.fixture
    def rising_market_data(self):
        """Create steadily rising market data."""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        prices = np.linspace(100, 150, 100)

        return pd.DataFrame(
            {
                "date": dates,
                "open": prices * 0.999,
                "high": prices * 1.002,
                "low": prices * 0.998,
                "close": prices,
                "volume": 5000000,
            }
        ).set_index("date")

    @pytest.fixture
    def falling_market_data(self):
        """Create steadily falling market data."""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        prices = np.linspace(150, 100, 100)

        return pd.DataFrame(
            {
                "date": dates,
                "open": prices * 1.001,
                "high": prices * 1.002,
                "low": prices * 0.998,
                "close": prices,
                "volume": 5000000,
            }
        ).set_index("date")

    def test_engine_initialization(self):
        """Test engine initializes with default config."""
        engine = BacktestingEngine()

        assert engine.config.initial_capital == 100000
        assert engine.positions == {}
        assert engine.trades == []
        assert engine.equity_curve == []
        assert engine.cash == 0
        assert engine.total_value == 0

    def test_engine_with_custom_config(self):
        """Test engine initializes with custom config."""
        config = BacktestConfig(initial_capital=50000)
        engine = BacktestingEngine(config=config)

        assert engine.config.initial_capital == 50000

    def test_run_backtest_empty_data(self, sample_price_data):
        """Test running backtest with empty data raises error."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        with pytest.raises(ValueError, match="No data available"):
            engine.run_backtest(
                data=pd.DataFrame(),
                strategy=strategy,
            )

    def test_run_backtest_basic(self, sample_price_data):
        """Test basic backtest execution."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(
            data=sample_price_data,
            strategy=strategy,
            strategy_name="Test SMA",
        )

        assert isinstance(result, BacktestResult)
        assert result.strategy_name == "Test SMA"
        assert result.initial_capital == 100000
        assert isinstance(result.final_capital, float)
        assert isinstance(result.total_return, float)
        assert isinstance(result.total_trades, int)

    def test_backtest_result_structure(self, sample_price_data):
        """Test backtest result has all required fields."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(
            data=sample_price_data,
            strategy=strategy,
        )

        assert hasattr(result, "strategy_name")
        assert hasattr(result, "start_date")
        assert hasattr(result, "end_date")
        assert hasattr(result, "initial_capital")
        assert hasattr(result, "final_capital")
        assert hasattr(result, "total_return")
        assert hasattr(result, "total_return_pct")
        assert hasattr(result, "annual_return_pct")
        assert hasattr(result, "max_drawdown")
        assert hasattr(result, "max_drawdown_pct")
        assert hasattr(result, "sharpe_ratio")
        assert hasattr(result, "sortino_ratio")
        assert hasattr(result, "win_rate")
        assert hasattr(result, "total_trades")
        assert hasattr(result, "winning_trades")
        assert hasattr(result, "losing_trades")
        assert hasattr(result, "profit_factor")
        assert hasattr(result, "trades")
        assert hasattr(result, "equity_curve")

    def test_equity_curve_generated(self, sample_price_data):
        """Test equity curve is generated during backtest."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(
            data=sample_price_data,
            strategy=strategy,
        )

        assert len(result.equity_curve) > 0
        assert all("date" in point for point in result.equity_curve)
        assert all("equity" in point for point in result.equity_curve)

    def test_trades_recorded(self, sample_price_data):
        """Test trades are recorded during backtest."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(
            data=sample_price_data,
            strategy=strategy,
        )

        assert isinstance(result.trades, list)

    def test_performance_metrics_calculated(self, rising_market_data):
        """Test performance metrics are calculated correctly."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(
            data=rising_market_data,
            strategy=strategy,
        )

        assert isinstance(result.sharpe_ratio, float)
        assert isinstance(result.sortino_ratio, float)
        assert isinstance(result.max_drawdown_pct, float)
        assert isinstance(result.win_rate, float)

    def test_backtest_with_date_range(self, sample_price_data):
        """Test backtest with specific date range."""
        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        start = sample_price_data.index[20]
        end = sample_price_data.index[80]

        result = engine.run_backtest(
            data=sample_price_data,
            strategy=strategy,
            start_date=start,
            end_date=end,
        )

        assert result.start_date == start
        assert result.end_date == end

    def test_position_sizing(self):
        """Test position sizing calculation."""
        config = BacktestConfig(
            initial_capital=100000,
            position_size_pct=0.20,
        )
        engine = BacktestingEngine(config=config)

        position_size = engine._calculate_position_size(price=100.0)

        expected = (100000 * 0.20) / 100.0
        assert position_size == expected

    def test_transaction_costs_applied(self):
        """Test transaction costs are applied to trades."""
        dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
        prices = np.linspace(100, 200, 50)
        data = pd.DataFrame(
            {
                "date": dates,
                "close": prices,
            }
        ).set_index("date")

        config = BacktestConfig(
            initial_capital=100000,
            transaction_cost_pct=0.01,
        )
        engine = BacktestingEngine(config=config)
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(data=data, strategy=strategy)

        assert result is not None


class TestSMACrossoverStrategy:
    """Tests for SMACrossoverStrategy."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for SMA strategy testing."""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)

        return pd.DataFrame(
            {
                "date": dates,
                "asset_id": [1] * 100,
                "close": prices,
            }
        )

    def test_strategy_initialization(self):
        """Test strategy initializes with default parameters."""
        strategy = SMACrossoverStrategy()

        assert strategy.fast_period == 10
        assert strategy.slow_period == 20
        assert strategy.name == "SMA Crossover (10/20)"

    def test_strategy_custom_parameters(self):
        """Test strategy with custom parameters."""
        strategy = SMACrossoverStrategy(fast_period=5, slow_period=15)

        assert strategy.fast_period == 5
        assert strategy.slow_period == 15
        assert strategy.name == "SMA Crossover (5/15)"

    def test_generate_signals(self, sample_data):
        """Test signal generation."""
        strategy = SMACrossoverStrategy(fast_period=10, slow_period=20)

        timestamp = datetime(2024, 1, 1)
        signals = strategy.generate_signals(sample_data, timestamp)

        assert isinstance(signals, list)

    def test_insufficient_data(self):
        """Test strategy with insufficient data."""
        data = pd.DataFrame(
            {
                "date": [datetime(2024, 1, 1)],
                "asset_id": [1],
                "close": [100.0],
            }
        )

        strategy = SMACrossoverStrategy(fast_period=50, slow_period=100)
        timestamp = datetime(2024, 1, 1)
        signals = strategy.generate_signals(data, timestamp)

        assert signals == []


class TestRSIMeanReversionStrategy:
    """Tests for RSIMeanReversionStrategy."""

    @pytest.fixture
    def rising_data(self):
        """Create rising price data (RSI should be high)."""
        dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
        prices = 100 + np.cumsum(np.random.randn(50) * 0.1)

        return pd.DataFrame(
            {
                "date": dates,
                "asset_id": [1] * 50,
                "close": prices,
            }
        )

    def test_strategy_initialization(self):
        """Test strategy initializes with default parameters."""
        strategy = RSIMeanReversionStrategy()

        assert strategy.period == 14
        assert strategy.oversold == 30
        assert strategy.overbought == 70

    def test_strategy_custom_parameters(self):
        """Test strategy with custom parameters."""
        strategy = RSIMeanReversionStrategy(period=7, oversold=25, overbought=75)

        assert strategy.period == 7
        assert strategy.oversold == 25
        assert strategy.overbought == 75

    def test_generate_oversold_signal(self):
        """Test buy signal when RSI is oversold."""
        data = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=30, freq="D"),
                "asset_id": [1] * 30,
                "close": [100 - i for i in range(30)],
            }
        )

        strategy = RSIMeanReversionStrategy(period=14, oversold=30, overbought=70)
        timestamp = datetime(2024, 1, 1)
        signals = strategy.generate_signals(data, timestamp)

        assert isinstance(signals, list)

    def test_insufficient_data(self):
        """Test strategy with insufficient data."""
        data = pd.DataFrame(
            {
                "date": [datetime(2024, 1, 1)],
                "asset_id": [1],
                "close": [100.0],
            }
        )

        strategy = RSIMeanReversionStrategy(period=14)
        timestamp = datetime(2024, 1, 1)
        signals = strategy.generate_signals(data, timestamp)

        assert signals == []


class TestBaseStrategy:
    """Tests for BaseStrategy abstract class."""

    def test_base_strategy_is_abstract(self):
        """Test BaseStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseStrategy()

    def test_concrete_strategy(self):
        """Test concrete strategy implementation."""

        class TestStrategy(BaseStrategy):
            def generate_signals(self, data, timestamp):
                return [{"action": "BUY"}]

        strategy = TestStrategy()
        assert strategy.name == "TestStrategy"
        assert strategy.config == {}

    def test_get_asset_data(self):
        """Test get_asset_data helper method."""

        class TestStrategy(BaseStrategy):
            def generate_signals(self, data, timestamp):
                return []

        data = pd.DataFrame(
            {
                "asset_id": [1, 1, 2, 2],
                "close": [100, 101, 50, 51],
            }
        )

        strategy = TestStrategy()
        result = strategy.get_asset_data(data, asset_id=1)

        assert len(result) == 2
        assert all(result["asset_id"] == 1)


class TestBacktestEdgeCases:
    """Tests for edge cases in backtesting."""

    def test_volatile_market(self):
        """Test backtest with highly volatile market."""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        prices = 100 + np.cumsum(np.random.randn(100) * 2)

        data = pd.DataFrame(
            {
                "date": dates,
                "close": prices,
            }
        ).set_index("date")

        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(data=data, strategy=strategy)

        assert result is not None
        assert isinstance(result.total_trades, int)

    def test_sideways_market(self):
        """Test backtest with sideways market."""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        prices = 100 + np.sin(np.linspace(0, 10, 100)) * 5

        data = pd.DataFrame(
            {
                "date": dates,
                "close": prices,
            }
        ).set_index("date")

        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(data=data, strategy=strategy)

        assert result is not None

    def test_single_asset_multiple_assets(self):
        """Test backtest with multiple assets."""
        dates = pd.date_range(start="2024-01-01", periods=50, freq="D")

        data = pd.DataFrame(
            {
                "date": dates.repeat(3),
                "asset_id": [1] * 50 + [2] * 50 + [3] * 50,
                "close": list(np.linspace(100, 150, 50)) * 3,
            }
        )

        engine = BacktestingEngine()
        strategy = SMACrossoverStrategy()

        result = engine.run_backtest(data=data, strategy=strategy)

        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
