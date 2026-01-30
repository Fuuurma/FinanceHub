# C-035: Dividend Tracking & Income Analytics

**Priority:** P0 - CRITICAL  
**Assigned to:** Backend Coder  
**Estimated Time:** 14-18 hours  
**Dependencies:** C-011 (Portfolio Analytics Enhancement), C-025 (CSV Bulk Import)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive dividend tracking system with automatic dividend detection, income projections, tax tracking, and yield analysis for income-focused investors.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 4.1 - Portfolio Tracking):**

- Automatic dividend tracking
- Cost basis tracking (FIFO, LIFO, specific lot)
- Transaction history export

**From Features Specification (Section 4.2 - Portfolio Analytics):**

- Total return (time-weighted, money-weighted)
- Performance vs benchmarks
- Portfolio beta calculation

**From Features Specification (Section 1.2 - Asset Details):**

- Corporate actions (splits, dividends, buybacks)

---

## ✅ CURRENT STATE

**What exists:**
- Portfolio tracking (C-025)
- Basic portfolio analytics (C-011)
- Transaction history

**What's missing:**
- Dividend payment tracking
- Dividend projection/forecasting
- Dividend yield calculations
- Tax reporting for dividends
- Dividend reinvestment tracking
- Ex-dividend date tracking
- Qualified vs non-qualified dividends
- Monthly/annual income summaries

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (3-4 hours)

**Create `apps/backend/src/investments/models/dividends.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from .portfolio import Portfolio, PortfolioPosition
from .asset import Asset

User = get_user_model()

class DividendPayment(models.Model):
    """Individual dividend payments received"""
    
    DIVIDEND_TYPE_CHOICES = [
        ('cash', 'Cash Dividend'),
        ('stock', 'Stock Dividend'),
        ('special', 'Special Dividend'),
        ('return_of_capital', 'Return of Capital'),
    ]
    
    QUALIFIED_CHOICES = [
        ('qualified', 'Qualified'),
        ('non_qualified', 'Non-Qualified'),
        ('unknown', 'Unknown'),
    ]
    
    # Portfolio and position
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='dividends')
    position = models.ForeignKey(PortfolioPosition, on_delete=models.CASCADE, related_name='dividends', null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='dividends')
    
    # Payment details
    dividend_type = models.CharField(max_length=20, choices=DIVIDEND_TYPE_CHOICES)
    amount_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    shares_held = models.DecimalField(max_digits=20, decimal_places=6)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Dates
    ex_dividend_date = models.DateField()
    record_date = models.DateField()
    payment_date = models.DateField()
    
    # Tax information
    qualified_status = models.CharField(max_length=20, choices=QUALIFIED_CHOICES, default='unknown')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)  # Applied tax rate
    tax_withheld = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # Tax amount withheld
    net_amount = models.DecimalField(max_digits=20, decimal_places=2)  # After tax
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    fx_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1.0)  # For foreign dividends
    
    # Reinvestment
    reinvested = models.BooleanField(default=False)
    reinvestment_transaction_id = models.IntegerField(null=True, blank=True)
    
    # Corporate action reference
    corporate_action_id = models.IntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio', '-payment_date']),
            models.Index(fields=['asset', '-payment_date']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['ex_dividend_date']),
        ]
        ordering = ['-payment_date']

class DividendForecast(models.Model):
    """Forecasted future dividend payments"""
    
    # Asset reference
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='dividend_forecasts')
    
    # Forecast details
    forecast_date = models.DateField()  # Expected ex-dividend date
    expected_amount = models.DecimalField(max_digits=10, decimal_places=4)
    frequency = models.CharField(max_length=20)  # monthly, quarterly, semi-annual, annual
    
    # Confidence
    confidence = models.CharField(max_length=20)  # high, medium, low
    based_on_period = models.CharField(max_length=50)  # e.g., "Q4 2025 actual"
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', 'forecast_date']),
            models.Index(fields=['forecast_date']),
        ]
        ordering = ['forecast_date']

class DividendIncomeSummary(models.Model):
    """Aggregated dividend income by period"""
    
    # Portfolio reference
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='dividend_summaries')
    
    # Period
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)  # Null for annual summaries
    quarter = models.IntegerField(null=True, blank=True)  # Null for non-quarterly
    
    # Income metrics
    gross_dividends = models.DecimalField(max_digits=20, decimal_places=2)  # Before tax
    tax_withheld = models.DecimalField(max_digits=20, decimal_places=2)
    net_dividends = models.DecimalField(max_digits=20, decimal_places=2)  # After tax
    
    # Breakdown
    qualified_dividends = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    non_qualified_dividends = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    return_of_capital = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # Reinvested
    dividends_reinvested = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    dividends_received_cash = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # Yield metrics
    portfolio_value_beginning = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    portfolio_value_ending = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    dividend_yield_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Payment count
    payment_count = models.IntegerField(default=0)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio', 'year', '-month']),
            models.Index(fields=['portfolio', 'year', '-quarter']),
            models.Index(fields=['year', '-month']),
        ]
        unique_together = [['portfolio', 'year', 'month', 'quarter']]
        ordering = ['-year', '-month']

class DividendTaxLot(models.Model):
    """Track tax lots for dividend reinvestments"""
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='dividend_tax_lots')
    dividend_payment = models.ForeignKey(DividendPayment, on_delete=models.CASCADE, related_name='tax_lots')
    
    # Tax lot details
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    shares_acquired = models.DecimalField(max_digits=20, decimal_places=6)
    cost_basis_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    total_cost_basis = models.DecimalField(max_digits=20, decimal_places=2)
    acquisition_date = models.DateField()
    
    # Sale tracking
    shares_sold = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    remaining_shares = models.DecimalField(max_digits=20, decimal_places=6)
    
    # Realized gain/loss
    realized_gain_loss = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio', 'asset']),
            models.Index(fields=['dividend_payment']),
        ]
        ordering = ['-acquisition_date']

class DividendYield(models.Model):
    """Calculated dividend yields for assets"""
    
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='dividend_yield')
    
    # Yield metrics
    trailing_yield = models.DecimalField(max_digits=10, decimal_places=4)  # TTM yield
    forward_yield = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # Forecasted
    current_yield = models.DecimalField(max_digits=10, decimal_places=4)  # Annualized current rate
    
    # Dividend details
    annual_dividend = models.DecimalField(max_digits=10, decimal_places=4)
    dividend_frequency = models.IntegerField()  # Payments per year
    last_dividend_amount = models.DecimalField(max_digits=10, decimal_places=4)
    last_dividend_date = models.DateField()
    
    # Payout tracking
    payout_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # % of earnings paid
    
    # Yield history
    yield_1m_ago = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    yield_3m_ago = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    yield_1y_ago = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-trailing_yield']),
            models.Index(fields=['-forward_yield']),
        ]

class ExDividendCalendar(models.Model):
    """Upcoming ex-dividend dates"""
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='ex_dividend_dates')
    
    # Dividend details
    ex_dividend_date = models.DateField()
    expected_amount = models.DecimalField(max_digits=10, decimal_places=4)
    
    # Status
    status = models.CharField(max_length=20)  # expected, confirmed, paid
    
    # Record and payment dates (when known)
    record_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['ex_dividend_date']),
            models.Index(fields=['asset', '-ex_dividend_date']),
        ]
        ordering = ['ex_dividend_date']
```

---

### **Phase 2: Dividend Tracking Service** (6-7 hours)

**Create `apps/backend/src/investments/services/dividend_service.py`:**

```python
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.db import transaction, models
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from investments.models.dividends import (
    DividendPayment, DividendForecast, DividendIncomeSummary,
    DividendTaxLot, DividendYield, ExDividendCalendar
)
from investments.models.portfolio import Portfolio, PortfolioPosition
from investments.models.asset import Asset
from investments.services.price_service import PriceService

class DividendTrackingService:
    
    def __init__(self):
        self.price_service = PriceService()
    
    @transaction.atomic
    def record_dividend_payment(
        self,
        portfolio_id: int,
        asset_id: int,
        ex_dividend_date: date,
        record_date: date,
        payment_date: date,
        amount_per_share: float,
        shares_held: float,
        dividend_type: str = 'cash',
        reinvested: bool = False
    ) -> Dict:
        """Record a dividend payment"""
        
        portfolio = Portfolio.objects.get(id=portfolio_id)
        asset = Asset.objects.get(id=asset_id)
        
        # Get position (may be closed if dividend paid after sale)
        position = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            asset=asset
        ).first()
        
        # Calculate totals
        total_amount = Decimal(str(amount_per_share)) * Decimal(str(shares_held))
        
        # Determine tax status (US stocks)
        qualified_status = self._determine_qualified_status(asset, ex_dividend_date)
        
        # Estimate tax (15% for qualified, ordinary rate for non-qualified)
        if qualified_status == 'qualified':
            tax_rate = Decimal('0.15')
        else:
            tax_rate = Decimal('0.22')  # Assume 22% ordinary
        
        tax_withheld = total_amount * tax_rate
        net_amount = total_amount - tax_withheld
        
        # Create dividend payment
        dividend = DividendPayment.objects.create(
            portfolio=portfolio,
            position=position,
            asset=asset,
            dividend_type=dividend_type,
            amount_per_share=Decimal(str(amount_per_share)),
            shares_held=Decimal(str(shares_held)),
            total_amount=total_amount,
            ex_dividend_date=ex_dividend_date,
            record_date=record_date,
            payment_date=payment_date,
            qualified_status=qualified_status,
            tax_rate=tax_rate,
            tax_withheld=tax_withheld,
            net_amount=net_amount,
            reinvested=reinvested
        )
        
        # Update income summary
        self._update_income_summary(portfolio, dividend)
        
        # Update dividend yield for asset
        self._update_dividend_yield(asset)
        
        return {
            'dividend_id': dividend.id,
            'total_amount': float(total_amount),
            'net_amount': float(net_amount),
            'tax_withheld': float(tax_withheld)
        }
    
    def _determine_qualified_status(self, asset: Asset, ex_dividend_date: date) -> str:
        """Determine if dividend is qualified (US tax rules)"""
        # Simplified logic - actual rules more complex
        if asset.asset_type != 'stock':
            return 'non_qualified'
        
        # Check if US stock
        if asset.exchange not in ['NYSE', 'NASDAQ', 'AMEX']:
            return 'non_qualified'
        
        # Check holding period (simplified - needs position history)
        return 'qualified'
    
    def _update_income_summary(self, portfolio: Portfolio, dividend: DividendPayment):
        """Update monthly/annual income summaries"""
        payment_date = dividend.payment_date
        
        # Update monthly summary
        DividendIncomeSummary.objects.update_or_create(
            portfolio=portfolio,
            year=payment_date.year,
            month=payment_date.month,
            defaults={
                'gross_dividends': models.F('gross_dividends') + dividend.total_amount,
                'tax_withheld': models.F('tax_withheld') + dividend.tax_withheld,
                'net_dividends': models.F('net_dividends') + dividend.net_amount,
                'qualified_dividends': models.F('qualified_dividends') + 
                    (dividend.total_amount if dividend.qualified_status == 'qualified' else 0),
                'non_qualified_dividends': models.F('non_qualified_dividends') + 
                    (dividend.total_amount if dividend.qualified_status == 'non_qualified' else 0),
                'dividends_reinvested': models.F('dividends_reinvested') + 
                    (dividend.net_amount if dividend.reinvested else 0),
                'dividends_received_cash': models.F('dividends_received_cash') + 
                    (0 if dividend.reinvested else dividend.net_amount),
                'payment_count': models.F('payment_count') + 1,
            }
        )
        
        # Update annual summary
        DividendIncomeSummary.objects.update_or_create(
            portfolio=portfolio,
            year=payment_date.year,
            month=None,
            quarter=None,
            defaults={
                'gross_dividends': models.F('gross_dividends') + dividend.total_amount,
                'tax_withheld': models.F('tax_withheld') + dividend.tax_withheld,
                'net_dividends': models.F('net_dividends') + dividend.net_amount,
                'payment_count': models.F('payment_count') + 1,
            }
        )
    
    def _update_dividend_yield(self, asset: Asset):
        """Update dividend yield metrics for asset"""
        # Get last 12 months of dividends
        twelve_months_ago = date.today() - timedelta(days=365)
        recent_dividends = DividendPayment.objects.filter(
            asset=asset,
            payment_date__gte=twelve_months_ago
        ).order_by('-payment_date')
        
        if not recent_dividends.exists():
            return
        
        # Calculate TTM annual dividend
        total_ttm = sum(d.total_amount for d in recent_dividends)
        
        # Get current price
        current_price = asset.current_price
        
        if current_price and current_price > 0:
            trailing_yield = float(total_ttm / current_price / 100)  # Assume 100 shares
        else:
            trailing_yield = 0
        
        # Get last dividend
        last_dividend = recent_dividends.first()
        
        # Estimate annual dividend
        frequency = self._estimate_dividend_frequency(asset)
        annual_dividend = float(last_dividend.amount_per_share) * frequency
        
        # Calculate current yield
        current_yield = (annual_dividend / float(current_price) * 100) if current_price else 0
        
        # Update or create yield record
        DividendYield.objects.update_or_create(
            asset=asset,
            defaults={
                'trailing_yield': Decimal(str(trailing_yield)),
                'current_yield': Decimal(str(current_yield)),
                'annual_dividend': Decimal(str(annual_dividend)),
                'dividend_frequency': frequency,
                'last_dividend_amount': last_dividend.amount_per_share,
                'last_dividend_date': last_dividend.payment_date,
            }
        )
    
    def _estimate_dividend_frequency(self, asset: Asset) -> int:
        """Estimate dividend payment frequency"""
        # Count payments in last year
        twelve_months_ago = date.today() - timedelta(days=365)
        payment_count = DividendPayment.objects.filter(
            asset=asset,
            payment_date__gte=twelve_months_ago
        ).count()
        
        # Estimate frequency
        if payment_count >= 10:
            return 12  # Monthly
        elif payment_count >= 4:
            return 4  # Quarterly
        elif payment_count >= 2:
            return 2  # Semi-annual
        else:
            return 1  # Annual
    
    def get_dividend_income(
        self,
        portfolio_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Get dividend income for date range"""
        dividends = DividendPayment.objects.filter(
            portfolio_id=portfolio_id,
            payment_date__gte=start_date,
            payment_date__lte=end_date
        )
        
        # Aggregate totals
        totals = dividends.aggregate(
            gross_total=Sum('total_amount'),
            tax_total=Sum('tax_withheld'),
            net_total=Sum('net_amount'),
            qualified_total=Sum(
                models.Case(
                    models.When(qualified_status='qualified', then='total_amount'),
                    default=0,
                    output_field=models.DecimalField()
                )
            ),
            reinvested_total=Sum(
                models.Case(
                    models.When(reinvested=True, then='net_amount'),
                    default=0,
                    output_field=models.DecimalField()
                )
            ),
            payment_count=Count('id')
        )
        
        # Get by month
        monthly_breakdown = dividends.extra(
            select={'month': 'EXTRACT(month FROM payment_date)'}
        ).values('month').annotate(
            gross=Sum('total_amount'),
            net=Sum('net_amount')
        ).order_by('month')
        
        # Get by asset
        by_asset = dividends.values('asset__symbol', 'asset__name').annotate(
            gross=Sum('total_amount'),
            net=Sum('net_amount'),
            payments=Count('id')
        ).order_by('-gross')
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'totals': {
                'gross_income': float(totals['gross_total'] or 0),
                'tax_withheld': float(totals['tax_total'] or 0),
                'net_income': float(totals['net_total'] or 0),
                'qualified_income': float(totals['qualified_total'] or 0),
                'reinvested': float(totals['reinvested_total'] or 0),
                'received_cash': float(totals['net_total'] or 0) - float(totals['reinvested_total'] or 0),
                'payment_count': totals['payment_count'] or 0
            },
            'monthly_breakdown': list(monthly_breakdown),
            'by_asset': list(by_asset)
        }
    
    def forecast_dividend_income(
        self,
        portfolio_id: int,
        months: int = 12
    ) -> Dict:
        """Forecast future dividend income"""
        portfolio = Portfolio.objects.get(id=portfolio_id)
        positions = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).select_related('asset')
        
        forecasted_payments = []
        total_forecasted = 0
        
        for position in positions:
            # Get dividend forecasts for this asset
            forecasts = DividendForecast.objects.filter(
                asset=position.asset,
                forecast_date__lte=date.today() + timedelta(days=months*30)
            ).order_by('forecast_date')[:months]
            
            for forecast in forecasts:
                payment_amount = float(forecast.expected_amount) * float(position.quantity)
                total_forecasted += payment_amount
                
                forecasted_payments.append({
                    'date': forecast.forecast_date.isoformat(),
                    'symbol': position.asset.symbol,
                    'amount': payment_amount,
                    'confidence': forecast.confidence
                })
        
        # Sort by date
        forecasted_payments.sort(key=lambda x: x['date'])
        
        return {
            'total_forecasted': total_forecasted,
            'monthly_forecast': total_forecasted / months,
            'payments': forecasted_payments
        }
    
    def calculate_portfolio_yield(self, portfolio_id: int) -> Dict:
        """Calculate dividend yield for portfolio"""
        portfolio = Portfolio.objects.get(id=portfolio_id)
        positions = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).select_related('asset')
        
        portfolio_value = 0
        weighted_yield = 0
        annual_income = 0
        
        position_yields = []
        
        for position in positions:
            asset_value = float(position.quantity) * float(position.asset.current_price)
            portfolio_value += asset_value
            
            # Get dividend yield
            try:
                dividend_yield = DividendYield.objects.get(asset=position.asset)
                trailing_yield = float(dividend_yield.trailing_yield)
                annual_position_income = asset_value * trailing_yield / 100
                annual_income += annual_position_income
                
                position_yields.append({
                    'symbol': position.asset.symbol,
                    'value': asset_value,
                    'weight': 0,  # Will calculate
                    'yield': trailing_yield,
                    'annual_income': annual_position_income
                })
            except DividendYield.DoesNotExist:
                pass
        
        # Calculate weights
        for pos in position_yields:
            pos['weight'] = pos['value'] / portfolio_value if portfolio_value > 0 else 0
            weighted_yield += pos['yield'] * pos['weight']
        
        return {
            'portfolio_value': portfolio_value,
            'portfolio_yield': weighted_yield,
            'estimated_annual_income': annual_income,
            'estimated_monthly_income': annual_income / 12,
            'position_yields': position_yields
        }
    
    def get_upcoming_ex_dividends(
        self,
        portfolio_id: int,
        days_ahead: int = 30
    ) -> List[Dict]:
        """Get upcoming ex-dividend dates for portfolio"""
        end_date = date.today() + timedelta(days=days_ahead)
        
        # Get assets in portfolio
        portfolio = Portfolio.objects.get(id=portfolio_id)
        asset_ids = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).values_list('asset_id', flat=True)
        
        # Get upcoming ex-dividend dates
        ex_dividends = ExDividendCalendar.objects.filter(
            asset_id__in=asset_ids,
            ex_dividend_date__gte=date.today(),
            ex_dividend_date__lte=end_date
        ).select_related('asset').order_by('ex_dividend_date')
        
        result = []
        for ex_div in ex_dividends:
            # Get shares held
            position = PortfolioPosition.objects.filter(
                portfolio=portfolio,
                asset=ex_div.asset
            ).first()
            
            if position:
                expected_payment = float(ex_div.expected_amount) * float(position.quantity)
                
                result.append({
                    'date': ex_div.ex_dividend_date.isoformat(),
                    'symbol': ex_div.asset.symbol,
                    'name': ex_div.asset.name,
                    'expected_amount': float(ex_div.expected_amount),
                    'shares_held': float(position.quantity),
                    'expected_payment': expected_payment,
                    'status': ex_div.status
                })
        
        return result
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/dividends.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.services.dividend_service import DividendTrackingService
from investments.models.portfolio import Portfolio
from datetime import datetime

router = Router(tags=['dividends'])
dividend_service = DividendTrackingService()

@router.get("/dividends/income/{portfolio_id}")
def get_dividend_income(
    request,
    portfolio_id: int,
    start_date: str,
    end_date: str
):
    """Get dividend income for date range"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    return dividend_service.get_dividend_income(portfolio_id, start, end)

@router.get("/dividends/forecast/{portfolio_id}")
def forecast_dividend_income(
    request,
    portfolio_id: int,
    months: int = 12
):
    """Forecast future dividend income"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    return dividend_service.forecast_dividend_income(portfolio_id, months)

@router.get("/dividends/yield/{portfolio_id}")
def calculate_portfolio_yield(request, portfolio_id: int):
    """Calculate portfolio dividend yield"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    return dividend_service.calculate_portfolio_yield(portfolio_id)

@router.get("/dividends/upcoming/{portfolio_id}")
def get_upcoming_ex_dividends(
    request,
    portfolio_id: int,
    days_ahead: int = 30
):
    """Get upcoming ex-dividend dates"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    return dividend_service.get_upcoming_ex_dividends(portfolio_id, days_ahead)

@router.get("/dividends/summary/{portfolio_id}")
def get_dividend_summary(
    request,
    portfolio_id: int,
    year: int
):
    """Get annual dividend summary"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    from investments.models.dividends import DividendIncomeSummary
    
    try:
        summary = DividendIncomeSummary.objects.get(
            portfolio=portfolio,
            year=year,
            month=None
        )
        
        return {
            'year': year,
            'gross_dividends': float(summary.gross_dividends),
            'tax_withheld': float(summary.tax_withheld),
            'net_dividends': float(summary.net_dividends),
            'qualified_dividends': float(summary.qualified_dividends),
            'non_qualified_dividends': float(summary.non_qualified_dividends),
            'dividends_reinvested': float(summary.dividends_reinvested),
            'payment_count': summary.payment_count
        }
    except DividendIncomeSummary.DoesNotExist:
        return {'error': 'No summary found for this year'}
```

---

## 📋 DELIVERABLES

- [ ] DividendPayment, DividendForecast, DividendIncomeSummary, DividendTaxLot, DividendYield, ExDividendCalendar models
- [ ] DividendTrackingService with comprehensive tracking and forecasting
- [ ] 6 API endpoints for dividend analysis
- [ ] Automatic income summary updates
- [ ] Tax status tracking (qualified vs non-qualified)
- [ ] Dividend reinvestment support
- [ ] Portfolio yield calculations
- [ ] Database migrations
- [ ] Unit tests (coverage >80%)

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Dividend payments recorded accurately
- [ ] Qualified/non-qualified status determined
- [ ] Tax withholding calculated correctly
- [ ] Income summaries updated automatically
- [ ] Dividend forecasts generated for portfolio assets
- [ ] Portfolio yield calculated as weighted average
- [ ] Ex-dividend calendar shows upcoming payments
- [ ] Reinvested dividends tracked separately
- [ ] Monthly and annual summaries working
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Dividend tracking accurate to 2 decimal places
- Forecast accuracy within 10% of actual
- Portfolio yield calculated <500ms
- Support for 1000+ dividend payments per portfolio
- Tax reporting export ready (CSV format)

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/035-dividend-tracking-system.md
