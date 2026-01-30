# C-028: IPO Calendar & New Listings Tracker

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 10-14 hours  
**Dependencies:** C-005 (Backend Improvements), C-027 (Universal Search)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive IPO calendar and new listings tracker with upcoming IPOs, historical IPO data, pricing information, and subscription alerts for new investment opportunities.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 1.1 - Asset Search & Screening):**

- New IPO calendar
- Stock/currency/commodity universe coverage

**From Features Specification (Section 6.2 - Research Tools):**

- IPO calendar
- Economic calendar (FOMC, GDP, CPI, etc.)

---

## ✅ CURRENT STATE

**What exists:**
- Basic asset tracking
- Price data for existing assets

**What's missing:**
- IPO calendar functionality
- Upcoming IPO listings
- Historical IPO performance tracking
- IPO alerts and notifications
- IPO pricing details

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (2-3 hours)

**Create `apps/backend/src/investments/models/ipo.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .asset import Asset

User = get_user_model()

class IPOCalendar(models.Model):
    """Upcoming and historical IPOs"""
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('priced', 'Priced'),
        ('listed', 'Listed'),
        ('withdrawn', 'Withdrawn'),
        ('postponed', 'Postponed'),
    ]
    
    # Company information
    company_name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=20, blank=True)  # Assigned ticker
    exchange = models.CharField(max_length=50, blank=True)  # NYSE, NASDAQ, etc.
    
    # IPO details
    expected_price_min = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    expected_price_max = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    actual_price = models.DecimalField(max_digits=20, decimal_digits=2, null=True)
    shares_offered = models.IntegerField(null=True)  # Number of shares
    deal_size = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Total deal value
    
    # Dates
    filed_date = models.DateField(null=True, blank=True)  # When S-1 was filed
    expected_date = models.DateField(null=True, blank=True)  # Expected IPO date
    priced_date = models.DateField(null=True, blank=True)  # Actual pricing date
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Company details
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    # Underwriters
    lead_underwriter = models.CharField(max_length=200, blank=True)
    underwriters = models.JSONField(default=list)  # ["Goldman Sachs", "Morgan Stanley", ...]
    
    # Market cap and valuation
    expected_valuation = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    
    # Lock-up period
    lockup_expiration_date = models.DateField(null=True, blank=True)
    
    # Performance (for listed IPOs)
    first_day_close = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    first_day_change_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to asset if listed
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['expected_date']
        indexes = [
            models.Index(fields=['expected_date', 'status']),
            models.Index(fields=['status', '-expected_date']),
            models.Index(fields=['sector', 'status']),
        ]

class IPOSubscription(models.Model):
    """User subscriptions for IPO alerts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ipo_subscriptions')
    
    # Subscription settings
    notify_upcoming = models.BooleanField(default=True)
    notify_priced = models.BooleanField(default=True)
    notify_listed = models.BooleanField(default=True)
    
    # Filters
    sectors = models.JSONField(default=list)  # Only specific sectors
    min_deal_size = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Minimum deal size
    exchanges = models.JSONField(default=list)  # Specific exchanges
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

class IPOAlert(models.Model):
    """Sent IPO alerts to users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ipo_alerts')
    ipo = models.ForeignKey(IPOCalendar, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=20)  # upcoming, priced, listed
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Delivery status
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    # User action
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    clicked = models.BooleanField(default=False)  # Clicked through to view details
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['ipo', 'user']),
        ]

class IPOPerformance(models.Model):
    """Track IPO performance over time"""
    
    ipo = models.OneToOneField(IPOCalendar, on_delete=models.CASCADE, related_name='performance')
    
    # Performance metrics at various intervals
    price_1_week = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_1_week_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    price_1_month = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_1_month_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    price_3_month = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_3_month_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    price_6_month = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_6_month_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    price_1_year = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_1_year_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # All-time high/low
    all_time_high = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    all_time_high_date = models.DateField(null=True, blank=True)
    all_time_low = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    all_time_low_date = models.DateField(null=True, blank=True)
    
    # Current status
    current_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    current_change_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['ipo']),
        ]
```

---

### **Phase 2: IPO Service** (4-5 hours)

**Create `apps/backend/src/investments/services/ipo_service.py`:**

```python
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from investments.models.ipo import IPOCalendar, IPOSubscription, IPOAlert, IPOPerformance
from investments.models.asset import Asset
from investments.services.notification_service import NotificationService

class IPOService:
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def get_ipo_calendar(
        self,
        status: str = 'upcoming',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sector: Optional[str] = None,
        exchange: Optional[str] = None
    ) -> List[Dict]:
        """
        Get IPO calendar with filters
        
        Returns: List of IPOs with details
        """
        queryset = IPOCalendar.objects.filter(status=status)
        
        if start_date:
            queryset = queryset.filter(expected_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(expected_date__lte=end_date)
        
        if sector:
            queryset = queryset.filter(sector=sector)
        
        if exchange:
            queryset = queryset.filter(exchange=exchange)
        
        ipos = queryset.order_by('expected_date')
        
        return [self._format_ipo(ipo) for ipo in ipos]
    
    def get_ipo_details(self, ipo_id: int) -> Dict:
        """Get detailed information about specific IPO"""
        try:
            ipo = IPOCalendar.objects.get(id=ipo_id)
        except IPOCalendar.DoesNotExist:
            return None
        
        details = self._format_ipo(ipo)
        
        # Add performance data if available
        if hasattr(ipo, 'performance'):
            details['performance'] = self._format_performance(ipo.performance)
        
        return details
    
    def _format_ipo(self, ipo: IPOCalendar) -> Dict:
        """Format IPO data for API response"""
        return {
            'id': ipo.id,
            'company_name': ipo.company_name,
            'ticker': ipo.ticker,
            'exchange': ipo.exchange,
            'expected_price_min': float(ipo.expected_price_min) if ipo.expected_price_min else None,
            'expected_price_max': float(ipo.expected_price_max) if ipo.expected_price_max else None,
            'actual_price': float(ipo.actual_price) if ipo.actual_price else None,
            'shares_offered': ipo.shares_offered,
            'deal_size': float(ipo.deal_size) if ipo.deal_size else None,
            'filed_date': ipo.filed_date.isoformat() if ipo.filed_date else None,
            'expected_date': ipo.expected_date.isoformat() if ipo.expected_date else None,
            'priced_date': ipo.priced_date.isoformat() if ipo.priced_date else None,
            'status': ipo.status,
            'sector': ipo.sector,
            'industry': ipo.industry,
            'description': ipo.description,
            'lead_underwriter': ipo.lead_underwriter,
            'underwriters': ipo.underwriters,
            'expected_valuation': float(ipo.expected_valuation) if ipo.expected_valuation else None,
            'lockup_expiration_date': ipo.lockup_expiration_date.isoformat() if ipo.lockup_expiration_date else None,
            'first_day_close': float(ipo.first_day_close) if ipo.first_day_close else None,
            'first_day_change_pct': float(ipo.first_day_change_pct) if ipo.first_day_change_pct else None,
        }
    
    def _format_performance(self, performance: IPOPerformance) -> Dict:
        """Format performance data"""
        return {
            'price_1_week': float(performance.price_1_week) if performance.price_1_week else None,
            'change_1_week_pct': float(performance.change_1_week_pct) if performance.change_1_week_pct else None,
            'price_1_month': float(performance.price_1_month) if performance.price_1_month else None,
            'change_1_month_pct': float(performance.change_1_month_pct) if performance.change_1_month_pct else None,
            'price_3_month': float(performance.price_3_month) if performance.price_3_month else None,
            'change_3_month_pct': float(performance.change_3_month_pct) if performance.change_3_month_pct else None,
            'price_6_month': float(performance.price_6_month) if performance.price_6_month else None,
            'change_6_month_pct': float(performance.change_6_month_pct) if performance.change_6_month_pct else None,
            'price_1_year': float(performance.price_1_year) if performance.price_1_year else None,
            'change_1_year_pct': float(performance.change_1_year_pct) if performance.change_1_year_pct else None,
            'all_time_high': float(performance.all_time_high) if performance.all_time_high else None,
            'all_time_high_date': performance.all_time_high_date.isoformat() if performance.all_time_high_date else None,
            'all_time_low': float(performance.all_time_low) if performance.all_time_low else None,
            'all_time_low_date': performance.all_time_low_date.isoformat() if performance.all_time_low_date else None,
            'current_price': float(performance.current_price) if performance.current_price else None,
            'current_change_pct': float(performance.current_change_pct) if performance.current_change_pct else None,
        }
    
    @transaction.atomic
    def create_ipo(self, data: Dict) -> Dict:
        """Create new IPO listing"""
        ipo = IPOCalendar.objects.create(
            company_name=data['company_name'],
            ticker=data.get('ticker'),
            exchange=data.get('exchange'),
            expected_price_min=data.get('expected_price_min'),
            expected_price_max=data.get('expected_price_max'),
            shares_offered=data.get('shares_offered'),
            deal_size=data.get('deal_size'),
            filed_date=data.get('filed_date'),
            expected_date=data.get('expected_date'),
            sector=data.get('sector'),
            industry=data.get('industry'),
            description=data.get('description'),
            lead_underwriter=data.get('lead_underwriter'),
            underwriters=data.get('underwriters', []),
            expected_valuation=data.get('expected_valuation'),
            lockup_expiration_date=data.get('lockup_expiration_date'),
        )
        
        return {'id': ipo.id, 'status': 'created'}
    
    @transaction.atomic
    def update_ipo_status(
        self,
        ipo_id: int,
        status: str,
        actual_price: Optional[float] = None,
        priced_date: Optional[date] = None
    ) -> Dict:
        """Update IPO status (priced, listed, withdrawn)"""
        ipo = IPOCalendar.objects.get(id=ipo_id)
        
        ipo.status = status
        
        if actual_price:
            ipo.actual_price = Decimal(str(actual_price))
        
        if priced_date:
            ipo.priced_date = priced_date
        
        ipo.save()
        
        # If listed, link to asset
        if status == 'listed' and ipo.ticker:
            try:
                asset = Asset.objects.get(symbol=ipo.ticker)
                ipo.asset = asset
                ipo.save()
                
                # Create performance tracking
                IPOPerformance.objects.create(ipo=ipo)
                
                # Calculate first day performance
                self._calculate_first_day_performance(ipo)
                
            except Asset.DoesNotExist:
                pass
        
        # Send alerts to subscribers
        self._send_ipo_alerts(ipo, status)
        
        return {'id': ipo.id, 'status': status}
    
    def _calculate_first_day_performance(self, ipo: IPOCalendar):
        """Calculate first day performance for IPO"""
        if not ipo.asset or not ipo.actual_price:
            return
        
        try:
            # Get first day's price data
            from investments.models.price import AssetPricesHistoric
            first_price = AssetPricesHistoric.objects.filter(
                asset=ipo.asset
            ).order_by('timestamp').first()
            
            if first_price:
                ipo.first_day_close = first_price.close
                ipo.first_day_change_pct = ((first_price.close - ipo.actual_price) / ipo.actual_price * 100)
                ipo.save()
        except:
            pass
    
    def _send_ipo_alerts(self, ipo: IPOCalendar, alert_type: str):
        """Send alerts to subscribers"""
        subscriptions = IPOSubscription.objects.filter(
            email_notifications=True
        )
        
        for subscription in subscriptions:
            # Check if IPO matches user's filters
            if not self._matches_subscription_filters(ipo, subscription):
                continue
            
            # Create alert
            alert = IPOAlert.objects.create(
                user=subscription.user,
                ipo=ipo,
                alert_type=alert_type
            )
            
            # Send notification
            message = self._generate_alert_message(ipo, alert_type)
            subject = f"IPO Alert: {ipo.company_name}"
            
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
    
    def _matches_subscription_filters(self, ipo: IPOCalendar, subscription: IPOSubscription) -> bool:
        """Check if IPO matches user's subscription filters"""
        # Check sector filter
        if subscription.sectors and ipo.sector not in subscription.sectors:
            return False
        
        # Check deal size filter
        if subscription.min_deal_size and ipo.deal_size and ipo.deal_size < subscription.min_deal_size:
            return False
        
        # Check exchange filter
        if subscription.exchanges and ipo.exchange not in subscription.exchanges:
            return False
        
        return True
    
    def _generate_alert_message(self, ipo: IPOCalendar, alert_type: str) -> str:
        """Generate alert message"""
        if alert_type == 'upcoming':
            message = f"Upcoming IPO: {ipo.company_name}\n"
            message += f"Expected Date: {ipo.expected_date}\n"
            message += f"Expected Price Range: ${ipo.expected_price_min} - ${ipo.expected_price_max}\n"
            message += f"Sector: {ipo.sector}\n"
        elif alert_type == 'priced':
            message = f"IPO Priced: {ipo.company_name} ({ipo.ticker})\n"
            message += f"IPO Price: ${ipo.actual_price}\n"
            message += f"Expected to trade on: {ipo.exchange}\n"
        elif alert_type == 'listed':
            message = f"Now Trading: {ipo.company_name} ({ipo.ticker})\n"
            message += f"Exchange: {ipo.exchange}\n"
            if ipo.first_day_change_pct:
                message += f"First Day Change: {ipo.first_day_change_pct}%\n"
        
        return message
    
    def subscribe_to_ipo_alerts(
        self,
        user_id: int,
        notify_upcoming: bool = True,
        notify_priced: bool = True,
        notify_listed: bool = True,
        sectors: Optional[List[str]] = None,
        min_deal_size: Optional[float] = None,
        exchanges: Optional[List[str]] = None
    ) -> Dict:
        """Subscribe user to IPO alerts"""
        subscription, created = IPOSubscription.objects.update_or_create(
            user_id=user_id,
            defaults={
                'notify_upcoming': notify_upcoming,
                'notify_priced': notify_priced,
                'notify_listed': notify_listed,
                'sectors': sectors or [],
                'min_deal_size': Decimal(str(min_deal_size)) if min_deal_size else None,
                'exchanges': exchanges or [],
            }
        )
        
        return {
            'id': subscription.id,
            'status': 'created' if created else 'updated'
        }
    
    def get_subscription(self, user_id: int) -> Dict:
        """Get user's IPO subscription settings"""
        try:
            subscription = IPOSubscription.objects.get(user_id=user_id)
            return {
                'notify_upcoming': subscription.notify_upcoming,
                'notify_priced': subscription.notify_priced,
                'notify_listed': subscription.notify_listed,
                'sectors': subscription.sectors,
                'min_deal_size': float(subscription.min_deal_size) if subscription.min_deal_size else None,
                'exchanges': subscription.exchanges,
            }
        except IPOSubscription.DoesNotExist:
            return None
    
    def get_ipo_statistics(self) -> Dict:
        """Get IPO market statistics"""
        from django.db.models import Count, Avg, Sum
        
        # Upcoming IPOs
        upcoming_count = IPOCalendar.objects.filter(status='upcoming').count()
        
        # Priced this month
        this_month = date.today().replace(day=1)
        priced_this_month = IPOCalendar.objects.filter(
            status='priced',
            priced_date__gte=this_month
        ).count()
        
        # Total deal size for upcoming IPOs
        total_deal_size = IPOCalendar.objects.filter(
            status='upcoming'
        ).aggregate(total=Sum('deal_size'))['total'] or 0
        
        # Average first day performance
        avg_first_day_change = IPOCalendar.objects.filter(
            status='listed',
            first_day_change_pct__isnull=False
        ).aggregate(avg=Avg('first_day_change_pct'))['avg']
        
        # Top sectors
        top_sectors = IPOCalendar.objects.filter(
            status='upcoming'
        ).values('sector').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'upcoming_count': upcoming_count,
            'priced_this_month': priced_this_month,
            'total_deal_size': float(total_deal_size),
            'avg_first_day_change_pct': float(avg_first_day_change) if avg_first_day_change else None,
            'top_sectors': list(top_sectors),
        }
    
    def update_performance_metrics(self):
        """Update performance metrics for all listed IPOs (scheduled task)"""
        listed_pos = IPOCalendar.objects.filter(
            status='listed',
            asset__isnull=False
        )
        
        for ipo in listed_pos:
            if not hasattr(ipo, 'performance'):
                IPOPerformance.objects.create(ipo=ipo)
            
            performance = ipo.performance
            
            # Get historical prices for each interval
            from investments.models.price import AssetPricesHistoric
            from datetime import timedelta
            
            # Get price history
            price_history = AssetPricesHistoric.objects.filter(
                asset=ipo.asset
            ).order_by('timestamp')
            
            if not price_history.exists():
                continue
            
            ipo_price = float(ipo.actual_price)
            
            # Calculate various interval returns
            today = date.today()
            
            # 1 week
            week_ago = today - timedelta(days=7)
            week_price = price_history.filter(timestamp__date__gte=week_ago).first()
            if week_price:
                performance.price_1_week = week_price.close
                performance.change_1_week_pct = ((week_price.close - ipo_price) / ipo_price * 100)
            
            # 1 month
            month_ago = today - timedelta(days=30)
            month_price = price_history.filter(timestamp__date__gte=month_ago).first()
            if month_price:
                performance.price_1_month = month_price.close
                performance.change_1_month_pct = ((month_price.close - ipo_price) / ipo_price * 100)
            
            # 3 month
            quarter_ago = today - timedelta(days=90)
            quarter_price = price_history.filter(timestamp__date__gte=quarter_ago).first()
            if quarter_price:
                performance.price_3_month = quarter_price.close
                performance.change_3_month_pct = ((quarter_price.close - ipo_price) / ipo_price * 100)
            
            # 6 month
            half_year_ago = today - timedelta(days=180)
            half_year_price = price_history.filter(timestamp__date__gte=half_year_ago).first()
            if half_year_price:
                performance.price_6_month = half_year_price.close
                performance.change_6_month_pct = ((half_year_price.close - ipo_price) / ipo_price * 100)
            
            # 1 year
            year_ago = today - timedelta(days=365)
            year_price = price_history.filter(timestamp__date__gte=year_ago).first()
            if year_price:
                performance.price_1_year = year_price.close
                performance.change_1_year_pct = ((year_price.close - ipo_price) / ipo_price * 100)
            
            # All-time high/low
            all_time_high = price_history.order_by('-close').first()
            if all_time_high:
                performance.all_time_high = all_time_high.close
                performance.all_time_high_date = all_time_high.timestamp.date()
            
            all_time_low = price_history.order_by('close').first()
            if all_time_low:
                performance.all_time_low = all_time_low.close
                performance.all_time_low_date = all_time_low.timestamp.date()
            
            # Current price
            current_price = price_history.order_by('-timestamp').first()
            if current_price:
                performance.current_price = current_price.close
                performance.current_change_pct = ((current_price.close - ipo_price) / ipo_price * 100)
            
            performance.save()
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/ipo.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from investments.services.ipo_service import IPOService

router = Router(tags=['ipo'])
ipo_service = IPOService()

@router.get("/ipo/calendar")
def get_ipo_calendar(
    request,
    status: str = 'upcoming',
    start_date: str = None,
    end_date: str = None,
    sector: str = None,
    exchange: str = None
):
    """Get IPO calendar with filters"""
    from datetime import datetime
    
    start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    
    return ipo_service.get_ipo_calendar(
        status=status,
        start_date=start,
        end_date=end,
        sector=sector,
        exchange=exchange
    )

@router.get("/ipo/{ipo_id}")
def get_ipo_details(request, ipo_id: int):
    """Get detailed IPO information"""
    return ipo_service.get_ipo_details(ipo_id)

@router.get("/ipo/statistics")
def get_ipo_statistics(request):
    """Get IPO market statistics"""
    return ipo_service.get_ipo_statistics()

@router.post("/ipo/subscribe")
def subscribe_ipo_alerts(request, data: dict):
    """Subscribe to IPO alerts"""
    result = ipo_service.subscribe_to_ipo_alerts(
        user_id=request.auth.id,
        notify_upcoming=data.get('notify_upcoming', True),
        notify_priced=data.get('notify_priced', True),
        notify_listed=data.get('notify_listed', True),
        sectors=data.get('sectors'),
        min_deal_size=data.get('min_deal_size'),
        exchanges=data.get('exchanges')
    )
    
    return result

@router.get("/ipo/subscription")
def get_ipo_subscription(request):
    """Get user's IPO subscription"""
    return ipo_service.get_subscription(request.auth.id)

@router.get("/ipo/performance/{ipo_id}")
def get_ipo_performance(request, ipo_id: int):
    """Get IPO performance data"""
    ipo = get_object_or_404(IPOCalendar, id=ipo_id)
    if hasattr(ipo, 'performance'):
        return ipo_service._format_performance(ipo.performance)
    return None
```

---

### **Phase 4: Data Seeding** (1-2 hours)

**Create management command to seed IPO data from public sources**

```python
# apps/backend/management/commands/seed_ipo_data.py
from django.core.management.base import BaseCommand
from investments.services.ipo_service import IPOService
import requests

class Command(BaseCommand):
    help = 'Seed IPO data from public sources'
    
    def handle(self, *args, **options):
        service = IPOService()
        
        # Sample IPO data (in production, fetch from IPO data APIs)
        upcoming_ipos = [
            {
                'company_name': 'TechStartup Inc.',
                'ticker': 'TECH',
                'exchange': 'NASDAQ',
                'expected_price_min': 15.00,
                'expected_price_max': 17.00,
                'shares_offered': 10000000,
                'deal_size': 160000000,
                'expected_date': '2026-02-15',
                'sector': 'Technology',
                'industry': 'Software',
                'description': 'Cloud-based enterprise software',
                'lead_underwriter': 'Goldman Sachs',
                'underwriters': ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan'],
                'expected_valuation': 2000000000,
            },
            # Add more IPOs...
        ]
        
        for ipo_data in upcoming_ipos:
            service.create_ipo(ipo_data)
        
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(upcoming_ipos)} IPOs'))
```

---

## 📋 DELIVERABLES

- [ ] IPOCalendar, IPOSubscription, IPOAlert, IPOPerformance models
- [ ] IPOService with 10+ methods
- [ ] 7 API endpoints
- [ ] IPO alert notification system
- [ ] Performance tracking for listed IPOs
- [ ] IPO statistics and analytics
- [ ] Database migrations
- [ ] Data seeding management command
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] IPO calendar displays upcoming and historical IPOs
- [ ] IPO details show comprehensive information
- [ ] Users can subscribe to IPO alerts with filters
- [ ] Alerts sent when IPOs are priced/listed
- [ ] Performance metrics calculated for listed IPOs
- [ ] Statistics provide market overview
- [ ] All filters working (date range, sector, exchange)
- [ ] Performance updates via scheduled task
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- API response time <500ms
- Support for 100+ upcoming IPOs
- Alert delivery rate >95%
- Performance metrics accurate within 1%
- Statistics calculated <2 seconds

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/028-ipo-calendar-tracker.md
