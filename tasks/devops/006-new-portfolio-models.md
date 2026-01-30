# Task D-006: Portfolio Management Models

**Assigned To:** Backend Coder (DevOps supervision)  
**Created By:** GAUDÍ (Architect)  
**Priority:** P1 - HIGH  
**Time Estimate:** 2.5 days (20 hours)  
**Dependencies:** D-002 (Database Migrations)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive portfolio management models with proper inheritance (UUIDModel, TimestampedModel, SoftDeleteModel).

---

## ⚠️ CRITICAL REMINDER

**ALL MODELS MUST INHERIT FROM:**
- `UUIDModel` - Provides UUID primary key
- `TimestampedModel` - Provides created_at, updated_at
- `SoftDeleteModel` - Provides soft delete functionality

**DO NOT create models without these base classes!**

---

## 📋 MODELS TO IMPLEMENT

### **1. TaxLot Model**

**File:** `apps/backend/src/investments/models/tax_lot.py`

**Purpose:** Track tax lots for cost basis tracking (FIFO, LIFO, specific lot)

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
from investments.models.portfolio import Portfolio
from investments.models.asset import Asset

class TaxLot(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Tax lot for tracking cost basis and gains/losses.
    Supports FIFO, LIFO, and specific lot identification methods.
    """
    
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='tax_lots'
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='tax_lots'
    )
    
    # Lot identification
    lot_number = models.IntegerField(help_text="Lot sequence number")
    acquisition_date = models.DateField(help_text="Date asset acquired")
    
    # Quantity and cost
    quantity = models.DecimalField(max_digits=20, decimal_places=6, help_text="Remaining quantity in lot")
    original_quantity = models.DecimalField(max_digits=20, decimal_places=6, help_text="Original quantity acquired")
    
    # Cost basis
    cost_per_share = models.DecimalField(max_digits=10, decimal_places=4, help_text="Cost per share (including commissions)")
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, help_text="Total cost basis")
    
    # Adjustments
    wash_sale_loss = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Disallowed wash sale loss")
    adjusted_cost = models.DecimalField(max_digits=20, decimal_places=2, help_text="Adjusted cost after wash sales")
    
    # Status
    is_open = models.BooleanField(default=True, help_text="True if lot has remaining quantity")
    close_date = models.DateField(null=True, blank=True, help_text="Date lot was fully closed")
    
    class Meta:
        db_table = 'tax_lots'
        unique_together = ['portfolio', 'asset', 'lot_number']
        ordering = ['acquisition_date', 'lot_number']
        indexes = [
            models.Index(fields=['portfolio', 'asset']),
            models.Index(fields=['is_open']),
            models.Index(fields=['acquisition_date']),
        ]
    
    def __str__(self):
        return f"TaxLot {self.lot_number}: {self.asset.symbol} - {self.quantity} shares"
    
    def calculate_unrealized_gain_loss(self, current_price):
        """Calculate unrealized gain/loss at current price."""
        if not self.is_open:
            return 0
        current_value = float(self.quantity) * float(current_price)
        cost_basis = float(self.quantity) * float(self.cost_per_share)
        return current_value - cost_basis
```

---

### **2. RebalancingRule Model**

**File:** `apps/backend/src/investments/models/rebalancing_rule.py`

**Purpose:** Store target allocations and rebalancing parameters for portfolios.

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
from investments.models.portfolio import Portfolio

class RebalancingRule(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Rebalancing rules for portfolio target allocations.
    Defines target percentages and drift tolerances.
    """
    
    portfolio = models.OneToOneField(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='rebalancing_rule'
    )
    
    # Asset allocation targets
    target_allocation_stocks = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=60,
        help_text="Target % for stocks"
    )
    target_allocation_bonds = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=30,
        help_text="Target % for bonds"
    )
    target_allocation_crypto = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=5,
        help_text="Target % for crypto"
    )
    target_allocation_cash = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=5,
        help_text="Target % for cash"
    )
    
    # Drift tolerance
    drift_tolerance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=5,
        help_text="Allowed drift before rebalancing (e.g., 5 = 5%)"
    )
    
    # Rebalancing settings
    rebalance_frequency = models.CharField(
        max_length=20,
        choices=[
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly'),
            ('QUARTERLY', 'Quarterly'),
            ('MANUAL', 'Manual only'),
            ('DRIFT_BASED', 'When drift exceeds tolerance'),
        ],
        default='MONTHLY'
    )
    
    last_rebalance_date = models.DateField(null=True, blank=True)
    next_rebalance_date = models.DateField(null=True, blank=True)
    
    # Rebalancing method
    rebalancing_method = models.CharField(
        max_length=20,
        choices=[
            ('SELL_BUY', 'Sell oversold then buy underweight'),
            ('BUY_SELL', 'Buy underweight then sell overweight'),
            ('MINIMIZE_TRADES', 'Minimize number of trades'),
            ('TAX_EFFICIENT', 'Maximize tax loss harvesting'),
        ],
        default='MINIMIZE_TRADES'
    )
    
    # Notifications
    notify_on_drift = models.BooleanField(default=True)
    drift_notification_threshold = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=5,
        help_text="Notify when drift exceeds this %"
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'rebalancing_rules'
        verbose_name = 'Rebalancing Rule'
        verbose_name_plural = 'Rebalancing Rules'
    
    def __str__(self):
        return f"{self.portfolio.name} Rebalancing Rule"
    
    def check_drift(self, current_allocation):
        """Check if current allocation exceeds drift tolerance."""
        drifts = {}
        tolerance = float(self.drift_tolerance_percentage)
        
        for asset_type in ['stocks', 'bonds', 'crypto', 'cash']:
            target = getattr(self, f'target_allocation_{asset_type}')
            current = current_allocation.get(asset_type, 0)
            drift = abs(float(current) - float(target))
            
            if drift > tolerance:
                drifts[asset_type] = {
                    'target': target,
                    'current': current,
                    'drift': drift
                }
        
        return drifts
```

---

### **3. PortfolioAllocation Model**

**File:** `apps/backend/src/investments/models/portfolio_allocation.py`

**Purpose:** Track actual portfolio allocations over time for analytics.

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel
from investments.models.portfolio import Portfolio

class PortfolioAllocation(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Historical snapshot of portfolio allocations.
    Used for analytics and performance tracking.
    """
    
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    
    # Snapshot date
    snapshot_date = models.DateField(help_text="Date of allocation snapshot")
    snapshot_time = models.TimeField(help_text="Time of snapshot")
    
    # Asset class allocations (percentages)
    allocation_stocks = models.DecimalField(max_digits=5, decimal_places=2)
    allocation_bonds = models.DecimalField(max_digits=5, decimal_digits=2)
    allocation_crypto = models.DecimalField(max_digits=5, decimal_places=2)
    allocation_cash = models.DecimalField(max_digits=5, decimal_places=2)
    allocation_other = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Sector breakdown (if available)
    sector_breakdown = models.JSONField(default=dict, help_text="Sector allocations")
    
    # Geographic breakdown
    geographic_breakdown = models.JSONField(default=dict, help_text="Country/region allocations")
    
    # Total value at snapshot
    total_value = models.DecimalField(max_digits=20, decimal_places=2)
    
    class Meta:
        db_table = 'portfolio_allocations'
        unique_together = ['portfolio', 'snapshot_date', 'snapshot_time']
        ordering = ['-snapshot_date', '-snapshot_time']
        indexes = [
            models.Index(fields=['portfolio', 'snapshot_date']),
            models.Index(fields=['snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} Allocation - {self.snapshot_date}"
    
    @classmethod
    def create_snapshot(cls, portfolio):
        """Create allocation snapshot from current portfolio state."""
        from datetime import date, datetime
        
        # Calculate current allocations
        total_value = portfolio.current_value
        positions = portfolio.positions.all()
        
        allocations = {'stocks': 0, 'bonds': 0, 'crypto': 0, 'cash': 0, 'other': 0}
        
        for position in positions:
            asset_type = position.asset.asset_type
            value = float(position.current_value)
            percentage = (value / float(total_value) * 100) if total_value > 0 else 0
            
            if asset_type in allocations:
                allocations[asset_type] += percentage
            else:
                allocations['other'] += percentage
        
        # Create snapshot
        snapshot = cls.objects.create(
            portfolio=portfolio,
            snapshot_date=date.today(),
            snapshot_time=datetime.now().time(),
            allocation_stocks=allocations['stocks'],
            allocation_bonds=allocations['bonds'],
            allocation_crypto=allocations['crypto'],
            allocation_cash=allocations['cash'],
            allocation_other=allocations['other'],
            total_value=total_value
        )
        
        return snapshot
```

---

## 🚀 IMPLEMENTATION STEPS

### **Phase 1: Create Models** (6 hours)

1. **Create TaxLot model**
   - File: `apps/backend/src/investments/models/tax_lot.py`
   - Use correct base classes
   - Add all fields from spec above
   - Add indexes for performance

2. **Create RebalancingRule model**
   - File: `apps/backend/src/investments/models/rebalancing_rule.py`
   - OneToOne relationship with Portfolio
   - Add drift tolerance fields

3. **Create PortfolioAllocation model**
   - File: `apps/backend/src/investments/models/portfolio_allocation.py`
   - Historical tracking
   - Snapshot creation method

### **Phase 2: Create Migrations** (2 hours)

```bash
cd apps/backend
python manage.py makemigrations investments
python manage.py migrate
```

### **Phase 3: Create Model Admin** (2 hours)

**File:** `apps/backend/src/investments/admin/portfolio_admin.py`

```python
from django.contrib import admin
from investments.models.tax_lot import TaxLot
from investments.models.rebalancing_rule import RebalancingRule
from investments.models.portfolio_allocation import PortfolioAllocation

@admin.register(TaxLot)
class TaxLotAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'asset', 'lot_number', 'quantity', 'is_open', 'acquisition_date']
    list_filter = ['is_open', 'acquisition_date']
    search_fields = ['portfolio__name', 'asset__symbol']

@admin.register(RebalancingRule)
class RebalancingRuleAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'rebalance_frequency', 'drift_tolerance_percentage', 'is_active']

@admin.register(PortfolioAllocation)
class PortfolioAllocationAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'snapshot_date', 'total_value']
    list_filter = ['snapshot_date']
    readonly_fields = ['snapshot_date', 'snapshot_time']
```

### **Phase 4: Write Tests** (6 hours)

**File:** `apps/backend/src/investments/tests/test_portfolio_models.py`

```python
from django.test import TestCase
from investments.models import Portfolio, TaxLot, RebalancingRule, PortfolioAllocation
from investments.models.asset import Asset
from django.contrib.auth.models import User

class TaxLotTest(TestCase):
    def test_create_tax_lot(self):
        """Test tax lot creation with correct inheritance."""
        lot = TaxLot.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            lot_number=1,
            acquisition_date='2026-01-01',
            quantity=100,
            original_quantity=100,
            cost_per_share=150.00,
            total_cost=15000.00
        )
        
        # Check base class fields
        self.assertIsNotNone(lot.id)
        self.assertIsNotNone(lot.created_at)
        self.assertIsNotNone(lot.updated_at)
        self.assertFalse(lot.is_deleted)
    
    def test_tax_lot_gain_loss_calculation(self):
        """Test unrealized gain/loss calculation."""
        # Test calculation logic
        pass

class RebalancingRuleTest(TestCase):
    def test_rebalancing_rule_creation(self):
        """Test rebalancing rule with correct inheritance."""
        rule = RebalancingRule.objects.create(
            portfolio=self.portfolio,
            target_allocation_stocks=60,
            target_allocation_bonds=30,
            target_allocation_crypto=5,
            target_allocation_cash=5
        )
        
        # Check base class fields
        self.assertIsNotNone(rule.id)
        self.assertIsNotNone(rule.created_at)
        self.assertIsNotNone(rule.updated_at)
    
    def test_drift_detection(self):
        """Test drift detection logic."""
        # Create rebalancing rule
        rule = RebalancingRule.objects.create(
            portfolio=self.portfolio,
            drift_tolerance_percentage=5
        )
        
        # Test drift calculation
        current = {'stocks': 70, 'bonds': 25, 'crypto': 3, 'cash': 2}
        drifts = rule.check_drift(current)
        
        self.assertIn('stocks', drifts)
        self.assertEqual(drifts['stocks']['drift'], 10)

class PortfolioAllocationTest(TestCase):
    def test_allocation_snapshot_creation(self):
        """Test creating allocation snapshot."""
        # Create snapshot from portfolio
        snapshot = PortfolioAllocation.create_snapshot(self.portfolio)
        
        # Verify base class fields
        self.assertIsNotNone(snapshot.id)
        self.assertIsNotNone(snapshot.created_at)
        self.assertIsNotNone(snapshot.updated_at)
        
        # Verify allocations sum to 100
        total = (
            snapshot.allocation_stocks +
            snapshot.allocation_bonds +
            snapshot.allocation_crypto +
            snapshot.allocation_cash +
            snapshot.allocation_other
        )
        self.assertAlmostEqual(float(total), 100.0, places=2)
```

### **Phase 5: API Endpoints** (4 hours)

**File:** `apps/backend/src/api/portfolio_models.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.models import TaxLot, RebalancingRule, PortfolioAllocation

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tax_lots(request, portfolio_id):
    """Get all tax lots for a portfolio."""
    lots = TaxLot.objects.filter(portfolio_id=portfolio_id, is_open=True)
    data = [{
        'id': lot.id,
        'asset': lot.asset.symbol,
        'lot_number': lot.lot_number,
        'quantity': float(lot.quantity),
        'cost_per_share': float(lot.cost_per_share),
        'total_cost': float(lot.total_cost),
        'acquisition_date': lot.acquisition_date
    } for lot in lots]
    return Response(data)

@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def rebalancing_rule(request, portfolio_id):
    """Get or update rebalancing rule."""
    if request.method == 'GET':
        try:
            rule = RebalancingRule.objects.get(portfolio_id=portfolio_id)
            return Response({
                'target_allocation_stocks': float(rule.target_allocation_stocks),
                'target_allocation_bonds': float(rule.target_allocation_bonds),
                'drift_tolerance_percentage': float(rule.drift_tolerance_percentage),
                'rebalance_frequency': rule.rebalance_frequency
            })
        except RebalancingRule.DoesNotExist:
            return Response({}, status=404)
    
    elif request.method == 'POST':
        rule = RebalancingRule.objects.create(
            portfolio_id=portfolio_id,
            **request.data
        )
        return Response({'id': rule.id}, status=201)
    
    elif request.method == 'PUT':
        rule = RebalancingRule.objects.get(portfolio_id=portfolio_id)
        for field, value in request.data.items():
            setattr(rule, field, value)
        rule.save()
        return Response({'status': 'updated'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_allocations(request, portfolio_id):
    """Get historical allocation snapshots."""
    allocations = PortfolioAllocation.objects.filter(
        portfolio_id=portfolio_id
    ).order_by('-snapshot_date')[:100]
    
    data = [{
        'date': str(alloc.snapshot_date),
        'stocks': float(alloc.allocation_stocks),
        'bonds': float(alloc.allocation_bonds),
        'crypto': float(alloc.allocation_crypto),
        'cash': float(alloc.allocation_cash),
        'total_value': float(alloc.total_value)
    } for alloc in allocations]
    
    return Response(data)
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] All 3 models created with correct base class inheritance
- [ ] Migrations created and applied successfully
- [ ] Model admin registered for all 3 models
- [ ] Unit tests pass (test inheritance, fields, methods)
- [ ] API endpoints functional
- [ ] Documentation complete

---

## 📋 DELIVERABLES

- [ ] 3 model files created (tax_lot.py, rebalancing_rule.py, portfolio_allocation.py)
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
**Estimate:** 20 hours (2.5 days)
