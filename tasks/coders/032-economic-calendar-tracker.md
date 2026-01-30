# C-032: Economic Calendar & Events Tracker

**Priority:** P0 - CRITICAL  
**Assigned to:** Backend Coder  
**Estimated Time:** 10-14 hours  
**Dependencies:** C-005 (Backend Improvements), C-020 (Alerts System)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive economic calendar tracking major economic events (FOMC, GDP, CPI, employment reports, etc.) with historical data, impact scores, and portfolio impact analysis.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 6.2 - Research Tools):**

- Economic calendar (FOMC, GDP, CPI, etc.)
- Earnings estimates
- Stock screener based on fundamentals

**From Features Specification (Section 6.1 - News Feed):**

- News impact score on assets
- Breaking news alerts

---

## ✅ CURRENT STATE

**What exists:**
- Basic news feed aggregation
- Price data
- Portfolio tracking

**What's missing:**
- Economic calendar functionality
- Economic event tracking
- Historical economic data
- Event impact analysis on portfolios
- Economic data notifications

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (2-3 hours)

**Create `apps/backend/src/investments/models/economic.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class EconomicEvent(models.Model):
    """Economic calendar events"""
    
    EVENT_TYPE_CHOICES = [
        ('monetary_policy', 'Monetary Policy (FOMC)'),
        ('employment', 'Employment (NFP)'),
        ('inflation', 'Inflation (CPI/PPI)'),
        ('gdp', 'GDP Growth'),
        ('retail_sales', 'Retail Sales'),
        ('consumer_confidence', 'Consumer Confidence'),
        ('manufacturing', 'Manufacturing (PMI/ISM)'),
        ('housing', 'Housing Data'),
        ('trade', 'Trade Balance'),
        ('earnings', 'Corporate Earnings'),
        ('other', 'Other Economic Event'),
    ]
    
    IMPORTANCE_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Very High'),
    ]
    
    # Event details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    event_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Country/Region
    country = models.CharField(max_length=5, default='US')  # ISO country code
    currency = models.CharField(max_length=3, default='USD')  # Affected currency
    
    # Importance
    importance = models.IntegerField(choices=IMPORTANCE_CHOICES, default=2)
    
    # Date and time
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True)
    
    # Actual, forecast, previous values
    actual_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    forecast_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    previous_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    
    # Units
    unit = models.CharField(max_length=20, blank=True)  # %, K, B, etc.
    
    # Impact assessment
    deviation_pct = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    better_than_expected = models.BooleanField(null=True)
    
    # Market reaction
    market_reaction_summary = models.JSONField(default=dict, blank=True)
    # Example: {"SP500": "+1.2%", "US10Y": "+0.05%", "DXY": "-0.3%"}
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_date', '-importance']),
            models.Index(fields=['event_type', '-event_date']),
            models.Index(fields=['country', 'event_date']),
        ]
        ordering = ['-event_date', '-importance']

class EconomicEventHistory(models.Model):
    """Historical economic data for analysis"""
    
    event = models.ForeignKey(EconomicEvent, on_delete=models.CASCADE, related_name='history')
    
    # Historical data point
    report_date = models.DateField()
    value = models.DecimalField(max_digits=20, decimal_places=4)
    revision = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    
    # Context
    period = models.CharField(max_length=20)  # e.g., "Q4 2025", "December 2025"
    
    class Meta:
        indexes = [
            models.Index(fields=['event', '-report_date']),
        ]
        ordering = ['-report_date']

class EconomicEventSubscription(models.Model):
    """User subscriptions for economic event alerts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='economic_subscriptions')
    
    # Event filters
    event_types = models.JSONField(default=list)  # Specific event types to track
    countries = models.JSONField(default=list)  # Specific countries
    min_importance = models.IntegerField(default=3)  # Only high importance+
    
    # Notification settings
    notify_before = models.BooleanField(default=True)  # Alert before event
    notify_before_hours = models.IntegerField(default=24)  # Hours before to notify
    notify_after = models.BooleanField(default=True)  # Alert when results released
    
    # Delivery preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    
    # Portfolio impact
    analyze_portfolio_impact = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

class EconomicEventAlert(models.Model):
    """Sent economic event alerts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='economic_alerts')
    event = models.ForeignKey(EconomicEvent, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=20)  # before, after, impact
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Portfolio impact (if analyzed)
    portfolio_impact = models.JSONField(null=True, blank=True)
    # Example: {"expected_change": "+1.5%", "affected_sectors": ["Technology", "Financials"]}
    
    # Delivery status
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    # User engagement
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['event', 'user']),
        ]

class MarketHoliday(models.Model):
    """Market holidays for trading calendar"""
    
    country = models.CharField(max_length=5)
    market = models.CharField(max_length=20)  # NYSE, NASDAQ, LSE, etc.
    holiday_name = models.CharField(max_length=100)
    holiday_date = models.DateField()
    
    # Trading status
    closed_all_day = models.BooleanField(default=True)
    early_close_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['country', 'holiday_date']),
            models.Index(fields=['market', 'holiday_date']),
        ]
```

---

### **Phase 2: Economic Calendar Service** (4-5 hours)

**Create `apps/backend/src/investments/services/economic_service.py`:**

```python
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.db import transaction
from django.db.models import Q, Avg
from django.utils import timezone
from investments.models.economic import (
    EconomicEvent, EconomicEventHistory, 
    EconomicEventSubscription, EconomicEventAlert, MarketHoliday
)
from investments.services.notification_service import NotificationService

class EconomicCalendarService:
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def get_economic_calendar(
        self,
        start_date: date,
        end_date: date,
        country: str = 'US',
        min_importance: int = 2,
        event_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get economic calendar for date range
        
        Returns: List of economic events with details
        """
        queryset = EconomicEvent.objects.filter(
            event_date__gte=start_date,
            event_date__lte=end_date,
            country=country,
            importance__gte=min_importance
        )
        
        if event_types:
            queryset = queryset.filter(event_type__in=event_types)
        
        events = queryset.order_by('-event_date', '-importance')
        
        return [self._format_event(event) for event in events]
    
    def _format_event(self, event: EconomicEvent) -> Dict:
        """Format economic event for API response"""
        # Calculate deviation if we have actual and forecast
        deviation_pct = None
        if event.actual_value and event.forecast_value and event.forecast_value != 0:
            deviation_pct = float((event.actual_value - event.forecast_value) / event.forecast_value * 100)
        
        # Determine if better than expected
        better_than_expected = None
        if deviation_pct is not None:
            # For employment, GDP, retail sales: higher is better
            # For inflation: lower is better
            if event.event_type == 'inflation':
                better_than_expected = deviation_pct < 0
            else:
                better_than_expected = deviation_pct > 0
        
        return {
            'id': event.id,
            'event_type': event.event_type,
            'event_name': event.event_name,
            'description': event.description,
            'country': event.country,
            'currency': event.currency,
            'importance': event.importance,
            'event_date': event.event_date.isoformat(),
            'event_time': event.event_time.strftime('%H:%M') if event.event_time else None,
            'actual_value': float(event.actual_value) if event.actual_value else None,
            'forecast_value': float(event.forecast_value) if event.forecast_value else None,
            'previous_value': float(event.previous_value) if event.previous_value else None,
            'unit': event.unit,
            'deviation_pct': deviation_pct,
            'better_than_expected': better_than_expected,
            'market_reaction': event.market_reaction_summary
        }
    
    @transaction.atomic
    def create_economic_event(self, data: Dict) -> Dict:
        """Create new economic event"""
        event = EconomicEvent.objects.create(
            event_type=data['event_type'],
            event_name=data['event_name'],
            description=data.get('description', ''),
            country=data.get('country', 'US'),
            currency=data.get('currency', 'USD'),
            importance=data.get('importance', 2),
            event_date=data['event_date'],
            event_time=data.get('event_time'),
            forecast_value=data.get('forecast_value'),
            previous_value=data.get('previous_value'),
            unit=data.get('unit', '')
        )
        
        return {'id': event.id, 'status': 'created'}
    
    @transaction.atomic
    def update_event_results(
        self,
        event_id: int,
        actual_value: float,
        market_reaction: Optional[Dict] = None
    ) -> Dict:
        """
        Update event with actual results
        Triggers alerts to subscribers
        """
        event = EconomicEvent.objects.get(id=event_id)
        event.actual_value = Decimal(str(actual_value))
        
        # Calculate deviation
        if event.forecast_value:
            event.deviation_pct = Decimal(str(
                (actual_value - float(event.forecast_value)) / float(event.forecast_value) * 100
            ))
            
            # Determine if better than expected
            if event.event_type == 'inflation':
                event.better_than_expected = event.deviation_pct < 0
            else:
                event.better_than_expected = event.deviation_pct > 0
        
        if market_reaction:
            event.market_reaction_summary = market_reaction
        
        event.save()
        
        # Add to history
        EconomicEventHistory.objects.create(
            event=event,
            report_date=event.event_date,
            value=Decimal(str(actual_value)),
            period=data.get('period', f"{event.event_date.strftime('%B %Y')}")
        )
        
        # Send alerts to subscribers
        self._send_event_alerts(event, 'after')
        
        return {'id': event.id, 'status': 'updated'}
    
    def get_upcoming_events(
        self,
        days_ahead: int = 7,
        country: str = 'US'
    ) -> List[Dict]:
        """Get upcoming high-impact events"""
        end_date = date.today() + timedelta(days=days_ahead)
        
        events = EconomicEvent.objects.filter(
            event_date__gte=date.today(),
            event_date__lte=end_date,
            country=country,
            importance__gte=3
        ).order_by('event_date', '-importance')
        
        return [self._format_event(event) for event in events]
    
    def get_event_history(
        self,
        event_type: str,
        country: str = 'US',
        periods: int = 12
    ) -> List[Dict]:
        """Get historical data for specific event type"""
        events = EconomicEvent.objects.filter(
            event_type=event_type,
            country=country
        ).order_by('-event_date')[:periods]
        
        history = []
        for event in events:
            historical_records = EconomicEventHistory.objects.filter(
                event=event
            ).order_by('-report_date')[:1]
            
            if historical_records:
                record = historical_records[0]
                history.append({
                    'date': record.report_date.isoformat(),
                    'period': record.period,
                    'value': float(record.value),
                    'revision': float(record.revision) if record.revision else None
                })
        
        return history
    
    def analyze_portfolio_impact(
        self,
        event: EconomicEvent,
        portfolio
    ) -> Dict:
        """
        Analyze expected impact of economic event on portfolio
        Based on sector exposure and historical correlations
        """
        from investments.models.portfolio import PortfolioPosition
        
        # Get portfolio positions
        positions = PortfolioPosition.objects.filter(
            portfolio=portfolio,
            is_open=True
        ).select_related('asset')
        
        # Define sector sensitivities to economic events
        sector_sensitivities = {
            'monetary_policy': {
                'Financials': 1.5,      # Highly sensitive to rates
                'Real Estate': -1.2,    # Negative correlation
                'Technology': -0.8,
                'Utilities': -1.0,
            },
            'employment': {
                'Consumer Discretionary': 1.2,
                'Financials': 0.8,
                'Industrials': 1.0,
                'Technology': 0.5,
            },
            'inflation': {
                'Energy': 1.3,
                'Materials': 1.1,
                'Financials': 0.7,
                'Real Estate': -0.9,
                'Technology': -0.6,
            },
            'gdp': {
                'Industrials': 1.2,
                'Consumer Discretionary': 1.1,
                'Materials': 1.0,
                'Technology': 0.8,
            }
        }
        
        sensitivities = sector_sensitivities.get(event.event_type, {})
        
        # Calculate sector exposure
        sector_exposure = {}
        portfolio_value = 0
        
        for position in positions:
            sector = position.asset.sector or 'Other'
            value = position.quantity * position.asset.current_price
            
            if sector not in sector_exposure:
                sector_exposure[sector] = Decimal('0')
            sector_exposure[sector] += value
            portfolio_value += value
        
        # Calculate weighted impact
        expected_impacts = []
        for sector, exposure in sector_exposure.items():
            weight = float(exposure / portfolio_value) if portfolio_value > 0 else 0
            sensitivity = sensitivities.get(sector, 0)
            
            # If event has actual value, calculate impact
            if event.actual_value and event.forecast_value:
                deviation = float(event.deviation_pct) / 100  # Convert to decimal
                impact = deviation * sensitivity * weight * 100  # % impact
                expected_impacts.append({
                    'sector': sector,
                    'exposure_pct': weight * 100,
                    'sensitivity': sensitivity,
                    'expected_impact_pct': impact
                })
        
        # Calculate total expected portfolio change
        total_impact = sum(item['expected_impact_pct'] for item in expected_impacts)
        
        # Sort by absolute impact
        expected_impacts.sort(key=lambda x: abs(x['expected_impact_pct']), reverse=True)
        
        return {
            'expected_change_pct': total_impact,
            'affected_sectors': [item['sector'] for item in expected_impacts[:5]],
            'sector_breakdown': expected_impacts[:5]
        }
    
    def subscribe_to_events(
        self,
        user_id: int,
        event_types: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        min_importance: int = 3,
        notify_before: bool = True,
        notify_after: bool = True,
        analyze_impact: bool = True
    ) -> Dict:
        """Subscribe user to economic event alerts"""
        subscription, created = EconomicEventSubscription.objects.update_or_create(
            user_id=user_id,
            defaults={
                'event_types': event_types or [],
                'countries': countries or ['US'],
                'min_importance': min_importance,
                'notify_before': notify_before,
                'notify_after': notify_after,
                'analyze_portfolio_impact': analyze_impact
            }
        )
        
        return {
            'id': subscription.id,
            'status': 'created' if created else 'updated'
        }
    
    def _send_event_alerts(self, event: EconomicEvent, alert_type: str):
        """Send alerts to subscribers"""
        subscriptions = EconomicEventSubscription.objects.filter(
            email_notifications=True
        )
        
        for subscription in subscriptions:
            # Check if event matches subscription filters
            if not self._matches_subscription_filters(event, subscription):
                continue
            
            # For 'after' alerts, analyze portfolio impact if requested
            portfolio_impact = None
            if alert_type == 'after' and subscription.analyze_portfolio_impact:
                # Get user's main portfolio
                from investments.models.portfolio import Portfolio
                portfolio = Portfolio.objects.filter(
                    user=subscription.user
                ).first()
                
                if portfolio:
                    portfolio_impact = self.analyze_portfolio_impact(event, portfolio)
            
            # Create alert
            alert = EconomicEventAlert.objects.create(
                user=subscription.user,
                event=event,
                alert_type=alert_type,
                portfolio_impact=portfolio_impact
            )
            
            # Send notification
            message = self._generate_alert_message(event, alert_type, portfolio_impact)
            subject = f"Economic Alert: {event.event_name}"
            
            try:
                self.notification_service.send_email(
                    user=subscription.user,
                    subject=subject,
                    message=message
                )
                alert.email_sent = True
                alert.email_sent_at = timezone.now()
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            alert.save()
    
    def _matches_subscription_filters(
        self,
        event: EconomicEvent,
        subscription: EconomicEventSubscription
    ) -> bool:
        """Check if event matches subscription filters"""
        # Check importance
        if event.importance < subscription.min_importance:
            return False
        
        # Check event types
        if subscription.event_types and event.event_type not in subscription.event_types:
            return False
        
        # Check countries
        if subscription.countries and event.country not in subscription.countries:
            return False
        
        return True
    
    def _generate_alert_message(
        self,
        event: EconomicEvent,
        alert_type: str,
        portfolio_impact: Optional[Dict]
    ) -> str:
        """Generate alert message"""
        if alert_type == 'before':
            message = f"Upcoming Economic Event: {event.event_name}\n"
            message += f"Date: {event.event_date}\n"
            message += f"Time: {event.event_time}\n" if event.event_time else ""
            message += f"Forecast: {event.forecast_value}\n" if event.forecast_value else ""
            message += f"Previous: {event.previous_value}\n" if event.previous_value else ""
            message += f"Importance: {event.get_importance_display()}\n"
        elif alert_type == 'after':
            message = f"Economic Event Released: {event.event_name}\n"
            message += f"Actual: {event.actual_value}\n"
            message += f"Forecast: {event.forecast_value}\n" if event.forecast_value else ""
            if event.deviation_pct:
                direction = "above" if event.better_than_expected else "below"
                message += f"Result: {abs(float(event.deviation_pct)):.1f}% {direction} expectations\n"
            if event.market_reaction_summary:
                message += f"\nMarket Reaction: {event.market_reaction_summary}\n"
            if portfolio_impact:
                message += f"\nExpected Portfolio Impact: {portfolio_impact['expected_change_pct']:.2f}%\n"
                if portfolio_impact['affected_sectors']:
                    message += f"Affected Sectors: {', '.join(portfolio_impact['affected_sectors'])}\n"
        
        return message
    
    def get_market_holidays(
        self,
        country: str = 'US',
        market: str = 'NYSE',
        start_date: date = None,
        end_date: date = None
    ) -> List[Dict]:
        """Get market holidays"""
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=365)
        
        holidays = MarketHoliday.objects.filter(
            country=country,
            market=market,
            holiday_date__gte=start_date,
            holiday_date__lte=end_date
        ).order_by('holiday_date')
        
        return [
            {
                'holiday_name': h.holiday_name,
                'holiday_date': h.holiday_date.isoformat(),
                'closed_all_day': h.closed_all_day,
                'early_close_time': h.early_close_time.strftime('%H:%M') if h.early_close_time else None
            }
            for h in holidays
        ]
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/economic.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.services.economic_service import EconomicCalendarService
from investments.models.economic import EconomicEvent
from datetime import datetime

router = Router(tags=['economic'])
economic_service = EconomicCalendarService()

@router.get("/economic/calendar")
def get_economic_calendar(
    request,
    start_date: str,
    end_date: str,
    country: str = 'US',
    min_importance: int = 2
):
    """Get economic calendar for date range"""
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    return economic_service.get_economic_calendar(
        start_date=start,
        end_date=end,
        country=country,
        min_importance=min_importance
    )

@router.get("/economic/upcoming")
def get_upcoming_events(
    request,
    days_ahead: int = 7,
    country: str = 'US'
):
    """Get upcoming high-impact economic events"""
    return economic_service.get_upcoming_events(days_ahead, country)

@router.get("/economic/event/{event_id}")
def get_event_details(request, event_id: int):
    """Get detailed economic event information"""
    event = get_object_or_404(EconomicEvent, id=event_id)
    return economic_service._format_event(event)

@router.get("/economic/history/{event_type}")
def get_event_history(
    request,
    event_type: str,
    country: str = 'US',
    periods: int = 12
):
    """Get historical data for economic event"""
    return economic_service.get_event_history(event_type, country, periods)

@router.get("/economic/holidays")
def get_market_holidays(
    request,
    country: str = 'US',
    market: str = 'NYSE'
):
    """Get market holidays"""
    return economic_service.get_market_holidays(country, market)

@router.post("/economic/subscribe")
def subscribe_economic_alerts(request, data: dict):
    """Subscribe to economic event alerts"""
    return economic_service.subscribe_to_events(
        user_id=request.auth.id,
        event_types=data.get('event_types'),
        countries=data.get('countries'),
        min_importance=data.get('min_importance', 3),
        notify_before=data.get('notify_before', True),
        notify_after=data.get('notify_after', True),
        analyze_impact=data.get('analyze_impact', True)
    )

@router.get("/economic/portfolio-impact/{event_id}")
def analyze_portfolio_impact(request, event_id: int, portfolio_id: int):
    """Analyze economic event impact on portfolio"""
    event = get_object_or_404(EconomicEvent, id=event_id)
    from investments.models.portfolio import Portfolio
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.auth)
    
    return economic_service.analyze_portfolio_impact(event, portfolio)
```

---

## 📋 DELIVERABLES

- [ ] EconomicEvent, EconomicEventHistory, EconomicEventSubscription, EconomicEventAlert, MarketHoliday models
- [ ] EconomicCalendarService with event tracking and portfolio impact analysis
- [ ] 8 API endpoints for economic calendar
- [ ] Event alert notification system
- [ ] Portfolio impact analysis
- [ ] Database migrations
- [ ] Sample economic data seeding
- [ ] Unit tests (coverage >80%)

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Economic calendar displays events for date range
- [ ] Events filtered by country, importance, type
- [ ] Historical data tracked for each event type
- [ ] Portfolio impact analysis calculates expected changes
- [ ] Sector sensitivities defined for major event types
- [ ] Alerts sent before and after events
- [ ] Market holidays tracked
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- API response time <300ms
- Support for 100+ economic events
- Portfolio impact calculated <500ms
- Alert delivery rate >95%
- Historical data for 5+ years

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/032-economic-calendar-tracker.md
