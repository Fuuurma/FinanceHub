# C-024: Earnings Calendar & Corporate Events Tracker

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 10-14 hours  
**Dependencies:** None  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive earnings calendar and corporate events tracker with alerts, historical data, and portfolio impact analysis.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 1.2 - Asset Details):**

- Earnings calendar & history
- Corporate actions (splits, dividends, buybacks)
- Management team & insider trading

**From Features Specification (Section 6.2 - Research Tools):**

- Economic calendar (FOMC, GDP, CPI, etc.)
- IPO calendar
- Earnings estimates
- Stock screener based on fundamentals

---

## ✅ CURRENT STATE

**What exists:**
- Asset tracking models
- Portfolio management
- Basic price history

**What's missing:**
- Earnings calendar data
- Corporate actions tracking
- Dividend history
- Events alerts
- Impact analysis on portfolios

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (3-4 hours)

**Create `apps/backend/src/investments/models/corporate_events.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .asset import Asset

User = get_user_model()

class EarningsEvent(models.Model):
    """Earnings announcements"""
    
    QUARTER_CHOICES = [
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='earnings')
    
    # Event details
    fiscal_quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES)
    fiscal_year = models.IntegerField()
    earnings_date = models.DateTimeField()
    earnings_time = models.CharField(max_length=20)  # 'pre-market', 'after-market', 'during'
    
    # Estimates vs actuals
    estimated_eps = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    actual_eps = models.DecimalField(max_digits=10, decimal_periods=4, null=True)
    estimated_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    actual_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    
    # Surprise
    eps_surprise = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # % difference
    eps_surprise_value = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    revenue_surprise = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Price reaction
    price_before = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    price_after = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    price_change_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Conference call
    conference_call_url = models.URLField(blank=True)
    conference_call_time = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-earnings_date']
        indexes = [
            models.Index(fields=['asset', '-earnings_date']),
            models.Index(fields=['earnings_date']),
        ]

class CorporateAction(models.Model):
    """Corporate actions (splits, dividends, buybacks, etc.)"""
    
    ACTION_TYPE_CHOICES = [
        ('dividend', 'Dividend'),
        ('split', 'Stock Split'),
        ('reverse_split', 'Reverse Split'),
        ('buyback', 'Share Buyback'),
        ('spinoff', 'Spin-off'),
        ('acquisition', 'Acquisition'),
        ('merger', 'Merger'),
        ('reorganization', 'Reorganization'),
        ('name_change', 'Name Change'),
        ('ticker_change', 'Ticker Change'),
        ('delisting', 'Delisting'),
        ('ipo', 'IPO'),
        ('secondary', 'Secondary Offering'),
    ]
    
    STATUS_CHOICES = [
        ('announced', 'Announced'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='corporate_actions')
    
    # Event details
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='announced')
    
    # Dates
    announcement_date = models.DateTimeField()
    record_date = models.DateTimeField(null=True, blank=True)
    ex_date = models.DateTimeField(null=True, blank=True)
    payable_date = models.DateTimeField(null=True, blank=True)
    effective_date = models.DateTimeField(null=True, blank=True)
    
    # Details (JSON for flexibility)
    details = models.JSONField(default=dict)
    """
    Example for dividend:
    {
        'amount': 0.92,
        'frequency': 'quarterly',
        'currency': 'USD'
    }
    
    Example for split:
    {
        'ratio': '3:1',
        'old_shares': 1,
        'new_shares': 3
    }
    
    Example for buyback:
    {
        'amount': 50000000000,
        'shares': 1000000000,
        'method': 'open_market'
    }
    """
    
    # Description
    description = models.TextField(blank=True)
    
    # Source
    source = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-announcement_date']
        indexes = [
            models.Index(fields=['asset', '-announcement_date']),
            models.Index(fields=['action_type', '-announcement_date']),
            models.Index(fields=['ex_date']),
        ]

class DividendHistory(models.Model):
    """Dividend payment history"""
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='dividends')
    
    # Payment details
    ex_dividend_date = models.DateTimeField()
    record_date = models.DateTimeField()
    payment_date = models.DateTimeField()
    
    # Dividend details
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    currency = models.CharField(max_length=3, default='USD')
    frequency = models.CharField(max_length=20, blank=True)  # monthly, quarterly, annual
    
    # Adjustments
    adjusted_amount = models.DecimalField(max_digits=10, decimal_places=4, null=True)  # Split-adjusted
    
    # Yield calculations
    price_on_ex_date = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    yield_on_ex_date = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-ex_dividend_date']
        indexes = [
            models.Index(fields=['asset', '-ex_dividend_date']),
            models.Index(fields=['payment_date']),
        ]

class EconomicEvent(models.Model):
    """Economic calendar events (FOMC, GDP, CPI, etc.)"""
    
    IMPORTANCE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    # Event details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    importance = models.CharField(max_length=10, choices=IMPORTANCE_CHOICES, default='medium')
    
    # Dates
    event_date = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True)  # 'monthly', 'quarterly', etc.
    
    # Data
    actual = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    forecast = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    previous = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    
    # Impact
    impact_description = models.TextField(blank=True)
    
    # Country
    country = models.CharField(max_length=3)  # USD, EUR, JPY, etc.
    
    # Source
    source = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date']
        indexes = [
            models.Index(fields=['event_date']),
            models.Index(fields=['importance', '-event_date']),
        ]

class EventAlert(models.Model):
    """User alerts for corporate events"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_alerts')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    
    # Alert configuration
    alert_type = models.CharField(max_length=50)  # 'earnings', 'dividend', 'split', 'economic_event'
    alert_before_days = models.IntegerField(default=1)
    
    # Notification preferences
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
```

---

### **Phase 2: Events Data Service** (3-4 hours)

**Create `apps/backend/src/investments/services/corporate_events_service.py`:**

```python
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from investments.models.corporate_events import (
    EarningsEvent,
    CorporateAction,
    DividendHistory,
    EconomicEvent
)
from investments.models import Portfolio, PortfolioPosition

class CorporateEventsService:
    
    def get_upcoming_earnings(self, days_ahead: int = 30) -> List[Dict]:
        """
        Get upcoming earnings announcements
        
        Returns: List of earnings events with portfolio impact
        """
        start_date = timezone.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        earnings = EarningsEvent.objects.filter(
            earnings_date__gte=start_date,
            earnings_date__lte=end_date
        ).select_related('asset').order_by('earnings_date')
        
        return [{
            'id': e.id,
            'asset_id': e.asset.id,
            'symbol': e.asset.symbol,
            'company_name': e.asset.name,
            'date': e.earnings_date.isoformat(),
            'time': e.earnings_time,
            'quarter': f"{e.fiscal_year} {e.fiscal_quarter}",
            'estimated_eps': float(e.estimated_eps) if e.estimated_eps else None,
        } for e in earnings]
    
    def get_upcoming_dividends(self, user_id: int = None) -> List[Dict]:
        """
        Get upcoming dividend payments
        
        If user_id provided, only for assets in user's portfolio
        """
        query = CorporateAction.objects.filter(
            action_type='dividend',
            status='announced',
            ex_date__gte=timezone.now()
        ).select_related('asset')
        
        if user_id:
            # Filter to user's portfolio
            portfolio_assets = PortfolioPosition.objects.filter(
                portfolio__user_id=user_id
            ).values_list('asset_id', flat=True)
            
            query = query.filter(asset_id__in=portfolio_assets)
        
        actions = query.order_by('ex_date')
        
        return [{
            'id': a.id,
            'asset_id': a.asset.id,
            'symbol': a.asset.symbol,
            'ex_date': a.ex_date.isoformat() if a.ex_date else None,
            'record_date': a.record_date.isoformat() if a.record_date else None,
            'payment_date': a.payable_date.isoformat() if a.payable_date else None,
            'amount': float(a.details.get('amount', 0)),
            'frequency': a.details.get('frequency', ''),
        } for a in actions]
    
    def get_corporate_actions_calendar(
        self,
        start_date: str = None,
        end_date: str = None,
        action_types: List[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Get corporate actions calendar grouped by date
        
        Returns: {date: [actions]}
        """
        if not start_date:
            start_date = timezone.now()
        else:
            start_date = datetime.fromisoformat(start_date)
        
        if not end_date:
            end_date = start_date + timedelta(days=30)
        else:
            end_date = datetime.fromisoformat(end_date)
        
        query = CorporateAction.objects.filter(
            announcement_date__gte=start_date,
            announcement_date__lte=end_date
        )
        
        if action_types:
            query = query.filter(action_type__in=action_types)
        
        actions = query.select_related('asset').order_by('announcement_date')
        
        # Group by date
        calendar = {}
        for action in actions:
            date_str = action.announcement_date.date().isoformat()
            if date_str not in calendar:
                calendar[date_str] = []
            
            calendar[date_str].append({
                'id': action.id,
                'type': action.action_type,
                'symbol': action.asset.symbol,
                'description': action.description,
                'details': action.details
            })
        
        return calendar
    
    def get_economic_calendar(
        self,
        start_date: str = None,
        end_date: str = None,
        importance: str = None
    ) -> List[Dict]:
        """
        Get economic calendar events
        
        Args:
            start_date: ISO format date string
            end_date: ISO format date string
            importance: Filter by importance (low, medium, high)
        """
        query = EconomicEvent.objects.all()
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(event_date__gte=start_date)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(event_date__lte=end_date)
        
        if importance:
            query = query.filter(importance=importance)
        
        events = query.order_by('event_date')
        
        return [{
            'id': e.id,
            'name': e.name,
            'date': e.event_date.isoformat(),
            'importance': e.importance,
            'actual': float(e.actual) if e.actual else None,
            'forecast': float(e.forecast) if e.forecast else None,
            'previous': float(e.previous) if e.previous else None,
            'country': e.country
        } for e in events]
    
    def analyze_earnings_impact(self, portfolio_id: int) -> Dict:
        """
        Analyze impact of upcoming earnings on portfolio
        
        Returns: {total_exposure, high_impact_positions, by_sector}
        """
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related('asset')
        
        # Get upcoming earnings for portfolio assets
        asset_ids = [p.asset_id for p in positions]
        upcoming_earnings = EarningsEvent.objects.filter(
            asset_id__in=asset_ids,
            earnings_date__gte=timezone.now(),
            earnings_date__lte=timezone.now() + timedelta(days=30)
        )
        
        total_exposure = 0
        high_impact = []
        by_sector = {}
        
        for earning in upcoming_earnings:
            position = positions.filter(asset_id=earning.asset_id).first()
            if not position:
                continue
            
            position_value = position.current_value
            total_exposure += position_value
            
            # Calculate impact score (simplified)
            impact_score = self._calculate_earnings_impact_score(earning, position)
            
            sector = earning.asset.sector or 'Unknown'
            if sector not in by_sector:
                by_sector[sector] = 0
            by_sector[sector] += position_value
            
            if impact_score > 0.7:  # High impact threshold
                high_impact.append({
                    'symbol': earning.asset.symbol,
                    'date': earning.earnings_date.isoformat(),
                    'position_value': float(position_value),
                    'impact_score': impact_score
                })
        
        return {
            'total_exposure': float(total_exposure),
            'high_impact_count': len(high_impact),
            'high_impact_positions': high_impact,
            'by_sector': by_sector
        }
    
    def _calculate_earnings_impact_score(self, earning: EarningsEvent, position) -> float:
        """
        Calculate earnings impact score (0-1)
        
        Factors:
        - Position size relative to portfolio
        - Historical earnings surprise
        - Options implied move
        """
        score = 0.5  # Base score
        
        # Position size factor (larger positions = higher impact)
        portfolio_value = position.portfolio.current_value
        position_weight = position.current_value / portfolio_value if portfolio_value > 0 else 0
        score += min(position_weight * 2, 0.3)  # Up to 0.3 bonus
        
        # Historical surprise factor
        if earning.eps_surprise:
            surprise_abs = abs(earning.eps_surprise)
            score += min(surprise_abs / 50, 0.2)  # Up to 0.2 bonus
        
        return min(score, 1.0)
    
    def get_dividend_projection(self, asset_id: int, periods: int = 4) -> Dict:
        """
        Project future dividend payments based on history
        
        Returns: {next_ex_date, next_amount, projection_next_12_months}
        """
        dividends = DividendHistory.objects.filter(
            asset_id=asset_id
        ).order_by('-ex_dividend_date')[:12]
        
        if not dividends:
            return {}
        
        # Calculate average dividend
        avg_dividend = sum(d.amount for d in dividends) / len(dividends)
        
        # Estimate frequency
        most_recent = dividends[0]
        frequency = most_recent.frequency or 'quarterly'
        
        # Project next 12 months
        frequency_map = {
            'monthly': 12,
            'quarterly': 4,
            'annual': 1
        }
        periods_per_year = frequency_map.get(frequency, 4)
        
        projected_annual = avg_dividend * periods_per_year
        
        return {
            'last_amount': float(dividends[0].amount),
            'last_ex_date': dividends[0].ex_dividend_date.isoformat(),
            'average_amount': float(avg_dividend),
            'frequency': frequency,
            'projected_next_12_months': float(projected_annual),
            'yield_percent': None  # Would need current price
        }
```

---

### **Phase 3: API Endpoints** (2-3 hours)

**Create `apps/backend/src/api/corporate_events.py`:**

```python
from ninja import Router
from investments.services.corporate_events_service import CorporateEventsService

router = Router(tags=['corporate_events'])
service = CorporateEventsService()

@router.get("/calendar/earnings")
def earnings_calendar(request, days_ahead: int = 30):
    """Get upcoming earnings calendar"""
    earnings = service.get_upcoming_earnings(days_ahead)
    return earnings

@router.get("/calendar/dividends")
def dividends_calendar(request, portfolio_only: bool = False):
    """Get upcoming dividend payments"""
    user_id = request.auth.id if portfolio_only else None
    dividends = service.get_upcoming_dividends(user_id)
    return dividends

@router.get("/calendar/corporate-actions")
def corporate_actions_calendar(
    request,
    start_date: str = None,
    end_date: str = None,
    action_types: list = None
):
    """Get corporate actions calendar"""
    calendar = service.get_corporate_actions_calendar(start_date, end_date, action_types)
    return calendar

@router.get("/calendar/economic")
def economic_calendar(
    request,
    start_date: str = None,
    end_date: str = None,
    importance: str = None
):
    """Get economic calendar"""
    events = service.get_economic_calendar(start_date, end_date, importance)
    return events

@router.get("/portfolios/{portfolio_id}/earnings-impact")
def earnings_impact_analysis(request, portfolio_id: int):
    """Analyze earnings impact on portfolio"""
    impact = service.analyze_earnings_impact(portfolio_id)
    return impact

@router.get("/assets/{asset_id}/dividend-projection")
def dividend_projection(request, asset_id: int, periods: int = 4):
    """Get dividend projection for asset"""
    projection = service.get_dividend_projection(asset_id, periods)
    return projection

@router.get("/assets/{asset_id}/corporate-actions")
def asset_corporate_actions(request, asset_id: int):
    """Get corporate actions for specific asset"""
    from investments.models.corporate_events import CorporateAction
    
    actions = CorporateAction.objects.filter(
        asset_id=asset_id
    ).order_by('-announcement_date')[:20]
    
    return [{
        'type': a.action_type,
        'status': a.status,
        'announcement_date': a.announcement_date.isoformat(),
        'details': a.details,
        'description': a.description
    } for a in actions]

@router.get("/assets/{asset_id}/earnings-history")
def earnings_history(request, asset_id: int, limit: int = 8):
    """Get earnings history for asset"""
    from investments.models.corporate_events import EarningsEvent
    
    earnings = EarningsEvent.objects.filter(
        asset_id=asset_id
    ).order_by('-earnings_date')[:limit]
    
    return [{
        'quarter': f"{e.fiscal_year} {e.fiscal_quarter}",
        'date': e.earnings_date.isoformat(),
        'estimated_eps': float(e.estimated_eps) if e.estimated_eps else None,
        'actual_eps': float(e.actual_eps) if e.actual_eps else None,
        'surprise_pct': float(e.eps_surprise) if e.eps_surprise else None,
        'revenue': float(e.actual_revenue) if e.actual_revenue else None
    } for e in earnings]
```

---

### **Phase 4: Data Scraping/Import** (2-3 hours)

**Create `apps/backend/src/investments/scrapers/corporate_events_scraper.py`:**

```python
import dramatiq
from datetime import datetime, timedelta
from investments.services.corporate_events_service import CorporateEventsService
from investments.models.corporate_events import EarningsEvent, CorporateAction

@dramatiq.actor
def scrape_earnings_calendar():
    """Scrape earnings calendar from external sources"""
    # Implement scraping from:
    # - Yahoo Finance earnings calendar
    # - Nasdaq earnings calendar
    # - EarningsWhispers
    pass

@dramatiq.actor
def scrape_corporate_actions():
    """Scrape corporate actions from external sources"""
    # Implement scraping from:
    # - Yahoo Finance corporate actions
    # - SEC filings (EDGAR)
    pass

@dramatiq.actor
def scrape_economic_calendar():
    """Scrape economic calendar from external sources"""
    # Implement scraping from:
    # - Forex Factory economic calendar
    # - Investing.com economic calendar
    # - Bloomberg economic calendar
    pass
```

---

## 📋 DELIVERABLES

- [ ] EarningsEvent, CorporateAction, DividendHistory, EconomicEvent, EventAlert models
- [ ] CorporateEventsService with 7 methods
- [ ] 8 API endpoints
- [ ] Earnings impact analysis
- [ ] Dividend projection
- [ ] Corporate actions calendar (grouped by date)
- [ ] Economic calendar with importance filter
- [ ] Scraping tasks (Dramatiq)
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Earnings calendar shows next 30 days
- [ ] Corporate actions grouped by date
- [ ] Economic calendar filterable by importance
- [ ] Earnings impact analysis calculates exposure
- [ ] Dividend projection estimates next 12 months
- [ ] Asset-specific actions and earnings history
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Calendar data <1 second to load
- Support for 1000+ events
- Impact analysis <500ms for 100 positions
- Scraping updates daily

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/024-earnings-corporate-events-tracker.md
