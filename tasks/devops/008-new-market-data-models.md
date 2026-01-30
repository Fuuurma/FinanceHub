# Task D-008: Market Data Models

**Assigned To:** Backend Coder (DevOps supervision)  
**Created By:** GAUDÍ (Architect)  
**Priority:** P2 - MEDIUM  
**Time Estimate:** 1 day (8 hours)  
**Dependencies:** D-002 (Database Migrations)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement market data models with proper inheritance (UUIDModel, TimestampedModel, SoftDeleteModel) for tracking screener criteria and market indices.

---

## ⚠️ CRITICAL REMINDER

**ALL MODELS MUST INHERIT FROM:**
- `UUIDModel` - Provides UUID primary key
- `TimestampedModel` - Provides created_at, updated_at
- `SoftDeleteModel` - Provides soft delete functionality

**DO NOT create models without these base classes!**

---

## 📋 MODELS TO IMPLEMENT

### **1. ScreenerCriteria Model**

**File:** `apps/backend/src/investments/models/screener_criteria.py`

**Purpose:** Store custom stock screener criteria for filtering and discovering investment opportunities.

```python
from django.db import models
from django.contrib.auth.models import User
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel

class ScreenerCriteria(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Custom screener criteria for filtering stocks.
    Users can save and reuse screening criteria.
    """
    
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='screener_criteria'
    )
    
    # Screener identification
    name = models.CharField(max_length=200, help_text="Name of this screener")
    description = models.TextField(blank=True, help_text="Description of screening strategy")
    
    # Market cap filter
    market_cap_min = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum market cap (in billions)"
    )
    market_cap_max = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum market cap (in billions)"
    )
    
    # Valuation metrics
    pe_ratio_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum P/E ratio"
    )
    pe_ratio_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum P/E ratio"
    )
    
    pb_ratio_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum P/B ratio"
    )
    pb_ratio_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum P/B ratio"
    )
    
    ps_ratio_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum P/S ratio"
    )
    ps_ratio_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum P/S ratio"
    )
    
    ev_ebitda_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum EV/EBITDA ratio"
    )
    ev_ebitda_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum EV/EBITDA ratio"
    )
    
    # Dividend filters
    dividend_yield_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum dividend yield (%)"
    )
    dividend_yield_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum dividend yield (%)"
    )
    
    # Growth metrics
    revenue_growth_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum revenue growth rate (%)"
    )
    earnings_growth_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum earnings growth rate (%)"
    )
    
    # Profitability
    roe_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum return on equity (%)"
    )
    roa_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum return on assets (%)"
    )
    profit_margin_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum profit margin (%)"
    )
    
    # Financial health
    debt_to_equity_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum debt-to-equity ratio"
    )
    current_ratio_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum current ratio"
    )
    
    # Price filters
    price_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum stock price"
    )
    price_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum stock price"
    )
    
    # Volume filters
    avg_volume_min = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum average daily volume"
    )
    
    # Sector and industry filters
    sectors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of sectors to include"
    )
    industries = models.JSONField(
        default=list,
        blank=True,
        help_text="List of industries to include"
    )
    
    # Exchange filter
    exchanges = models.JSONField(
        default=list,
        blank=True,
        help_text="List of exchanges (NYSE, NASDAQ, etc.)"
    )
    
    # Technical indicators
    sma_50_above = models.BooleanField(
        default=False,
        help_text="Price above 50-day SMA"
    )
    sma_200_above = models.BooleanField(
        default=False,
        help_text="Price above 200-day SMA"
    )
    rsi_oversold = models.BooleanField(
        default=False,
        help_text="RSI < 30 (oversold)"
    )
    rsi_overbought = models.BooleanField(
        default=False,
        help_text="RSI > 70 (overbought)"
    )
    
    # Analyst ratings
    analyst_rating_min = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum analyst rating (1-5 scale)"
    )
    
    # Sort options
    sort_by = models.CharField(
        max_length=50,
        default='market_cap',
        help_text="Field to sort results by"
    )
    sort_order = models.CharField(
        max_length=10,
        choices=[('ASC', 'Ascending'), ('DESC', 'Descending')],
        default='DESC'
    )
    
    # Limit
    max_results = models.IntegerField(default=100, help_text="Maximum number of results")
    
    # Favorite
    is_favorite = models.BooleanField(default=False, help_text="Mark as favorite screener")
    
    class Meta:
        db_table = 'screener_criteria'
        ordering = ['-is_favorite', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name}"
    
    def to_query_dict(self):
        """Convert screener criteria to query dictionary."""
        return {
            'market_cap': {
                'min': float(self.market_cap_min) if self.market_cap_min else None,
                'max': float(self.market_cap_max) if self.market_cap_max else None
            },
            'pe_ratio': {
                'min': float(self.pe_ratio_min) if self.pe_ratio_min else None,
                'max': float(self.pe_ratio_max) if self.pe_ratio_max else None
            },
            'pb_ratio': {
                'min': float(self.pb_ratio_min) if self.pb_ratio_min else None,
                'max': float(self.pb_ratio_max) if self.pb_ratio_max else None
            },
            'dividend_yield': {
                'min': float(self.dividend_yield_min) if self.dividend_yield_min else None,
                'max': float(self.dividend_yield_max) if self.dividend_yield_max else None
            },
            'revenue_growth': {
                'min': float(self.revenue_growth_min) if self.revenue_growth_min else None
            },
            'earnings_growth': {
                'min': float(self.earnings_growth_min) if self.earnings_growth_min else None
            },
            'roe': {
                'min': float(self.roe_min) if self.roe_min else None
            },
            'debt_to_equity': {
                'max': float(self.debt_to_equity_max) if self.debt_to_equity_max else None
            },
            'sectors': self.sectors,
            'industries': self.industries,
            'exchanges': self.exchanges,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order,
            'max_results': self.max_results
        }
```

---

### **2. MarketIndex Model**

**File:** `apps/backend/src/assets/models/market_index.py`

**Purpose:** Track market indices (S&P 500, NASDAQ, Dow Jones, etc.) for benchmarking and analysis.

```python
from django.db import models
from utils.helpers.uuid_model import UUIDModel
from utils.helpers.timestamped_model import TimestampedModel
from utils.helpers.soft_delete_model import SoftDeleteModel

class MarketIndex(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Market indices tracking (S&P 500, NASDAQ, Dow Jones, etc.).
    Used for benchmarking portfolio performance.
    """
    
    # Index identification
    symbol = models.CharField(
        max_length=20,
        unique=True,
        help_text="Index symbol (e.g., SPX, NDX, DJI)"
    )
    name = models.CharField(max_length=200, help_text="Index name")
    
    # Index details
    description = models.TextField(blank=True, help_text="Index description")
    country = models.CharField(max_length=5, default='US', help_text="Country code")
    exchange = models.CharField(max_length=100, blank=True, help_text="Exchange name")
    
    # Index type
    index_type = models.CharField(
        max_length=50,
        choices=[
            ('BROAD_MARKET', 'Broad Market'),
            ('SECTOR', 'Sector'),
            ('INDUSTRY', 'Industry'),
            ('STYLE', 'Style'),
            ('COMMODITY', 'Commodity'),
            ('BOND', 'Bond'),
            ('CURRENCY', 'Currency'),
            ('OTHER', 'Other'),
        ],
        default='BROAD_MARKET'
    )
    
    # Current data
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Current index value"
    )
    previous_close = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Previous close value"
    )
    
    # Daily change
    daily_change = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Daily change in points"
    )
    daily_change_percent = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Daily change percentage"
    )
    
    # Period ranges
    day_high = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Day high"
    )
    day_low = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Day low"
    )
    
    week_52_high = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="52-week high"
    )
    week_52_low = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="52-week low"
    )
    
    # Volume
    volume = models.BigIntegerField(null=True, blank=True, help_text="Trading volume")
    avg_volume = models.BigIntegerField(null=True, blank=True, help_text="Average daily volume")
    
    # Market cap (for total market indices)
    total_market_cap = models.DecimalField(
        max_digits=25,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total market cap of index"
    )
    
    # Dividend and earnings data
    dividend_yield = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Index dividend yield (%)"
    )
    pe_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Index P/E ratio"
    )
    
    # Last updated
    last_updated = models.DateTimeField(null=True, blank=True, help_text="Last data update timestamp")
    
    # Active status
    is_active = models.BooleanField(default=True, help_text="Whether index is actively tracked")
    
    class Meta:
        db_table = 'market_indices'
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['index_type']),
            models.Index(fields=['country']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-last_updated']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    def calculate_daily_change(self):
        """Calculate daily change and percentage."""
        if self.current_value and self.previous_close:
            self.daily_change = self.current_value - self.previous_close
            if self.previous_close != 0:
                self.daily_change_percent = (self.daily_change / self.previous_close) * 100
            else:
                self.daily_change_percent = 0
        return self.daily_change, self.daily_change_percent
    
    def calculate_period_return(self, start_value):
        """
        Calculate return percentage from a starting value.
        Useful for calculating YTD, 1-year, etc. returns.
        """
        if not start_value or not self.current_value or start_value == 0:
            return 0
        
        return ((float(self.current_value) - float(start_value)) / float(start_value)) * 100
    
    def is_near_52_week_high(self, threshold_percent=2.0):
        """Check if current value is within threshold_percent of 52-week high."""
        if not self.current_value or not self.week_52_high:
            return False
        
        threshold = float(self.week_52_high) * (threshold_percent / 100)
        return float(self.current_value) >= (float(self.week_52_high) - threshold)
    
    def is_near_52_week_low(self, threshold_percent=2.0):
        """Check if current value is within threshold_percent of 52-week low."""
        if not self.current_value or not self.week_52_low:
            return False
        
        threshold = float(self.week_52_low) * (threshold_percent / 100)
        return float(self.current_value) <= (float(self.week_52_low) + threshold)
    
    def update_from_api_data(self, api_data):
        """
        Update index data from API response.
        
        Expected API data format:
        {
            'value': 4500.25,
            'previous_close': 4480.50,
            'high': 4510.00,
            'low': 4475.00,
            'volume': 5000000000,
            'last_updated': '2026-01-30T16:00:00Z'
        }
        """
        from datetime import datetime
        
        self.current_value = api_data.get('value')
        self.previous_close = api_data.get('previous_close')
        self.day_high = api_data.get('high')
        self.day_low = api_data.get('low')
        self.volume = api_data.get('volume')
        
        # Calculate daily change
        self.calculate_daily_change()
        
        # Update timestamp
        if 'last_updated' in api_data:
            self.last_updated = api_data['last_updated']
        else:
            self.last_updated = datetime.now()
        
        self.save()
```

---

## 🚀 IMPLEMENTATION STEPS

### **Phase 1: Create Models** (3 hours)

1. **Create ScreenerCriteria model**
   - File: `apps/backend/src/investments/models/screener_criteria.py`
   - Use correct base classes (UUIDModel, TimestampedModel, SoftDeleteModel)
   - Add comprehensive filtering fields
   - Implement to_query_dict() method for API usage

2. **Create MarketIndex model**
   - File: `apps/backend/src/assets/models/market_index.py`
   - Use correct base classes
   - Add performance tracking fields
   - Implement calculation methods (daily change, period returns, 52-week proximity)

### **Phase 2: Create Migrations** (1 hour)

```bash
cd apps/backend
python manage.py makemigrations investments assets
python manage.py migrate
```

### **Phase 3: Create Model Admin** (1 hour)

**File:** `apps/backend/src/investments/admin/screener_admin.py`

```python
from django.contrib import admin
from investments.models.screener_criteria import ScreenerCriteria

@admin.register(ScreenerCriteria)
class ScreenerCriteriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
```

**File:** `apps/backend/src/assets/admin/market_index_admin.py`

```python
from django.contrib import admin
from assets.models.market_index import MarketIndex

@admin.register(MarketIndex)
class MarketIndexAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_value', 'daily_change_percent', 'last_updated', 'is_active']
    list_filter = ['index_type', 'country', 'is_active']
    search_fields = ['symbol', 'name']
    readonly_fields = ['created_at', 'updated_at']
```

### **Phase 4: Write Tests** (2 hours)

**File:** `apps/backend/src/investments/tests/test_screener_criteria.py`

```python
from django.test import TestCase
from investments.models.screener_criteria import ScreenerCriteria
from django.contrib.auth.models import User

class ScreenerCriteriaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
    
    def test_screener_criteria_with_inheritance(self):
        """Test screener criteria creation with correct base class inheritance."""
        criteria = ScreenerCriteria.objects.create(
            user=self.user,
            name='Value Stocks',
            description='Find undervalued stocks',
            pe_ratio_max=15,
            pb_ratio_max=2,
            dividend_yield_min=2,
            is_favorite=True
        )
        
        # Check base class fields
        self.assertIsNotNone(criteria.id)
        self.assertIsNotNone(criteria.created_at)
        self.assertIsNotNone(criteria.updated_at)
        self.assertFalse(criteria.is_deleted)
        
        # Check criteria fields
        self.assertEqual(criteria.name, 'Value Stocks')
        self.assertTrue(criteria.is_favorite)
    
    def test_to_query_dict_method(self):
        """Test conversion to query dictionary."""
        criteria = ScreenerCriteria.objects.create(
            user=self.user,
            name='Growth Stocks',
            pe_ratio_min=20,
            pe_ratio_max=50,
            revenue_growth_min=10,
            earnings_growth_min=15
        )
        
        query_dict = criteria.to_query_dict()
        
        self.assertIn('pe_ratio', query_dict)
        self.assertEqual(query_dict['pe_ratio']['min'], 20.0)
        self.assertEqual(query_dict['pe_ratio']['max'], 50.0)
        self.assertEqual(query_dict['revenue_growth']['min'], 10.0)
        self.assertEqual(query_dict['earnings_growth']['min'], 15.0)
```

**File:** `apps/backend/src/assets/tests/test_market_index.py`

```python
from django.test import TestCase
from assets.models.market_index import MarketIndex
from decimal import Decimal
from datetime import datetime

class MarketIndexTest(TestCase):
    def test_market_index_with_inheritance(self):
        """Test market index creation with correct base class inheritance."""
        index = MarketIndex.objects.create(
            symbol='SPX',
            name='S&P 500 Index',
            index_type='BROAD_MARKET',
            country='US',
            exchange='NYSE',
            current_value=Decimal('4500.25'),
            previous_close=Decimal('4480.50')
        )
        
        # Check base class fields
        self.assertIsNotNone(index.id)
        self.assertIsNotNone(index.created_at)
        self.assertIsNotNone(index.updated_at)
        self.assertFalse(index.is_deleted)
        
        # Check index fields
        self.assertEqual(index.symbol, 'SPX')
        self.assertEqual(index.name, 'S&P 500 Index')
    
    def test_calculate_daily_change(self):
        """Test daily change calculation."""
        index = MarketIndex.objects.create(
            symbol='NDX',
            name='NASDAQ 100 Index',
            current_value=Decimal('16000.00'),
            previous_close=Decimal('15800.00')
        )
        
        daily_change, daily_change_pct = index.calculate_daily_change()
        
        self.assertEqual(float(daily_change), 200.0)
        self.assertAlmostEqual(float(daily_change_pct), 1.2658, places=2)
    
    def test_calculate_period_return(self):
        """Test period return calculation."""
        index = MarketIndex.objects.create(
            symbol='DJI',
            name='Dow Jones Industrial Average',
            current_value=Decimal('35000.00'),
            previous_close=Decimal('34800.00')
        )
        
        # Calculate YTD return (from 34000 to 35000)
        ytd_return = index.calculate_period_return(Decimal('34000.00'))
        
        expected_return = ((35000.00 - 34000.00) / 34000.00) * 100
        self.assertAlmostEqual(float(ytd_return), expected_return, places=2)
    
    def test_52_week_high_proximity(self):
        """Test 52-week high proximity check."""
        index = MarketIndex.objects.create(
            symbol='SPX',
            name='S&P 500 Index',
            current_value=Decimal('4500.00'),
            week_52_high=Decimal('4550.00'),
            week_52_low=Decimal('4000.00')
        )
        
        # Within 2% threshold
        is_near = index.is_near_52_week_high(threshold_percent=2.0)
        
        # 4500 is within 2% of 4550 (4550 * 0.02 = 91, so threshold is 4550 - 91 = 4459)
        self.assertTrue(is_near)
        
        # Not within 1% threshold
        is_near = index.is_near_52_week_high(threshold_percent=1.0)
        self.assertFalse(is_near)
    
    def test_update_from_api_data(self):
        """Test updating from API data."""
        index = MarketIndex.objects.create(
            symbol='RUT',
            name='Russell 2000 Index'
        )
        
        api_data = {
            'value': '2000.50',
            'previous_close': '1985.00',
            'high': '2010.00',
            'low': '1975.00',
            'volume': 1500000000
        }
        
        index.update_from_api_data(api_data)
        
        self.assertEqual(float(index.current_value), 2000.50)
        self.assertEqual(float(index.previous_close), 1985.00)
        self.assertEqual(float(index.day_high), 2010.00)
        self.assertEqual(float(index.day_low), 1975.00)
        self.assertIsNotNone(index.daily_change)
        self.assertIsNotNone(index.daily_change_percent)
```

### **Phase 5: API Endpoints** (1 hour)

**File:** `apps/backend/src/api/market_data_models.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.models.screener_criteria import ScreenerCriteria
from assets.models.market_index import MarketIndex

# Screener Criteria Endpoints

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def screener_criteria_list(request):
    """Get all screener criteria or create new one."""
    if request.method == 'GET':
        criteria_list = ScreenerCriteria.objects.filter(
            user=request.user,
            is_deleted=False
        ).order_by('-is_favorite', '-created_at')
        
        data = [{
            'id': crit.id,
            'name': crit.name,
            'description': crit.description,
            'is_favorite': crit.is_favorite,
            'created_at': str(crit.created_at)
        } for crit in criteria_list]
        
        return Response(data)
    
    elif request.method == 'POST':
        criteria = ScreenerCriteria.objects.create(
            user=request.user,
            **request.data
        )
        
        return Response({
            'id': criteria.id,
            'name': criteria.name
        }, status=201)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def screener_criteria_detail(request, criteria_id):
    """Get, update, or delete screener criteria."""
    try:
        criteria = ScreenerCriteria.objects.get(
            id=criteria_id,
            user=request.user,
            is_deleted=False
        )
    except ScreenerCriteria.DoesNotExist:
        return Response({'error': 'Screener criteria not found'}, status=404)
    
    if request.method == 'GET':
        return Response({
            'id': criteria.id,
            'name': criteria.name,
            'description': criteria.description,
            'market_cap_min': float(criteria.market_cap_min) if criteria.market_cap_min else None,
            'market_cap_max': float(criteria.market_cap_max) if criteria.market_cap_max else None,
            'pe_ratio_min': float(criteria.pe_ratio_min) if criteria.pe_ratio_min else None,
            'pe_ratio_max': float(criteria.pe_ratio_max) if criteria.pe_ratio_max else None,
            'dividend_yield_min': float(criteria.dividend_yield_min) if criteria.dividend_yield_min else None,
            'dividend_yield_max': float(criteria.dividend_yield_max) if criteria.dividend_yield_max else None,
            'revenue_growth_min': float(criteria.revenue_growth_min) if criteria.revenue_growth_min else None,
            'earnings_growth_min': float(criteria.earnings_growth_min) if criteria.earnings_growth_min else None,
            'roe_min': float(criteria.roe_min) if criteria.roe_min else None,
            'debt_to_equity_max': float(criteria.debt_to_equity_max) if criteria.debt_to_equity_max else None,
            'sectors': criteria.sectors,
            'industries': criteria.industries,
            'exchanges': criteria.exchanges,
            'sort_by': criteria.sort_by,
            'sort_order': criteria.sort_order,
            'max_results': criteria.max_results,
            'is_favorite': criteria.is_favorite
        })
    
    elif request.method == 'PUT':
        for field, value in request.data.items():
            setattr(criteria, field, value)
        criteria.save()
        return Response({'status': 'updated'})
    
    elif request.method == 'DELETE':
        criteria.soft_delete()
        return Response({'status': 'deleted'})

# Market Index Endpoints

@api_view(['GET'])
def market_indices(request):
    """Get all market indices."""
    indices = MarketIndex.objects.filter(
        is_deleted=False,
        is_active=True
    ).order_by('symbol')
    
    data = [{
        'id': idx.id,
        'symbol': idx.symbol,
        'name': idx.name,
        'index_type': idx.index_type,
        'current_value': float(idx.current_value) if idx.current_value else None,
        'daily_change': float(idx.daily_change) if idx.daily_change else None,
        'daily_change_percent': float(idx.daily_change_percent) if idx.daily_change_percent else None,
        'day_high': float(idx.day_high) if idx.day_high else None,
        'day_low': float(idx.day_low) if idx.day_low else None,
        'week_52_high': float(idx.week_52_high) if idx.week_52_high else None,
        'week_52_low': float(idx.week_52_low) if idx.week_52_low else None,
        'last_updated': str(idx.last_updated) if idx.last_updated else None
    } for idx in indices]
    
    return Response(data)

@api_view(['GET'])
def market_index_detail(request, symbol):
    """Get detailed information for a specific index."""
    try:
        index = MarketIndex.objects.get(
            symbol=symbol.upper(),
            is_deleted=False
        )
    except MarketIndex.DoesNotExist:
        return Response({'error': 'Index not found'}, status=404)
    
    return Response({
        'id': index.id,
        'symbol': index.symbol,
        'name': index.name,
        'description': index.description,
        'country': index.country,
        'exchange': index.exchange,
        'index_type': index.index_type,
        'current_value': float(index.current_value) if index.current_value else None,
        'previous_close': float(index.previous_close) if index.previous_close else None,
        'daily_change': float(index.daily_change) if index.daily_change else None,
        'daily_change_percent': float(index.daily_change_percent) if index.daily_change_percent else None,
        'day_high': float(index.day_high) if index.day_high else None,
        'day_low': float(index.day_low) if index.day_low else None,
        'week_52_high': float(index.week_52_high) if index.week_52_high else None,
        'week_52_low': float(index.week_52_low) if index.week_52_low else None,
        'volume': index.volume,
        'avg_volume': index.avg_volume,
        'dividend_yield': float(index.dividend_yield) if index.dividend_yield else None,
        'pe_ratio': float(index.pe_ratio) if index.pe_ratio else None,
        'last_updated': str(index.last_updated) if index.last_updated else None,
        'is_near_52_high': index.is_near_52_week_high(),
        'is_near_52_low': index.is_near_52_week_low()
    })

@api_view(['POST'])
def update_market_index(request, symbol):
    """Update market index from API data."""
    try:
        index = MarketIndex.objects.get(
            symbol=symbol.upper(),
            is_deleted=False
        )
    except MarketIndex.DoesNotExist:
        return Response({'error': 'Index not found'}, status=404)
    
    index.update_from_api_data(request.data)
    
    return Response({
        'status': 'updated',
        'current_value': float(index.current_value),
        'daily_change_percent': float(index.daily_change_percent)
    })
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Both models created with correct base class inheritance (UUIDModel, TimestampedModel, SoftDeleteModel)
- [ ] Migrations created and applied successfully
- [ ] Model admin registered for both models
- [ ] Unit tests pass (test inheritance, fields, calculation methods)
- [ ] API endpoints functional
- [ ] Documentation complete

---

## 📋 DELIVERABLES

- [ ] 2 model files created (screener_criteria.py, market_index.py)
- [ ] Migration files generated
- [ ] Model admin configured
- [ ] Unit tests written and passing
- [ ] API endpoints implemented
- [ ] API documentation updated

---

**Created:** January 30, 2026  
**Created By:** GAUDÍ (Architect)  
**Assigned To:** Backend Coder (DevOps supervision)  
**Priority:** P2 - MEDIUM  
**Estimate:** 8 hours (1 day)
