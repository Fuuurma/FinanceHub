# C-022: Strategy Backtesting Engine

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 18-24 hours  
**Dependencies:** C-021 (Technical Indicators Engine)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive backtesting engine for testing trading strategies on historical data with performance metrics and visualization.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 3.3 - Technical Analysis):**

- Backtesting engine for strategies
- Strategy builder (visual or code)
- Paper trading account

**From Features Specification (Section 8.1 - Algorithmic Trading):**

- Backtesting engine
- Strategy builder (visual or code)
- Paper trading account
- Order routing automation
- Execution algorithms (TWAP, VWAP, implementation shortfall)

---

## ✅ CURRENT STATE

**What exists:**
- Historical price data model
- Technical indicators library (C-021)
- Portfolio tracking system
- Transaction history

**What's missing:**
- Backtesting engine
- Strategy definition framework
- Performance metrics calculation
- Trade simulation logic
- Results visualization data

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (3-4 hours)

**Create `apps/backend/src/investments/models/backtesting.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .asset import Asset
from .portfolio import Portfolio

User = get_user_model()

class TradingStrategy(models.Model):
    """Trading strategy definitions"""
    
    STRATEGY_TYPE_CHOICES = [
        ('code', 'Custom Code (Python)'),
        ('visual', 'Visual Builder'),
        ('preset', 'Preset Strategy'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strategies')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    strategy_type = models.CharField(max_length=20, choices=STRATEGY_TYPE_CHOICES)
    
    # Strategy definition
    code = models.TextField(blank=True)  # Python code for custom strategies
    config = models.JSONField(default=dict)  # Visual strategy config or preset params
    
    # Backtesting settings
    initial_capital = models.DecimalField(max_digits=20, decimal_places=2, default=100000)
    commission = models.DecimalField(max_digits=10, decimal_places=4, default=0.001)  # 0.1%
    slippage = models.DecimalField(max_digits=10, decimal_places=4, default=0.0001)  # 0.01%
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Backtest(models.Model):
    """Backtest run results"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE, related_name='backtests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Backtest parameters
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    assets = models.ManyToManyField(Asset)
    timeframe = models.CharField(max_length=10)  # 1d, 1h, etc.
    
    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_return = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    sortino_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    profit_factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Trade statistics
    total_trades = models.IntegerField(null=True)
    winning_trades = models.IntegerField(null=True)
    losing_trades = models.IntegerField(null=True)
    avg_win = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    avg_loss = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    largest_win = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    largest_loss = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    
    # Performance curve data
    equity_curve = models.JSONField(null=True)  # Array of {date, value}
    drawdown_curve = models.JSONField(null=True)  # Array of {date, drawdown}
    
    # Execution
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['strategy', '-created_at']),
        ]

class BacktestTrade(models.Model):
    """Individual trades from backtest"""
    
    backtest = models.ForeignKey(Backtest, on_delete=models.CASCADE, related_name='trades')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    
    # Trade details
    entry_date = models.DateTimeField()
    exit_date = models.DateTimeField(null=True)
    entry_price = models.DecimalField(max_digits=20, decimal_places=4)
    exit_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    
    # Type
    action = models.CharField(max_length=10)  # BUY, SELL
    position_type = models.CharField(max_length=10)  # LONG, SHORT
    
    # Results
    exit_reason = models.CharField(max_length=50, blank=True)  # stop_loss, take_profit, signal, etc.
    pnl = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    pnl_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    return_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    
    # Duration
    bars_held = models.IntegerField(null=True)
    
    class Meta:
        ordering = ['entry_date']
        indexes = [
            models.Index(fields=['backtest', 'entry_date']),
        ]

class PaperTradingAccount(models.Model):
    """Paper trading for live testing"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE)
    
    # Account details
    account_name = models.CharField(max_length=200)
    initial_capital = models.DecimalField(max_digits=20, decimal_places=2)
    current_capital = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Settings
    commission = models.DecimalField(max_digits=10, decimal_places=4, default=0.001)
    slippage = models.DecimalField(max_digits=10, decimal_places=4, default=0.0001)
    
    # Status
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    
    # Performance
    total_return = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    class Meta:
        verbose_name = "Paper Trading Account"
```

---

### **Phase 2: Backtesting Engine** (8-10 hours)

**Create `apps/backend/src/investments/services/backtesting_engine.py`:**

```python
from typing import List, Dict, Callable
from decimal import Decimal
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from django.utils import timezone
from investments.models import Asset, Backtest, BacktestTrade, TradingStrategy
from investments.models.backtesting import Backtest as BacktestModel
from investments.services.indicator_service import IndicatorCalculationService

class BacktestingEngine:
    """
    Comprehensive backtesting engine for trading strategies
    Supports multiple asset types, timeframes, and strategies
    """
    
    def __init__(self, backtest_id: int):
        self.backtest = BacktestModel.objects.get(id=backtest_id)
        self.strategy = self.backtest.strategy
        self.indicator_service = IndicatorCalculationService()
        
        # Portfolio state
        self.cash = float(self.strategy.initial_capital)
        self.positions = {}  # {asset_id: {quantity, entry_price, entry_date}}
        self.trades = []
        self.equity_curve = []
        self.drawdown_curve = []
        
        # Performance tracking
        self.peak_equity = self.cash
        self.current_equity = self.cash
    
    def run(self) -> Dict:
        """Execute backtest"""
        try:
            self.backtest.status = 'running'
            self.backtest.started_at = timezone.now()
            self.backtest.save()
            
            # Load historical data
            data = self._load_historical_data()
            
            # Execute strategy
            self._execute_strategy(data)
            
            # Calculate performance metrics
            metrics = self._calculate_metrics()
            
            # Save results
            self._save_results(metrics)
            
            self.backtest.status = 'completed'
            self.backtest.completed_at = timezone.now()
            self.backtest.save()
            
            return metrics
            
        except Exception as e:
            self.backtest.status = 'failed'
            self.backtest.error_message = str(e)
            self.backtest.save()
            raise
    
    def _load_historical_data(self) -> pd.DataFrame:
        """Load and prepare historical data"""
        assets = list(self.backtest.assets.all())
        
        all_data = []
        for asset in assets:
            from investments.models import AssetPricesHistoric
            
            prices = AssetPricesHistoric.objects.filter(
                asset=asset,
                timestamp__gte=self.backtest.start_date,
                timestamp__lte=self.backtest.end_date
            ).order_by('timestamp')
            
            for price in prices:
                all_data.append({
                    'timestamp': price.timestamp,
                    'asset_id': asset.id,
                    'symbol': asset.symbol,
                    'open': float(price.open_price),
                    'high': float(price.high_price),
                    'low': float(price.low_price),
                    'close': float(price.close_price),
                    'volume': price.volume
                })
        
        df = pd.DataFrame(all_data)
        return df
    
    def _execute_strategy(self, data: pd.DataFrame):
        """Execute trading strategy on historical data"""
        # Group by timestamp
        grouped = data.groupby('timestamp')
        
        for timestamp, group in grouped:
            # Calculate portfolio value
            portfolio_value = self._calculate_portfolio_value(group, timestamp)
            self.equity_curve.append({
                'date': timestamp.isoformat(),
                'value': portfolio_value
            })
            
            # Track drawdown
            if portfolio_value > self.peak_equity:
                self.peak_equity = portfolio_value
            
            drawdown = (self.peak_equity - portfolio_value) / self.peak_equity * 100
            self.drawdown_curve.append({
                'date': timestamp.isoformat(),
                'drawdown': drawdown
            })
            
            # Execute strategy logic
            signals = self._generate_signals(group, timestamp)
            
            # Execute trades based on signals
            self._execute_signals(signals, group, timestamp)
    
    def _generate_signals(self, data: pd.DataFrame, timestamp) -> List[Dict]:
        """Generate trading signals based on strategy"""
        signals = []
        
        if self.strategy.strategy_type == 'code':
            # Execute custom Python code
            signals = self._execute_custom_strategy(data, timestamp)
        elif self.strategy.strategy_type == 'visual':
            # Execute visual strategy
            signals = self._execute_visual_strategy(data, timestamp)
        elif self.strategy.strategy_type == 'preset':
            # Execute preset strategy
            signals = self._execute_preset_strategy(data, timestamp)
        
        return signals
    
    def _execute_custom_strategy(self, data: pd.DataFrame, timestamp) -> List[Dict]:
        """Execute custom Python strategy"""
        signals = []
        
        try:
            # Prepare context for strategy code
            context = {
                'data': data,
                'timestamp': timestamp,
                'positions': self.positions.copy(),
                'cash': self.cash,
                'indicators': self.indicator_service
            }
            
            # Execute strategy code
            exec(self.strategy.code, context)
            
            # Extract signals
            signals = context.get('signals', [])
            
        except Exception as e:
            print(f"Strategy execution error: {e}")
        
        return signals
    
    def _execute_visual_strategy(self, data: pd.DataFrame, timestamp) -> List[Dict]:
        """Execute visual builder strategy"""
        signals = []
        config = self.strategy.config
        
        for asset_id in data['asset_id'].unique():
            asset_data = data[data['asset_id'] == asset_id]
            
            # Example: Simple moving average crossover
            if config.get('strategy') == 'sma_crossover':
                fast_period = config.get('fast_period', 10)
                slow_period = config.get('slow_period', 20)
                
                # Get SMAs
                fast_sma = self.indicator_service.calculate_indicator(
                    asset_id, 'sma', self.backtest.timeframe, fast_period
                )
                slow_sma = self.indicator_service.calculate_indicator(
                    asset_id, 'sma', self.backtest.timeframe, slow_period
                )
                
                if fast_sma['values'] and slow_sma['values']:
                    current_fast = fast_sma['values'][-1]
                    current_slow = slow_sma['values'][-1]
                    prev_fast = fast_sma['values'][-2] if len(fast_sma['values']) > 1 else current_fast
                    prev_slow = slow_sma['values'][-2] if len(slow_sma['values']) > 1 else current_slow
                    
                    # Crossover signals
                    if prev_fast <= prev_slow and current_fast > current_slow:
                        signals.append({
                            'asset_id': asset_id,
                            'action': 'BUY',
                            'type': 'LONG',
                            'reason': 'SMA crossover'
                        })
                    elif prev_fast >= prev_slow and current_fast < current_slow:
                        signals.append({
                            'asset_id': asset_id,
                            'action': 'SELL',
                            'type': 'LONG',
                            'reason': 'SMA crossover'
                        })
        
        return signals
    
    def _execute_preset_strategy(self, data: pd.DataFrame, timestamp) -> List[Dict]:
        """Execute preset strategy"""
        # Implement preset strategies (e.g., RSI, Mean Reversion, Momentum)
        return []
    
    def _execute_signals(self, signals: List[Dict], data: pd.DataFrame, timestamp):
        """Execute trading signals"""
        for signal in signals:
            asset_id = signal['asset_id']
            action = signal['action']
            
            asset_data = data[data['asset_id'] == asset_id].iloc[0]
            price = asset_data['close']
            
            if action == 'BUY':
                self._execute_buy(asset_id, price, timestamp, signal)
            elif action == 'SELL':
                self._execute_sell(asset_id, price, timestamp, signal)
    
    def _execute_buy(self, asset_id: int, price: float, timestamp, signal: Dict):
        """Execute buy order"""
        # Calculate position size (simplified - use 10% of cash)
        position_size = self.cash * 0.1
        quantity = position_size / price
        
        # Apply commission and slippage
        commission_cost = position_size * float(self.strategy.commission)
        slippage_cost = position_size * float(self.strategy.slippage)
        total_cost = position_size + commission_cost + slippage_cost
        
        if total_cost <= self.cash:
            self.cash -= total_cost
            self.positions[asset_id] = {
                'quantity': quantity,
                'entry_price': price,
                'entry_date': timestamp
            }
    
    def _execute_sell(self, asset_id: int, price: float, timestamp, signal: Dict):
        """Execute sell order"""
        if asset_id in self.positions:
            position = self.positions[asset_id]
            quantity = position['quantity']
            
            # Calculate proceeds
            gross_proceeds = quantity * price
            commission_cost = gross_proceeds * float(self.strategy.commission)
            slippage_cost = gross_proceeds * float(self.strategy.slippage)
            net_proceeds = gross_proceeds - commission_cost - slippage_cost
            
            # Calculate P&L
            pnl = net_proceeds - (quantity * position['entry_price'])
            pnl_pct = (pnl / (quantity * position['entry_price'])) * 100
            
            # Record trade
            self.trades.append({
                'asset_id': asset_id,
                'entry_date': position['entry_date'],
                'exit_date': timestamp,
                'entry_price': position['entry_price'],
                'exit_price': price,
                'quantity': quantity,
                'pnl': pnl,
                'pnl_percentage': pnl_pct,
                'exit_reason': signal.get('reason', 'signal')
            })
            
            # Update cash
            self.cash += net_proceeds
            del self.positions[asset_id]
    
    def _calculate_portfolio_value(self, data: pd.DataFrame, timestamp) -> float:
        """Calculate total portfolio value"""
        total_value = self.cash
        
        for asset_id, position in self.positions.items():
            asset_data = data[data['asset_id'] == asset_id]
            if not asset_data.empty:
                current_price = asset_data.iloc[0]['close']
                position_value = position['quantity'] * current_price
                total_value += position_value
        
        self.current_equity = total_value
        return total_value
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {}
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Calculate returns from equity curve
        if len(self.equity_curve) > 1:
            initial = self.equity_curve[0]['value']
            final = self.equity_curve[-1]['value']
            total_return = ((final - initial) / initial) * 100
        else:
            total_return = 0
        
        # Sharpe Ratio (simplified - assumes 5% risk-free rate)
        if len(self.equity_curve) > 1:
            returns = pd.Series([e['value'] for e in self.equity_curve]).pct_change().dropna()
            sharpe_ratio = (returns.mean() * 252 - 0.05) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Max drawdown
        max_drawdown = max([d['drawdown'] for d in self.drawdown_curve]) if self.drawdown_curve else 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def _save_results(self, metrics: Dict):
        """Save backtest results to database"""
        # Update backtest with metrics
        for key, value in metrics.items():
            setattr(self.backtest, key, value)
        
        self.backtest.equity_curve = self.equity_curve
        self.backtest.drawdown_curve = self.drawdown_curve
        self.backtest.save()
        
        # Save trades
        for trade in self.trades:
            BacktestTrade.objects.create(
                backtest=self.backtest,
                asset_id=trade['asset_id'],
                entry_date=trade['entry_date'],
                exit_date=trade['exit_date'],
                entry_price=trade['entry_price'],
                exit_price=trade['exit_price'],
                quantity=trade['quantity'],
                exit_reason=trade.get('exit_reason', ''),
                pnl=trade['pnl'],
                pnl_percentage=trade['pnl_percentage']
            )
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/backtesting.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.models import Backtest, TradingStrategy
from investments.services.backtesting_engine import BacktestingEngine
import dramatiq

router = Router(tags=['backtesting'])

class BacktestCreateSchema(Schema):
    strategy_id: int
    start_date: str
    end_date: str
    asset_ids: list[int]
    timeframe: str = '1d'

class StrategyCreateSchema(Schema):
    name: str
    description: str = None
    strategy_type: str  # code, visual, preset
    code: str = None
    config: dict = {}
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0001

@router.post("/strategies")
def create_strategy(request, data: StrategyCreateSchema):
    """Create new trading strategy"""
    strategy = TradingStrategy.objects.create(
        user=request.auth,
        **data.dict()
    )
    return {"id": strategy.id, "name": strategy.name}

@router.get("/strategies")
def list_strategies(request):
    """List user's strategies"""
    strategies = TradingStrategy.objects.filter(user=request.auth)
    return [{
        "id": s.id,
        "name": s.name,
        "type": s.strategy_type,
        "status": s.status,
        "created_at": s.created_at
    } for s in strategies]

@router.post("/backtests")
def create_backtest(request, data: BacktestCreateSchema):
    """Create and run backtest"""
    strategy = get_object_or_404(TradingStrategy, id=data.strategy_id, user=request.auth)
    
    backtest = Backtest.objects.create(
        strategy=strategy,
        user=request.auth,
        start_date=data.start_date,
        end_date=data.end_date,
        timeframe=data.timeframe
    )
    backtest.assets.set(data.asset_ids)
    
    # Run backtest asynchronously
    run_backtest.send(backtest.id)
    
    return {"id": backtest.id, "status": "pending"}

@router.get("/backtests/{backtest_id}")
def get_backtest_results(request, backtest_id: int):
    """Get backtest results"""
    backtest = get_object_or_404(Backtest, id=backtest_id, user=request.user)
    
    return {
        "id": backtest.id,
        "status": backtest.status,
        "metrics": {
            "total_return": float(backtest.total_return) if backtest.total_return else None,
            "sharpe_ratio": float(backtest.sharpe_ratio) if backtest.sharpe_ratio else None,
            "max_drawdown": float(backtest.max_drawdown) if backtest.max_drawdown else None,
            "win_rate": float(backtest.win_rate) if backtest.win_rate else None,
            "profit_factor": float(backtest.profit_factor) if backtest.profit_factor else None,
        },
        "equity_curve": backtest.equity_curve,
        "drawdown_curve": backtest.drawdown_curve,
        "trades_count": backtest.trades.count()
    }

@router.get("/backtests/{backtest_id}/trades")
def get_backtest_trades(request, backtest_id: int):
    """Get backtest trades"""
    backtest = get_object_or_404(Backtest, id=backtest_id, user=request.user)
    trades = backtest.trades.all()
    
    return [{
        "asset": t.asset.symbol,
        "entry_date": t.entry_date,
        "exit_date": t.exit_date,
        "entry_price": float(t.entry_price),
        "exit_price": float(t.exit_price) if t.exit_price else None,
        "quantity": float(t.quantity),
        "pnl": float(t.pnl) if t.pnl else None,
        "pnl_percentage": float(t.pnl_percentage) if t.pnl_percentage else None,
        "exit_reason": t.exit_reason
    } for t in trades]

# Dramatiq task
@dramatiq.actor
def run_backtest(backtest_id: int):
    """Run backtest asynchronously"""
    engine = BacktestingEngine(backtest_id)
    engine.run()
```

---

## 📋 DELIVERABLES

- [ ] TradingStrategy, Backtest, BacktestTrade, PaperTradingAccount models
- [ ] BacktestingEngine with execution logic
- [ ] Support for custom Python strategies
- [ ] Support for visual builder strategies
- [ ] Performance metrics calculation
- [ ] Equity and drawdown curves
- [ ] 6 API endpoints
- [ ] Async Dramatiq task for running backtests
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Backtest runs on historical date range
- [ ] Supports multiple assets
- [ ] Calculates 8+ performance metrics
- [ ] Generates equity curve data
- [ ] Generates drawdown curve data
- [ ] Records all individual trades
- [ ] Custom Python strategies execute safely
- [ ] Visual SMA crossover strategy works
- [ ] Async execution via Dramatiq
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Backtest execution time: 1 year of data in <30 seconds
- Support for 1000+ trades per backtest
- Strategy execution overhead <10% of total time
- All performance metrics accurate to 2 decimal places

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/022-strategy-backtesting-engine.md
