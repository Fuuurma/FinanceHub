# Task C-022: Strategy Backtesting Engine

**Priority:** P1 HIGH  
**Estimated Time:** 18-24 hours  
**Assigned To:** Backend Coder  
**Status:** PENDING

## ⚡ Quick Start Guide

**What to do FIRST (in order):**

1. **Setup (Step 1):** Install dependencies (15m) - pandas, numpy
2. **Backend (Step 2):** Create models (3h) - TradingStrategy, Backtest, BacktestTrade
3. **Backend (Step 3):** Create base strategy (2h) - BaseStrategy abstract class
4. **Backend (Step 4):** Create preset strategies (3h) - SMA crossover, RSI mean reversion
5. **Backend (Step 5):** Create backtesting engine (6h) - Core execution logic ⭐ CRITICAL
6. **Backend (Step 6):** Create performance calculator (2h) - Sharpe, Sortino, etc.
7. **Backend (Step 7):** Create API endpoints (3h) - 6 REST endpoints
8. **Backend (Step 8):** Create Dramatiq task (1h) - Async execution
9. **Testing (Step 9):** Write tests (2h) - Test backtest execution
10. **Frontend (Step 10):** Create results page (2h) - Display metrics

**Total: 20 hours (estimate)**

---

## Overview
Implement comprehensive backtesting engine for testing trading strategies on historical data with performance metrics and visualization.

---

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### STEP 1: Install Dependencies (15 minutes)

```bash
pip install pandas numpy scipy
```

### STEP 2: Create Database Models (3 hours)

**File:** `apps/backend/src/investments/models/backtesting.py`

See current file (747 lines) - models already defined ✅

**CREATE MIGRATION:**
```bash
python manage.py makemigrations investments
python manage.py migrate investments
```

---

### STEP 3: Create Base Strategy Interface (2 hours) ⭐ CRITICAL

**File:** `apps/backend/src/investments/services/strategies/base_strategy.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from datetime import datetime

class BaseStrategy(ABC):
    """
    Base class for ALL trading strategies.
    
    Every strategy MUST inherit from this class and implement
    the generate_signals() method.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        """
        Generate trading signals.
        
        Args:
            data: DataFrame with OHLCV data
            timestamp: Current timestamp
        
        Returns:
            List of signals:
            [
                {
                    'asset_id': 123,
                    'action': 'BUY',  # or 'SELL'
                    'type': 'LONG',
                    'reason': 'SMA crossover'
                }
            ]
        """
        pass
    
    def get_asset_data(self, data: pd.DataFrame, asset_id: int) -> pd.DataFrame:
        """Helper: Get data for specific asset."""
        return data[data['asset_id'] == asset_id]
```

---

### STEP 4: Create Preset Strategies (3 hours)

**File:** `apps/backend/src/investments/services/strategies/sma_crossover.py`

```python
from .base_strategy import BaseStrategy
from typing import Dict, List
import pandas as pd
from datetime import datetime

class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    Buy: Fast SMA crosses above Slow SMA
    Sell: Fast SMA crosses below Slow SMA
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.fast_period = self.config.get('fast_period', 10)
        self.slow_period = self.config.get('slow_period', 20)
        self.price_history = {}
    
    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> List[Dict]:
        signals = []
        
        for asset_id in data['asset_id'].unique():
            asset_data = self.get_asset_data(data, asset_id)
            if asset_data.empty:
                continue
            
            close = asset_data.iloc[-1]['close']
            
            # Update history
            if asset_id not in self.price_history:
                self.price_history[asset_id] = []
            self.price_history[asset_id].append(close)
            
            prices = self.price_history[asset_id]
            
            # Need enough data
            if len(prices) < self.slow_period + 1:
                continue
            
            # Calculate SMAs
            fast_sma = sum(prices[-self.fast_period:]) / self.fast_period
            slow_sma = sum(prices[-self.slow_period:]) / self.slow_period
            
            # Previous SMAs
            prev_fast = sum(prices[-self.fast_period-1:-1]) / self.fast_period
            prev_slow = sum(prices[-self.slow_period-1:-1]) / self.slow_period
            
            # Crossovers
            if prev_fast <= prev_slow and fast_sma > slow_sma:
                signals.append({
                    'asset_id': asset_id,
                    'action': 'BUY',
                    'type': 'LONG',
                    'reason': f'SMA{self.fast_period} > SMA{self.slow_period}'
                })
            elif prev_fast >= prev_slow and fast_sma < slow_sma:
                signals.append({
                    'asset_id': asset_id,
                    'action': 'SELL',
                    'type': 'LONG',
                    'reason': f'SMA{self.fast_period} < SMA{self.slow_period}'
                })
        
        return signals
```

---

### STEP 5: Create Backtesting Engine (6 hours) ⭐ MOST CRITICAL

**Key Components:**

1. **Initialize** - Load strategy, set portfolio state
2. **Load Data** - Fetch historical prices
3. **Execute** - Loop through timestamps, generate signals, execute trades
4. **Calculate Metrics** - Sharpe, Sortino, max drawdown, etc.
5. **Save Results** - Store in database

**Core Execution Flow:**
```
for each timestamp:
    1. Calculate portfolio value
    2. Track drawdown
    3. Generate trading signals
    4. Execute trades (buy/sell)
    5. Update positions and cash
```

**Position Sizing:**
- Use 10% of cash per position
- Or use Kelly Criterion: f* = (bp - q) / b
- Or use fixed fractional: position_size = account_value * risk_per_trade

**Transaction Costs:**
- Commission: trade_value * commission_rate
- Slippage: trade_value * slippage_rate
- Apply to BOTH buys and sells

---

### STEP 6: Performance Metrics (2 hours)

**Key Metrics:**

1. **Total Return**: ((final - initial) / initial) * 100

2. **Sharpe Ratio**: (return - risk_free) / volatility
   - Assumes 252 trading days/year
   - Risk-free rate: 5% (0.05)

3. **Sortino Ratio**: (return - risk_free) / downside_deviation
   - Only considers downside volatility

4. **Max Drawdown**: Maximum peak-to-trough decline
   - Track peak equity
   - Drawdown = (peak - current) / peak

5. **Win Rate**: (winning_trades / total_trades) * 100

6. **Profit Factor**: gross_profit / gross_loss

---

### STEP 7: Create API Endpoints (3 hours)

**File:** `apps/backend/src/api/backtesting.py`

```python
from ninja import Router
from investments.models import Backtest, TradingStrategy
from investments.services.backtesting_engine import BacktestingEngine
import dramatiq

router = Router()

@router.post("/backtests")
def create_backtest(request, data: BacktestCreateSchema):
    """Create and run backtest."""
    backtest = Backtest.objects.create(**data.dict())
    backtest.assets.set(data.asset_ids)
    
    # Run asynchronously
    run_backtest.send(backtest.id)
    
    return {"id": backtest.id, "status": "pending"}

@router.get("/backtests/{backtest_id}")
def get_backtest(request, backtest_id: int):
    """Get backtest results."""
    backtest = Backtest.objects.get(id=backtest_id)
    return {
        "metrics": {
            "total_return": backtest.total_return,
            "sharpe_ratio": backtest.sharpe_ratio,
            "max_drawdown": backtest.max_drawdown,
        },
        "equity_curve": backtest.equity_curve,
    }

@dramatiq.actor
def run_backtest(backtest_id: int):
    """Run backtest asynchronously."""
    engine = BacktestingEngine(backtest_id)
    engine.run()
```

---

## 📚 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Not Accounting for Transaction Costs
```python
# WRONG - Ignores commission and slippage
self.cash -= quantity * price

# CORRECT - Includes costs
cost = (quantity * price) * (1 + commission + slippage)
self.cash -= cost
```

### ❌ Mistake 2: Look-Ahead Bias
```python
# WRONG - Uses future data in signal generation
signal = data['close'].iloc[-1]  # This is current bar
if signal > data['close'].mean():  # This includes future!

# CORRECT - Only use historical data
historical_close = data['close'].iloc[:-1]
current_close = data['close'].iloc[-1]
if current_close > historical_close.mean():
    signal = 'BUY'
```

### ❌ Mistake 3: Not Handling Insufficient Funds
```python
# WRONG - Allows negative cash
self.cash -= trade_value

# CORRECT - Check before trading
if trade_value <= self.cash:
    self.cash -= trade_value
else:
    return  # Skip trade
```

### ❌ Mistake 4: Incorrect Sharpe Ratio Calculation
```python
# WRONG - Daily returns, not annualized
sharpe = returns.mean() / returns.std()

# CORRECT - Annualized (252 trading days)
sharpe = (returns.mean() * 252 - 0.05) / (returns.std() * sqrt(252))
```

### ❌ Mistake 5: Not Using Database Transactions
```python
# WRONG - Partial save if error occurs
backtest.save()
BacktestTrade.objects.create(...)  # If this fails, backtest is saved but inconsistent

# CORRECT - All or nothing
with transaction.atomic():
    backtest.save()
    BacktestTrade.objects.create(...)
```

---

## ❓ FAQ

**Q: How much historical data do I need?**  
A: Minimum 1 year (252 trading days). For robust results, use 3-5 years.

**Q: What timeframe should I use?**  
A: Daily (1d) for long-term strategies, Hourly (1h) for intraday. Start with daily.

**Q: How do I handle multiple assets?**  
A: Process all assets at each timestamp. Each asset generates its own signals. Use 10% cash per asset position.

**Q: Should I include commission in backtests?**  
A: YES! Realistic backtests need transaction costs. Default: 0.1% commission + 0.01% slippage.

**Q: What's a good Sharpe ratio?**  
A: > 1.0 = Good, > 2.0 = Very Good, > 3.0 = Excellent. Negative = Bad.

**Q: How do I prevent overfitting?**  
A: Use out-of-sample testing. Train on 70% of data, test on 30%. Never test on training data.

**Q: Can users write custom strategies?**  
A: YES! Use Python code strategy type. Safely execute with `exec()` in sandboxed environment.

---

## 📋 CHECKLIST BEFORE SUBMITTING

- [ ] All models created with base classes
- [ ] Migration created and applied
- [ ] BaseStrategy abstract class defined
- [ ] At least 2 preset strategies work (SMA, RSI)
- [ ] Backtesting engine executes correctly
- [ ] Transaction costs applied
- [ ] Performance metrics accurate
- [ ] API endpoints working
- [ ] Dramatiq async task working
- [ ] Tests pass
- [ ] Equity curve data generated
- [ ] Drawdown curve data generated

---

## 🎯 SUCCESS CRITERIA

1. ✅ Backtest runs on historical date range
2. ✅ Supports multiple assets simultaneously
3. ✅ Calculates 8+ performance metrics accurately
4. ✅ Generates equity curve for visualization
5. ✅ Generates drawdown curve
6. ✅ Records all individual trades
7. ✅ Custom Python strategies execute safely
8. ✅ SMA crossover preset strategy works
9. ✅ Async execution via Dramatiq works
10. ✅ All tests passing

---

**Start with Step 1 (install dependencies) and work through each step sequentially.**
