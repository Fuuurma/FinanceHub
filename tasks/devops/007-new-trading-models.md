# Task D-007: Trading Models

**Assigned To:** Backend Coder (DevOps supervision)  
**Created By:** GAUDÍ (Architect)  
**Priority:** P1 - HIGH  
**Time Estimate:** 1.5 days (12 hours)  
**Dependencies:** D-002 (Database Migrations)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive trading models with proper inheritance (UUIDModel, TimestampedModel, SoftDeleteModel) for tracking trades and order executions.

---

## ⚠️ CRITICAL REMINDER

**ALL MODELS MUST INHERIT FROM:**
- `UUIDModel` - Provides UUID primary key
- `TimestampedModel` - Provides created_at, updated_at
- `SoftDeleteModel` - Provides soft delete functionality

**DO NOT create models without these base classes!**

---

## 📋 MODELS TO IMPLEMENT

### **1. Trade Model**

**File:** `apps/backend/src/trading/models/trade.py`

**Purpose:** Track all trades (buy/sell) with detailed execution and P&L information.

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
from investments.models.portfolio import Portfolio
from investments.models.asset import Asset

class Trade(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Trade record for buy/sell transactions.
    Tracks execution details and calculates profit/loss.
    """
    
    # Relationships
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='trades'
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='trades'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trades'
    )
    
    # Trade identification
    trade_reference = models.CharField(max_length=50, unique=True, help_text="Unique trade reference ID")
    
    # Trade type and side
    trade_type = models.CharField(
        max_length=20,
        choices=[
            ('MARKET', 'Market Order'),
            ('LIMIT', 'Limit Order'),
            ('STOP', 'Stop Order'),
            ('STOP_LIMIT', 'Stop Limit Order'),
        ],
        default='MARKET'
    )
    
    side = models.CharField(
        max_length=10,
        choices=[
            ('BUY', 'Buy'),
            ('SELL', 'Sell'),
        ]
    )
    
    # Execution details
    quantity = models.DecimalField(max_digits=20, decimal_places=6, help_text="Quantity traded")
    price = models.DecimalField(max_digits=10, decimal_places=4, help_text="Execution price per share")
    
    # Financials
    gross_amount = models.DecimalField(max_digits=20, decimal_places=2, help_text="Quantity × Price")
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Trading commission/fees")
    net_amount = models.DecimalField(max_digits=20, decimal_places=2, help_text="Gross amount - Commission (for buys) or + Commission (for sells)")
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # Execution timing
    order_date = models.DateField(help_text="Date order was placed")
    execution_date = models.DateField(help_text="Date trade was executed")
    execution_time = models.TimeField(null=True, blank=True, help_text="Time of execution")
    
    # Order status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PARTIALLY_FILLED', 'Partially Filled'),
            ('FILLED', 'Filled'),
            ('CANCELLED', 'Cancelled'),
            ('REJECTED', 'Rejected'),
        ],
        default='FILLED'
    )
    
    # Broker/exchange info
    broker = models.CharField(max_length=100, blank=True, help_text="Broker or exchange name")
    order_id = models.CharField(max_length=100, blank=True, help_text="Broker order ID")
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'trades'
        ordering = ['-execution_date', '-execution_time']
        indexes = [
            models.Index(fields=['portfolio', 'execution_date']),
            models.Index(fields=['asset', 'execution_date']),
            models.Index(fields=['status']),
            models.Index(fields=['trade_reference']),
            models.Index(fields=['side']),
        ]
    
    def __str__(self):
        return f"{self.side} {self.quantity} {self.asset.symbol} @ {self.price}"
    
    def calculate_profit_loss(self, exit_price=None):
        """
        Calculate realized profit/loss for a sell trade.
        For buy trades, returns 0.
        """
        if self.side != 'SELL':
            return 0
        
        # Find corresponding buy trades (FIFO method)
        buy_trades = Trade.objects.filter(
            portfolio=self.portfolio,
            asset=self.asset,
            side='BUY',
            status='FILLED',
            execution_date__lte=self.execution_date
        ).order_by('execution_date', 'execution_time')
        
        total_buy_cost = 0
        total_buy_quantity = 0
        
        for buy in buy_trades:
            if total_buy_quantity >= self.quantity:
                break
            total_buy_cost += float(buy.net_amount)
            total_buy_quantity += float(buy.quantity)
        
        if total_buy_quantity == 0:
            return 0
        
        # Calculate realized P&L
        sell_proceeds = float(self.net_amount)
        buy_cost = total_buy_cost * (float(self.quantity) / total_buy_quantity)
        
        return sell_proceeds - buy_cost
    
    def calculate_return_percentage(self):
        """Calculate return percentage for sell trades."""
        pnl = self.calculate_profit_loss()
        if pnl == 0 or self.side != 'SELL':
            return 0
        
        # Find cost basis
        buy_trades = Trade.objects.filter(
            portfolio=self.portfolio,
            asset=self.asset,
            side='BUY',
            status='FILLED',
            execution_date__lte=self.execution_date
        ).order_by('execution_date', 'execution_time')
        
        total_buy_cost = 0
        total_buy_quantity = 0
        
        for buy in buy_trades:
            if total_buy_quantity >= self.quantity:
                break
            total_buy_cost += float(buy.net_amount)
            total_buy_quantity += float(buy.quantity)
        
        if total_buy_cost == 0:
            return 0
        
        buy_cost_for_quantity = total_buy_cost * (float(self.quantity) / total_buy_quantity)
        return (pnl / buy_cost_for_quantity) * 100
```

---

### **2. OrderExecution Model**

**File:** `apps/backend/src/trading/models/order_execution.py`

**Purpose:** Track partial fills and detailed execution information for orders.

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
from trading.models.trade import Trade
from investments.models.asset import Asset

class OrderExecution(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Detailed order execution records for tracking partial fills.
    Links to parent Trade and provides granular execution details.
    """
    
    # Relationships
    trade = models.ForeignKey(
        Trade,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_executions'
    )
    
    # Execution identification
    execution_reference = models.CharField(max_length=50, unique=True, help_text="Unique execution reference ID")
    broker_execution_id = models.CharField(max_length=100, blank=True, help_text="Broker's execution ID")
    
    # Execution details
    fill_quantity = models.DecimalField(max_digits=20, decimal_places=6, help_text="Quantity filled in this execution")
    fill_price = models.DecimalField(max_digits=10, decimal_places=4, help_text="Price per share for this fill")
    
    # Financials
    fill_amount = models.DecimalField(max_digits=20, decimal_places=2, help_text="fill_quantity × fill_price")
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Commission for this execution")
    
    # Timing
    execution_timestamp = models.DateTimeField(help_text="Exact timestamp of execution")
    
    # Liquidity and venue
    liquidity = models.CharField(
        max_length=20,
        choices=[
            ('MAKER', 'Maker'),
            ('TAKER', 'Taker'),
            ('UNKNOWN', 'Unknown'),
        ],
        default='UNKNOWN',
        help_text="Whether order provided or took liquidity"
    )
    
    execution_venue = models.CharField(max_length=100, blank=True, help_text="Exchange or venue where executed")
    
    # Partial fill info
    is_partial_fill = models.BooleanField(default=False, help_text="True if this is a partial fill")
    remaining_quantity = models.DecimalField(max_digits=20, decimal_places=6, default=0, help_text="Quantity remaining to be filled")
    
    # Market conditions
    bid_price_at_execution = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    ask_price_at_execution = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'order_executions'
        ordering = ['-execution_timestamp']
        indexes = [
            models.Index(fields=['trade', 'execution_timestamp']),
            models.Index(fields=['asset', 'execution_timestamp']),
            models.Index(fields=['execution_reference']),
            models.Index(fields=['execution_timestamp']),
        ]
    
    def __str__(self):
        return f"Execution {self.execution_reference}: {self.fill_quantity} {self.asset.symbol} @ {self.fill_price}"
    
    def calculate_slippage(self, expected_price):
        """Calculate slippage as percentage difference from expected price."""
        if not expected_price or expected_price == 0:
            return 0
        
        actual_price = float(self.fill_price)
        expected = float(expected_price)
        
        slippage = ((actual_price - expected) / expected) * 100
        return slippage
```

---

## 🚀 IMPLEMENTATION STEPS

### **Phase 1: Create Models** (4 hours)

1. **Create Trade model**
   - File: `apps/backend/src/trading/models/trade.py`
   - Use correct base classes (UUIDModel, TimestampedModel, SoftDeleteModel)
   - Add all fields from spec above
   - Add indexes for performance
   - Implement profit/loss calculation methods

2. **Create OrderExecution model**
   - File: `apps/backend/src/trading/models/order_execution.py`
   - ForeignKey relationship to Trade
   - Track partial fills and detailed execution info
   - Add slippage calculation method

### **Phase 2: Create Migrations** (1 hour)

```bash
cd apps/backend
python manage.py makemigrations trading
python manage.py migrate
```

### **Phase 3: Create Model Admin** (1 hour)

**File:** `apps/backend/src/trading/admin/trading_admin.py`

```python
from django.contrib import admin
from trading.models.trade import Trade
from trading.models.order_execution import OrderExecution

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['trade_reference', 'portfolio', 'asset', 'side', 'quantity', 'price', 'execution_date', 'status']
    list_filter = ['side', 'status', 'trade_type', 'execution_date']
    search_fields = ['trade_reference', 'asset__symbol', 'portfolio__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OrderExecution)
class OrderExecutionAdmin(admin.ModelAdmin):
    list_display = ['execution_reference', 'trade', 'fill_quantity', 'fill_price', 'execution_timestamp', 'is_partial_fill']
    list_filter = ['is_partial_fill', 'execution_timestamp', 'liquidity']
    search_fields = ['execution_reference', 'broker_execution_id']
    readonly_fields = ['created_at', 'updated_at']
```

### **Phase 4: Write Tests** (4 hours)

**File:** `apps/backend/src/trading/tests/test_trading_models.py`

```python
from django.test import TestCase
from trading.models import Trade, OrderExecution
from investments.models import Portfolio, Asset
from django.contrib.auth.models import User
from decimal import Decimal

class TradeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.portfolio = Portfolio.objects.create(name='Test Portfolio', user=self.user)
        self.asset = Asset.objects.create(symbol='AAPL', name='Apple Inc.')
    
    def test_trade_creation_with_inheritance(self):
        """Test trade creation with correct base class inheritance."""
        trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            user=self.user,
            trade_reference='TRD-001',
            side='BUY',
            quantity=Decimal('100'),
            price=Decimal('150.00'),
            gross_amount=Decimal('15000.00'),
            commission=Decimal('10.00'),
            net_amount=Decimal('15010.00'),
            order_date='2026-01-30',
            execution_date='2026-01-30'
        )
        
        # Check base class fields
        self.assertIsNotNone(trade.id)
        self.assertIsNotNone(trade.created_at)
        self.assertIsNotNone(trade.updated_at)
        self.assertFalse(trade.is_deleted)
        
        # Check trade fields
        self.assertEqual(trade.side, 'BUY')
        self.assertEqual(trade.quantity, Decimal('100'))
    
    def test_profit_loss_calculation(self):
        """Test profit/loss calculation for sell trade."""
        # Create buy trade
        buy_trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            user=self.user,
            trade_reference='TRD-001',
            side='BUY',
            quantity=Decimal('100'),
            price=Decimal('150.00'),
            gross_amount=Decimal('15000.00'),
            commission=Decimal('10.00'),
            net_amount=Decimal('15010.00'),
            order_date='2026-01-29',
            execution_date='2026-01-29'
        )
        
        # Create sell trade
        sell_trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            user=self.user,
            trade_reference='TRD-002',
            side='SELL',
            quantity=Decimal('100'),
            price=Decimal('160.00'),
            gross_amount=Decimal('16000.00'),
            commission=Decimal('10.00'),
            net_amount=Decimal('15990.00'),
            order_date='2026-01-30',
            execution_date='2026-01-30'
        )
        
        pnl = sell_trade.calculate_profit_loss()
        expected_pnl = 15990.00 - 15010.00  # Sell proceeds - Buy cost
        self.assertAlmostEqual(float(pnl), expected_pnl, places=2)
    
    def test_return_percentage_calculation(self):
        """Test return percentage calculation."""
        # Create buy and sell trades
        buy_trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            user=self.user,
            trade_reference='TRD-001',
            side='BUY',
            quantity=Decimal('100'),
            price=Decimal('150.00'),
            gross_amount=Decimal('15000.00'),
            commission=Decimal('10.00'),
            net_amount=Decimal('15010.00'),
            order_date='2026-01-29',
            execution_date='2026-01-29'
        )
        
        sell_trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            user=self.user,
            trade_reference='TRD-002',
            side='SELL',
            quantity=Decimal('100'),
            price=Decimal('165.00'),
            gross_amount=Decimal('16500.00'),
            commission=Decimal('10.00'),
            net_amount=Decimal('16490.00'),
            order_date='2026-01-30',
            execution_date='2026-01-30'
        )
        
        return_pct = sell_trade.calculate_return_percentage()
        expected_return = ((16490.00 - 15010.00) / 15010.00) * 100
        self.assertAlmostEqual(float(return_pct), expected_return, places=2)

class OrderExecutionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.portfolio = Portfolio.objects.create(name='Test Portfolio', user=self.user)
        self.asset = Asset.objects.create(symbol='AAPL', name='Apple Inc.')
        
        self.trade = Trade.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            user=self.user,
            trade_reference='TRD-001',
            side='BUY',
            quantity=Decimal('100'),
            price=Decimal('150.00'),
            gross_amount=Decimal('15000.00'),
            commission=Decimal('10.00'),
            net_amount=Decimal('15010.00'),
            order_date='2026-01-30',
            execution_date='2026-01-30'
        )
    
    def test_execution_creation_with_inheritance(self):
        """Test execution creation with correct base class inheritance."""
        execution = OrderExecution.objects.create(
            trade=self.trade,
            asset=self.asset,
            user=self.user,
            execution_reference='EXE-001',
            fill_quantity=Decimal('50'),
            fill_price=Decimal('150.25'),
            fill_amount=Decimal('7512.50'),
            execution_timestamp='2026-01-30 10:30:00'
        )
        
        # Check base class fields
        self.assertIsNotNone(execution.id)
        self.assertIsNotNone(execution.created_at)
        self.assertIsNotNone(execution.updated_at)
        self.assertFalse(execution.is_deleted)
    
    def test_partial_fill_tracking(self):
        """Test partial fill tracking."""
        execution = OrderExecution.objects.create(
            trade=self.trade,
            asset=self.asset,
            user=self.user,
            execution_reference='EXE-001',
            fill_quantity=Decimal('50'),
            fill_price=Decimal('150.25'),
            fill_amount=Decimal('7512.50'),
            execution_timestamp='2026-01-30 10:30:00',
            is_partial_fill=True,
            remaining_quantity=Decimal('50')
        )
        
        self.assertTrue(execution.is_partial_fill)
        self.assertEqual(execution.remaining_quantity, Decimal('50'))
    
    def test_slippage_calculation(self):
        """Test slippage calculation."""
        execution = OrderExecution.objects.create(
            trade=self.trade,
            asset=self.asset,
            user=self.user,
            execution_reference='EXE-001',
            fill_quantity=Decimal('100'),
            fill_price=Decimal('150.50'),
            fill_amount=Decimal('15050.00'),
            execution_timestamp='2026-01-30 10:30:00'
        )
        
        expected_price = Decimal('150.00')
        slippage = execution.calculate_slippage(expected_price)
        
        # (150.50 - 150.00) / 150.00 * 100 = 0.333%
        expected_slippage = ((150.50 - 150.00) / 150.00) * 100
        self.assertAlmostEqual(float(slippage), expected_slippage, places=2)
```

### **Phase 5: API Endpoints** (2 hours)

**File:** `apps/backend/src/api/trading_models.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from trading.models import Trade, OrderExecution
from django.db.models import Sum, Q

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def trades(request, portfolio_id):
    """Get all trades or create a new trade."""
    if request.method == 'GET':
        trades = Trade.objects.filter(
            portfolio_id=portfolio_id,
            is_deleted=False
        ).order_by('-execution_date', '-execution_time')
        
        data = [{
            'id': trade.id,
            'trade_reference': trade.trade_reference,
            'asset': trade.asset.symbol,
            'side': trade.side,
            'quantity': float(trade.quantity),
            'price': float(trade.price),
            'net_amount': float(trade.net_amount),
            'execution_date': str(trade.execution_date),
            'status': trade.status,
            'profit_loss': float(trade.calculate_profit_loss()) if trade.side == 'SELL' else 0,
            'return_percentage': float(trade.calculate_return_percentage()) if trade.side == 'SELL' else 0
        } for trade in trades]
        
        return Response(data)
    
    elif request.method == 'POST':
        from datetime import datetime
        import uuid
        
        trade = Trade.objects.create(
            portfolio_id=portfolio_id,
            trade_reference=f"TRD-{uuid.uuid4().hex[:8].upper()}",
            **request.data
        )
        
        return Response({
            'id': trade.id,
            'trade_reference': trade.trade_reference
        }, status=201)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def trade_detail(request, portfolio_id, trade_id):
    """Get, update, or soft delete a specific trade."""
    try:
        trade = Trade.objects.get(id=trade_id, portfolio_id=portfolio_id, is_deleted=False)
    except Trade.DoesNotExist:
        return Response({'error': 'Trade not found'}, status=404)
    
    if request.method == 'GET':
        return Response({
            'id': trade.id,
            'trade_reference': trade.trade_reference,
            'asset': trade.asset.symbol,
            'side': trade.side,
            'quantity': float(trade.quantity),
            'price': float(trade.price),
            'gross_amount': float(trade.gross_amount),
            'commission': float(trade.commission),
            'net_amount': float(trade.net_amount),
            'trade_type': trade.trade_type,
            'status': trade.status,
            'order_date': str(trade.order_date),
            'execution_date': str(trade.execution_date),
            'execution_time': str(trade.execution_time) if trade.execution_time else None,
            'broker': trade.broker,
            'order_id': trade.order_id,
            'notes': trade.notes,
            'profit_loss': float(trade.calculate_profit_loss()) if trade.side == 'SELL' else 0,
            'return_percentage': float(trade.calculate_return_percentage()) if trade.side == 'SELL' else 0
        })
    
    elif request.method == 'PUT':
        for field, value in request.data.items():
            setattr(trade, field, value)
        trade.save()
        return Response({'status': 'updated'})
    
    elif request.method == 'DELETE':
        trade.soft_delete()
        return Response({'status': 'deleted'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trade_executions(request, trade_id):
    """Get all executions for a specific trade."""
    executions = OrderExecution.objects.filter(
        trade_id=trade_id,
        is_deleted=False
    ).order_by('-execution_timestamp')
    
    data = [{
        'id': exe.id,
        'execution_reference': exe.execution_reference,
        'fill_quantity': float(exe.fill_quantity),
        'fill_price': float(exe.fill_price),
        'fill_amount': float(exe.fill_amount),
        'commission': float(exe.commission),
        'execution_timestamp': str(exe.execution_timestamp),
        'is_partial_fill': exe.is_partial_fill,
        'remaining_quantity': float(exe.remaining_quantity),
        'liquidity': exe.liquidity,
        'execution_venue': exe.execution_venue
    } for exe in executions]
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trading_summary(request, portfolio_id):
    """Get trading summary statistics for a portfolio."""
    from django.db.models import Count, Sum, F
    
    trades = Trade.objects.filter(
        portfolio_id=portfolio_id,
        is_deleted=False,
        status='FILLED'
    )
    
    buy_trades = trades.filter(side='BUY')
    sell_trades = trades.filter(side='SELL')
    
    total_buy_amount = buy_trades.aggregate(Sum('net_amount'))['net_amount__sum'] or 0
    total_sell_amount = sell_trades.aggregate(Sum('net_amount'))['net_amount__sum] or 0
    
    total_realized_pnl = sum([t.calculate_profit_loss() for t in sell_trades])
    
    return Response({
        'total_trades': trades.count(),
        'buy_trades': buy_trades.count(),
        'sell_trades': sell_trades.count(),
        'total_buy_amount': float(total_buy_amount),
        'total_sell_amount': float(total_sell_amount),
        'total_realized_pnl': float(total_realized_pnl),
        'total_commission': float(trades.aggregate(Sum('commission'))['commission__sum'] or 0)
    })
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Both models created with correct base class inheritance (UUIDModel, TimestampedModel, SoftDeleteModel)
- [ ] Migrations created and applied successfully
- [ ] Model admin registered for both models
- [ ] Unit tests pass (test inheritance, fields, methods, P&L calculations)
- [ ] API endpoints functional
- [ ] Documentation complete

---

## 📋 DELIVERABLES

- [ ] 2 model files created (trade.py, order_execution.py)
- [ ] Migration files generated
- [ ] Model admin configured
- [ ] Unit tests written and passing
- [ ] API endpoints implemented
- [ ] API documentation updated

---

**Created:** January 30, 2026  
**Created By:** GAUDÍ (Architect)  
**Assigned To:** Backend Coder (DevOps supervision)  
**Priority:** P1 - HIGH  
**Estimate:** 12 hours (1.5 days)
